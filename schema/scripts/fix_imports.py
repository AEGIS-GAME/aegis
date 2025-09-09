# noqa: INP001

"""Fix protobuf Python imports in generated files and fix index.ts export."""

import re
from itertools import chain
from pathlib import Path

PYTHON_DIR = Path(__file__).parent.parent / "python"


def fix_imports(file: Path) -> None:
    """Fix the broken imports caused by protoc Python plugin."""
    content = file.read_text()

    # Replace 'import xyz_pb2 as _xyz_pb2' with 'from . import xyz_pb2 as _xyz_pb2'
    pattern = re.compile(r"^import (.+_pb2) as (.+_pb2)", re.MULTILINE)
    fixed_content = pattern.sub(r"from . import \1 as \2", content)

    _ = file.write_text(fixed_content)


def main() -> None:
    """Run all fixes."""
    print(f"Fixing imports in {PYTHON_DIR}")
    for py_file in chain(PYTHON_DIR.glob("*.py"), PYTHON_DIR.glob("*.pyi")):
        print(f"Fixing {py_file.name}")
        fix_imports(py_file)
    print("Done fixing files.")


if __name__ == "__main__":
    main()
