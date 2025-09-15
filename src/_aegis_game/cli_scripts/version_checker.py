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
        # First try to find package.json (for development)
        package_json_path: Path = self.client_dir / "package.json"
        if package_json_path.exists():
            try:
                with package_json_path.open() as f:
                    data = json.load(f)  # pyright: ignore[reportAny]
                    return data.get("version")  # pyright: ignore[reportAny]
            except (json.JSONDecodeError, KeyError):
                pass

        # For installed clients, we can't determine version from executable alone
        # Return None to indicate we can't determine the version
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

        if not local_version:
            return latest_version is not None

        if not latest_version:
            return False

        # Simple version comparison (assumes semantic versioning)
        try:
            local_parts: list[int] = [int(x) for x in local_version.split(".")]
            latest_parts = [int(x) for x in latest_version.split(".")]
        except ValueError:
            # If version parsing fails, assume no update available
            return False
        else:
            # Pad with zeros if needed
            max_len: int = max(len(local_parts), len(latest_parts))
            local_parts.extend([0] * (max_len - len(local_parts)))
            latest_parts.extend([0] * (max_len - len(latest_parts)))

            return latest_parts > local_parts

    def get_version_info(self) -> dict[str, Any]:  # pyright: ignore[reportExplicitAny]
        """Get comprehensive version information."""
        local_version: str | None = self.get_local_version()
        latest_version: str | None = self.get_latest_version()

        # Check if client exists (either package.json or executable)
        client_exists = False
        if self.client_dir.exists():
            # Check for package.json (development) or executable (installed)
            if (self.client_dir / "package.json").exists():
                client_exists = True
            else:
                # Check for executable files
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
