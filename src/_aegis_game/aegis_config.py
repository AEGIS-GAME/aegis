from functools import lru_cache
from pathlib import Path
from typing import cast

import yaml

from .types import AegisConfig, FeatureKey

CONFIG_PATH = Path.cwd() / "config" / "config.yaml"


@lru_cache
def load_config() -> AegisConfig:
    """Load and cache the main configuration file."""
    if not CONFIG_PATH.exists():
        error = f"Main config file not found: {CONFIG_PATH}"
        raise FileNotFoundError(error)

    with CONFIG_PATH.open() as f:
        return cast("AegisConfig", yaml.safe_load(f))


def has_feature(feature: FeatureKey) -> bool:
    """Check if a feature is enabled in the config."""
    config = load_config()

    return config.get("features", {}).get(feature, False) or config.get(
        "competition_specific", {}
    ).get(feature, False)


def get_feature_value(feature: FeatureKey) -> bool | int | None:
    """Get a feature value from the config."""
    config = load_config()

    return config.get("features", {}).get(feature) or config.get(
        "competition_specific", {}
    ).get(feature)
