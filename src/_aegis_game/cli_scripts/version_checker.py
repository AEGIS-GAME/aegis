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
        return release.get("tag_name", "").lstrip("v") if release else None  # pyright: ignore[reportAny]

    def is_update_available(self) -> bool:
        """Check if a newer version is available."""
        local_version = self.get_local_version()
        latest_version = self.get_latest_version()

        if not local_version or not latest_version:
            return False

        return local_version != latest_version

    def get_version_info(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        """Get comprehensive version information."""
        local_version: str | None = self.get_local_version()
        latest_version: str | None = self.get_latest_version()

        client_exists = False
        if self.client_dir.exists():
            # Check for client-version.txt (primary indicator) or package.json (development)
            if (self.client_dir / "client-version.txt").exists() or (self.client_dir / "package.json").exists():
                client_exists = True
            # Check for executable files (installed client)
            else:
                executable_patterns = ["*.exe", "*.app", "*.AppImage"]
                for pattern in executable_patterns:
                    if list(self.client_dir.glob(pattern)):
                        client_exists = True
                        break

        print(f"Debug: Looking for client in: {self.client_dir.absolute()}")
        print(f"Debug: Client directory exists: {self.client_dir.exists()}")
        if self.client_dir.exists():
            print(
                f"Debug: Client directory contents: {list(self.client_dir.iterdir())}"
            )

        return {
            "local_version": local_version,
            "latest_version": latest_version,
            "update_available": self.is_update_available(),
            "client_exists": client_exists,
        }
