"""Update the AEGIS client to the latest version."""

import sys

from .client_installer import ClientInstaller
from .version_checker import VersionChecker


def main() -> None:  # noqa: C901
    """Entry point for the client updater."""
    checker = VersionChecker()
    version_info = checker.get_version_info()

    if not version_info["client_exists"]:
        print("No AEGIS client found. Run 'aegis init' first to install the client.")
        sys.exit(1)

    local_version: str | None = version_info["local_version"]  # pyright: ignore[reportAny]
    latest_version: str | None = version_info["latest_version"]  # pyright: ignore[reportAny]

    if not latest_version:
        print("Failed to fetch latest version from GitHub.")
        sys.exit(1)

    client_dir = checker.client_dir
    version_file = client_dir / "client-version.txt"
    if not version_file.exists():
        print(f"Creating client-version.txt with version {latest_version}")
        try:
            with version_file.open("w") as f:
                _ = f.write(latest_version)
        except Exception as e:  # noqa: BLE001
            print(f"Warning: Failed to create client-version.txt: {e}")

    def compare_versions(version1: str, version2: str) -> int:
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

    normalized_local = (
        local_version.lstrip("v").lstrip("client-") if local_version else ""
    )
    normalized_latest = (
        latest_version.lstrip("v").lstrip("client-") if latest_version else ""
    )

    if (
        normalized_local
        and normalized_latest
        and compare_versions(normalized_local, normalized_latest) >= 0
    ):
        print(f"Client is already up to date (version {normalized_local})")
        return

    print(f"Client Update available: {normalized_local} → {normalized_latest}")
    print("Downloading and installing latest client release...")

    # Download and install the latest release
    installer = ClientInstaller()
    installer.install()

    print("Client update completed!")
