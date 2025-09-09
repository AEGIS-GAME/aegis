from .common import Cell, Location
from .constants import Constants


class World:
    def __init__(  # noqa: PLR0913
        self,
        width: int,
        height: int,
        seed: int,
        start_energy: int,
        cells: list[Cell],
        init_spawns: dict[Location, int],
    ) -> None:
        self.width: int = width
        self.height: int = height
        self.rounds: int = Constants.DEFAULT_MAX_ROUNDS
        self.seed: int = seed
        self.start_energy: int = start_energy
        self.cells: list[Cell] = cells
        self.total_survivors: int = sum(cell.number_of_survivors() for cell in cells)
        self.init_spawns: dict[Location, int] = init_spawns

        self._validate_map()

    def _validate_map(self) -> None:
        min_size = Constants.WORLD_MIN
        max_size = Constants.WORLD_MAX

        if self.width < min_size:
            error = f"World width must be at least {min_size}"
            raise ValueError(error)

        if self.width > max_size:
            error = f"World width must not exceed {max_size}"
            raise ValueError(error)

        if self.height < min_size:
            error = f"World height must be at least {min_size}"
            raise ValueError(error)

        if self.height > max_size:
            error = f"World height must not exceed {max_size}"
            raise ValueError(error)
