"""Load configuration from environment variables and/or a YAML file.

Priority (highest wins, independently per key):
1. ``MYDROPBOX_PERSONAL_FOLDER`` / ``MYDROPBOX_BASE_PATH`` environment variables
2. YAML file, first one found:
   a. ``~/.mydropbox.yaml``        — user-level, never committed (recommended)
   b. ``./mydropbox.yaml``         — project-level (add to .gitignore)
   c. Package ``config/config.yaml`` — edit in place or copy to one of the above
3. Defaults (``None`` / ``{}``)
"""

import os
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
    """Return ``{'personal_folder': str|None, 'base_path': str|None, 'labpc_users': dict}``."""
    config = {"personal_folder": None, "base_path": None, "labpc_users": {}}

    config_path = _find_yaml_config()
    if config_path is not None:
        with open(config_path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        # Support both ``dropbox: {...}`` nested and flat top-level keys
        cfg = data.get("dropbox", data)

        config["personal_folder"] = cfg.get("PERSONAL_FOLDER") or cfg.get("personal_folder")

        raw = cfg.get("DROPBOX_BASE_PATH") or cfg.get("base_path")
        if raw and str(raw).lower() not in ("none", "null", ""):
            config["base_path"] = str(raw)

        config["labpc_users"] = data.get("labpc_users") or cfg.get("labpc_users") or {}

    # Environment variables take priority over the YAML file.
    env_personal_folder = os.getenv("MYDROPBOX_PERSONAL_FOLDER")
    if env_personal_folder:
        config["personal_folder"] = env_personal_folder

    env_base_path = os.getenv("MYDROPBOX_BASE_PATH")
    if env_base_path:
        config["base_path"] = env_base_path

    return config
