from __future__ import annotations

from enum import Enum


class Direction(Enum):
    """
    Represents the eight principal compass directions plus the center (no movement).

    Each direction has a tuple value representing its (dx, dy) movement on a grid.
    """

    NORTH = (0, 1)
    """Direction that points north (up)."""

    NORTHEAST = (1, 1)
    """Direction that points northeast (up and right)."""

    EAST = (1, 0)
    """Direction that points east (right)."""

    SOUTHEAST = (1, -1)
    """Direction that points southeast (down and right)."""

    SOUTH = (0, -1)
    """Direction that points south (down)."""

    SOUTHWEST = (-1, -1)
    """Direction that points southwest (down and left)."""

    WEST = (-1, 0)
    """Direction that points west (left)."""

    NORTHWEST = (-1, 1)
    """Direction that points northwest (up and left)."""

    CENTER = (0, 0)
    """Direction that points center (not moving)."""

    @property
    def dx(self) -> int:
        """The change in the x direction."""
        return self.value[0]

    @property
    def dy(self) -> int:
        """The change in the y direction."""
        return self.value[1]

    def rotate_left(self) -> Direction:
        """
        Rotate the direction 45 degrees counter-clockwise (left).

        The center direction returns itself unchanged.

        Returns:
            The direction rotated left.

        """
        if self == Direction.CENTER:
            return self
        new_index = (dir_to_index[self] - 1) % 8
        return dir_order[new_index]

    def rotate_right(self) -> Direction:
        """
        Rotate the direction 45 degrees clockwise (right).

        The center direction returns itself unchanged.

        Returns:
            The direction rotated right.

        """
        if self == Direction.CENTER:
            return self
        new_index = (dir_to_index[self] + 1) % 8
        return dir_order[new_index]

    def get_opposite(self) -> Direction:
        """
        Get the opposite direction (180 degrees rotation).

        The center direction returns itself unchanged.

        Returns:
            The opposite direction.

        """
        if self == Direction.CENTER:
            return self
        new_index = (dir_to_index[self] + 4) % 8
        return dir_order[new_index]


dir_order = [
    Direction.NORTH,
    Direction.NORTHEAST,
    Direction.EAST,
    Direction.SOUTHEAST,
    Direction.SOUTH,
    Direction.SOUTHWEST,
    Direction.WEST,
    Direction.NORTHWEST,
    Direction.CENTER,
]
dir_to_index = {d: i for i, d in enumerate(dir_order)}
