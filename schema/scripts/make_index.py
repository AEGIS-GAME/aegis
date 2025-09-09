# noqa: INP001

"""Generate index.aegis.ts and index.ts for TS schema."""

from pathlib import Path

TS_DIR = Path(__file__).parent.parent / "ts"
INDEX_AEGIS = TS_DIR / "index.aegis.ts"
INDEX_MAIN = TS_DIR / "index.ts"


def generate_index_aegis_ts() -> None:
    """Make index.aegis.ts with exports."""
    exports: list[str] = []

    for ts_file in TS_DIR.glob("*.ts"):
        if ts_file.name in ("index.ts", "index.aegis.ts"):
            continue
        module = ts_file.stem
        exports.append(f"export * from './{module}';")

    index_content = "\n".join(exports) + "\n"
    _ = INDEX_AEGIS.write_text(index_content)
    print(f"Generated {INDEX_AEGIS} with {len(exports)} exports.")


def generate_index_ts() -> None:
    """Make index.ts with schema namespace import."""
    index_content = "export * as schema from './index.aegis'\n"
    _ = INDEX_MAIN.write_text(index_content)
    print(f"Generated {INDEX_MAIN} with schema namespace import.")


if __name__ == "__main__":
    generate_index_aegis_ts()
    generate_index_ts()
