"""
MyDropbox - A library for managing UHM Ocean BGC Group Dropbox paths

This library provides easy access to commonly used paths in the research group's
Dropbox structure, making it easier to write portable and maintainable code.

Author: Raphaël Bajon
"""

__version__ = "0.1.0"
__author__ = "Raphaël Bajon"
__license__ = "MIT"

# Import project management
from .project import ProjectPaths, create_project
# Import dropbox management
from .dropbox import get_dropbox, DropboxPaths, PersonalPaths, GroupPaths 
from .dropbox.utils import check_sync_status, auto_discover_paths

from .config.loadconfig import _load_config

__all__ = [
    "ProjectPaths",
    "create_project",
    "get_dropbox",
    "DropboxPaths",
    "PersonalPaths",
    "GroupPaths",
    "check_sync_status", 
    "auto_discover_paths"
]


# Initialize default dropbox instance
_config = _load_config()
dropbox = get_dropbox(
    base_path=_config["base_path"],
    personal_folder=_config["personal_folder"]
)
