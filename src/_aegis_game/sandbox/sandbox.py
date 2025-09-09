# pyright: reportMissingTypeStubs = false
from __future__ import annotations

import logging
import re
from typing import TYPE_CHECKING, cast

from RestrictedPython.compile import (
    compile_restricted,  # pyright: ignore[reportUnknownVariableType]
)

from _aegis_game.logger import LOGGER

from .typed_ast import NodeTransformer

if TYPE_CHECKING:
    from pathlib import Path
    from types import CodeType

logger = logging.getLogger(__name__)


class Sandbox:
    def __init__(self, code: dict[str, CodeType]) -> None:
        """
        Initialize CodeSandbox with compiled code modules.

        Args:
            code: Dictionary mapping module names to compiled code objects.

        """
        self.code: dict[str, CodeType] = code.copy()

    @classmethod
    def from_directory_dict(cls, files: dict[str, str]) -> Sandbox:
        """
        Create CodeSandbox from a dictionary of filename -> source code mappings.

        Args:
            files: Dictionary mapping filenames to their source code content.

        Returns:
            A new CodeSandbox instance with compiled modules.

        Raises:
            CompilationError: If any file fails to compile.

        """
        code: dict[str, CodeType] = {}

        for filename, source in files.items():
            if not filename.endswith(".py"):
                LOGGER.warning(f"Skipping non-Python file: {filename}")
                continue

            module_name = filename.removesuffix(".py")
            cleaned_source = cls._strip_stub_import(source)

            try:
                compiled = cast(
                    "CodeType",
                    compile_restricted(
                        cleaned_source,
                        filename,
                        "exec",
                        policy=NodeTransformer,
                    ),
                )
            except Exception as e:
                error = f"Failed to compile {filename}: {e}"
                raise CompilationError(error) from e

            code[module_name] = compiled

        return cls(code)

    @classmethod
    def from_directory(cls, directory_path: Path) -> Sandbox:
        """
        Create CodeSandbox from a directory containing Python files.

        Args:
            directory_path: Path to directory containing Python files.

        Returns:
            A new CodeSandbox instance with compiled modules from the directory.

        Raises:
            CodeSandboxError: If directory doesn't exist or is inaccessible.
            CompilationError: If any file fails to compile.

        """
        if not directory_path.exists():
            error = f"Directory does not exist: {directory_path}"
            raise SandboxError(error)

        if not directory_path.is_dir():
            error = f"Path is not a directory: {directory_path}"
            raise SandboxError(error)

        try:
            files: dict[str, str] = {}
            for file_path in directory_path.glob("*.py"):
                if file_path.is_file():
                    try:
                        files[file_path.name] = file_path.read_text(encoding="utf-8")
                    except (OSError, UnicodeDecodeError) as e:
                        LOGGER.warning(f"Failed to read {file_path}: {e}")
                        continue

            if not files:
                LOGGER.warning(f"No readable Python files found in {directory_path}")

            return cls.from_directory_dict(files)

        except OSError as e:
            error = f"Failed to access directory {directory_path}: {e}"
            raise SandboxError(error) from e

    @staticmethod
    def _strip_stub_import(code: str) -> str:
        """
        Remove aegis_game.stub import statements from code.

        Args:
            code: Source code to process.

        Returns:
            Code with aegis_game.stub imports removed.

        """
        pattern = r"^.*from\s+aegis_game\.stub\s+import.*(?:\r\n|\r|\n)?"
        return re.sub(pattern, "", code, flags=re.MULTILINE)

    def __getitem__(self, module_name: str) -> CodeType:
        """Get the compiled module code by module name."""
        return self.code[module_name]

    def __contains__(self, module_name: str) -> bool:
        """Check if module is in the sandbox using `in`."""
        return module_name in self.code


class SandboxError(Exception):
    """Base exception for CodeSandbox operations."""


class CompilationError(SandboxError):
    """Raised when code compilation fails."""
