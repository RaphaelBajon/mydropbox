from pathlib import Path
from typing import Optional

from mydropbox.dropbox.base_path import DiscoverablePaths


class DataPaths(DiscoverablePaths):
    """Paths for data directories (raw, interim, processed)."""

    def __init__(self, base_path: Path, max_depth: Optional[int] = 2):
        super().__init__(base_path, max_depth=max_depth)
        self.base = self._path  # backward compat
        # Ensure standard attrs exist as plain Paths if dirs not yet created
        for name in ("raw", "interim", "processed"):
            if name not in self.__dict__:
                setattr(self, name, self._path / name)

    def __repr__(self):
        return f"DataPaths('{self._path}')"