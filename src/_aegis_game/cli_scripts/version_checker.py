import json
from pathlib import Path
from typing import Any

import requests


class VersionChecker:
    """Handles version checking for AEGIS client updates."""

    OWNER: str = "AEGIS-GAME"
    REPO: str = "aegis"

    def __init__(self) -> None:
        self.client_dir: Path = self._find_client_directory()

    def _find_client_directory(self) -> Path:
        """Find the client directory, searching up from current directory."""
        current_dir = Path.cwd()

        # First, try the current directory
        if (current_dir / "client").exists():
            return current_dir / "client"

        # Search up the directory tree for AEGIS project root
        for parent in current_dir.parents:
            client_dir = parent / "client"
            if client_dir.exists():
                return client_dir

        # If not found, return relative path (fallback)
        return Path("client")

    def get_local_version(self) -> str | None:
        """Get the version of the locally installed client."""
        # First try to find client-version.txt
        version_file_path: Path = self.client_dir / "client-version.txt"
        if version_file_path.exists():
            try:
                with version_file_path.open() as f:
                    version = f.read().strip()
                    return version if version else None
            except Exception as e:  # noqa: BLE001
                print(f"Error reading client-version.txt: {e}")

        # Fallback to package.json (for development)
        package_json_path: Path = self.client_dir / "package.json"
        if package_json_path.exists():
            try:
                with package_json_path.open() as f:
                    data = json.load(f)  # pyright: ignore[reportAny]
                    return data.get("version")  # pyright: ignore[reportAny]
            except (json.JSONDecodeError, KeyError):
                pass

        return None

    def get_latest_version(self) -> str | None:
        """Get the latest version from GitHub releases."""
        url = f"https://api.github.com/repos/{self.OWNER}/{self.REPO}/releases/latest"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException:
            return None

        release: dict[str, Any] = response.json()  # pyright: ignore[reportAny, reportExplicitAny]

        if not release:
            return None

        return (
            release.get("tag_name", "").lstrip("v").lstrip("client-")  # pyright: ignore[reportAny]
            if release
            else None
        )

    def _compare_versions(self, version1: str, version2: str) -> int:
        """Compare two semantic versions. Returns -1 if version1 < version2, 0 if equal, 1 if version1 > version2."""

        def version_parts(version: str) -> list[int]:
            return [int(part) for part in version.split(".")]

        parts1 = version_parts(version1)
        parts2 = version_parts(version2)

        # Pad with zeros to make equal length
        max_len = max(len(parts1), len(parts2))
        parts1.extend([0] * (max_len - len(parts1)))
        parts2.extend([0] * (max_len - len(parts2)))

        for p1, p2 in zip(parts1, parts2, strict=True):
            if p1 < p2:
                return -1
            elif p1 > p2:  # noqa: RET505
                return 1

        return 0

    def is_update_available(self) -> bool:
        """Check if a newer version is available."""
        local_version = self.get_local_version()
        latest_version = self.get_latest_version()

        if not local_version or not latest_version:
            return False

        # Normalize both versions before comparing
        normalized_local = (
            local_version.lstrip("v").lstrip("client-") if local_version else ""
        )
        normalized_latest = (
            latest_version.lstrip("v").lstrip("client-") if latest_version else ""
        )

        # Use semantic version comparison - update available if local < latest
        return self._compare_versions(normalized_local, normalized_latest) < 0

    def get_version_info(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        """Get comprehensive version information."""
        local_version: str | None = self.get_local_version()
        latest_version: str | None = self.get_latest_version()

        client_exists = False
        if self.client_dir.exists():
            # Check for client-version.txt (primary indicator) or package.json (development)
            if (self.client_dir / "client-version.txt").exists() or (
                self.client_dir / "package.json"
            ).exists():
                client_exists = True
            else:
                # Check for executable files (installed client)
                executable_patterns = ["*.exe", "*.app", "*.AppImage"]
                for pattern in executable_patterns:
                    if list(self.client_dir.glob(pattern)):
                        client_exists = True
                        break

        return {
            "local_version": local_version,
            "latest_version": latest_version,
            "update_available": self.is_update_available(),
            "client_exists": client_exists,
        }
