from pathlib import Path

from google.protobuf.message import DecodeError

from .common import Cell, Location
from .common.objects import Rubble, Survivor
from .schemas import world_pb2
from .schemas.cell_pb2 import Cell as PbCell
from .schemas.cell_pb2 import CellType
from .schemas.world_object_pb2 import SurvivorState
from .world import World


def get_cell_type(cell: Cell) -> CellType:
    if cell.is_spawn_cell():
        return CellType.SPAWN
    if cell.is_charging_cell():
        return CellType.CHARGING
    if cell.is_killer_cell():
        return CellType.KILLER
    return CellType.NORMAL


def cell_type_from_proto(cell: Cell, cell_type: CellType) -> None:
    if cell_type == CellType.SPAWN:
        cell.set_spawn_cell()
    elif cell_type == CellType.CHARGING:
        cell.set_charging_cell()
    elif cell_type == CellType.KILLER:
        cell.set_killer_cell()


def cell_from_proto(proto_cell: PbCell) -> Cell:
    loc = proto_cell.loc
    cell = Cell(loc.x, loc.y)

    cell_type_from_proto(cell, proto_cell.type)
    cell.move_cost = proto_cell.moveCost
    cell.agents = list(proto_cell.agents)

    for layer_proto in proto_cell.layers:
        if layer_proto.HasField("survivor"):
            s = layer_proto.survivor
            # Convert protobuf state to Survivor.State enum
            state = Survivor.State.ALIVE if s.state == 0 else Survivor.State.DEAD
            survivor = Survivor(s.id, s.health, state)
            cell.add_layer(survivor)
        elif layer_proto.HasField("rubble"):
            r = layer_proto.rubble
            rubble = Rubble(
                r.id,
                r.energy_required,
                r.agents_required,
            )
            cell.add_layer(rubble)

    return cell


def serialize_world(world: World) -> world_pb2.World:
    proto_world = world_pb2.World()
    proto_world.width = world.width
    proto_world.height = world.height
    proto_world.seed = world.seed
    proto_world.start_energy = world.start_energy
    proto_world.total_survivors = world.total_survivors

    for cell in world.cells:
        proto_cell = proto_world.cells.add()
        proto_cell.loc.x = cell.location.x
        proto_cell.loc.y = cell.location.y
        proto_cell.moveCost = cell.move_cost
        proto_cell.type = get_cell_type(cell)
        proto_cell.agents.extend(cell.agents)

        for layer in cell.get_layers():
            layer_proto = proto_cell.layers.add()
            if isinstance(layer, Survivor):
                survivor_proto = layer_proto.survivor
                survivor_proto.id = layer.id
                survivor_proto.health = layer.health
                # Use the actual survivor state instead of inferring from health
                survivor_proto.state = (
                    SurvivorState.ALIVE if layer.is_alive() else SurvivorState.DEAD
                )
            elif isinstance(layer, Rubble):
                rubble_proto = layer_proto.rubble
                rubble_proto.id = layer.id
                rubble_proto.energy_required = layer.energy_required
                rubble_proto.agents_required = layer.agents_required

    return proto_world


def init_spawns_from_proto(world: world_pb2.World) -> dict[Location, int]:
    spawns: dict[Location, int] = {}

    for spawn in world.init_spawns:
        loc = Location(spawn.loc.x, spawn.loc.y)
        spawns[loc] = spawns.get(loc, 0) + spawn.amount

    return spawns


def deserialize_world(data: bytes) -> World:
    try:
        proto_world = world_pb2.World()
        _ = proto_world.ParseFromString(data)
    except DecodeError as e:
        error = "Failed to decode binary world file"
        raise ValueError(error) from e

    cells = [cell_from_proto(proto_cell) for proto_cell in proto_world.cells]

    spawns = init_spawns_from_proto(proto_world)
    return World(
        proto_world.width,
        proto_world.height,
        proto_world.seed,
        proto_world.start_energy,
        cells,
        spawns,
    )


def load_world(filename: Path) -> World:
    with filename.open("rb") as file:
        return deserialize_world(file.read())
