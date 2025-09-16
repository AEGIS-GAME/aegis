from __future__ import annotations

from typing import override

from .world_object import WorldObject


class Survivor(WorldObject):
    """
    Represents a survivor in the world.

    Attributes:
        id: Unique identifier for the survivor.
        health: Current health of the survivor.

    """

    def __init__(self, survivor_id: int = -1, health: int = 1) -> None:
        super().__init__()
        self.id: int = survivor_id
        self.health: int = health

    def is_alive(self) -> bool:
        """
        Check if the survivor is alive.

        Returns:
            True if the survivor's health attribute is greather than zero, otherwise False.

        """
        return self.health > 0

    @override
    def __str__(self) -> str:
        return f"SURVIVOR ( ID {self.id} , HP {self.health} )"

    @override
    def __repr__(self) -> str:
        return self.__str__()
