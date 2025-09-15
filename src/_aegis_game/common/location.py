from __future__ import annotations

from typing import override

from _aegis_game.common.direction import Direction


class Location:
    """
    Represents a coordinate location with x and y integer values.

    Attributes:
        x: The x-coordinate.
        y: The y-coordinate.

    """

    def __init__(self, x: int, y: int) -> None:
        """
        Initialize a Location with given x and y coordinates.

        Args:
            x: The x-coordinate.
            y: The y-coordinate.

        """
        self.x: int = x
        self.y: int = y

    def add(self, direction: Direction) -> Location:
        """
        Return a new location by moving this Location in the specified direction.

        Args:
            direction: The direction to move.

        Returns:
            A new location in the given direction.

        """
        return Location(self.x + direction.dx, self.y + direction.dy)

    def direction_to(self, location: Location) -> Direction:
        """
        Determine the cardinal direction from this location to another location.

        Args:
            location: The target location.

        Returns:
            The cardinal direction pointing towards the target location.

        """
        dx = location.x - self.x
        dy = location.y - self.y

        key = (dx > 0) - (dx < 0), (dy > 0) - (dy < 0)

        direction_map = {
            (1, 1): Direction.NORTHEAST,
            (1, -1): Direction.SOUTHEAST,
            (-1, 1): Direction.NORTHWEST,
            (-1, -1): Direction.SOUTHWEST,
            (1, 0): Direction.EAST,
            (-1, 0): Direction.WEST,
            (0, 1): Direction.NORTH,
            (0, -1): Direction.SOUTH,
            (0, 0): Direction.CENTER,
        }

        return direction_map.get(key, Direction.CENTER)

    def distance_to(self, location: Location) -> int:
        """
        Calculate the squared Euclidean distance from this location to another.

        Args:
            location: The target location.

        Returns:
            The squared distance between the two locations.

        """
        dx = self.x - location.x
        dy = self.y - location.y
        return dx * dx + dy * dy

    def is_adjacent_to(self, location: Location) -> bool:
        """
        Check if this Location is adjacent to another Location.

        Args:
            location: The target location.

        Returns:
            True if the other location is adjacent, else False.

        """
        dx = self.x - location.x
        dy = self.y - location.y
        return -1 <= dx <= 1 and -1 <= dy <= 1

    @override
    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

    @override
    def __repr__(self) -> str:
        return self.__str__()

    @override
    def __hash__(self) -> int:
        value = 3
        value = 89 * value + self.x
        return 89 * value + self.y

    @override
    def __eq__(self, other: object) -> bool:
        if isinstance(other, Location):
            return self.x == other.x and self.y == other.y
        return False

    @override
    def __ne__(self, other: object) -> bool:
        if isinstance(other, Location):
            return not self.__eq__(other)
        return False

    def __lt__(self, other: object) -> bool:
        if isinstance(other, Location):
            if self.x < other.x:
                return True
            if self.x == other.x:
                return self.y < other.y
        return False

    def __gt__(self, other: object) -> bool:
        if isinstance(other, Location):
            if self.x > other.x:
                return True
            if self.x == other.x:
                return self.y > other.y
        return False

    def __le__(self, other: object) -> bool:
        if isinstance(other, Location):
            return self.__lt__(other) or self.__eq__(other)
        return False

    def __ge__(self, other: object) -> bool:
        if isinstance(other, Location):
            return self.__gt__(other) or self.__eq__(other)
        return False
