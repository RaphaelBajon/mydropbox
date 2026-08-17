# MyDropbox

A Python library for managing UHM Ocean BGC Group Dropbox paths in research code.

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why?

Hardcoded Dropbox paths break on other machines and when folders are renamed. `mydropbox` auto-discovers your Dropbox tree and exposes every folder as a chainable Python attribute — no configuration needed.

## Installation

```bash
pip install git+https://github.com/raphaelbajon/mydropbox.git
# or clone and install locally
git clone https://github.com/raphaelbajon/mydropbox.git && pip install -e mydropbox
```

## Quick Start

```python
from mydropbox import get_dropbox

db = get_dropbox(personal_folder="Your Name")

# Group folders
db.group.datasets / "observations.nc"
db.group.collaborative_projects

# Personal folders
db.personal.mycode / "scripts"
db.personal.projects / "new_analysis"
```

## Configuration

**Inline (simplest)**
```python
db = get_dropbox(personal_folder="Raphaël Bajon")
```

**Config file (recommended — keeps your name out of shared code)**
```bash
# 1. Copy the shipped template to your home directory
cp mydropbox/config/config.yaml ~/.mydropbox.yaml
# 2. Edit ~/.mydropbox.yaml and set PERSONAL_FOLDER: "Your Name"
#    (~/.mydropbox.yaml is never committed to Git)
```
```python
# The pre-built `dropbox` instance reads ~/.mydropbox.yaml (or the env vars
# below) automatically at import time — no arguments needed.
from mydropbox import dropbox
dropbox.personal.mycode
```

**Environment variables (useful for CI / the lab PC, no dotfile needed)**
```bash
export MYDROPBOX_PERSONAL_FOLDER="Your Name"
export MYDROPBOX_BASE_PATH="/custom/path"   # optional
```

**Group only**
```python
db = get_dropbox()   # personal is None
db.group.datasets / "shared.nc"
```

## Discovery Depth

By default, `get_dropbox` discovers 2 levels deep for fast startup. Adjust with `group_depth` / `personal_depth`:

```python
db = get_dropbox(personal_folder="Your Name", group_depth=1, personal_depth=3)
```

Drill deeper into a specific branch at runtime without re-loading everything:

```python
db.group.datasets.expand(2)          # 2 more levels from here
db.group.datasets.argo.floats_2025   # now accessible

# Chain directly
node = db.group.datasets.expand(2).argo
```

## Full pathlib API

Every node is a `pathlib.Path`-compatible object. All `Path` methods work at every level:

```python
db.group.datasets.exists()
db.group.datasets.glob("*.nc")
db.personal.projects.iterdir()
db.personal.mycode.stat()

# Directories chain as attributes (DiscoverablePaths).
# Files are plain pathlib.Path objects exposed the same way.
# Dots in the extension become underscores: "cruise_2025.nc" → cruise_2025_nc
db.group.datasets.cruise_2025_nc          # Path to cruise_2025.nc
db.personal.mycode.analysis.compute_flux_py  # nested file

# The / operator is equivalent and clearer for dynamic names:
file = db.group.datasets / "cruise_2025.nc"
```

## Projects

See [PROJECTS_GUIDE.md](PROJECTS_GUIDE.md) for creating and managing standardized research project structures.

## License

MIT — free to modify for your research needs. See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute.
