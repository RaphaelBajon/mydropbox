from pathlib import Path


class DataPaths:
    """Paths for data directories (raw, interim, processed)."""

    def __init__(self, base_path: Path):
        self.base = base_path
        self.raw = base_path / "raw"
        self.interim = base_path / "interim"
        self.processed = base_path / "processed"

    def __repr__(self):
        return f"DataPaths('{self.base}')"