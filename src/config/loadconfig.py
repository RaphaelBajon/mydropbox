import sys
import os
from pathlib import Path


def _find_config_file():
    """Find configuration file. Returns (path, type) or (None, None)."""
    search_locations = [
        # Python configs (higher priority)
        (Path.cwd() / "mydropbox_config.py", "python"),
        (Path.home() / ".mydropbox_config.py", "python"),
        (Path(__file__).parent.parent / "mydropbox_config.py", "python"),
        (Path(__file__).parent / "mydropbox_config.py", "python"),  # Inside package directory
        # JSON configs
        (Path.cwd() / "mydropbox_config.json", "json"),
        (Path.home() / ".mydropbox_config.json", "json"),
        (Path(__file__).parent.parent / "mydropbox_config.json", "json"),
        (Path(__file__).parent / "mydropbox_config.json", "json"),  # Inside package directory
        # Templates (lowest priority)
        (Path.cwd() / "mydropbox_config_template.py", "python"),
        (Path(__file__).parent.parent / "mydropbox_config_template.py", "python"),
        (Path(__file__).parent / "mydropbox_config_template.py", "python"),  # Inside package directory
        (Path.cwd() / "mydropbox_config_template.json", "json"),
        (Path(__file__).parent.parent / "mydropbox_config_template.json", "json"),
        (Path(__file__).parent / "mydropbox_config_template.json", "json"),  # Inside package directory
    ]

    for path, config_type in search_locations:
        if path.exists() and path.is_file():
            return path, config_type

    return None, None


def _load_python_config(config_path):
    """Load config from Python file. Returns dict or None."""
    config_dir = str(config_path.parent)
    if config_dir not in sys.path:
        sys.path.insert(0, config_dir)
        cleanup_path = True
    else:
        cleanup_path = False

    try:
        module_name = config_path.stem
        config_module = __import__(module_name)

        return {
            "personal_folder": getattr(config_module, "PERSONAL_FOLDER", None),
            "base_path": getattr(config_module, "DROPBOX_BASE_PATH", None),
        }
    except (ImportError, AttributeError):
        return None
    finally:
        if cleanup_path:
            sys.path.remove(config_dir)


def _load_json_config(config_path):
    """Load config from JSON file. Returns dict or None."""
    try:
        with open(config_path, 'r') as f:
            data = json.load(f)

        return {
            "personal_folder": data.get("personal_folder"),
            "base_path": data.get("dropbox_base_path"),
        }
    except (json.JSONDecodeError, IOError, KeyError):
        return None


def _load_config():
    """
    Load configuration from available sources.

    Priority:
    1. Environment variables (highest)
    2. Config files (Python or JSON)
    3. Defaults (None)

    Returns:
        dict: {'personal_folder': str or None, 'base_path': str or None}
    """
    # Start with environment variables
    config = {
        "personal_folder": os.getenv("MYDROPBOX_PERSONAL_FOLDER"),
        "base_path": os.getenv("MYDROPBOX_BASE_PATH"),
    }

    # If not fully configured, try config file
    if not config["personal_folder"] or not config["base_path"]:
        config_path, config_type = _find_config_file()
        print('finding config')
        print(config_path, config_type)
        if config_path and config_type:
            file_config = (
                _load_python_config(config_path) if config_type == "python"
                else _load_json_config(config_path)
            )

            if file_config:
                # Use file values only if not set by environment
                config["personal_folder"] = config["personal_folder"] or file_config.get("personal_folder")
                config["base_path"] = config["base_path"] or file_config.get("base_path")

    return config