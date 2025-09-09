from . import location_pb2 as _location_pb2
from . import team_pb2 as _team_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Spawn(_message.Message):
    __slots__ = ("agentId", "loc", "team")
    AGENTID_FIELD_NUMBER: _ClassVar[int]
    LOC_FIELD_NUMBER: _ClassVar[int]
    TEAM_FIELD_NUMBER: _ClassVar[int]
    agentId: int
    loc: _location_pb2.Location
    team: _team_pb2.Team
    def __init__(self, agentId: _Optional[int] = ..., loc: _Optional[_Union[_location_pb2.Location, _Mapping]] = ..., team: _Optional[_Union[_team_pb2.Team, str]] = ...) -> None: ...

class InitSpawn(_message.Message):
    __slots__ = ("loc", "amount")
    LOC_FIELD_NUMBER: _ClassVar[int]
    AMOUNT_FIELD_NUMBER: _ClassVar[int]
    loc: _location_pb2.Location
    amount: int
    def __init__(self, loc: _Optional[_Union[_location_pb2.Location, _Mapping]] = ..., amount: _Optional[int] = ...) -> None: ...
