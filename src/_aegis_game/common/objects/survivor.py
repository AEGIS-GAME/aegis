from __future__ import annotations

from enum import Enum
from typing import override

from .world_object import WorldObject


class Survivor(WorldObject):
    """
    Represents a survivor in the world.

    Attributes:
        id: Unique identifier for the survivor.
        health: Current health of the survivor.

    """

    def __init__(
        self, survivor_id: int = -1, health: int = 1, state: State | None = None
    ) -> None:
        super().__init__()
        self._state: Survivor.State = state if state is not None else self.State.ALIVE
        self.id: int = survivor_id
        self.health: int = health

    def is_alive(self) -> bool:
        """
        Check if the survivor is alive.

        Returns:
            True if the survivor is ALIVE, False otherwise.

        """
        return self._state == self.State.ALIVE

    def set_state(self, state: State) -> None:
        self._state = state

    def get_state(self) -> State:
        return self._state

    @override
    def __str__(self) -> str:
        return f"SURVIVOR ( ID {self.id} , HP {self.health} )"

    @override
    def __repr__(self) -> str:
        return self.__str__()

    class State(Enum):
        ALIVE = 0
        DEAD = 1
