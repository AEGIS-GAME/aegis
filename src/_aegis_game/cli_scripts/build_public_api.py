"""
Generate `aegis_game/stub.py` from API functions with decorators.

This script extracts only the necessary function stubs with their docstrings.
It filters functions based on enabled feature flags and writes the resulting stubs
into `aegis_game/stub.py`.

Designed to be run manually when updating the public-facing stub interface
based on feature flags or function changes.
"""

import ast
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

from _aegis_game.aegis_config import has_feature
from _aegis_game.types.others import FeatureKey


@dataclass
class FunctionStub:
    """Represents a function stub with its metadata."""

    name: str
    signature: str
    docstring: str | None

    def format(self, *, is_last: bool = False) -> str:
        """Format the function stub as a string."""
        stub = self.signature
        if self.docstring:
            stub += self._format_docstring()
        if not is_last:
            stub += "\n"
        return stub

    def _format_docstring(self) -> str:
        """Format the docstring with proper indentation."""
        if self.docstring is None:
            return ""

        lines = self.docstring.splitlines()
        if len(lines) == 1:
            return f'\n    """{lines[0]}"""'

        indented_lines = "\n".join(
            f"    {line}" if line.strip() else "" for line in lines
        )
        return f'\n    """\n{indented_lines}\n\n    """'


class ASTFunctionParser:
    """Handles parsing of function definitions from AST nodes."""

    @staticmethod
    def format_return_annotation(returns: ast.expr | None) -> str:
        """Format the return type annotation of a function."""
        return ast.unparse(returns) if returns else ""

    @staticmethod
    def format_arguments(args: ast.arguments) -> str:
        """Format the argument list of a function into a string."""
        formatted_args: list[str] = []

        # Filter out 'self' parameter
        total_args = [arg for arg in args.args if arg.arg != "self"]
        defaults = args.defaults
        num_defaults = len(defaults)
        num_args = len(total_args)

        # Handle regular arguments with defaults
        for i, arg in enumerate(total_args):
            has_default = i >= num_args - num_defaults
            default_value = (
                defaults[i - (num_args - num_defaults)] if has_default else None
            )

            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            if default_value is not None:
                arg_str += f" = {ast.unparse(default_value)}"

            formatted_args.append(arg_str)

        # Handle *args
        if args.vararg:
            vararg_str = f"*{args.vararg.arg}"
            if args.vararg.annotation:
                vararg_str += f": {ast.unparse(args.vararg.annotation)}"
            formatted_args.append(vararg_str)

        return ", ".join(formatted_args)

    @staticmethod
    def extract_feature_key(decorator_node: ast.AST) -> FeatureKey | None:
        """Extract the feature key string from a decorator AST node."""
        if not isinstance(decorator_node, ast.Call) or not decorator_node.args:
            return None

        arg = decorator_node.args[0]
        if not isinstance(arg, ast.Constant):
            return None

        value = arg.value
        if isinstance(value, str) and value in FeatureKey.__args__:
            return value  # pyright: ignore[reportReturnType]

        return None

    @classmethod
    def should_include_function(cls, func: ast.FunctionDef) -> bool:
        """Determine whether a function should be included based on feature flags."""
        for decorator in func.decorator_list:
            feature_key = cls.extract_feature_key(decorator)
            if feature_key is not None and not has_feature(feature_key):
                return False
        return True

    @classmethod
    def parse_function(cls, func: ast.FunctionDef) -> FunctionStub:
        """Parse a function definition into a FunctionStub."""
        signature = (
            f"def {func.name}({cls.format_arguments(func.args)}) -> "
            f"{cls.format_return_annotation(func.returns)}:"
        )
        docstring = ast.get_docstring(func)

        return FunctionStub(name=func.name, signature=signature, docstring=docstring)


class ResourceReader:
    """Handles reading and parsing of Python source files."""

    @staticmethod
    def read_source(package: str, filename: str) -> str | None:
        """Read source code from a package resource."""
        try:
            return resources.read_text(package, filename)
        except (FileNotFoundError, OSError) as e:
            print(f"Error reading {filename} from {package}: {e}")
            return None

    @classmethod
    def get_all_exports(cls) -> list[str]:
        """Read and parse __init__.py from the `aegis_game` package to extract __all__."""
        source = cls.read_source("aegis_game", "__init__.py")
        if source is None:
            return []

        tree = ast.parse(source)
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue

            for target in node.targets:
                if not (isinstance(target, ast.Name) and target.id == "__all__"):
                    continue

                if not isinstance(node.value, ast.List):
                    continue

                return [
                    elt.value
                    for elt in node.value.elts
                    if isinstance(elt, ast.Constant)
                    and isinstance(elt.value, str)
                    and elt.value != "main"
                ]

        print("Warning: __all__ not found in __init__.py")
        return []

    @classmethod
    def get_method_names(cls) -> list[str]:
        """Extract method names from the game.py methods function."""
        source = cls.read_source("_aegis_game", "game.py")
        if source is None:
            return []

        tree = ast.parse(source)

        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue

            for func in node.body:
                if not (isinstance(func, ast.FunctionDef) and func.name == "methods"):
                    continue

                return cls._extract_method_names_from_function(func)

        return []

    @staticmethod
    def _extract_method_names_from_function(func: ast.FunctionDef) -> list[str]:
        """Extract method names from a methods function that returns a dict."""
        methods: list[str] = []

        for node in ast.walk(func):
            if not (isinstance(node, ast.Return) and isinstance(node.value, ast.Dict)):
                continue

            methods.extend(
                key.value
                for key in node.value.keys
                if isinstance(key, ast.Constant)
                and isinstance(key.value, str)
                and not key.value[0].isupper()
            )

        return methods

    @classmethod
    def get_functions_from_module(
        cls, package: str, module: str, method_names: list[str]
    ) -> list[ast.FunctionDef]:
        """Get function definitions from a specific module."""
        source = cls.read_source(package, module)
        if source is None:
            return []

        tree = ast.parse(source)
        return [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name in method_names
        ]


class StubGenerator:
    """Main class for generating stub files."""

    def __init__(self) -> None:
        self.parser: ASTFunctionParser = ASTFunctionParser()
        self.reader: ResourceReader = ResourceReader()

    def _build_header(self, stubs: list[FunctionStub]) -> str:
        """Generate the import/header section for the stub file."""
        needs_numpy = any("predict" in stub.name for stub in stubs)
        needs_messages = any("message" in stub.name for stub in stubs)

        imports: list[str] = []
        if needs_numpy:
            imports.extend(["import numpy as np", "from numpy.typing import NDArray"])

        relative_imports = self.reader.get_all_exports()
        if not needs_messages and "Message" in relative_imports:
            relative_imports.remove("Message")

        relative_imports.sort()

        import_lines: list[str] = []
        import_lines.extend(imports)
        import_lines.append("from . import (")
        import_lines.extend(f"    {name}," for name in relative_imports)
        import_lines.append(")\n\n")

        import_block = "\n".join(import_lines)

        return f'''"""
Autogenerated from API functions.

Do not modify manually.
"""
# ruff: noqa: F401
# pyright: reportReturnType=false
# pyright: reportUnusedImport=false
# pyright: reportUnusedParameter=false

{import_block}
'''

    def _collect_functions(self) -> list[ast.FunctionDef]:
        """Collect all relevant function definitions from modules."""
        method_names = self.reader.get_method_names()

        # Get functions from agent_controller.py
        ac_functions = self.reader.get_functions_from_module(
            "_aegis_game", "agent_controller.py", method_names
        )
        ac_names = {func.name for func in ac_functions}

        # Get functions from game.py (excluding those already in agent_controller)
        game_functions = self.reader.get_functions_from_module(
            "_aegis_game", "game.py", method_names
        )
        game_functions = [func for func in game_functions if func.name not in ac_names]

        return ac_functions + game_functions

    def _write_stub_file(self, content: str) -> None:
        """Write the generated content to the stub file."""
        output_path = Path(__file__).parent.parent.parent / "aegis_game" / "stub.py"
        try:
            _ = output_path.write_text(content, encoding="utf-8", newline="\n")
            print("Successfully generated stub.")
        except (OSError, PermissionError) as e:
            print(f"Error writing stub.py: {e}")

    def generate(self) -> None:
        """Generate the complete stub file."""
        all_functions = self._collect_functions()

        # Filter functions based on feature flags
        included_functions = [
            func for func in all_functions if self.parser.should_include_function(func)
        ]

        # Convert to function stubs
        stubs = [self.parser.parse_function(func) for func in included_functions]

        # Generate content
        header = self._build_header(stubs)
        stub_content = "\n\n".join(
            stub.format(is_last=(i == len(stubs) - 1)) for i, stub in enumerate(stubs)
        )

        content = header + stub_content + "\n"

        # Write to file
        self._write_stub_file(content)
        print(f"Generated stub with {len(stubs)} functions")


def main() -> None:
    """Entry point for the stub generator."""
    generator = StubGenerator()
    generator.generate()


if __name__ == "__main__":
    main()
