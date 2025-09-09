from __future__ import annotations

from typing import override

from .world_object import WorldObject


class Rubble(WorldObject):
    """
    Represents a rubble object in the world.

    Attributes:
        id: Unique identifier for the rubble.
        energy_required: Amount of energy needed to remove the rubble.
        agents_required: Number of agents required to remove the rubble.

    """

    def __init__(
        self, rubble_id: int = -1, energy_required: int = 1, agents_required: int = 1
    ) -> None:
        super().__init__()
        self.id: int = rubble_id
        self.energy_required: int = energy_required
        self.agents_required: int = agents_required

    @override
    def __str__(self) -> str:
        return (
            f"RUBBLE ( ID {self.id} , "
            f"NUM_TO_RM {self.agents_required} , "
            f"RM_ENG {self.energy_required} )"
        )

    @override
    def __repr__(self) -> str:
        return self.__str__()
