"""
Group paths module for MyDropbox.

Manages paths to shared group folders within the Dropbox.
"""

from .base_path import DiscoverablePaths


class GroupPaths(DiscoverablePaths):
    """
    Access to group shared folders.

    Every immediate subdirectory of the group Dropbox root is exposed as
    an attribute whose name is the snake_case version of the folder name.

    Example::

        db.group.datasets          # Path to the Datasets folder
        db.group.group_notes       # Path to the Group_notes folder
        db.group / "custom_folder" # Works like a plain Path
    """

    def __repr__(self):
        return f"GroupPaths('{self._path}', {len(self.get_all_paths())} folders)"
