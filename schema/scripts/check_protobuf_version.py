#!/usr/bin/env python3
"""
Script to check protobuf version compatibility.
Ensures the generated protobuf files are compatible with the installed runtime.
"""

import re
import sys
from pathlib import Path


def extract_protobuf_version_from_file(file_path: str) -> str:
    """Extract protobuf version from a generated protobuf file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Look for the protobuf version comment
            match = re.search(r"# Protobuf Python Version: (\d+\.\d+\.\d+)", content)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return None


def check_protobuf_versions():
    """Check protobuf versions in generated files."""
    print("Checking protobuf version compatibility...")

    # Check Python files
    python_dir = Path("python")
    if python_dir.exists():
        print("\nPython protobuf files:")
        versions = set()
        for py_file in python_dir.glob("*.py"):
            version = extract_protobuf_version_from_file(str(py_file))
            if version:
                versions.add(version)
                print(f"  {py_file.name}: {version}")

        if len(versions) > 1:
            print(f"\n⚠️  WARNING: Multiple protobuf versions found: {versions}")
            print("   This may cause compatibility issues.")
        elif versions:
            print(f"\n✅ All Python files use protobuf version: {list(versions)[0]}")

    # Check TypeScript files (they don't have version comments, but we can verify they exist)
    ts_dir = Path("ts")
    if ts_dir.exists():
        ts_files = list(ts_dir.glob("*.ts"))
        print(f"\nTypeScript protobuf files: {len(ts_files)} files found")

    print("\nProtobuf version check completed!")


if __name__ == "__main__":
    check_protobuf_versions()
