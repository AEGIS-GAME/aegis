# pyright: reportAny = false
# pyright: reportExplicitAny = false
import platform
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any, ClassVar

import requests

from .version_checker import VersionChecker


class ClientInstaller:
    """Handles downloading and installing the AEGIS client."""

    OWNER: str = "AEGIS-GAME"
    REPO: str = "aegis"
    CHUNK_SIZE: int = 8192
    CLIENT_DIR: Path = Path("client")

    PLATFORM_ASSETS: ClassVar[dict[str, str]] = {
        "windows": "win-client.zip",
        "darwin": "mac-client.zip",
        "linux": "linux-client.zip",
    }

    EXECUTABLE_PATTERNS: ClassVar[list[str]] = ["*.app", "*.AppImage", "*.exe"]

    def __init__(self) -> None:
        self.VERSION_CHECKER: VersionChecker = VersionChecker()
        self.platform: str = self._detect_platform()
        self.asset_name: str = self.PLATFORM_ASSETS[self.platform]
        self.version: str | None = self.VERSION_CHECKER.get_latest_version()
        if not self.version:
            msg = "No client version found"
            raise ValueError(msg)

    def _detect_platform(self) -> str:
        """Detect the current platform."""
        system = platform.system().lower()

        if system.startswith("win"):
            return "windows"
        if system.startswith("darwin"):
            return "darwin"
        if system.startswith("linux"):
            return "linux"
        sys.exit(f"Unsupported platform: {system}")

    def _get_latest_release(self) -> dict[str, Any]:
        """Fetch the latest client release from GitHub."""
        url = f"https://api.github.com/repos/{self.OWNER}/{self.REPO}/releases/latest"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            sys.exit(f"Failed to fetch releases: {e}")

        release = response.json()

        if not release:
            sys.exit("No client release found")

        return release

    def _find_asset(self, release: dict[str, Any]) -> dict[str, Any]:
        """Find the matching asset in the GitHub release."""
        for asset in release["assets"]:
            if asset["name"] == self.asset_name:
                return asset

        sys.exit(
            f"Asset '{self.asset_name}' not found in release {release['tag_name']}"
        )

    def _download_with_progress(self, url: str, output_path: Path) -> None:
        """Download client zip file with progress indicator."""
        try:
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            sys.exit(f"Download failed: {e}")

        total_size = int(response.headers.get("Content-Length", 0))
        downloaded = 0

        with output_path.open("wb") as f:
            for chunk in response.iter_content(chunk_size=self.CHUNK_SIZE):
                if not chunk:
                    continue

                _ = f.write(chunk)
                downloaded += len(chunk)
                self._show_progress(downloaded, total_size)

        print(f"\nDownload complete: {output_path}")

    def _show_progress(self, downloaded: int, total_size: int) -> None:
        """Display download progress."""
        downloaded_mb = downloaded / (1024 * 1024)

        if total_size:
            total_mb = total_size / (1024 * 1024)
            percent = (downloaded / total_size) * 100
            print(
                f"Downloaded {downloaded_mb:.2f} MB / {total_mb:.2f} MB ({percent:.1f}%)",
                end="\r",
            )
        else:
            print(f"Downloaded {downloaded_mb:.2f} MB", end="\r")

    def _extract_archive(self, zip_path: Path) -> None:
        """Extract the downloaded archive."""
        if self.CLIENT_DIR.exists():
            shutil.rmtree(self.CLIENT_DIR)

        self.CLIENT_DIR.mkdir(parents=True, exist_ok=True)

        try:
            if self.platform == "windows":
                with zipfile.ZipFile(zip_path, "r") as zip_file:
                    zip_file.extractall(self.CLIENT_DIR)
            else:
                _ = subprocess.run(  # noqa: S603
                    ["unzip", "-o", str(zip_path), "-d", str(self.CLIENT_DIR)],  # noqa: S607
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
        except Exception as e:  # noqa: BLE001
            sys.exit(f"Failed to extract archive: {e}")

        print(f"Extracted to: {self.CLIENT_DIR}")

    def _create_version_file(self) -> None:
        """Create client-version.txt file with the current version."""
        version_file = self.CLIENT_DIR / "client-version.txt"
        if not self.version:
            msg = "No client version found"
            raise ValueError(msg)
        try:
            # Ensure we store clean version without prefixes
            clean_version = self.version.lstrip("v").lstrip("client-")
            with version_file.open("w") as f:
                _ = f.write(clean_version)
            print(f"Created version file: {version_file}")
        except Exception as e:  # noqa: BLE001
            print(f"Warning: Failed to create version file: {e}")

    def _find_executable(self) -> Path | None:
        """Find the main executable in the extracted files."""
        for pattern in self.EXECUTABLE_PATTERNS:
            matches = list(self.CLIENT_DIR.rglob(pattern))
            if matches:
                return matches[0]
        return None

    def _move_executable_to_root(self) -> str | None:
        """Move the main executable to the root of CLIENT_DIR."""
        executable = self._find_executable()

        if not executable:
            print("Warning: No executable found")
            return None

        if executable.parent == self.CLIENT_DIR:
            print(f"Executable already at root: {executable.name}")
            return executable.name

        destination = self.CLIENT_DIR / executable.name

        if destination.exists():
            if destination.is_dir():
                shutil.rmtree(destination)
            else:
                destination.unlink()

        _ = shutil.move(str(executable), str(destination))
        print(f"Moved executable to: {destination}")

        return executable.name

    def _cleanup_directory(self, keep_name: str) -> None:
        """Remove all files except the main executable."""
        for item in self.CLIENT_DIR.iterdir():
            if item.name == keep_name:
                continue

            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

        print(f"Cleaned directory, kept only: {keep_name}")

    def install(self) -> None:
        """Download and install the latest client."""
        zip_path = Path(self.asset_name)

        if zip_path.exists():
            print(f"Archive '{zip_path}' already exists, skipping download")
        else:
            print("Fetching latest release...")
            release = self._get_latest_release()
            asset = self._find_asset(release)

            print(f"Downloading {self.asset_name} from {release['tag_name']}...")
            self._download_with_progress(asset["browser_download_url"], zip_path)

        print("Extracting client files...")
        self._extract_archive(zip_path)

        executable_name = self._move_executable_to_root()

        if executable_name:
            self._cleanup_directory(executable_name)
            self._create_version_file()
            print(f"Installation complete! Client available in: {self.CLIENT_DIR}")
        else:
            print("Installation completed with warnings")

        if zip_path.exists():
            zip_path.unlink()
            print(f"Cleaned up downloaded archive: {zip_path}")


def main() -> None:
    """Entry point for the client installer."""
    installer = ClientInstaller()
    installer.install()
