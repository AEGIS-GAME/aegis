from . import location_pb2 as _location_pb2
from . import spawn_pb2 as _spawn_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Turn(_message.Message):
    __slots__ = ("agentId", "energy_level", "steps_taken", "loc", "commands", "spawns")
    AGENTID_FIELD_NUMBER: _ClassVar[int]
    ENERGY_LEVEL_FIELD_NUMBER: _ClassVar[int]
    STEPS_TAKEN_FIELD_NUMBER: _ClassVar[int]
    LOC_FIELD_NUMBER: _ClassVar[int]
    COMMANDS_FIELD_NUMBER: _ClassVar[int]
    SPAWNS_FIELD_NUMBER: _ClassVar[int]
    agentId: int
    energy_level: int
    steps_taken: int
    loc: _location_pb2.Location
    commands: _containers.RepeatedScalarFieldContainer[str]
    spawns: _containers.RepeatedCompositeFieldContainer[_spawn_pb2.Spawn]
    def __init__(self, agentId: _Optional[int] = ..., energy_level: _Optional[int] = ..., steps_taken: _Optional[int] = ..., loc: _Optional[_Union[_location_pb2.Location, _Mapping]] = ..., commands: _Optional[_Iterable[str]] = ..., spawns: _Optional[_Iterable[_Union[_spawn_pb2.Spawn, _Mapping]]] = ...) -> None: ...
