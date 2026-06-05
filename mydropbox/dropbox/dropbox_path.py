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

    def __init__(self, base_path: Optional[str] = None, personal_folder: Optional[str] = None,
                 group_depth: Optional[int] = 2, personal_depth: Optional[int] = 2):
        """
        Initialize Dropbox paths.

        Args:
            base_path: Custom base path to Dropbox. If None, tries to auto-detect
                      or uses ~/Dropbox/UHM_Ocean_BGC_Group Dropbox
            personal_folder: Name of your personal folder within the group Dropbox.
                           If None, personal paths will not be initialized.
                           Example: "John Doe", etc.
            group_depth: How many directory levels to discover eagerly under
                        ``db.group``.  1 = immediate children only (fastest);
                        2 = children + grandchildren (default);  None = full tree.
            personal_depth: Same as ``group_depth`` but for ``db.personal``.
        """
        self._base_path_found = False
        if base_path is None:
            # Try common Dropbox locations
            possible_paths = [
                # personal computer options
                Path.home() / "UHM_Ocean_BGC_Group Dropbox",
                Path.home() / "Dropbox" / "UHM_Ocean_BGC_Group Dropbox",
                Path.home() / "Library" / "CloudStorage" / "Dropbox" / "UHM_Ocean_BGC_Group Dropbox",
                Path("/Users") / os.getenv("USER", "") / "Dropbox" / "UHM_Ocean_BGC_Group Dropbox",
                Path("/Users") / os.getenv("USER", "") / "UHM_Ocean_BGC_Group Dropbox",
                # labpc option
                Path("/mnt/md0/group_data/UHM_Ocean_BGC_Group Dropbox"),
            ]

            for path in possible_paths:
                if path.exists():
                    self.base_path = path
                    self._base_path_found = True
                    break
            else:
                # Default fallback
                self.base_path = Path.home() / "Dropbox" / "UHM_Ocean_BGC_Group Dropbox"
        else:
            self.base_path = Path(base_path)

        # Initialize group paths (always available)
        self.group = GroupPaths(self.base_path, max_depth=group_depth)
        
        self._configure_for_labpc = False
        self._configure_for_persopc = False

        if self.group.parts[1] == 'mnt':
            self._configure_for_labpc = True
            path_lab_fixed = {
                'Seth Bushinsky': 'seth',
                'Raphaël Bajon': 'raph',
                'Zachary Nachod': 'zach',
                'Haichao Guo': 'haichao',
                }
        else:
            self._configure_for_persopc = True

        # Initialize personal paths only if personal_folder is specified
        if personal_folder is not None and self._configure_for_persopc:
            self.personal = PersonalPaths(self.base_path / personal_folder, max_depth=personal_depth)
        elif personal_folder is not None and self._configure_for_labpc:
            # On labpc, personal folders are under /mnt/md0/group_data/personal/
            self.personal = PersonalPaths(self.base_path.parent.parent / path_lab_fixed[personal_folder] / "UHM_Ocean_BGC_Group Dropbox" / personal_folder, max_depth=personal_depth)
        else:
            self.personal = None

    def __repr__(self):
        personal_info = f", personal_folder='{self.personal}'" if self.personal else ""
        return f"DropboxPaths(base_path='{self.base_path}'{personal_info})"


# Convenience function for quick access
def get_dropbox(base_path: Optional[str] = None, personal_folder: Optional[str] = None,
                group_depth: Optional[int] = 2, personal_depth: Optional[int] = 2) -> DropboxPaths:
    """
    Convenience function to get a DropboxPaths instance.

    Args:
        base_path: Optional custom base path.
        personal_folder: Name of your personal folder (e.g., "Your Name").
        group_depth: Levels of subdirectories to discover under ``db.group``.
                     1 = immediate children (fastest); 2 = default; None = full tree.
        personal_depth: Same as ``group_depth`` but for ``db.personal``.

    Returns:
        DropboxPaths instance

    Example:
        >>> db = get_dropbox(personal_folder="John Doe")
        >>> db = get_dropbox(personal_folder="John Doe", group_depth=1, personal_depth=3)
    """
    return DropboxPaths(base_path, personal_folder, group_depth=group_depth, personal_depth=personal_depth)
