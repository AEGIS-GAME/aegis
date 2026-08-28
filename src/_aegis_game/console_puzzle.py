import importlib.util
from collections.abc import Callable
from pathlib import Path


class ConsolePuzzle:
    def __init__(self, puzzle: str, check: Callable[[str], bool]) -> None:
        self.puzzle: str = puzzle
        self.check: Callable[[str], bool] = check

    @classmethod
    def load(cls, path: Path) -> "ConsolePuzzle":
        spec = importlib.util.spec_from_file_location("aegis_console_puzzle", path)
        if spec is None or spec.loader is None:
            error = f"Unable to load console puzzle from {path}"
            raise ValueError(error)

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for name in ("puzzle", "check"):
            if not hasattr(module, name):
                error = f"Console puzzle {path} must define '{name}'"
                raise ValueError(error)

        return cls(module.puzzle, module.check)
