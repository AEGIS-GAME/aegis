import shutil
from importlib import resources
from pathlib import Path


def _find_project_root() -> Path:
    """Find the project root directory by looking for .venv."""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".venv").exists():
            return current
        current = current.parent
    msg = "Could not find project root (.venv)"
    raise FileNotFoundError(msg)


def _get_templates_dir(kind: str) -> Path:
    """
    Get the templates directory path for the given template kind.

    This works both for development (source code) and PyPI installation.
    """
    try:
        # First try to find templates in the installed package
        with resources.path("_aegis_game.templates", kind) as template_path:
            return template_path
    except (ImportError, FileNotFoundError):
        # Fallback to development path (source code)
        project_root = _find_project_root()
        dev_templates_dir = project_root / "src" / "_aegis_game" / "templates" / kind
        if dev_templates_dir.exists():
            return dev_templates_dir

        # If neither exists, raise a clear error
        msg = f"Template '{kind}' not found. Please ensure templates are populated."
        raise FileNotFoundError(msg) from None


def _copy_directory_excluding_cache(src: Path, dest: Path) -> None:
    """Copy directory excluding __pycache__ and other cache files."""

    def ignore_patterns(_: str, names: list[str]) -> list[str]:
        """Ignore __pycache__, .pyc, and other cache files."""
        return [
            name
            for name in names
            if name in {"__pycache__", ".pyc", ".pyo", ".pyd"}
            or name.endswith((".pyc", ".pyo", ".pyd"))
        ]

    _ = shutil.copytree(src, dest, ignore=ignore_patterns)


def _copy_template_to_workspace(
    template_dir: Path, workspace_dir: Path
) -> tuple[bool, bool, bool, bool]:
    """Copy template files to the workspace directory."""
    created_world = False
    created_agent = False
    created_config = False
    created_predictions = False

    # Copy worlds
    world_src = template_dir / "worlds"
    world_dest = workspace_dir / "worlds"
    if world_src.exists():
        if not world_dest.exists():
            _copy_directory_excluding_cache(world_src, world_dest)
            created_world = True
        else:
            print("  - worlds/: exists, skipped")

    # Copy agents
    agent_src = template_dir / "agents"
    agent_dest = workspace_dir / "agents"
    if agent_src.exists():
        if not agent_dest.exists():
            _copy_directory_excluding_cache(agent_src, agent_dest)
            created_agent = True
        else:
            print("  - agents/: exists, skipped")

    # Copy config
    config_src = template_dir / "config"
    config_dest = workspace_dir / "config"
    if config_src.exists():
        if not config_dest.exists():
            _copy_directory_excluding_cache(config_src, config_dest)
            created_config = True
        else:
            print("  - config/: exists, skipped")

    # Copy prediction data
    predictions_src = template_dir / "prediction_data"
    predictions_dest = workspace_dir / "prediction_data"
    if predictions_src.exists():
        if not predictions_dest.exists():
            _copy_directory_excluding_cache(predictions_src, predictions_dest)
            created_predictions = True
        else:
            print("  - prediction_data/: exists, skipped")

    return created_world, created_agent, created_config, created_predictions


def _print_summary(  # noqa: PLR0913
    *,
    created_world: bool,
    created_agent: bool,
    created_config: bool,
    created_predictions: bool,
    include_predictions: bool,
    agent_folder_name: str,
) -> None:
    print("[aegis] Init scaffold:")
    print(
        f"\t- worlds/ExampleWorld.world: {'copied' if created_world else 'exists, skipped'}"
    )
    print(
        f"\t- agents/{agent_folder_name}: {'copied' if created_agent else 'exists, skipped'}"
    )
    print(
        f"\t- config/config.yaml: {'copied' if created_config else 'exists, skipped'}"
    )
    if include_predictions:
        print(
            f"\t- prediction_data: {'copied' if created_predictions else 'exists, skipped'}"
        )


def init_scaffold(kind: str = "path") -> None:
    """
    Copy predefined scaffold files into the current working directory.

    kind: one of "path" (default), "mas", or "comp".
    """
    cwd = Path.cwd()

    # Find the templates directory (works for both dev and PyPI installation)
    try:
        templates_dir = _get_templates_dir(kind)
    except FileNotFoundError as e:
        msg = f"[aegis] init failed: {e}"
        raise FileNotFoundError(msg) from e

    print(f"[aegis] Initializing {kind} template from {templates_dir}")

    # Copy the entire template structure to the current working directory
    created_world, created_agent, created_config, created_predictions = (
        _copy_template_to_workspace(templates_dir, cwd)
    )

    # Determine agent folder name and whether to include predictions
    agent_folder_name = (
        "agent_path"
        if kind == "path"
        else "agent_mas"
        if kind == "mas"
        else "agent_comp"
    )
    include_predictions = kind in {"mas", "comp"}

    _print_summary(
        created_world=created_world,
        created_agent=created_agent,
        created_config=created_config,
        created_predictions=created_predictions,
        include_predictions=include_predictions,
        agent_folder_name=agent_folder_name,
    )
