from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True)
class Attributes:
    energy_multiplier: float
    action_cooldown: int


class AgentType(Enum):
    MEDIC = Attributes(0.5, 10)
    """Medic type."""
    ENGINEER = Attributes(0.75, 10)
    """Engineer type."""
    COMMANDER = Attributes(1.0, 10)
    """Commander type. Also used when the config `ALLOW_AGENT_TYPES` is disabled."""

    @property
    def energy_multiplier(self) -> float:
        """Multiplier applied to the world's start energy to determine the agent's energy."""
        return self.value.energy_multiplier

    @property
    def action_cooldown(self) -> int:
        """Action cooldown of the agent."""
        return self.value.action_cooldown
