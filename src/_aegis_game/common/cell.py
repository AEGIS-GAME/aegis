from __future__ import annotations

from typing import override

from _aegis_game.types import CellType

from .location import Location
from .objects import Survivor, WorldObject


class Cell:
    def __init__(self, x: int, y: int) -> None:
        self.type: CellType = CellType.NORMAL_CELL
        self.layers: list[WorldObject] = []
        self.move_cost: int = 1
        self.agents: list[int] = []
        self.location: Location = Location(x, y)

    def setup_cell(self, cell_state_type: str) -> None:
        cell_state_type = cell_state_type.upper().strip()

        if cell_state_type == "CHARGING":
            self.type = CellType.CHARGING_CELL
        elif cell_state_type == "KILLER":
            self.type = CellType.KILLER_CELL
        elif cell_state_type == "SPAWN":
            self.type = CellType.SPAWN_CELL

    def is_charging_cell(self) -> bool:
        return self.type == CellType.CHARGING_CELL

    def is_killer_cell(self) -> bool:
        return self.type == CellType.KILLER_CELL

    def is_normal_cell(self) -> bool:
        return self.type == CellType.NORMAL_CELL

    def is_spawn_cell(self) -> bool:
        return self.type == CellType.SPAWN_CELL

    def set_spawn_cell(self) -> None:
        self.type = CellType.SPAWN_CELL

    def set_charging_cell(self) -> None:
        self.type = CellType.CHARGING_CELL

    def set_killer_cell(self) -> None:
        self.type = CellType.KILLER_CELL

    def get_layers(self) -> list[WorldObject]:
        return self.layers

    def add_layer(self, layer: WorldObject) -> None:
        self.layers.append(layer)

    def remove_top_layer(self) -> WorldObject:
        """
        Remove and returns the topmost layer from the cell.

        Assumes the caller has already checked that the cell has a top layer.

        Returns:
            WorldObject: The topmost world object layer.

        Raises:
            IndexError: If there are no layers to remove.

        """
        return self.layers.pop(0)

    def get_top_layer(self) -> WorldObject | None:
        if not self.layers:
            return None
        return self.layers[0]

    def set_top_layer(self, top_layer: WorldObject | None) -> None:
        self.layers.clear()
        if top_layer is None:
            return
        self.layers.append(top_layer)

    def number_of_survivors(self) -> int:
        count = 0
        for layer in self.layers:
            if isinstance(layer, Survivor):
                count += 1
        return count

    def is_spawn(self) -> bool:
        return self.type == CellType.SPAWN_CELL

    @override
    def __str__(self) -> str:
        if not self.layers:
            layers_str = "  (no layers)"
        else:
            layers_str = "\n".join(
                f"  {i + 1} - {layer}" for i, layer in enumerate(self.layers)
            )

        return (
            f"Cell at ({self.location.x}, {self.location.y}) - "
            f"Move Cost: {self.move_cost}\n"
            f"Type: {self.type}\n"
            f"Layers:\n"
            f"{layers_str}\n"
        )

    @override
    def __repr__(self) -> str:
        return self.__str__()
