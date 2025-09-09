from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Team(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GOOBS: _ClassVar[Team]
    VOIDSEERS: _ClassVar[Team]
GOOBS: Team
VOIDSEERS: Team

class TeamInfo(_message.Message):
    __slots__ = ("saved_alive", "saved_dead", "saved", "predicted_right", "predicted_wrong", "predicted", "score", "units", "team")
    SAVED_ALIVE_FIELD_NUMBER: _ClassVar[int]
    SAVED_DEAD_FIELD_NUMBER: _ClassVar[int]
    SAVED_FIELD_NUMBER: _ClassVar[int]
    PREDICTED_RIGHT_FIELD_NUMBER: _ClassVar[int]
    PREDICTED_WRONG_FIELD_NUMBER: _ClassVar[int]
    PREDICTED_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    UNITS_FIELD_NUMBER: _ClassVar[int]
    TEAM_FIELD_NUMBER: _ClassVar[int]
    saved_alive: int
    saved_dead: int
    saved: int
    predicted_right: int
    predicted_wrong: int
    predicted: int
    score: int
    units: int
    team: Team
    def __init__(self, saved_alive: _Optional[int] = ..., saved_dead: _Optional[int] = ..., saved: _Optional[int] = ..., predicted_right: _Optional[int] = ..., predicted_wrong: _Optional[int] = ..., predicted: _Optional[int] = ..., score: _Optional[int] = ..., units: _Optional[int] = ..., team: _Optional[_Union[Team, str]] = ...) -> None: ...
