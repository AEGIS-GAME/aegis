from typing import override

from _aegis_game.types import CellType

from .location import Location
from .objects import WorldObject


class CellInfo:
    """
    Represents information about a cell in the world.

    Attributes:
        type: The type of the cell.
        location: The coordinates of the cell.
        move_cost: The movement cost to traverse this cell.
        agents: List of agent IDs currently in this cell.
        layers: Stack of world objects present in the cell.

    """

    def __init__(
        self,
        layers: list[WorldObject],
        cell_type: CellType,
        location: Location | None,
        move_cost: int,
        agents: list[int] | None,
    ) -> None:
        self.type: CellType = cell_type
        self.location: Location = location if location is not None else Location(-1, -1)
        self.move_cost: int = move_cost
        self.agents: list[int] = agents if agents is not None else []
        self.layers: list[WorldObject] = layers

    @property
    def top_layer(self) -> WorldObject | None:
        """Get the top-most layer of the cell."""
        return self.layers[0] if self.layers else None

    def is_killer_cell(self) -> bool:
        """
        Check if the cell is a killer cell.

        Returns:
            A boolean value indicating whether cell is a KILLER_CELL.

        """
        return self.type == CellType.KILLER_CELL

    @override
    def __str__(self) -> str:
        return (
            f"{self.type.name} (\n"
            f"  X: {self.location.x},\n"
            f"  Y: {self.location.y},\n"
            f"  Move Cost: {self.move_cost},\n"
            f"  Num Agents: {len(self.agents)},\n"
            f"  Agent IDs: {self.agents},\n"
            f"  Top Layer: {self.top_layer}\n"
            f")"
        )

    @override
    def __repr__(self) -> str:
        return self.__str__()
