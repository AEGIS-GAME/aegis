from . import location_pb2 as _location_pb2
from . import spawn_pb2 as _spawn_pb2
from . import team_pb2 as _team_pb2
from . import turn_pb2 as _turn_pb2
from . import world_pb2 as _world_pb2
from . import world_object_pb2 as _world_object_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DroneScan(_message.Message):
    __slots__ = ("location", "team", "duration")
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    TEAM_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    location: _location_pb2.Location
    team: _team_pb2.Team
    duration: int
    def __init__(self, location: _Optional[_Union[_location_pb2.Location, _Mapping]] = ..., team: _Optional[_Union[_team_pb2.Team, str]] = ..., duration: _Optional[int] = ...) -> None: ...

class DroneScanUpdate(_message.Message):
    __slots__ = ("drone_scans",)
    DRONE_SCANS_FIELD_NUMBER: _ClassVar[int]
    drone_scans: _containers.RepeatedCompositeFieldContainer[DroneScan]
    def __init__(self, drone_scans: _Optional[_Iterable[_Union[DroneScan, _Mapping]]] = ...) -> None: ...

class SurvivorHealthUpdate(_message.Message):
    __slots__ = ("location", "survivor_id", "new_health", "new_state")
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    SURVIVOR_ID_FIELD_NUMBER: _ClassVar[int]
    NEW_HEALTH_FIELD_NUMBER: _ClassVar[int]
    NEW_STATE_FIELD_NUMBER: _ClassVar[int]
    location: _location_pb2.Location
    survivor_id: int
    new_health: int
    new_state: _world_object_pb2.SurvivorState
    def __init__(self, location: _Optional[_Union[_location_pb2.Location, _Mapping]] = ..., survivor_id: _Optional[int] = ..., new_health: _Optional[int] = ..., new_state: _Optional[_Union[_world_object_pb2.SurvivorState, str]] = ...) -> None: ...

class GamesHeader(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GameHeader(_message.Message):
    __slots__ = ("world", "rounds", "spawns")
    WORLD_FIELD_NUMBER: _ClassVar[int]
    ROUNDS_FIELD_NUMBER: _ClassVar[int]
    SPAWNS_FIELD_NUMBER: _ClassVar[int]
    world: _world_pb2.World
    rounds: int
    spawns: _containers.RepeatedCompositeFieldContainer[_spawn_pb2.Spawn]
    def __init__(self, world: _Optional[_Union[_world_pb2.World, _Mapping]] = ..., rounds: _Optional[int] = ..., spawns: _Optional[_Iterable[_Union[_spawn_pb2.Spawn, _Mapping]]] = ...) -> None: ...

class Round(_message.Message):
    __slots__ = ("round", "layers_removed", "dead_ids", "turns", "team_info", "drone_scans", "survivor_health_updates")
    ROUND_FIELD_NUMBER: _ClassVar[int]
    LAYERS_REMOVED_FIELD_NUMBER: _ClassVar[int]
    DEAD_IDS_FIELD_NUMBER: _ClassVar[int]
    TURNS_FIELD_NUMBER: _ClassVar[int]
    TEAM_INFO_FIELD_NUMBER: _ClassVar[int]
    DRONE_SCANS_FIELD_NUMBER: _ClassVar[int]
    SURVIVOR_HEALTH_UPDATES_FIELD_NUMBER: _ClassVar[int]
    round: int
    layers_removed: _containers.RepeatedCompositeFieldContainer[_location_pb2.Location]
    dead_ids: _containers.RepeatedScalarFieldContainer[int]
    turns: _containers.RepeatedCompositeFieldContainer[_turn_pb2.Turn]
    team_info: _containers.RepeatedCompositeFieldContainer[_team_pb2.TeamInfo]
    drone_scans: _containers.RepeatedCompositeFieldContainer[DroneScan]
    survivor_health_updates: _containers.RepeatedCompositeFieldContainer[SurvivorHealthUpdate]
    def __init__(self, round: _Optional[int] = ..., layers_removed: _Optional[_Iterable[_Union[_location_pb2.Location, _Mapping]]] = ..., dead_ids: _Optional[_Iterable[int]] = ..., turns: _Optional[_Iterable[_Union[_turn_pb2.Turn, _Mapping]]] = ..., team_info: _Optional[_Iterable[_Union[_team_pb2.TeamInfo, _Mapping]]] = ..., drone_scans: _Optional[_Iterable[_Union[DroneScan, _Mapping]]] = ..., survivor_health_updates: _Optional[_Iterable[_Union[SurvivorHealthUpdate, _Mapping]]] = ...) -> None: ...

class GameFooter(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GamesFooter(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
