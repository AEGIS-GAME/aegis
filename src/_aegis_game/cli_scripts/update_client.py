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

    if not version_info["update_available"]:
        print(f"Client is up to date (version {version_info['local_version']})")
        return

    print(
        f"Client Update available: {version_info['local_version']} -> {version_info['latest_version']}"
    )
    print("Updating client...")

    # Reuse the client installer logic
    installer = ClientInstaller()
    installer.install()

    print("Client update completed!")
