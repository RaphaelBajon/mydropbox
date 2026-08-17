"""
MyDropbox - A library for managing UHM Ocean BGC Group Dropbox paths

This library provides easy access to commonly used paths in the research group's
Dropbox structure, making it easier to write portable and maintainable code.

Author: Raphaël Bajon
"""

__version__ = "0.2.1"
__author__ = "Raphaël Bajon"
__license__ = "MIT"

# Import project management
from .project import ProjectPaths, create_project
# Import dropbox management
from .dropbox import get_dropbox, DropboxPaths, PersonalPaths, GroupPaths 
from .dropbox.utils import check_sync_status, evict_to_online_only, auto_discover_paths

from .config.loadconfig import load_config

__all__ = [
    "ProjectPaths",
    "create_project",
    "get_dropbox",
    "DropboxPaths",
    "PersonalPaths",
    "GroupPaths",
    "check_sync_status",
    "evict_to_online_only",
    "auto_discover_paths"
]


# Initialize default dropbox instance
# Named `default_dropbox` to avoid shadowing the `mydropbox.dropbox` subpackage,
# which would break `from mydropbox.dropbox.utils import ...` on Linux.
config = load_config()
default_dropbox = get_dropbox(
    base_path=config["base_path"],
    personal_folder=config["personal_folder"]
)
# Keep `dropbox` as an alias for backwards compatibility
dropbox = default_dropbox
