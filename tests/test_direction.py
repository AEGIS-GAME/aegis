"""Tests for the Direction enum."""

from __future__ import annotations

import pytest

from src._aegis_game.common import Direction


class TestBasics:
    """Test basic Direction enum functionality."""

    def test_direction_values(self) -> None:
        """Test that each direction has the correct (dx, dy) values."""
        assert Direction.NORTH.value == (0, 1)
        assert Direction.NORTHEAST.value == (1, 1)
        assert Direction.EAST.value == (1, 0)
        assert Direction.SOUTHEAST.value == (1, -1)
        assert Direction.SOUTH.value == (0, -1)
        assert Direction.SOUTHWEST.value == (-1, -1)
        assert Direction.WEST.value == (-1, 0)
        assert Direction.NORTHWEST.value == (-1, 1)
        assert Direction.CENTER.value == (0, 0)

    def test_dx_property(self) -> None:
        """Test the dx property returns correct x-axis change."""
        assert Direction.NORTH.dx == 0
        assert Direction.NORTHEAST.dx == 1
        assert Direction.EAST.dx == 1
        assert Direction.SOUTHEAST.dx == 1
        assert Direction.SOUTH.dx == 0
        assert Direction.SOUTHWEST.dx == -1
        assert Direction.WEST.dx == -1
        assert Direction.NORTHWEST.dx == -1
        assert Direction.CENTER.dx == 0

    def test_dy_property(self) -> None:
        """Test the dy property returns correct y-axis change."""
        assert Direction.NORTH.dy == 1
        assert Direction.NORTHEAST.dy == 1
        assert Direction.EAST.dy == 0
        assert Direction.SOUTHEAST.dy == -1
        assert Direction.SOUTH.dy == -1
        assert Direction.SOUTHWEST.dy == -1
        assert Direction.WEST.dy == 0
        assert Direction.NORTHWEST.dy == 1
        assert Direction.CENTER.dy == 0


class TestRotation:
    """Test direction rotation methods."""

    @pytest.mark.parametrize(
        ("direction", "expected"),
        [
            (Direction.NORTH, Direction.NORTHWEST),
            (Direction.NORTHEAST, Direction.NORTH),
            (Direction.EAST, Direction.NORTHEAST),
            (Direction.SOUTHEAST, Direction.EAST),
            (Direction.SOUTH, Direction.SOUTHEAST),
            (Direction.SOUTHWEST, Direction.SOUTH),
            (Direction.WEST, Direction.SOUTHWEST),
            (Direction.NORTHWEST, Direction.WEST),
            (Direction.CENTER, Direction.CENTER),
        ],
    )
    def test_rotate_left(self, direction: Direction, expected: Direction) -> None:
        """Test rotating left (counter-clockwise) 45 degrees."""
        assert direction.rotate_left() == expected

    @pytest.mark.parametrize(
        ("direction", "expected"),
        [
            (Direction.NORTH, Direction.NORTHEAST),
            (Direction.NORTHEAST, Direction.EAST),
            (Direction.EAST, Direction.SOUTHEAST),
            (Direction.SOUTHEAST, Direction.SOUTH),
            (Direction.SOUTH, Direction.SOUTHWEST),
            (Direction.SOUTHWEST, Direction.WEST),
            (Direction.WEST, Direction.NORTHWEST),
            (Direction.NORTHWEST, Direction.NORTH),
            (Direction.CENTER, Direction.CENTER),
        ],
    )
    def test_rotate_right(self, direction: Direction, expected: Direction) -> None:
        """Test rotating right (clockwise) 45 degrees."""
        assert direction.rotate_right() == expected

    def test_multiple_rotations(self) -> None:
        """Test that 8 rotations in one direction return to original."""
        direction = Direction.NORTH

        # 8 left rotations should return to start
        current = direction
        for _ in range(8):
            current = current.rotate_left()
        assert current == direction

        # 8 right rotations should return to start
        current = direction
        for _ in range(8):
            current = current.rotate_right()
        assert current == direction

    def test_left_right_inverse(self) -> None:
        """Test that rotating left then right returns to original."""
        for direction in [d for d in Direction if d != Direction.CENTER]:
            rotated_left = direction.rotate_left()
            back_to_original = rotated_left.rotate_right()
            assert back_to_original == direction


class TestOpposite:
    """Test the get_opposite method."""

    @pytest.mark.parametrize(
        ("direction", "expected"),
        [
            (Direction.NORTH, Direction.SOUTH),
            (Direction.NORTHEAST, Direction.SOUTHWEST),
            (Direction.EAST, Direction.WEST),
            (Direction.SOUTHEAST, Direction.NORTHWEST),
            (Direction.SOUTH, Direction.NORTH),
            (Direction.SOUTHWEST, Direction.NORTHEAST),
            (Direction.WEST, Direction.EAST),
            (Direction.NORTHWEST, Direction.SOUTHEAST),
            (Direction.CENTER, Direction.CENTER),
        ],
    )
    def test_get_opposite(self, direction: Direction, expected: Direction) -> None:
        """Test that get_opposite returns the correct opposite direction."""
        assert direction.get_opposite() == expected

    def test_opposite_symmetry(self) -> None:
        """Test that the opposite of an opposite is the original."""
        for direction in Direction:
            opposite = direction.get_opposite()
            opposite_of_opposite = opposite.get_opposite()
            assert opposite_of_opposite == direction


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_all_directions_exist(self) -> None:
        """Test that all expected directions exist in the enum."""
        expected_directions = {
            "NORTH",
            "NORTHEAST",
            "EAST",
            "SOUTHEAST",
            "SOUTH",
            "SOUTHWEST",
            "WEST",
            "NORTHWEST",
            "CENTER",
        }
        actual_directions = {d.name for d in Direction}
        assert actual_directions == expected_directions

    def test_direction_count(self) -> None:
        """Test that there are exactly 9 directions."""
        dir_expected_length: int = 9
        assert len(Direction) == dir_expected_length

    def test_enum_iteration(self) -> None:
        """Test that we can iterate over all directions."""
        directions = list(Direction)
        dir_expected_length: int = 9
        assert len(directions) == dir_expected_length
        assert Direction.NORTH in directions
        assert Direction.CENTER in directions
