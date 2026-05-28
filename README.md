# MyDropbox

A Python library for managing UHM Ocean BGC Group Dropbox paths in your research code.

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-0.1.0-green.svg)](CHANGELOG.md)

## Why This Library?

When working with shared Dropbox folders in a research group, hardcoding paths can lead to:
- Code that breaks when folder structures change
- Non-portable scripts that don't work on colleagues' machines
- Difficult-to-maintain codebases with scattered path definitions

`mydropbox` centralizes all your common Dropbox paths in one place, making your code cleaner and more maintainable.

## Installation

### Option 1: Install from GitHub (Recommended for Group)
```bash
# Install directly from GitHub
pip install git+https://github.com/raphaelbajon/mydropbox.git

# Or clone and install
git clone https://github.com/raphaelbajon/mydropbox.git
cd mydropbox
pip install -e .
```

## Usage

### Quick Start

```python
from mydropbox import get_dropbox

# Initialize with your personal folder name
db = get_dropbox(personal_folder="Your Name")

# Access your personal folders
data_file = db.personal.datasets / "my_ocean_data.nc"
code_dir = db.personal.mycode / "analysis_scripts"
paper_draft = db.personal.papers / "carbon_cycle_2026.docx"

# Access group folders (works without personal_folder too)
group_data = db.group.datasets / "shared_observations.nc"
meeting_notes = db.group.group_notes / "2026-01-meeting.md"
```

### Configuration Options

**Option 1: Direct specification (simplest)**
```python
from mydropbox import get_dropbox
db = get_dropbox(personal_folder="Raphaël Bajon")
```

**Option 2: Using a config file (recommended for privacy)**

```python
# 1. Copy mydropbox_config_template.py to mydropbox_config.py
# 2. Edit mydropbox_config.py and set your name

from config.mydropbox_config import PERSONAL_FOLDER
from mydropbox import get_dropbox

db = get_dropbox(personal_folder=PERSONAL_FOLDER)
```

**Option 3: Group access only (no personal paths)**

```python
from mydropbox import dropbox

# Only group paths are available
shared_data = dropbox.group.datasets / "observations.nc"
# dropbox.personal is None
```

### Working with Paths

The library uses Python's `pathlib.Path` objects, which are more powerful than strings:

```python

# Read a file
readme = (dropbox.personal.projects / "README.md").read_text()

# Create subdirectories
new_project = dropbox.personal.projects / "new_analysis"
new_project.mkdir(exist_ok=True)
```

### Custom Dropbox Location

If your Dropbox is in a non-standard location:

```python
from mydropbox import get_dropbox

db = get_dropbox("/custom/path/to/UHM_Ocean_BGC_Group Dropbox")
print(db.personal.datasets)
```

### Examples of Available Paths (that I have on my personal dropbox)

#### Personal Paths (`dropbox.personal`)
- `admin` - Administrative documents
- `datasets` - Your personal datasets
- `meeting` - Meeting notes and agendas
- `mycode` - Your code repository
- `papers` - Research papers and manuscripts
- `phd` - PhD-related materials
- `projects` - Research projects
- `slides` - Presentation slides
- `soc_tools` - Southern Ocean Carbon tools
- `team` - Team collaboration files
- `utils` - Utility scripts and tools

#### Group Paths (`dropbox.group`)
- `assorted_content` - Miscellaneous shared content
- `collaborative_projects` - Group collaborative projects
- `datasets` - Shared group datasets
- `group_notes` - Group meeting notes and documentation
- `lab_field_data` - Laboratory and field data
- `ocean_reports` - Ocean observation reports

## Project Management

:smirk: MyDropbox includes a powerful project management module to create [standardized research project structures](#project-structure). See [the Projects Guide](PROJECTS_GUIDE.md) for all the explanations of this feature!

```python
from mydropbox import get_dropbox, create_project

db = get_dropbox(personal_folder="Your Name")

project = create_project(
    base_path=db.personal.projects,
    name="Project_01",
    template="full",  # or "simple" or "minimal"
    description="Description of Project_01",
    author="Your Name"
)

project.data.raw        # raw data
project.data.processed  # processed data
project.notebooks       # notebooks
project.src             # source code
project.plots.exploratory  # exploratory figures
project.plots.publication  # figures for publication
```

**For the full project structure, templates, and examples, see [PROJECTS_GUIDE.md](PROJECTS_GUIDE.md)**

## Example Workflows

### Data Analysis Script

```python
from mydropbox import get_dropbox
import xarray as xr
import matplotlib.pyplot as plt

# Initialize with your personal folder
db = get_dropbox(personal_folder="Your Name")

# Load data
ds = xr.open_dataset(db.personal.datasets / "soc_carbon_flux.nc")

# Analyze
flux_mean = ds.carbon_flux.mean(dim='time')

# Save figure
fig_path = db.personal.projects / "flux_analysis" / "mean_flux.png"
fig_path.parent.mkdir(exist_ok=True)
plt.figure()
flux_mean.plot()
plt.savefig(fig_path)
print(f"Figure saved to {fig_path}")
```

## Tips

1. **Use Path objects**: They handle cross-platform differences automatically
2. **Check existence**: Always verify files exist before opening them
3. **Create directories**: Use `path.mkdir(parents=True, exist_ok=True)` to avoid errors
4. **Relative paths**: Build paths dynamically for maximum flexibility

## License

MIT License - Feel free to modify for your research needs.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

To contribute:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

## Support

- **Issues**: Open an issue on GitHub
- **Group discussions**: Bring it up in lab meetings
- **Questions**: Check the examples or documentation

## Acknowledgments

Developed for the UHM Ocean BGC Research Group.

---

**Current Version**: 0.1.0  
**Last Updated**: January 28, 2026
