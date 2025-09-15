"""Update the AEGIS client to the latest version."""

import sys

from .client_installer import ClientInstaller
from .version_checker import VersionChecker


def main() -> None:
    """Entry point for the client updater."""
    checker = VersionChecker()
    version_info = checker.get_version_info()

    if not version_info["client_exists"]:
        print("No AEGIS client found. Run 'aegis init' first to install the client.")
        sys.exit(1)

    local_version: str | None = version_info["local_version"]
    latest_version: str | None = version_info["latest_version"]

    if not latest_version:
        print("Failed to fetch latest version from GitHub.")
        sys.exit(1)

    if local_version == latest_version:
        print(f"Client is already up to date (version {local_version})")
        return

    print(f"Client Update available: {local_version} → {latest_version}")
    print("Downloading and installing latest client release...")

    # Download and install the latest release
    installer = ClientInstaller()
    installer.install()

    print("Client update completed!")
