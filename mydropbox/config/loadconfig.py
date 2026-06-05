"""Load configuration from a YAML file.

Lookup order (first file found wins):
1. ``~/.mydropbox.yaml``        — user-level, never committed (recommended)
2. ``./mydropbox.yaml``         — project-level (add to .gitignore)
3. Package ``config/config.yaml`` — edit in place or copy to one of the above
"""

from pathlib import Path
import yaml

def _find_yaml_config() -> Path | None:
    """Return the first YAML config file found, or None."""
    candidates = [
        Path.home() / ".mydropbox.yaml",
        Path.cwd() / "mydropbox.yaml",
        Path(__file__).parent / "config.yaml",  # package default
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def load_config() -> dict:
    """Return ``{'personal_folder': str|None, 'base_path': str|None}``."""
    config = {"personal_folder": None, "base_path": None}

    config_path = _find_yaml_config()
    if config_path is None:
        return config

    with open(config_path, encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    # Support both ``dropbox: {...}`` nested and flat top-level keys
    cfg = data.get("dropbox", data)

    config["personal_folder"] = cfg.get("PERSONAL_FOLDER") or cfg.get("personal_folder")

    raw = cfg.get("DROPBOX_BASE_PATH") or cfg.get("base_path")
    if raw and str(raw).lower() not in ("none", "null", ""):
        config["base_path"] = str(raw)

    return config
