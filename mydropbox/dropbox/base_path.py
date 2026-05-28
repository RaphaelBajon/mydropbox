"""
Base class for auto-discovering Dropbox path containers.

Both GroupPaths and PersonalPaths share identical path-delegation logic;
this base class holds it once.
"""

from pathlib import Path
from typing import Dict, Optional


class DiscoverablePaths:
    """
    Wraps a ``pathlib.Path`` and exposes every subdirectory as a chainable
    attribute, up to ``max_depth`` levels deep.

    Attribute chaining::

        db.group.datasets.argo.floats_2025           # DiscoverablePaths
        db.group.datasets.argo.floats_2025 / "f.nc"  # plain Path

    Full ``pathlib.Path`` API is available at every level via transparent
    attribute delegation — anything not found on the instance is forwarded
    to the underlying ``Path`` object::

        db.group.datasets.exists()
        db.group.datasets.glob("*.nc")
        db.group.datasets.stat()
        db.group.datasets.read_text()   # if it were a file

    Args:
        base_path: Directory this node represents.
        max_depth: How many levels of subdirectories to discover eagerly.
                   ``1``  → immediate children only (fastest import).
                   ``2``  → children + grandchildren (default).
                   ``None`` → unlimited (discovers full tree on creation).

    Subclasses only need to override ``__repr__``.
    """

    def __init__(self, base_path, max_depth: Optional[int] = 2):
        self._path = Path(base_path)
        self._max_depth = max_depth
        self._discover_all_paths()

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def _discover_all_paths(self):
        """Eagerly scan immediate children and attach each subdirectory as a
        ``DiscoverablePaths`` attribute.  Recursion stops when ``max_depth``
        reaches 0."""
        if self._max_depth is not None and self._max_depth <= 0:
            return

        from .utils import auto_discover_paths

        child_depth = (self._max_depth - 1) if self._max_depth is not None else None
        discovered = auto_discover_paths(self._path, max_depth=1)
        for attr_name, path in discovered.items():
            setattr(self, attr_name, DiscoverablePaths(path, max_depth=child_depth))

    def expand(self, depth: int = 1) -> "DiscoverablePaths":
        """Discover additional levels below *this* node without touching the
        rest of the tree.

        Useful during interactive work when the global ``max_depth`` was kept
        small for a fast import but you now need to go deeper into one specific
        branch::

            db = get_dropbox(group_depth=1)   # fast startup
            # later, drill into one sub-tree:
            db.group.datasets.expand(2)       # 2 more levels from here
            db.group.datasets.argo.floats_2025  # now accessible

        Args:
            depth: Number of additional levels to discover below this node.
                   ``1`` (default) discovers immediate children.
                   ``2`` discovers children + grandchildren, etc.

        Returns:
            ``self``, so calls can be chained:
            ``node = db.group.datasets.expand(3).argo``
        """
        self._max_depth = depth
        self._discover_all_paths()
        return self

    def get_all_paths(self) -> Dict[str, "DiscoverablePaths"]:
        """Return all immediately-discovered subdirectories as a
        ``{name: DiscoverablePaths}`` dict."""
        return {
            name: getattr(self, name)
            for name in self.__dict__
            if not name.startswith("_")
            and isinstance(getattr(self, name), DiscoverablePaths)
        }

    # ------------------------------------------------------------------
    # Full pathlib.Path API via transparent delegation
    # ------------------------------------------------------------------

    def __getattr__(self, name: str):
        """Forward any attribute not found on this instance to the underlying
        ``Path`` object, giving access to the complete ``pathlib`` API."""
        # Guard against missing _path during construction / pickling
        if name.startswith("_"):
            raise AttributeError(name)
        try:
            path = object.__getattribute__(self, "_path")
        except AttributeError:
            raise AttributeError(name)
        return getattr(path, name)

    # ------------------------------------------------------------------
    # Dunder methods that __getattr__ cannot intercept
    # ------------------------------------------------------------------

    def __truediv__(self, other):
        """Support the ``/`` path-join operator."""
        return self._path / other

    def __rtruediv__(self, other):
        """Support ``other / discoverable_paths``."""
        return Path(other) / self._path

    def __str__(self):
        return str(self._path)

    def __repr__(self):
        return f"DiscoverablePaths('{self._path}')"

    def __fspath__(self):
        """``os.PathLike`` protocol — usable anywhere a Path is expected."""
        return str(self._path)

    def __eq__(self, other):
        if isinstance(other, DiscoverablePaths):
            return self._path == other._path
        return self._path == other

    def __hash__(self):
        return hash(self._path)

    def __lt__(self, other):
        if isinstance(other, DiscoverablePaths):
            return self._path < other._path
        return self._path < other

    def __iter__(self):
        """Iterate directory contents (delegates to ``Path.iterdir``)."""
        return self._path.iterdir()
