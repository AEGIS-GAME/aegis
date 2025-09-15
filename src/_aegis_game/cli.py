import sys
import traceback

from .args_parser import parse_args
from .cli_scripts.client_installer import main as install_client
from .cli_scripts.init_scaffold import init_scaffold
from .cli_scripts.update_client import main as update_client
from .play import run


def main() -> None:  # noqa: C901
    args = parse_args()

    if args.command == "run":
        try:
            if args.launch_args is None:
                sys.exit(1)
            run(args.launch_args)
        except Exception as e:  # noqa: BLE001
            print(f"ERROR: {e}", file=sys.stderr)
            traceback.print_exc()
            sys.exit(1)

    elif args.command == "forge":
        from .cli_scripts.build_public_api import main as build_api  # noqa: PLC0415

        try:
            build_api()
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            sys.exit(1)
    elif args.command == "init":
        try:
            if args.init_args is None:
                sys.exit(1)
            init_scaffold(args.init_args.init_type)
            install_client()
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            sys.exit(1)
    elif args.command == "update":
        try:
            if args.update_args is None:
                sys.exit(1)
            update_client()
        except Exception:  # noqa: BLE001
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()
