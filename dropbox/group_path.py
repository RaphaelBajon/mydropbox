from pathlib import Path


class GroupPaths:
    """Access to group shared folders."""

    def __init__(self, base_path: Path):
        self.base = base_path

        # Main folders
        self.assorted_content = self.base / "Assorted content"
        self.collaborative_projects = self.base / "Collaborative_projects"
        self.datasets = self.base / "Datasets"
        self.group_notes = self.base / "Group_notes"
        self.lab_field_data = self.base / "Lab_Field_Data"
        self.ocean_reports = self.base / "Ocean_Reports"

    def __repr__(self):
        return f"GroupPaths(base='{self.base}')"