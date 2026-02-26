# MyDropbox Quick Reference

## Installation

```bash
# From GitHub
pip install git+https://github.com/[YOUR_GROUP]/mydropbox.git

# From local directory
pip install -e /path/to/mydropbox_package
```

## Configuration

```python
# Option 1: Direct (simplest)
from mydropbox import get_dropbox

db = get_dropbox(personal_folder="Your Name")

# Option 2: Config file (recommended for privacy)
# 1. Copy mydropbox_config_template.py to mydropbox_config.py
# 2. Edit and set PERSONAL_FOLDER = "Your Name"
from config.mydropbox_config import PERSONAL_FOLDER
from mydropbox import get_dropbox

db = get_dropbox(personal_folder=PERSONAL_FOLDER)

# Option 3: Environment variable
import os

db = get_dropbox(personal_folder=os.getenv("DROPBOX_PERSONAL_FOLDER"))

# Option 4: Group access only (no personal folder)
from mydropbox import dropbox
# Only dropbox.group is available, dropbox.personal is None
```

## Basic Usage

```python
from mydropbox import get_dropbox

# Initialize with your personal folder name
db = get_dropbox(personal_folder="Your Name")

# Personal paths
data = db.personal.datasets / "file.nc"
code = db.personal.mycode / "script.py"
project = db.personal.projects / "my_project"

# Group paths (works without personal_folder too)
shared = db.group.datasets / "shared_data.nc"
notes = db.group.group_notes / "meeting.md"
```

### Personal (`db.personal`)
```python
db.personal.admin           # Administrative files
db.personal.datasets        # Your datasets
db.personal.meeting         # Meeting notes
db.personal.mycode          # Your code
db.personal.papers          # Papers & manuscripts
db.personal.phd             # PhD materials
db.personal.projects        # Research projects
db.personal.slides          # Presentations
db.personal.soc_tools       # Southern Ocean Carbon tools
db.personal.team            # Team files
db.personal.utils           # Utility scripts
db.personal.pco2_adjusted   # Adjusted pCO2 data
```

### Group (`db.group`)
```python
db.group.assorted_content      # Misc content
db.group.collaborative_projects # Group projects
db.group.datasets              # Shared datasets
db.group.group_notes           # Group notes
db.group.lab_field_data        # Lab/field data
db.group.ocean_reports         # Ocean reports
```

## Project Management

```python
from mydropbox import get_dropbox, create_project

# Create standardized project structure
db = get_dropbox(personal_folder="Your Name")
project = create_project(
    db.personal.projects,
    "my_analysis_2026",
    template="full"  # or "simple" or "minimal"
)

# Access project paths
project.data.raw              # Original data
project.data.interim          # Intermediate data
project.data.processed        # Final data
project.src.base              # Source code
project.notebooks             # Jupyter notebooks
project.plots.exploratory     # Quick plots
project.plots.publication     # Publication figures
project.results               # Model outputs
project.config                # Config files

# Helper methods
project.save_dataset(data, "file.nc", location="processed")
project.save_figure(fig, "plot.png", location="publication", dpi=300)
project.list_datasets(location="all", pattern="*.nc")
```

## All Available Paths

### Personal (`dropbox.personal`)
```python
dropbox.personal.admin           # Administrative files
dropbox.personal.datasets        # Your datasets
dropbox.personal.meeting         # Meeting notes
dropbox.personal.mycode          # Your code
dropbox.personal.papers          # Papers & manuscripts
dropbox.personal.phd             # PhD materials
dropbox.personal.projects        # Research projects
dropbox.personal.slides          # Presentations
dropbox.personal.soc_tools       # Southern Ocean Carbon tools
dropbox.personal.team            # Team files
dropbox.personal.utils           # Utility scripts
dropbox.personal.pco2_adjusted   # Adjusted pCO2 data
```

### Group (`dropbox.group`)
```python
dropbox.group.assorted_content      # Misc content
dropbox.group.collaborative_projects # Group projects
dropbox.group.datasets              # Shared datasets
dropbox.group.group_notes           # Group notes
dropbox.group.lab_field_data        # Lab/field data
dropbox.group.ocean_reports         # Ocean reports
```

## Common Path Operations

```python
from pathlib import Path

# Check existence
if data_file.exists():
    print("Found!")

# Create directories
new_dir = dropbox.personal.projects / "new_analysis"
new_dir.mkdir(parents=True, exist_ok=True)

# List files
py_files = list(dropbox.personal.mycode.glob("*.py"))
all_files = list(dropbox.personal.datasets.rglob("*.nc"))

# Get file info
path.name       # filename.txt
path.stem       # filename
path.suffix     # .txt
path.parent     # parent directory
path.stat()     # file statistics

# Read/write
content = path.read_text()
path.write_text("new content")
```

## Example: Load and Save Data

```python
import xarray as xr
from mydropbox import get_dropbox

# Initialize
db = get_dropbox(personal_folder="Your Name")

# Load
input_file = db.personal.datasets / "raw_data.nc"
ds = xr.open_dataset(input_file)

# Process
processed = ds.mean(dim='time')

# Save
output_dir = db.personal.projects / "analysis_2026"
output_dir.mkdir(exist_ok=True)
output_file = output_dir / "processed_data.nc"
processed.to_netcdf(output_file)
print(f"Saved to: {output_file}")
```

## Example: Project Structure

```python
from mydropbox import get_dropbox

# Initialize
db = get_dropbox(personal_folder="Your Name")

project = "antarctic_carbon_budget"
base = db.personal.projects / project

# Create structure
for subdir in ['data', 'figures', 'notebooks', 'scripts', 'results']:
    (base / subdir).mkdir(parents=True, exist_ok=True)

print(f"Project created at: {base}")
```

## Custom Dropbox Location

```python
from mydropbox import get_dropbox

# Specify custom path and personal folder
db = get_dropbox(
    base_path="/custom/path/to/Dropbox",
    personal_folder="Your Name"
)
my_data = db.personal.datasets / "file.nc"
```

## Git Commands (Quick Reference)

```bash
# First time setup
git clone https://github.com/[GROUP]/mydropbox.git
cd mydropbox
pip install -e .

# Update to latest
git pull origin main

# Make changes
git add .
git commit -m "Description of changes"
git push origin main

# Create a branch for new features
git checkout -b feature/my-feature
# ... make changes ...
git push origin feature/my-feature
```

## Version Info

```python
import mydropbox
print(mydropbox.__version__)  # 0.1.0
```

## Help & Support

- **Documentation**: README.md
- **Examples**: examples.py
- **Contributing**: CONTRIBUTING.md
- **Issues**: GitHub Issues
- **Changelog**: CHANGELOG.md

---

**Version**: 0.1.0 | **License**: MIT | **Author**: Raphaël Bajon
