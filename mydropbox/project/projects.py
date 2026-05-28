"""
MyDropbox Projects - Project structure management for research

This module provides standardized project structures following data science
and research best practices, including the Cookiecutter Data Science structure.

Author: Raphaël Bajon
"""

from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
import json

from .source import SourcePaths
from .plot import PlotPaths
from .data import DataPaths
from mydropbox.dropbox.base_path import DiscoverablePaths

_VALID_TEMPLATES = {"full", "simple", "minimal"}


class ProjectPaths(DiscoverablePaths):
    """
    Manages paths within a research project with a standardized structure.
    
    Standard structure:
    project_name/
    ├── README.md
    ├── data/
    │   ├── raw/          # Original, immutable data
    │   ├── interim/      # Intermediate transformed data
    │   └── processed/    # Final data for analysis
    ├── notebooks/        # Jupyter notebooks
    ├── src/              # Source code (or 'code/')
    │   ├── data/         # Scripts to download or generate data
    │   ├── features/     # Scripts to turn raw data into features
    │   ├── models/       # Scripts to train models
    │   └── visualization/# Scripts to create visualizations
    ├── plots/            # Generated figures and plots
    │   ├── exploratory/  # EDA plots
    │   └── publication/  # Publication-ready figures
    ├── docs/             # Documentation
    ├── reports/          # Generated analysis (HTML, PDF, LaTeX)
    ├── results/          # Model outputs, predictions, etc.
    └── config/           # Configuration files
    
    Attributes:
        base: Base path to the project
        data: Data directory with raw, interim, processed subdirs
        notebooks: Jupyter notebooks
        src: Source code directory
        plots: Plots and figures
        docs: Documentation
        reports: Generated reports
        results: Model results and outputs
        config: Configuration files
    """
    
    def __init__(self, base_path: Path, auto_create: bool = False,
                 max_depth: Optional[int] = 2,
                 template: str = "full"):
        """
        Initialize project paths.

        Args:
            base_path: Path to the project directory.
            auto_create: If True, create directory structure automatically.
            max_depth: Eagerly discover sub-directories this many levels deep
                       (same semantics as ``DiscoverablePaths.max_depth``).
            template: Template to use when ``auto_create=True``.
                      One of ``"full"``, ``"simple"``, ``"minimal"``.
        """
        # super().__init__ sets _path / _max_depth and calls _discover_all_paths()
        super().__init__(base_path, max_depth=max_depth)
        self.base = self._path  # backward-compat alias

        # File paths — not directories, never auto-discovered
        self.readme = self._path / "README.md"
        self.gitignore = self._path / ".gitignore"
        self.requirements = self._path / "requirements.txt"
        self.environment_yml = self._path / "environment.yml"

        if auto_create:
            self.create_structure(template=template)

    # ------------------------------------------------------------------
    # Discovery override
    # ------------------------------------------------------------------

    def _discover_all_paths(self):
        """Override: use typed sub-path classes for known dirs; auto-discover
        everything else so custom folders (e.g. ``manuscripts/``) work too."""
        base = self._path
        depth = self._max_depth
        child_depth = (depth - 1) if depth is not None else None

        # Typed sub-paths — always set even before dirs exist on disk
        self.data = DataPaths(base / "data", max_depth=depth)
        self.src = SourcePaths(base / "src", max_depth=depth)
        self.plots = PlotPaths(base / "plots", max_depth=depth)

        # Auto-discover everything else that exists on disk
        from mydropbox.dropbox.utils import auto_discover_paths
        known = {"data", "src", "plots"}
        for name, path in auto_discover_paths(base, max_depth=1).items():
            if name not in known:
                setattr(self, name, DiscoverablePaths(path, max_depth=child_depth))

        # Plain-Path fallbacks for standard dirs not yet created
        for name in ("notebooks", "docs", "reports", "results", "config"):
            if name not in self.__dict__:
                setattr(self, name, base / name)

    def create_structure(self, template: str = "full"):
        """
        Create the project directory structure.

        Args:
            template: Structure template to use.
                - ``"full"``    — complete data science structure (default)
                - ``"simple"``  — data, src, plots, notebooks
                - ``"minimal"`` — just data and src

        Raises:
            ValueError: If *template* is not one of the valid options.
        """
        if template not in _VALID_TEMPLATES:
            raise ValueError(
                f"Unknown template {template!r}. "
                f"Choose one of: {sorted(_VALID_TEMPLATES)}"
            )
        if template == "minimal":
            dirs = [
                self.data.raw,
                self.data.processed,
                self.src.base,
            ]
        elif template == "simple":
            dirs = [
                self.data.raw,
                self.data.interim,
                self.data.processed,
                self.src.base,
                self.plots.base,
                self.notebooks,
            ]
        else:  # full
            dirs = [
                # Data
                self.data.raw,
                self.data.interim,
                self.data.processed,
                # Source code
                self.src.data,
                self.src.features,
                self.src.models,
                self.src.visualization,
                # Plots
                self.plots.exploratory,
                self.plots.publication,
                # Other
                self.notebooks,
                self.docs,
                self.reports,
                self.results,
                self.config,
            ]
        
        # Create all directories
        for directory in dirs:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Create README if it doesn't exist
        if not self.readme.exists():
            self._create_readme()
        
        # Create .gitignore if it doesn't exist
        if not self.gitignore.exists():
            self._create_gitignore()
        
        # Create __init__.py in src
        src_init = self.src.base / "__init__.py"
        if not src_init.exists():
            src_init.write_text('"""Source code for the project."""\n')
        
        # Refresh all paths now that directories exist on disk
        self._discover_all_paths()

        return self
    
    def _create_readme(self):
        """Create a basic README.md template."""
        template = f"""# {self.base.name}

## Project Overview

[Brief description of the project]

## Project Structure

```
{self.base.name}/
├── data/
│   ├── raw/          # Original, immutable data
│   ├── interim/      # Intermediate data
│   └── processed/    # Final data for analysis
├── notebooks/        # Jupyter notebooks for exploration
├── src/              # Source code
├── plots/            # Generated figures
├── docs/             # Documentation
├── reports/          # Generated analysis
├── results/          # Model outputs
└── config/           # Configuration files
```

## Getting Started

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run analysis:
   ```bash
   python src/main.py
   ```

## Data

- **Raw data**: Located in `data/raw/`
- **Processed data**: Located in `data/processed/`

## Results

[Describe main findings]

## Author

[Your name]

## Date

Created: {datetime.now().strftime('%Y-%m-%d')}
"""
        self.readme.write_text(template)
    
    def _create_gitignore(self):
        """Create a .gitignore for data science projects."""
        template = """# Data files (too large for git)
data/raw/*
data/interim/*
data/processed/*
!data/raw/.gitkeep
!data/interim/.gitkeep
!data/processed/.gitkeep

# Jupyter Notebook checkpoints
.ipynb_checkpoints/
*/.ipynb_checkpoints/*

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# Virtual environments
venv/
env/
ENV/

# IDEs
.vscode/
.idea/
*.swp
.DS_Store

# Results that can be regenerated
results/*.pkl
results/*.h5
plots/exploratory/*

# Keep publication plots
!plots/publication/

# Configuration with sensitive data
config/secrets.yml
config/local_config.yml
"""
        self.gitignore.write_text(template)
    
    def save_dataset(self, data, filename: str, location: str = "processed", **kwargs):
        """
        Save a dataset to the appropriate data folder.
        
        Args:
            data: Data to save (xarray Dataset, pandas DataFrame, etc.)
            filename: Name of the file
            location: Where to save - "raw", "interim", or "processed"
            **kwargs: Additional arguments passed to the save method
        """
        if location == "raw":
            path = self.data.raw / filename
        elif location == "interim":
            path = self.data.interim / filename
        elif location == "processed":
            path = self.data.processed / filename
        else:
            raise ValueError(f"Unknown location: {location}")
        
        # Try different save methods based on data type
        if hasattr(data, 'to_netcdf'):  # xarray
            data.to_netcdf(path, **kwargs)
        elif hasattr(data, 'to_csv'):  # pandas
            data.to_csv(path, **kwargs)
        elif type(data).__module__.startswith('numpy'):
            import numpy as np
            np.save(path, data, **kwargs)
        elif type(data).__module__.startswith('torch'):
            import torch
            torch.save(data, path, **kwargs)
        else:
            raise TypeError(f"Don't know how to save {type(data)}")
        
        return path
    
    def save_figure(self, fig, filename: str, location: str = "exploratory", 
                   dpi: int = 300, **kwargs):
        """
        Save a figure to the plots directory.
        
        Args:
            fig: Matplotlib figure or similar
            filename: Name of the file (with extension)
            location: "exploratory" or "publication"
            dpi: Resolution (default 300 for publication quality)
            **kwargs: Additional arguments for savefig
        """
        if location == "exploratory":
            path = self.plots.exploratory / filename
        elif location == "publication":
            path = self.plots.publication / filename
        else:
            path = self.plots.base / filename
        
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if hasattr(fig, 'savefig'):  # matplotlib
            fig.savefig(path, dpi=dpi, bbox_inches='tight', **kwargs)
        elif hasattr(fig, 'write_image'):  # plotly
            fig.write_image(str(path), **kwargs)
        else:
            raise TypeError(f"Don't know how to save {type(fig)}")
        
        return path
    
    def list_datasets(self, location: str = "all", pattern: str = "*") -> Dict[str, List[Path]]:
        """
        List all datasets in the project.
        
        Args:
            location: "raw", "interim", "processed", or "all"
            pattern: Glob pattern to filter files (e.g., "*.nc")
        
        Returns:
            Dictionary mapping location to list of files
        """
        results = {}
        
        if location in ["raw", "all"] and self.data.raw.exists():
            results["raw"] = sorted(self.data.raw.glob(pattern))
        if location in ["interim", "all"] and self.data.interim.exists():
            results["interim"] = sorted(self.data.interim.glob(pattern))
        if location in ["processed", "all"] and self.data.processed.exists():
            results["processed"] = sorted(self.data.processed.glob(pattern))
        
        return results
    
    def create_metadata(self, description: str = "", author: str = "", 
                       tags: List[str] = None):
        """
        Create a metadata file for the project.
        
        Args:
            description: Project description
            author: Project author
            tags: List of tags/keywords
        """
        metadata = {
            "name": self.base.name,
            "description": description,
            "author": author,
            "created": datetime.now().isoformat(),
            "tags": tags or [],
            "structure_version": "1.0",
        }
        
        metadata_file = self.base / "project_metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
        return metadata_file
    
    def __repr__(self):
        exists = "\u2713" if self.base.exists() else "\u2717"
        return f"ProjectPaths({exists} '{self.base.name}')"


# Convenience function to create a new project
def create_project(base_path: Path, name: str, template: str = "full",
                  description: str = "", author: str = "") -> ProjectPaths:
    """
    Create a new project with standardized structure.
    
    Args:
        base_path: Where to create the project (e.g., dropbox.personal.projects)
        name: Project name
        template: "full", "simple", or "minimal"
        description: Project description
        author: Project author
    
    Returns:
        ProjectPaths instance for the new project
    
    Example:
        >>> from mydropbox import get_dropbox
        >>> db = get_dropbox(personal_folder="Your Name")
        >>> project = create_project(
        ...     db.personal.projects,
        ...     "antarctic_carbon_flux_2026",
        ...     template="full",
        ...     description="Analysis of carbon flux in Antarctic waters",
        ...     author="Your Name"
        ... )
        >>> # Now use project.data.raw, project.src, etc.
    """
    project_path = base_path / name
    project = ProjectPaths(project_path, auto_create=False)
    project.create_structure(template=template)
    
    if description or author:
        project.create_metadata(description=description, author=author)
    
    return project


if __name__ == "__main__":
    # Demo
    print("Project Structure Demo")
    print("=" * 60)
    
    # Create a demo project
    from pathlib import Path
    import tempfile
    
    with tempfile.TemporaryDirectory() as tmpdir:
        demo_project = create_project(
            Path(tmpdir),
            "demo_carbon_analysis",
            template="full",
            description="Demo Southern Ocean Carbon Analysis",
            author="Research Team"
        )
        
        print(f"\nCreated project: {demo_project}")
        print(f"\nProject structure:")
        print(f"  Data (raw):       {demo_project.data.raw}")
        print(f"  Data (processed): {demo_project.data.processed}")
        print(f"  Source code:      {demo_project.src.base}")
        print(f"  Notebooks:        {demo_project.notebooks}")
        print(f"  Plots:            {demo_project.plots.base}")
        
        print(f"\nFiles created:")
        print(f"  README:           {demo_project.readme.exists()}")
        print(f"  .gitignore:       {demo_project.gitignore.exists()}")
        
        print("\nDirectory tree created successfully!")
