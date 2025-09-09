from __future__ import annotations

from enum import Enum


class Team(Enum):
    """
    Enum representing the team of an agent.

    Attributes:
        GOOBS (int): The Goobs team.
        VOIDSEERS (int): The Voidseers team.

    """

    GOOBS = 0
    """Team Goobs"""
    VOIDSEERS = 1
    """Team Voidseers"""

    def opponent(self) -> Team:
        """
        Get the opposing team.

        Returns:
            The opponent team of the current team.

        """
        return Team.VOIDSEERS if self == Team.GOOBS else Team.GOOBS
