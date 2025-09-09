from typing import Literal, TypedDict


class WorldSize(TypedDict):
    width: int
    height: int


class WorldInfo(TypedDict):
    size: WorldSize
    seed: int
    start_energy: int


class Loc(TypedDict):
    x: int
    y: int


Attributes = Literal[
    "health",
    "energy_required",
    "agents_required",
]


class Layer(TypedDict):
    type: str
    attributes: dict[Attributes, int]


class CellInfoRaw(TypedDict):
    loc: Loc
    moveCost: int
    type: str | None
    layers: list[Layer]


class WorldRaw(TypedDict):
    world_info: WorldInfo
    cells: list[CellInfoRaw]
