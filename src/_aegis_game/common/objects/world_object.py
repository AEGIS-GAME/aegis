from __future__ import annotations

from abc import ABC, abstractmethod
from typing import override


class WorldObject(ABC):
    def __init__(self) -> None:
        self.id: int = -1

    @abstractmethod
    @override
    def __str__(self) -> str:
        pass
