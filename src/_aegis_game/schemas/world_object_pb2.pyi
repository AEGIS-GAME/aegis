from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SurvivorState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ALIVE: _ClassVar[SurvivorState]
    DEAD: _ClassVar[SurvivorState]
ALIVE: SurvivorState
DEAD: SurvivorState

class Survivor(_message.Message):
    __slots__ = ("id", "health", "state")
    ID_FIELD_NUMBER: _ClassVar[int]
    HEALTH_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    id: int
    health: int
    state: SurvivorState
    def __init__(self, id: _Optional[int] = ..., health: _Optional[int] = ..., state: _Optional[_Union[SurvivorState, str]] = ...) -> None: ...

class Rubble(_message.Message):
    __slots__ = ("id", "energy_required", "agents_required")
    ID_FIELD_NUMBER: _ClassVar[int]
    ENERGY_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    AGENTS_REQUIRED_FIELD_NUMBER: _ClassVar[int]
    id: int
    energy_required: int
    agents_required: int
    def __init__(self, id: _Optional[int] = ..., energy_required: _Optional[int] = ..., agents_required: _Optional[int] = ...) -> None: ...

class WorldObject(_message.Message):
    __slots__ = ("survivor", "rubble")
    SURVIVOR_FIELD_NUMBER: _ClassVar[int]
    RUBBLE_FIELD_NUMBER: _ClassVar[int]
    survivor: Survivor
    rubble: Rubble
    def __init__(self, survivor: _Optional[_Union[Survivor, _Mapping]] = ..., rubble: _Optional[_Union[Rubble, _Mapping]] = ...) -> None: ...
