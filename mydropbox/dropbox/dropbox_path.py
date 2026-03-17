from pathlib import Path
from typing import Optional
import os

from .group_path import GroupPaths
from .personal_path import PersonalPaths


class DropboxPaths:
    """
    Main class for accessing Dropbox folder paths.

    Attributes:
        base_path: Root path to the Dropbox folder
        group: Access to group shared folders
        personal: Access to personal folders (if personal_folder is specified)
    """

    def __init__(self, base_path: Optional[str] = None, personal_folder: Optional[str] = None):
        """
        Initialize Dropbox paths.

        Args:
            base_path: Custom base path to Dropbox. If None, tries to auto-detect
                      or uses ~/Dropbox/UHM_Ocean_BGC_Group Dropbox
            personal_folder: Name of your personal folder within the group Dropbox.
                           If None, personal paths will not be initialized.
                           Example: "Raphaël Bajon", "John Doe", etc.
        """
        if base_path is None:
            # Try common Dropbox locations
            possible_paths = [
                Path.home() / "UHM_Ocean_BGC_Group Dropbox",
                Path.home() / "Dropbox" / "UHM_Ocean_BGC_Group Dropbox",
                Path.home() / "Library" / "CloudStorage" / "Dropbox" / "UHM_Ocean_BGC_Group Dropbox",
                Path("/Users") / os.getenv("USER", "") / "Dropbox" / "UHM_Ocean_BGC_Group Dropbox"
            ]

            for path in possible_paths:
                if path.exists():
                    self.base_path = path
                    break
            else:
                # Default fallback
                self.base_path = Path.home() / "Dropbox" / "UHM_Ocean_BGC_Group Dropbox"
        else:
            self.base_path = Path(base_path)

        # Initialize group paths (always available)
        self.group = GroupPaths(self.base_path)

        # Initialize personal paths only if personal_folder is specified
        if personal_folder is not None:
            self.personal = PersonalPaths(self.base_path / personal_folder)
        else:
            self.personal = None

    def __repr__(self):
        personal_info = f", personal_folder='{self.personal.base.name}'" if self.personal else ""
        return f"DropboxPaths(base_path='{self.base_path}'{personal_info})"


# Convenience function for quick access
def get_dropbox(base_path: Optional[str] = None, personal_folder: Optional[str] = None) -> DropboxPaths:
    """
    Convenience function to get a DropboxPaths instance.

    Args:
        base_path: Optional custom base path
        personal_folder: Name of your personal folder (e.g., "Your Name")

    Returns:
        DropboxPaths instance

    Example:
        >>> db = get_dropbox(personal_folder="John Doe")
        >>> data_path = db.personal.datasets
    """
    return DropboxPaths(base_path, personal_folder)
