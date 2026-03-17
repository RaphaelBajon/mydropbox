from pathlib import Path


class SourcePaths:
    """Paths for source code directories."""

    def __init__(self, base_path: Path):
        self.base = base_path
        self.data = base_path / "data"  # Data loading/processing
        self.features = base_path / "features"  # Feature engineering
        self.models = base_path / "models"  # Model training
        self.visualization = base_path / "visualization"  # Plotting

    def __repr__(self):
        return f"SourcePaths('{self.base}')"