"""
Personal paths module for MyDropbox.

Manages paths to personal folders within the group Dropbox.
"""

from .base_path import DiscoverablePaths


class PersonalPaths(DiscoverablePaths):
    """
    Access to personal folders within the group Dropbox.

    Every immediate subdirectory of your personal folder is exposed as an
    attribute whose name is the snake_case version of the folder name.

    Example::

        db.personal.datasets   # Path to your Datasets folder
        db.personal.mycode     # Path to your code folder
        db.personal / "tmp"    # Works like a plain Path
    """

    def __repr__(self):
        return f"PersonalPaths('{self._path}', {len(self.get_all_paths())} folders)"
