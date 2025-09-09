# pyright: reportImportCycles = false

from typing import TYPE_CHECKING

from .agent_type import AgentType
from .common import Direction, Location
from .constants import Constants
from .logger import AGENT_LOGGER
from .message_buffer import MessageBuffer
from .sandbox.core import LumenCore
from .sandbox.sandbox import Sandbox
from .team import Team
from .types import MethodDict

if TYPE_CHECKING:
    from .game import Game


class Agent:
    def __init__(  # noqa: PLR0913
        self,
        game: "Game",
        agent_id: int,
        location: Location,
        team: Team,
        energy_level: int,
        agent_type: AgentType,
    ) -> None:
        self.game: Game = game
        self.has_visited: list[bool] = [False] * (game.world.height * game.world.width)
        self.id: int = agent_id
        self.team: Team = team
        self.location: Location = location
        self.energy_level: int = energy_level
        self.type: AgentType = agent_type
        self.action_cooldown: int = agent_type.action_cooldown
        self.core: LumenCore | None = None
        self.message_buffer: MessageBuffer = MessageBuffer()
        self.steps_taken: int = 0
        self.debug: bool = False
        self.errors: list[str] = []

    def process_beginning_of_turn(self) -> None:
        if self.core is None:
            error = "Trying to run an agent that hasn't launched"
            raise RuntimeError(error)

        self.action_cooldown = max(0, self.action_cooldown - Constants.COOLDOWN_TICK)

    def process_end_of_turn(self) -> None:
        self.game.game_pb.end_turn(self)

    def turn(self) -> None:
        self.process_beginning_of_turn()
        self.errors.clear()
        self.core.run()  # pyright: ignore[reportOptionalMemberAccess]
        self.log_errors()
        self.penalize_for_errors()
        self.process_end_of_turn()

    def kill(self) -> None:
        self.core.kill()  # pyright: ignore[reportOptionalMemberAccess]

    def launch(
        self, code: Sandbox | None, methods: MethodDict, *, debug: bool = False
    ) -> None:
        if code is None:
            error = "No code provided to launch."
            raise ValueError(error)

        self.core = LumenCore(code, methods, self.error)
        self.debug = debug

    def apply_movement_cost(self, direction: Direction) -> None:
        if direction == Direction.CENTER:
            return

        cell = self.game.get_cell_at(self.location.add(direction))
        self.add_energy(-cell.move_cost)
        self.steps_taken += 1

    def add_energy(self, energy: int) -> None:
        self.energy_level += energy
        self.energy_level = min(Constants.MAX_ENERGY_LEVEL, self.energy_level)

    def add_cooldown(self, cooldown: int = -1) -> None:
        self.action_cooldown = self.type.action_cooldown if cooldown == -1 else cooldown

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def log_errors(self) -> None:
        for error in self.errors:
            if self.debug:
                self.log(error, is_error=True)
            else:
                AGENT_LOGGER.warning(
                    f"[Agent#({self.id}:{self.team.name})@{self.game.round}] [ERROR] Error thrown this round. (Turn on debug to see error message)"
                )

    def log(self, *args: object, is_error: bool = False) -> None:
        if not self.debug:
            return

        agent_id = self.id
        prefix = f"[Agent#({agent_id}:{self.team.name})@{self.game.round}]"

        if is_error:
            AGENT_LOGGER.error(f"{prefix} {' '.join(map(str, args))}")
        else:
            AGENT_LOGGER.info(f"{prefix} {' '.join(map(str, args))}")

    def penalize_for_errors(self) -> None:
        if self.errors:
            self.add_energy(Constants.ENERGY_PENALTY_FOR_ERRORS)
            AGENT_LOGGER.warning(
                f"[Agent#({self.id}:{self.team.name})@{self.game.round}] [ERROR] penalized {Constants.ENERGY_PENALTY_FOR_ERRORS} energy for error."
            )
