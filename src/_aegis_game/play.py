from pathlib import Path

from google.protobuf.message import DecodeError

from .aegis_config import has_feature
from .args_parser import LaunchArgs
from .game import Game
from .game_pb import GamePb
from .logger import LOGGER, setup_console_and_file_logging, setup_console_logging
from .sandbox.sandbox import Sandbox
from .server_websocket import WebSocketServer
from .team import Team
from .world_pb import load_world


def log_game_end(game: Game, args: LaunchArgs, i: int) -> None:
    LOGGER.info("========== AEGIS END ==========")
    LOGGER.info(f"Finished on round {game.round}")
    LOGGER.info(f"Reason: {getattr(game.reason, 'value', 'Unknown')}")
    LOGGER.info("")
    LOGGER.info(f"{'Team':<12} {'Score':>8} {'Saved':>8}")
    if has_feature("ALLOW_AGENT_PREDICTIONS"):
        LOGGER.info(f"{'Team':<12} {'Score':>8} {'Saved':>8} {'Predictions':>14}")
        LOGGER.info("-" * 46)
    else:
        LOGGER.info("-" * 31)

    for team in Team:
        if team == Team.VOIDSEERS and args.agent2 is None:
            continue

        score = game.team_info.get_score(team)
        saved = game.team_info.get_saved(team)
        predictions = game.team_info.get_predicted_right(team)

        if has_feature("ALLOW_AGENT_PREDICTIONS"):
            LOGGER.info(f"{team.name:<12} {score:>8} {saved:>8} {predictions:>14}")
        else:
            LOGGER.info(f"{team.name:<12} {score:>8} {saved:>8}")

    if has_feature("ALLOW_AGENT_PREDICTIONS"):
        LOGGER.info("=" * 46)
    else:
        LOGGER.info("=" * 31)

    if i < len(args.world) - 1:
        print("\n" + "=" * 80 + "\n\n")


def make_game_start_string(args: LaunchArgs, world: str) -> str:
    if args.agent and not args.agent2:
        return f"GOOBS on {world}"

    if args.agent2 and not args.agent:
        return f"VOIDSEERS on {world}"

    # TODO @dante: This will have to show actual team names
    return f"GOOBS vs VOIDSEERS on {world}"


def run(args: LaunchArgs) -> None:
    if args.agent is None and args.agent2 is None:
        error = "At least one agent must be provided"
        raise ValueError(error)

    setup_console_and_file_logging() if args.log else setup_console_logging()

    sandbox_goobs = (
        Sandbox.from_directory(Path.cwd() / "agents" / args.agent)
        if args.agent is not None
        else None
    )
    sandbox_seers = (
        Sandbox.from_directory(Path.cwd() / "agents" / args.agent2)
        if args.agent2 is not None
        else None
    )
    ws_server = WebSocketServer(wait_for_client=args.client)
    game_pb = GamePb()

    ws_server.start()
    game_pb.make_games_header(ws_server)

    for i, arg_world in enumerate(args.world):
        world_name = f"{arg_world}"
        world_path = Path.cwd() / "worlds" / f"{world_name}.world"

        try:
            world = load_world(world_path)
        except (FileNotFoundError, DecodeError) as e:
            error = f"Unable to load world {world_path}!"
            raise ValueError(error) from e

        world.rounds = args.rounds

        try:
            game = Game([sandbox_goobs, sandbox_seers], args, world, game_pb)
        except ValueError as e:
            enhanced_msg = f"Error in world '{world_name}': {e}"
            raise ValueError(enhanced_msg) from e

        LOGGER.info("========== AEGIS START ==========")
        LOGGER.info(make_game_start_string(args, world_name))

        game_pb.make_game_header(world)
        while game.running:
            try:
                game.run_round()
            except Exception:  # noqa: BLE001
                LOGGER.exception("This shouldn't have happened. Internal error.")
                game.running = False

        game_pb.make_game_footer()
        log_game_end(game, args, i)
    game_pb.make_games_footer()
    ws_server.finish()
