from pathlib import Path


class PersonalPaths:
    """Access to personal Raphaël Bajon folders."""

    def __init__(self, base_path: Path):
        self.base = base_path

        # Main folders
        self.admin = self.base / "admin"
        self.datasets = self.base / "datasets"
        self.meeting = self.base / "meeting"
        self.mycode = self.base / "mycode"
        self.papers = self.base / "papers"
        self.phd = self.base / "phd"
        self.projects = self.base / "projects"
        self.slides = self.base / "slides"
        self.soc_tools = self.base / "soc_tools"
        self.team = self.base / "team"
        self.utils = self.base / "utils"

        # Special file
        self.pco2_adjusted = self.base / "2023_06 Se...justed pCO2"

    def __repr__(self):
        return f"PersonalPaths(base='{self.base}')"