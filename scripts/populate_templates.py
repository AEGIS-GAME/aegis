"""
Script to populate the template directories for aegis init command.

This script copies the necessary files into the templates directory structure:
- templates/path/ - for pathfinding assignment
- templates/mas/ - for multi-agent assignment
- templates/comp/ - for competition

Run this script manually or integrate it into your build process.
"""

import shutil
import sys
from pathlib import Path

TEMPLATE_STRUCTURE: dict[str, dict[str, str | None]] = {
    "path": {
        "agents": "agents/agent_path",
        "worlds": "worlds/path-worlds",
        "config": "config/presets/pathfinding-assignment.yaml",
        "predictions": None,
    },
    "mas": {
        "agents": "agents/agent_mas",
        "worlds": "worlds/mas-worlds",
        "config": "config/presets/multi-agent-assignment.yaml",
        "predictions": "prediction_data",
    },
    "comp": {
        "agents": "agents/agent_comp",
        "worlds": "worlds/comp-worlds",
        "config": "config/presets/competiton-versus.yaml",
        "predictions": "prediction_data",
    },
}


def get_project_root() -> Path:
    """Get the project root directory."""
    current = Path.cwd()
    while current != current.parent:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    msg = "Could not find project root (pyproject.toml)"
    raise FileNotFoundError(msg)


def copy_directory_excluding_cache(src: Path, dest: Path) -> None:
    """Copy directory excluding __pycache__ and other cache files."""
    if dest.exists():
        shutil.rmtree(dest)

    def ignore_patterns(_: str, names: list[str]) -> list[str]:
        """Ignore __pycache__, .pyc, and other cache files."""
        return [
            name
            for name in names
            if name in {"__pycache__", ".pyc", ".pyo", ".pyd"}
            or name.endswith((".pyc", ".pyo", ".pyd"))
        ]

    _ = shutil.copytree(src, dest, ignore=ignore_patterns)


def _copy_agents(
    agents_path: str | None, project_root: Path, template_dir: Path
) -> None:
    """Copy agents directory to template."""
    if not agents_path:
        print("No agents specified")
        return

    agents_src = project_root / agents_path
    if not agents_src.exists():
        print(f"Warning: {agents_path} not found")
        return

    agents_dest = template_dir / "agents"
    agents_dest.mkdir(parents=True, exist_ok=True)

    # Extract the agent folder name (e.g., "agent_path" from "agents/agent_path")
    agent_folder_name = agents_path.split("/")[-1]
    agent_dest = agents_dest / agent_folder_name
    copy_directory_excluding_cache(agents_src, agent_dest)
    # print(f"Copied agents: {agents_path}")


def _copy_worlds(
    worlds_path: str | None, project_root: Path, template_dir: Path
) -> None:
    """Copy worlds directory to template."""
    if not worlds_path:
        print("No worlds specified")
        return

    worlds_src = project_root / worlds_path
    if not worlds_src.exists():
        print(f"Warning: {worlds_path} not found")
        return

    worlds_dest = template_dir / "worlds"
    if worlds_dest.exists():
        shutil.rmtree(worlds_dest)
    worlds_dest.mkdir(parents=True, exist_ok=True)

    # Copy entire directory
    copy_directory_excluding_cache(worlds_src, worlds_dest)
    # print(f"Copied worlds: {worlds_path}")


def _copy_predictions(
    predictions_path: str | None, project_root: Path, template_dir: Path
) -> None:
    """Copy prediction data to template."""
    if not predictions_path:
        print("No predictions specified")
        return

    predictions_src = project_root / predictions_path
    if not predictions_src.exists():
        print(f"Warning: {predictions_path} not found")
        return

    predictions_dest = template_dir / "prediction_data"
    copy_directory_excluding_cache(predictions_src, predictions_dest)
    # print(f"Copied prediction data: {predictions_path}")


def _copy_config(
    config_path: str | None, project_root: Path, template_dir: Path
) -> None:
    """Copy and rename config file to template."""
    if not config_path:
        print("No config specified")
        return

    config_src = project_root / config_path
    if not config_src.exists():
        print(f"Warning: {config_path} not found")
        return

    config_dest = template_dir / "config"
    config_dest.mkdir(parents=True, exist_ok=True)
    _ = shutil.copy2(config_src, config_dest / "config.yaml")
    # print(f"Copied config: {config_path} -> config.yaml")


def populate_template(
    template_name: str, template_config: dict[str, str | None], project_root: Path
) -> None:
    """Populate a single template directory."""
    template_dir = project_root / "src" / "_aegis_game" / "templates" / template_name

    if template_dir.exists():
        shutil.rmtree(template_dir)
    template_dir.mkdir(parents=True, exist_ok=True)

    # Copy all template components
    _copy_agents(template_config["agents"], project_root, template_dir)
    _copy_worlds(template_config["worlds"], project_root, template_dir)
    _copy_predictions(template_config["predictions"], project_root, template_dir)
    _copy_config(template_config["config"], project_root, template_dir)

    print(f"Template {template_name} populated successfully")


def main() -> None:
    """Populate templates for aegis init command."""
    try:
        project_root = get_project_root()

        # Clear the entire templates directory before populating
        templates_dir = project_root / "src" / "_aegis_game" / "templates"
        if templates_dir.exists():
            print("Clearing existing templates directory...")
            shutil.rmtree(templates_dir)
        templates_dir.mkdir(parents=True, exist_ok=True)

        for template_name, template_config in TEMPLATE_STRUCTURE.items():
            populate_template(template_name, template_config, project_root)

        print("\nAll templates populated successfully!")
        print("\nTemplate structure created:")
        for template_name in TEMPLATE_STRUCTURE:
            template_dir = project_root / "src" / "_aegis" / "templates" / template_name
            print(f"  - {template_name}: {template_dir}")

    except Exception as e:  # noqa: BLE001
        print(f"Error populating templates: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
