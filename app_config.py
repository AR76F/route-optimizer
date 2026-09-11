from pathlib import Path
from typing import Any, Dict
import tomllib


BRANCH_CONFIG_DIR = Path(__file__).resolve().parent / "config" / "branches"


def load_branch_profiles() -> Dict[str, Dict[str, Any]]:
    profiles: Dict[str, Dict[str, Any]] = {}

    for config_path in sorted(BRANCH_CONFIG_DIR.glob("*.toml")):
        with config_path.open("rb") as config_file:
            profile = tomllib.load(config_file)

        branch = profile.get("branch", {})
        label = branch.get("label")
        if not label:
            raise ValueError(f"Branch config is missing branch.label: {config_path}")

        profiles[label] = branch

    if not profiles:
        raise RuntimeError(f"No branch profiles found in {BRANCH_CONFIG_DIR}")

    return profiles


BRANCH_PROFILES = load_branch_profiles()

SUPPORTED_BRANCHES = [
    label
    for label, _profile in sorted(
        BRANCH_PROFILES.items(),
        key=lambda item: item[1].get("display_order", 999),
    )
]

BRANCH_DEFAULT_LANGUAGES = {
    label: profile.get("default_language", "en")
    for label, profile in BRANCH_PROFILES.items()
}
