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

    print("Downloading and installing latest client release...")

    # Always download and install the latest release
    installer = ClientInstaller()
    installer.install()

    print("Client update completed!")
