"""
Base class for auto-discovering Dropbox path containers.

Both GroupPaths and PersonalPaths share identical path-delegation logic;
this base class holds it once.
"""

from pathlib import Path
from typing import Dict


class DiscoverablePaths:
    """
    Base class that wraps a Path and exposes every immediate subdirectory
    as an attribute, discovered automatically at construction time.

    Subclasses only need to override ``__repr__``.
    """

    def __init__(self, base_path):
        self._path = Path(base_path)
        self._discover_all_paths()

    def _discover_all_paths(self):
        """Scan the directory and attach each subdirectory as an attribute."""
        from .utils import auto_discover_paths

        discovered = auto_discover_paths(self._path, max_depth=1)
        for attr_name, path in discovered.items():
            setattr(self, attr_name, path)

    def get_all_paths(self) -> Dict[str, Path]:
        """Return all discovered paths as a ``{name: Path}`` dict."""
        return {
            name: getattr(self, name)
            for name in dir(self)
            if not name.startswith("_")
            and name != "get_all_paths"
            and isinstance(getattr(self, name), Path)
        }

    # ------------------------------------------------------------------
    # Path-like interface (delegation to self._path)
    # ------------------------------------------------------------------

    def __truediv__(self, other):
        return self._path / other

    def __str__(self):
        return str(self._path)

    def __fspath__(self):
        return str(self._path)

    def __eq__(self, other):
        if isinstance(other, DiscoverablePaths):
            return self._path == other._path
        return self._path == other

    def __hash__(self):
        return hash(self._path)

    def exists(self):
        return self._path.exists()

    def is_dir(self):
        return self._path.is_dir()

    def is_file(self):
        return self._path.is_file()

    def iterdir(self):
        return self._path.iterdir()

    def glob(self, pattern):
        return self._path.glob(pattern)

    def rglob(self, pattern):
        return self._path.rglob(pattern)

    def mkdir(self, *args, **kwargs):
        return self._path.mkdir(*args, **kwargs)

    def rename(self, target):
        return self._path.rename(target)

    def resolve(self, *args, **kwargs):
        return self._path.resolve(*args, **kwargs)

    @property
    def name(self):
        return self._path.name

    @property
    def parent(self):
        return self._path.parent

    @property
    def stem(self):
        return self._path.stem

    @property
    def suffix(self):
        return self._path.suffix
