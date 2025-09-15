# pyright: reportImportCycles = false
from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray

from .aegis_config import has_feature
from .agent import Agent
from .agent_type import AgentType
from .common import CellInfo, Direction, Location
from .common.objects.rubble import Rubble
from .common.objects.survivor import Survivor
from .constants import Constants
from .decorator import requires
from .message import Message
from .team import Team

if TYPE_CHECKING:
    from .game import Game


class AgentController:
    def __init__(self, game: "Game", agent: "Agent") -> None:
        self._game: Game = game
        self._agent: Agent = agent

    def assert_not_none(self, value: object) -> None:
        if value is None:
            error = "Argument has invalid None value"
            raise AgentError(error)

    def assert_spawn(self, loc: Location, team: Team) -> None:
        if loc not in self._game.get_spawns():
            error = f"Invalid spawn: {loc}"
            raise AgentError(error)

        units = self._game.team_info.get_units(team)
        if units == self._game.args.amount:
            error = "Max agents reached."
            raise AgentError(error)

    def assert_loc(self, loc: Location) -> None:
        self.assert_not_none(loc)
        if not self._game.on_map(loc):
            error = "Location is not on the map"
            raise AgentError(error)

    def assert_move(self, direction: Direction) -> None:
        self.assert_not_none(direction)
        new_loc = self._agent.location.add(direction)

        if not self._game.on_map(new_loc):
            error = "Agent moved off the map"
            raise AgentError(error)

    def assert_dig(self, agent: Agent) -> None:
        if has_feature("ALLOW_AGENT_TYPES") and agent.type not in (
            AgentType.ENGINEER,
            AgentType.COMMANDER,
        ):
            error = "Action not allowed. Only ENGINEER and COMMANDER can dig."
            raise AgentError(error)

    def assert_save(self, agent: Agent) -> None:
        if has_feature("ALLOW_AGENT_TYPES") and agent.type not in (
            AgentType.MEDIC,
            AgentType.COMMANDER,
        ):
            error = "Action not allowed. Only MEDIC and COMMANDER can save."
            raise AgentError(error)

    def assert_predict(self) -> None:
        if not has_feature("ALLOW_AGENT_PREDICTIONS"):
            msg = "Predictions are not enabled, therefore this method is not available."
            raise AgentError(msg)

    def assert_scan(self) -> None:
        if not has_feature("ALLOW_DRONE_SCAN"):
            msg = "Drone scan is not enabled, therefore this method is not available."
            raise AgentError(msg)

    # Public Agent Methods

    def get_round_number(self) -> int:
        """Return the current round number."""
        return self._game.round

    def get_id(self) -> int:
        """Return the id of the agent."""
        return self._agent.id

    def get_type(self) -> AgentType:
        """Return the type of the agent."""
        return self._agent.type

    def get_team(self) -> Team:
        """Return the current team of the agent."""
        return self._agent.team

    def get_location(self) -> Location:
        """Return the current location of the agent."""
        return self._agent.location

    def get_energy_level(self) -> int:
        """Return the current energy level of the agent."""
        return self._agent.energy_level

    def get_lumens(self) -> int:
        return self._game.team_info.get_lumens(self._agent.team)

    def move(self, direction: Direction) -> None:
        """
        Move the agent in the specified direction.

        Args:
            direction: The direction in which the agent should move.

        Raises:
            AgentError: If the move is invalid.

        """
        self.assert_move(direction)
        self._agent.add_cooldown()
        self._agent.apply_movement_cost(direction)
        new_loc = self._agent.location.add(direction)
        self._game.move_agent(self._agent.id, self._agent.location, new_loc)
        self._agent.location = new_loc

    def save(self) -> None:
        """
        Save a survivor located at the agent's current location.

        If no survivor is present, the function has no effect.

        Raises:
            AgentError: If saving is invalid according to game rules.

        """
        self.assert_save(self._agent)
        self._agent.add_cooldown()
        cell = self._game.get_cell_at(self._agent.location)
        top_layer = cell.get_top_layer()
        if top_layer is None or not isinstance(top_layer, Survivor):
            return

        self._game.save(top_layer, self._agent)

    def recharge(self) -> None:
        """
        Recharge the agent's energy if on a charging cell.

        Energy restored is equal to `Constants.NORMAL_CHARGE` per recharge,
        but cannot exceed `Constants.MAX_ENERGY_LEVEL`.

        Does nothing if the agent is not on a charging cell.
        """
        cell = self._game.get_cell_at(self._agent.location)
        if not cell.is_charging_cell():
            return

        energy = min(
            Constants.NORMAL_CHARGE,
            Constants.MAX_ENERGY_LEVEL - self._agent.energy_level,
        )

        self._agent.add_energy(energy)

    def dig(self) -> None:
        """
        Dig rubble at the agent's current location.

        Raises:
            AgentError: If digging is invalid according to game rules.

        """
        self.assert_dig(self._agent)
        self._agent.add_cooldown()
        cell = self._game.get_cell_at(self._agent.location)
        top_layer = cell.get_top_layer()
        if top_layer is None or not isinstance(top_layer, Rubble):
            return

        self._game.dig(self._agent)

    @requires("ALLOW_AGENT_PREDICTIONS")
    def predict(self, surv_id: int, label: np.int32) -> None:
        """
        Submit a prediction.

        Args:
            surv_id: The unique ID of the survivor.
            label: The predicted symbol label/classification.

        Raises:
            AgentError: If predictions are not enabled.

        """
        self.assert_predict()
        self._game.predict(surv_id, label, self._agent)

    @requires("ALLOW_AGENT_PREDICTIONS")
    def read_pending_predictions(
        self,
    ) -> list[tuple[int, NDArray[np.uint8], NDArray[np.int32]]]:
        """
        Retrieve the list of pending predictions stored by the agent's team.

        Each prediction is represented as a tuple containing:

            1. surv_id: The ID of the saved survivor that triggered this prediction.
            2. image_to_predict: The symbol image data for model input.
            3. all_unique_labels: The set of possible symbol labels.

        Returns:
            A list of pending symbol predictions. Returns an empty list if no pending
            predictions are available.

        Raises:
            AgentError: If predictions are not enabled.

        """
        self.assert_predict()
        return self._game.get_prediction_info_for_agent(self._agent.team)

    @requires("ALLOW_AGENT_MESSAGES")
    def send_message(self, message: str, dest_ids: list[int]) -> None:
        """
        Send a message to team members, excluding self.

        If `dest_ids` is empty, the message is broadcast to all team members
        except the sender.

        Args:
            message: The content of the message to send.
            dest_ids: A list of agent IDs to send the message to.

        """
        if not dest_ids:
            dest_ids = [
                agent.id
                for agent in self._game.agents.values()
                if agent.team == self._agent.team and agent.id != self._agent.id
            ]
        else:
            dest_ids = [aid for aid in dest_ids if aid != self._agent.id]

        msg = Message(
            message=message,
            round_num=self._game.round,
            sender_id=self._agent.id,
        )

        for agent_id in dest_ids:
            self._game.get_agent(agent_id).message_buffer.add_message(msg)

    @requires("ALLOW_AGENT_MESSAGES")
    def read_messages(self, round_num: int = -1) -> list[Message]:
        """
        Retrieve messages from the agent's message buffer.

        Args:
            round_num: If provided only messages from this round are returned.

        Returns:
            A list of messages.

        """
        if round_num == -1:
            return self._agent.message_buffer.get_all_messages()
        return self._agent.message_buffer.get_messages(round_num)

    @requires("ALLOW_DRONE_SCAN")
    def drone_scan(self, loc: Location) -> None:
        """
        Scan a location using a drone.

        Args:
            loc: The location to scan.

        Raises:
            AgentError: If drone scan is not enabled or location is invalid.

        """
        self.assert_scan()
        self.assert_loc(loc)

        self._game.start_drone_scan(loc, self._agent.team)
        self._agent.add_energy(-Constants.DRONE_SCAN_ENERGY_COST)

    def get_cell_info_at(self, loc: Location) -> CellInfo:
        """
        Return the cell info at a given location.

        If the location is adjacent (1 tile away) to the agent or has been scanned by a drone,
        all layers and agents at that location are visible. Otherwise, only the top layer is
        visible and agent presence is hidden.

        If `HIDDEN_MOVE_COSTS` feature is enabled, unvisited cells have `move_cost = 1`.

        Args:
            loc: The location to query.

        Returns:
            A CellInfo object following visibility rules.

        """
        self.assert_loc(loc)

        idx = loc.x + loc.y * self._game.world.width
        cell_info = self._game.get_cell_info_at(loc)

        is_adjacent = self._agent.location.is_adjacent_to(loc)
        is_scanned = self._game.is_loc_drone_scanned(loc, self._agent.team)

        if not is_adjacent or not is_scanned:
            cell_info.agents = []
            top = cell_info.top_layer
            cell_info.layers = [top] if top is not None else []

        if has_feature("HIDDEN_MOVE_COSTS") and not self._agent.has_visited[idx]:
            cell_info.move_cost = 1

        return cell_info

    @requires("ALLOW_AGENT_TYPES")
    def spawn_agent(self, loc: Location, agent_type: AgentType) -> None:
        """
        Spawn an agent at a specified location with a given type.

        Args:
            loc: A valid spawn location.
            agent_type: The type of agent to spawn.

        Raises:
            AgentError: If spawn location is invalid or max amount reached.

        """
        self.assert_spawn(loc, self._agent.team)
        self._game.spawn_agent(loc, self._agent.team, agent_type)

    def log(self, *args: object) -> None:
        """
        Log a message.

        Args:
            *args: One or more items to log.

        """
        self._agent.log(*args)


class AgentError(Exception):
    """An error that occurs during agent actions or validations."""
