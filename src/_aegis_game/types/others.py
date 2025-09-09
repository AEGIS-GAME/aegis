from collections.abc import Callable
from enum import Enum
from typing import Any, Literal, TypedDict, override


class CellType(Enum):
    """Enum representing different types of cells."""

    NORMAL_CELL = 0
    CHARGING_CELL = 1
    KILLER_CELL = 2
    SPAWN_CELL = 3

    @override
    def __str__(self) -> str:
        name = self.name.lower().replace("_cell", "")
        return name.capitalize()

    @override
    def __repr__(self) -> str:
        return self.__str__()


class GameOverReason(Enum):
    ALL_AGENTS_DEAD = "All team agents are dead"
    ALL_SURVIVORS_SAVED = "All survivors have been rescued"
    MAX_ROUNDS_REACHED = "Maximum number of rounds reached"


FeatureKey = Literal[
    "ALLOW_AGENT_PREDICTIONS",
    "ALLOW_AGENT_MESSAGES",
    "ALLOW_DRONE_SCAN",
    "ALLOW_AGENT_TYPES",
    "HIDDEN_MOVE_COSTS",
    "ALLOW_CUSTOM_AGENT_COUNT",
    "DEFAULT_AGENT_AMOUNT",
    "SURV_HEALTH_DECAY_RATE",
    "ADVANCED_SCORING_SYSTEM",
]

CompetitionSettingKey = Literal["VERSUS_MODE",]

ConfigType = Literal["assignment", "competition"]


class FeaturesConfig(TypedDict):
    ALLOW_AGENT_PREDICTIONS: bool
    ALLOW_AGENT_MESSAGES: bool
    ALLOW_DRONE_SCAN: bool
    ALLOW_AGENT_TYPES: bool
    HIDDEN_MOVE_COSTS: bool
    ALLOW_CUSTOM_AGENT_COUNT: bool
    DEFAULT_AGENT_AMOUNT: int
    SURV_HEALTH_DECAY_RATE: int
    ADVANCED_SCORING_SYSTEM: bool


class CompetitionConfig(TypedDict):
    VERSUS_MODE: bool


class ClientConfig(TypedDict):
    CONFIG_TYPE: ConfigType


class AegisConfig(TypedDict):
    features: FeaturesConfig
    competition_specific: CompetitionConfig
    client: ClientConfig


# `create_methods` return type
MethodDict = dict[str, type | Callable[..., Any]]  # pyright: ignore[reportExplicitAny]
