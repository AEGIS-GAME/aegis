from . import location_pb2 as _location_pb2
from . import world_object_pb2 as _world_object_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CellType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NORMAL: _ClassVar[CellType]
    SPAWN: _ClassVar[CellType]
    KILLER: _ClassVar[CellType]
    CHARGING: _ClassVar[CellType]
NORMAL: CellType
SPAWN: CellType
KILLER: CellType
CHARGING: CellType

class Cell(_message.Message):
    __slots__ = ("loc", "moveCost", "type", "agents", "layers")
    LOC_FIELD_NUMBER: _ClassVar[int]
    MOVECOST_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    AGENTS_FIELD_NUMBER: _ClassVar[int]
    LAYERS_FIELD_NUMBER: _ClassVar[int]
    loc: _location_pb2.Location
    moveCost: int
    type: CellType
    agents: _containers.RepeatedScalarFieldContainer[int]
    layers: _containers.RepeatedCompositeFieldContainer[_world_object_pb2.WorldObject]
    def __init__(self, loc: _Optional[_Union[_location_pb2.Location, _Mapping]] = ..., moveCost: _Optional[int] = ..., type: _Optional[_Union[CellType, str]] = ..., agents: _Optional[_Iterable[int]] = ..., layers: _Optional[_Iterable[_Union[_world_object_pb2.WorldObject, _Mapping]]] = ...) -> None: ...
