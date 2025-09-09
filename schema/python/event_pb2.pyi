from . import game_pb2 as _game_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Event(_message.Message):
    __slots__ = ("games_header", "game_header", "round", "game_footer", "games_footer", "drone_scan_update")
    GAMES_HEADER_FIELD_NUMBER: _ClassVar[int]
    GAME_HEADER_FIELD_NUMBER: _ClassVar[int]
    ROUND_FIELD_NUMBER: _ClassVar[int]
    GAME_FOOTER_FIELD_NUMBER: _ClassVar[int]
    GAMES_FOOTER_FIELD_NUMBER: _ClassVar[int]
    DRONE_SCAN_UPDATE_FIELD_NUMBER: _ClassVar[int]
    games_header: _game_pb2.GamesHeader
    game_header: _game_pb2.GameHeader
    round: _game_pb2.Round
    game_footer: _game_pb2.GameFooter
    games_footer: _game_pb2.GamesFooter
    drone_scan_update: _game_pb2.DroneScanUpdate
    def __init__(self, games_header: _Optional[_Union[_game_pb2.GamesHeader, _Mapping]] = ..., game_header: _Optional[_Union[_game_pb2.GameHeader, _Mapping]] = ..., round: _Optional[_Union[_game_pb2.Round, _Mapping]] = ..., game_footer: _Optional[_Union[_game_pb2.GameFooter, _Mapping]] = ..., games_footer: _Optional[_Union[_game_pb2.GamesFooter, _Mapping]] = ..., drone_scan_update: _Optional[_Union[_game_pb2.DroneScanUpdate, _Mapping]] = ...) -> None: ...
