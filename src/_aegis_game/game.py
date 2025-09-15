import random
import time
from collections.abc import Callable
from typing import cast

import numpy as np
from numpy.typing import NDArray

from _aegis_game.decorator import requires

from .aegis_config import get_feature_value, has_feature
from .agent import Agent
from .agent_controller import AgentController
from .agent_predictions.prediction_handler import PredictionHandler
from .agent_type import AgentType
from .args_parser import LaunchArgs
from .common import Cell, CellInfo, Direction, Location
from .common.objects import Rubble, Survivor
from .constants import Constants
from .game_pb import GamePb
from .id_gen import IDGenerator
from .logger import LOGGER
from .sandbox.sandbox import Sandbox
from .team import Team
from .team_info import TeamInfo
from .types import GameOverReason, MethodDict
from .world import World


class Game:
    def __init__(
        self,
        code: list[Sandbox | None],
        args: LaunchArgs,
        world: World,
        game_pb: GamePb,
    ) -> None:
        random.seed(world.seed)
        self.code: list[Sandbox | None] = code
        self.args: LaunchArgs = args
        self.running: bool = True
        self.reason: GameOverReason | None = None
        self.world: World = world
        self.round: int = 0
        self.id_gen: IDGenerator = IDGenerator()
        self.team_info: TeamInfo = TeamInfo()
        self.team_info.add_lumens(Team.GOOBS, Constants.INITIAL_TEAM_LUMENS)
        self.team_info.add_lumens(Team.VOIDSEERS, Constants.INITIAL_TEAM_LUMENS)
        self.game_pb: GamePb = game_pb
        # key is location, value is team -> num of agents queuing to remove the layer this round
        self._queued_layers_to_remove: dict[Location, dict[Team, int]] = {}
        self._drone_scans: dict[Location, dict[Team, int]] = {}
        self._pending_drone_scans: dict[Location, dict[Team, int]] = {}
        self._prediction_handler: PredictionHandler | None = (
            PredictionHandler(args) if has_feature("ALLOW_AGENT_PREDICTIONS") else None
        )
        self.agents: dict[int, Agent] = {}
        self.team_agents: dict[Team, str] = {}
        if self.args.agent is not None:
            self.team_agents[Team.GOOBS] = self.args.agent
        if self.args.agent2 is not None:
            self.team_agents[Team.VOIDSEERS] = self.args.agent2
        self._init_spawn()

    def _init_spawn(self) -> None:
        if has_feature("ALLOW_AGENT_TYPES"):
            # if agent types enabled, spawn one commander at a random spawn location for each team (team needs to spawn rest of agents)

            spawns = self.get_spawns()
            spawn_loc = random.choice(spawns)

            self._spawn_agents_at(spawn_loc, 1)

        else:
            # if no agent types, spawn commanders up to agent amount specified

            spawns = self.world.init_spawns

            # spawns that need to be filled
            positive_spawns = {loc: amt for loc, amt in spawns.items() if amt > 0}

            remaining = self.args.amount

            for loc, amt in positive_spawns.items():
                # if remaining <= 0:
                #     # really shouldn't be intended by user for this to happen, almost tempted to raise an error here saying "run world with minimum self.args.amount agents"
                #     return

                # to_spawn = min(
                #     amt, remaining
                # )  # should also not have to take the min imo for same reason

                # if we run out of remaining agents before filling all amt's, raise an error
                if remaining < amt:
                    required_agents = sum(amt for amt in positive_spawns.values())
                    msg = f"Not enough agents to fill world spawns! The world requires at least {required_agents} agents, but only {self.args.amount} were provided. Please use {required_agents} agents on this world."
                    raise ValueError(msg)

                self._spawn_agents_at(loc, amt)
                remaining -= amt

            # prio spawns filled, choose from any spawn

            if len(positive_spawns) > 0 and remaining > 0:
                LOGGER.warning(
                    f"Ran world with {self.args.amount} agents, but world only specifies spawns for {sum(amt for amt in positive_spawns.values())} agents. Ensure this was intended usage."
                )

            all_spawns = self.get_spawns()
            while remaining > 0:
                loc = random.choice(all_spawns)
                self._spawn_agents_at(loc, 1)
                remaining -= 1

    def _spawn_agents_at(self, loc: Location, count: int) -> None:
        if self.args.agent is not None:
            for _ in range(count):
                self.spawn_agent(loc, Team.GOOBS, AgentType.COMMANDER)
        if self.args.agent2 is not None:
            for _ in range(count):
                self.spawn_agent(loc, Team.VOIDSEERS, AgentType.COMMANDER)

    def _run_turn(self, agent: Agent) -> None:
        start = time.perf_counter()
        agent.turn()
        end = time.perf_counter()
        duration = end - start
        if duration >= Constants.MAX_TURN_TIME_LIMIT:
            LOGGER.warning(
                f"{agent.id}'s turn took {duration:.2f}s (over {Constants.MAX_TURN_TIME_LIMIT}s limit)"
            )
            self.kill_agent(agent.id)

    def run_round(self) -> None:
        self.tick_drone_scans()
        self.round += 1
        self.game_pb.start_round(self.round)
        self.team_info.add_lumens(Team.GOOBS, Constants.LUMENS_PER_ROUND)
        self.team_info.add_lumens(Team.VOIDSEERS, Constants.LUMENS_PER_ROUND)
        self.for_each_agent(self._run_turn)
        self.rotate_message_buffers()
        self.activate_pending_drone_scans()
        self.game_pb.send_drone_scan_update(self._drone_scans)
        self.apply_survivor_health_decay()
        self.grim_reaper()
        self.serialize_team_info()
        self.serialize_drone_scans()
        self.game_pb.end_round()
        self.check_game_over()

    def rotate_message_buffers(self) -> None:
        """
        Advance all agents' message buffers to the next round.

        This commits any pending messages and ensures that all agents' buffers
        are synchronized for the upcoming round.
        """
        for agent_id in self.agents:
            agent = self.get_agent(agent_id)
            agent.message_buffer.next_round(self.round + 1)

    def check_game_over(self) -> None:
        if self.round == self.world.rounds and self.reason is None:
            self.reason = GameOverReason.MAX_ROUNDS_REACHED

        saved_survs = self.team_info.get_saved(Team.GOOBS)
        saved_survs += self.team_info.get_saved(Team.VOIDSEERS)
        if saved_survs == self.world.total_survivors and self.reason is None:
            self.reason = GameOverReason.ALL_SURVIVORS_SAVED

        if self.reason is not None:
            self.stop()
            if has_feature("ADVANCED_SCORING_SYSTEM"):
                for team in Team:
                    alive_agents = self.team_info.get_units(team)
                    alive_agent_score = alive_agents * Constants.ALIVE_AGENT_SCORE
                    self.team_info.add_score(team, alive_agent_score)

    def grim_reaper(self) -> None:
        dead_agents: list[Agent] = []

        for agent in self.agents.values():
            died = False
            cell = self.get_cell_at(agent.location)
            if agent.energy_level <= 0:
                LOGGER.info("Agent %s ran out of energy and died.\n", agent.id)
                died = True
            elif cell and cell.is_killer_cell():
                LOGGER.info("Agent %s ran into killer cell and died.\n", agent.id)
                died = True

            if died:
                dead_agents.append(agent)

        for agent in dead_agents:
            self.kill_agent(agent.id)

        self.process_layers_queued_to_be_removed()

    def stop(self) -> None:
        self.running = False
        self.for_each_agent(lambda agent: self.kill_agent(agent.id))

    def end_if_no_units(self, _team: Team) -> None:
        if self.reason is not None:
            return

        if len(self.agents) != 0:
            return

        # units = self.team_info.get_units(team)
        # if units != 0:
        #     return

        self.reason = GameOverReason.ALL_AGENTS_DEAD

    def kill_agent(self, agent_id: int) -> None:
        agent = self.agents[agent_id]
        del self.agents[agent_id]
        self.remove_agent_from_loc(agent_id, agent.location)
        agent.kill()
        self.game_pb.add_dead(agent_id)
        self.team_info.add_units(agent.team, -1)
        self.end_if_no_units(agent.team)

    def spawn_agent(
        self,
        loc: Location,
        team: Team,
        agent_type: AgentType,
        agent_id: int | None = None,
    ) -> None:
        agent_id = self.id_gen.next_id() if agent_id is None else agent_id
        energy = int(self.world.start_energy * agent_type.energy_multiplier)
        agent = Agent(self, agent_id, loc, team, energy, agent_type)
        ac = AgentController(self, agent)
        agent.launch(self.code[team.value], self.methods(ac), debug=self.args.debug)
        self.add_agent(agent, loc)
        self.team_info.add_units(agent.team, 1)
        self.game_pb.add_spawn(agent.id, agent.team, agent.location)

    def add_agent(self, agent: Agent, loc: Location) -> None:
        if agent not in self.agents:
            self.agents[agent.id] = agent

            cell = self.get_cell_at(loc)
            cell.agents.append(agent.id)
            LOGGER.info("Added agent %s", agent.id)

    def get_agent(self, agent_id: int) -> Agent:
        return self.agents[agent_id]

    def for_each_agent(self, fn: Callable[[Agent], None]) -> None:
        for agent in list(self.agents.values()):
            fn(agent)

    def queue_layer_to_remove(self, loc: Location, team: Team) -> None:
        # init the Location, so it will have its layer removed this round
        if loc not in self._queued_layers_to_remove:
            self._queued_layers_to_remove[loc] = {}

        # add this team to list of teams wanting to remove the layer this round
        if team not in self._queued_layers_to_remove[loc]:
            self._queued_layers_to_remove[loc][team] = 1
        else:
            self._queued_layers_to_remove[loc][team] += 1

    def process_layers_queued_to_be_removed(self) -> None:
        # check if each loc should actually have its top layer removed this round
        for loc, teams_data in self._queued_layers_to_remove.items():
            # set true if at least one team meets threshold to remove the layer
            will_remove = False
            agents_needed_to_remove = 1
            top_layer = self.get_cell_info_at(loc).top_layer
            if isinstance(top_layer, Rubble):
                agents_needed_to_remove = top_layer.agents_required
            # see if each team met threshold to acc remove the layer
            for team, num_agents_queued in teams_data.items():
                if num_agents_queued >= agents_needed_to_remove:
                    will_remove = True
                    # award team properly for whatever layer they just removed
                    self.reward_layer_removal(loc, team)

            if will_remove:
                # ensures we only call remove_layer ONCE per loc per round
                self.remove_layer(loc)

        self._queued_layers_to_remove.clear()

    def reward_layer_removal(self, loc: Location, team: Team) -> None:
        top_layer = self.get_cell_info_at(loc).top_layer

        if isinstance(top_layer, Survivor):
            points = 0
            decay_rate = get_feature_value("SURV_HEALTH_DECAY_RATE")
            if decay_rate is not None and decay_rate > 0:
                points = top_layer.health
            else:
                points = (
                    Constants.SURVIVOR_SAVE_ALIVE_SCORE
                    if top_layer.is_alive()
                    else Constants.SURVIVOR_SAVE_DEAD_SCORE
                )

            self.team_info.add_saved(team, 1, is_alive=top_layer.is_alive())
            self.team_info.add_score(team, points)

    def remove_layer(self, loc: Location) -> None:
        cell = self.get_cell_at(loc)
        _ = cell.remove_top_layer()
        self.game_pb.add_removed_layer(loc)

    def mark_surrounding_cells_visited(self, agent: Agent, loc: Location) -> None:
        for direction in Direction:
            if direction == Direction.CENTER:
                continue

            new_loc = loc.add(direction)
            if not self.on_map(new_loc):
                continue

            index = new_loc.x + new_loc.y * self.world.width
            agent.has_visited[index] = True

    def add_agent_to_loc(self, agent_id: int, loc: Location) -> None:
        self.get_cell_at(loc).agents.append(agent_id)
        agent = self.get_agent(agent_id)
        if has_feature("HIDDEN_MOVE_COSTS"):
            self.mark_surrounding_cells_visited(agent, loc)

    def remove_agent_from_loc(self, agent_id: int, loc: Location) -> None:
        self.get_cell_at(loc).agents.remove(agent_id)

    def move_agent(self, agent_id: int, start_loc: Location, end_loc: Location) -> None:
        self.remove_agent_from_loc(agent_id, start_loc)
        self.add_agent_to_loc(agent_id, end_loc)

    def start_drone_scan(self, loc: Location, team: Team) -> None:
        if loc not in self._pending_drone_scans:
            self._pending_drone_scans[loc] = {}
        self._pending_drone_scans[loc][team] = Constants.DRONE_SCAN_DURATION

    def activate_pending_drone_scans(self) -> None:
        """Activate pending drone scans by moving them to active drone scans."""
        for loc, teams in self._pending_drone_scans.items():
            if loc not in self._drone_scans:
                self._drone_scans[loc] = {}
            for team, duration in teams.items():
                self._drone_scans[loc][team] = duration
                LOGGER.info(
                    f"Started drone scan at {loc} for team {team.name} with duration of {duration} rounds"
                )
        self._pending_drone_scans.clear()

    def is_loc_drone_scanned(self, loc: Location, team: Team) -> bool:
        return loc in self._drone_scans and team in self._drone_scans[loc]

    def get_drone_scan_duration(self, loc: Location, team: Team) -> int:
        return self._drone_scans[loc][team]

    def tick_drone_scans(self) -> None:
        for loc, teams in self._drone_scans.items():
            for team, duration in list(teams.items()):
                teams[team] = duration - 1
                if teams[team] <= 0:
                    del self._drone_scans[loc][team]

    def serialize_drone_scans(self) -> None:
        """Add all active drone scans to the protobuf data for this round."""
        for loc, teams in self._drone_scans.items():
            for team, duration in teams.items():
                self.game_pb.add_drone_scan(loc, team, duration)

    def apply_survivor_health_decay(self) -> None:
        """Apply health decay to all survivors based on config setting."""
        decay_rate = get_feature_value("SURV_HEALTH_DECAY_RATE")
        if decay_rate is None or decay_rate <= 0:
            return  # Decay rate of 0 turns off health decay

        for cell in self.world.cells:
            for layer in cell.layers:
                if isinstance(layer, Survivor) and layer.is_alive():
                    layer.health = max(0, layer.health - decay_rate)

                    if layer.health <= 0:
                        layer.set_state(Survivor.State.DEAD)
                        LOGGER.info(f"Survivor {layer.id} died from health decay")

                    # Track health change for client (only once per survivor per round)
                    self.game_pb.add_survivor_health_update(
                        cell.location, layer.id, layer.health, layer.get_state().value
                    )

    def save(self, survivor: Survivor, agent: Agent) -> None:
        if (
            agent.location in self._queued_layers_to_remove
            and agent.team in self._queued_layers_to_remove[agent.location]
        ):
            LOGGER.info(
                f"Skipping saving survivor {survivor.id} at {agent.location} for team {agent.team} because someone else on that team saved this surv already"
            )
            return

        agent.add_energy(-Constants.SAVE_ENERGY_COST)
        self.queue_layer_to_remove(agent.location, agent.team)

        LOGGER.info(
            f"Saving survivor {survivor.id} at {agent.location} for team {agent.team.name} on round {self.round}"
        )
        if (
            has_feature("ALLOW_AGENT_PREDICTIONS")
            and self._prediction_handler is not None
        ):
            LOGGER.info(
                f"Creating pending prediction for team {agent.team} and surv_id {survivor.id}"
            )
            self._prediction_handler.create_pending_prediction(
                agent.team,
                survivor.id,
            )

    def dig(self, agent: Agent) -> None:
        rubble_energy_required = cast(
            "Rubble", self.get_cell_info_at(agent.location).top_layer
        ).energy_required
        if agent.energy_level < rubble_energy_required:
            return

        agent.add_energy(-rubble_energy_required)
        self.queue_layer_to_remove(agent.location, agent.team)

    def predict(self, surv_id: int, label: np.int32, agent: Agent) -> None:
        if (
            not has_feature("ALLOW_AGENT_PREDICTIONS")
            or self._prediction_handler is None
        ):
            return

        is_correct = self._prediction_handler.predict(agent.team, surv_id, label)

        if is_correct is None:
            LOGGER.warning(
                f"Agent {agent.id} attempted invalid prediction for surv_id {surv_id}"
            )
            return
        score = Constants.PRED_CORRECT_SCORE if is_correct else 0
        self.team_info.add_score(agent.team, score)
        self.team_info.add_predicted(agent.team, 1, correct=is_correct)

    def on_map(self, loc: Location) -> bool:
        """
        Check whether a location is within the bounds of the world.

        Args:
            loc: The location to check.

        Returns:
            A boolean indicating whetever the given location is on the map.

        """
        return 0 <= loc.x < self.world.width and 0 <= loc.y < self.world.height

    def get_cell_at(self, loc: Location) -> Cell:
        index = loc.x + loc.y * self.world.width
        return self.world.cells[index]

    def get_cell_info_at(self, location: Location) -> CellInfo:
        cell = self.get_cell_at(location)
        return CellInfo(
            cell.layers, cell.type, cell.location, cell.move_cost, cell.agents
        )

    def serialize_team_info(self) -> None:
        self.game_pb.add_team_info(Team.GOOBS, self.team_info)
        self.game_pb.add_team_info(Team.VOIDSEERS, self.team_info)

    def get_survs(self) -> list[Location]:
        """Return a list of survivor locations."""
        return [
            cell.location for cell in self.world.cells if cell.number_of_survivors() > 0
        ]

    @requires("ALLOW_AGENT_TYPES")
    def get_spawns(self) -> list[Location]:
        """Return a list of spawn locations."""
        return [cell.location for cell in self.world.cells if cell.is_spawn()]

    def get_charging_cells(self) -> list[Location]:
        """Return a list of charging locations."""
        return [cell.location for cell in self.world.cells if cell.is_charging_cell()]

    def get_prediction_info_for_agent(
        self, team: Team
    ) -> list[tuple[int, NDArray[np.uint8], NDArray[np.int32]]]:
        if (
            not has_feature("ALLOW_AGENT_PREDICTIONS")
            or self._prediction_handler is None
        ):
            return []
        return self._prediction_handler.read_pending_predictions(team)

    def methods(self, ac: AgentController) -> MethodDict:
        return {
            "AgentType": AgentType,
            "Direction": Direction,
            "Location": Location,
            "Rubble": Rubble,
            "Survivor": Survivor,
            "get_round_number": ac.get_round_number,
            "get_id": ac.get_id,
            "get_type": ac.get_type,
            "get_team": ac.get_team,
            "get_location": ac.get_location,
            "get_energy_level": ac.get_energy_level,
            "get_lumens": ac.get_lumens,
            "get_cell_info_at": ac.get_cell_info_at,
            "send_message": ac.send_message,
            "read_messages": ac.read_messages,
            "drone_scan": ac.drone_scan,
            "move": ac.move,
            "save": ac.save,
            "dig": ac.dig,
            "recharge": ac.recharge,
            "predict": ac.predict,
            "read_pending_predictions": ac.read_pending_predictions,
            "spawn_agent": ac.spawn_agent,
            "on_map": self.on_map,
            "get_charging_cells": self.get_charging_cells,
            "get_spawns": self.get_spawns,
            "get_survs": self.get_survs,
            "log": ac.log,
        }
