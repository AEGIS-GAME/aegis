#!/usr/bin/env python3
"""
Script to fix line endings in generated protobuf files.
Converts CRLF (Windows) to LF (Unix) line endings.
"""

import glob
import os
from pathlib import Path


def fix_line_endings_in_file(file_path: str) -> int:
    """Convert CRLF line endings to LF in a single file.

    Returns:
        int: Number of CRLF sequences replaced
    """
    try:
        # Read file as binary to detect line endings
        with open(file_path, "rb") as f:
            content = f.read()

        # Check if file has CRLF endings
        if b"\r\n" in content:
            # Convert CRLF to LF
            new_content = content.replace(b"\r\n", b"\n")

            # Write back with LF endings
            with open(file_path, "wb") as f:
                f.write(new_content)

            replaced_count = content.count(b"\r\n")
            print(f"Fixed {replaced_count} CRLF sequences in: {file_path}")
            return replaced_count
        else:
            print(f"Already LF endings: {file_path}")
            return 0

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0


def fix_line_endings_in_directory(directory: str, pattern: str = "*") -> int:
    """Fix line endings in all files matching the pattern in the directory.

    Returns:
        int: Total number of CRLF sequences replaced
    """
    directory_path = Path(directory)
    if not directory_path.exists():
        print(f"Directory does not exist: {directory}")
        return 0

    # Find all files matching the pattern
    search_pattern = directory_path / pattern
    files = glob.glob(str(search_pattern))

    if not files:
        print(f"No files found matching pattern: {search_pattern}")
        return 0

    print(f"Found {len(files)} files to process in {directory}")

    total_replaced = 0
    for file_path in files:
        if os.path.isfile(file_path):
            total_replaced += fix_line_endings_in_file(file_path)

    return total_replaced


def main():
    """Main function to fix line endings in all generated protobuf files."""
    print("Fixing line endings in generated protobuf files...")

    total_replaced = 0

    # Fix Python files
    print("\nProcessing Python files...")
    total_replaced += fix_line_endings_in_directory("python", "*.py")
    total_replaced += fix_line_endings_in_directory("python", "*.pyi")

    # Fix TypeScript files
    print("\nProcessing TypeScript files...")
    total_replaced += fix_line_endings_in_directory("ts", "*.ts")

    if total_replaced > 0:
        print(
            f"\nLine ending fix completed! Replaced {total_replaced} CRLF sequences with LF."
        )
    else:
        print("\nLine ending fix completed! All files already had LF endings.")


if __name__ == "__main__":
    main()
