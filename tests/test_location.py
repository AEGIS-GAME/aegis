"""Tests for the Location class."""

from __future__ import annotations

import pytest

from _aegis_game.common.direction import Direction
from _aegis_game.common.location import Location


class TestLocationInit:
    """Tests for Location object initialization."""

    def test_init_sets_coordinate(self) -> None:
        """Test that the constructor correctly assigns x and y."""
        expected_x = 3
        expected_y = 4
        loc = Location(3, 4)
        assert loc.x == expected_x
        assert loc.y == expected_y


class TestAdd:
    """Tests for the `add` method, which moves a Location in a given Direction."""

    @pytest.mark.parametrize(
        ("start", "direction", "expected"),
        [
            (Location(0, 0), Direction.NORTH, Location(0, 1)),
            (Location(5, 5), Direction.SOUTHWEST, Location(4, 4)),
            (Location(2, 7), Direction.NORTHEAST, Location(3, 8)),
            (Location(-2, 3), Direction.CENTER, Location(-2, 3)),
        ],
    )
    def test_add_moves_in_correct_direction(
        self, start: Location, direction: Direction, expected: Location
    ) -> None:
        """Test that `add` returns a new Location offset by the given direction's dx and dy."""
        res = start.add(direction)
        assert res == expected
        assert res is not start


class TestDirectionTo:
    """Tests for the `direction_to` method, which determines the Direction to another Location."""

    @pytest.mark.parametrize(
        ("start", "end", "expected"),
        [
            (Location(0, 0), Location(1, 1), Direction.NORTHEAST),
            (Location(0, 0), Location(1, -1), Direction.SOUTHEAST),
            (Location(0, 0), Location(-1, 1), Direction.NORTHWEST),
            (Location(0, 0), Location(-1, -1), Direction.SOUTHWEST),
            (Location(0, 0), Location(1, 0), Direction.EAST),
            (Location(0, 0), Location(-1, 0), Direction.WEST),
            (Location(0, 0), Location(0, 1), Direction.NORTH),
            (Location(0, 0), Location(0, -1), Direction.SOUTH),
            (Location(2, 2), Location(2, 2), Direction.CENTER),
        ],
    )
    def test_direction_to(
        self, start: Location, end: Location, expected: Direction
    ) -> None:
        """Test that `direction_to` correctly returns the Direction from one Location to another."""
        assert start.direction_to(end) == expected


class TestDistanceTo:
    """Tests for the `distance_to` method, which computes squared Euclidean distance."""

    def test_distance_squared(self) -> None:
        """Test that `distance_to` returns squared Euclidean distance."""
        expected = 25
        assert Location(0, 0).distance_to(Location(3, 4)) == expected
        expected = 0
        assert Location(1, 1).distance_to(Location(1, 1)) == expected
        expected = 52
        assert Location(-1, -1).distance_to(Location(5, 3)) == expected


class TestIsAdjacentTo:
    """Tests for the `is_adjacent_to` method, which checks neighboring positions."""

    @pytest.mark.parametrize(
        ("loc1", "loc2", "expected"),
        [
            (Location(0, 0), Location(0, 1), True),
            (Location(0, 0), Location(1, 0), True),
            (Location(0, 0), Location(1, 1), True),
            (Location(0, 0), Location(2, 0), False),
            (Location(0, 0), Location(0, 2), False),
        ],
    )
    def test_is_adjacent_to(
        self,
        loc1: Location,
        loc2: Location,
        expected: bool,  # noqa: FBT001
    ) -> None:
        """Test that `is_adjacent_to` correctly detects adjacency."""
        assert loc1.is_adjacent_to(loc2) is expected


class TestStringRepresentations:
    """Tests for `__str__` and `__repr__` methods."""

    def test_str_and_repr(self) -> None:
        """Test that __str__ and __repr__ return expected format."""
        loc = Location(3, -2)
        expected_str = "(3, -2)"
        assert str(loc) == expected_str
        assert repr(loc) == expected_str


class TestHashEquality:
    """Tests for equality and hashing behavior."""

    def test_hash_and_equality(self) -> None:
        """Test that Locations with same coords are equal and have same hash."""
        loc1 = Location(1, 2)
        loc2 = Location(1, 2)
        loc3 = Location(2, 1)
        assert loc1 == loc2
        assert hash(loc1) == hash(loc2)
        assert loc1 != loc3


class TestOrderingComparisons:
    """Tests for ordering comparison methods: <, >, <=, >=."""

    def test_lt_gt_le_ge(self) -> None:
        """Test that comparison operators compare first by x, then by y when x is equal."""
        a = Location(0, 0)
        b = Location(1, 0)
        c = Location(1, 1)
        assert a < b
        assert c > b
        assert a <= b
        assert c >= b
        assert a <= Location(0, 0)
        assert b >= Location(1, 0)
