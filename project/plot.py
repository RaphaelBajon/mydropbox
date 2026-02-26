from pathlib import Path

class PlotPaths:
    """Paths for plot directories."""

    def __init__(self, base_path: Path):
        self.base = base_path
        self.exploratory = base_path / "exploratory"
        self.publication = base_path / "publication"

    def __repr__(self):
        return f"PlotPaths('{self.base}')"