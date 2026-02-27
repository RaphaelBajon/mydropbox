# Project Management Guide

The MyDropbox projects module helps you create and manage standardized research project structures following data science best practices.

## Why Use Standardized Project Structure?

✅ **Reproducibility**: Others can understand and reproduce your work  
✅ **Organization**: Everything has a place, easy to find  
✅ **Collaboration**: Team members know where to find things  
✅ **Best Practices**: Follows Cookiecutter Data Science standards  
✅ **Automation**: Quickly set up new projects

## Quick Start

```python
from mydropbox import get_dropbox, create_project

# Initialize Dropbox
db = get_dropbox(personal_folder="Your Name")

# Create a new project
project = create_project(
    base_path=db.personal.projects,
    name="antarctic_carbon_flux_2026",
    template="full",  # or "simple" or "minimal"
    description="Analysis of Antarctic carbon flux using BGC-Argo data",
    author="Your Name"
)

# Use the project paths
data_file = project.data.raw / "argo_floats_2026.nc"
script = project.src.data / "download_argo.py"
figure = project.plots.publication / "flux_timeseries.png"
```

## Project Structure

### Full Template (Default)

```
project_name/
├── README.md              # Project overview and documentation
├── .gitignore            # Git ignore rules for data science
├── requirements.txt      # Python dependencies
├── environment.yml       # Conda environment (optional)
├── project_metadata.json # Automated metadata
│
├── data/
│   ├── raw/              # Original, immutable data (never edit!)
│   ├── interim/          # Intermediate transformed data
│   └── processed/        # Final data ready for analysis
│
├── notebooks/            # Jupyter notebooks for exploration
│   ├── 01_exploratory.ipynb
│   ├── 02_analysis.ipynb
│   └── 03_visualization.ipynb
│
├── src/                  # Source code (reusable functions)
│   ├── __init__.py
│   ├── data/             # Scripts to download/generate data
│   ├── features/         # Scripts to create features from raw data
│   ├── models/           # Scripts to train models
│   └── visualization/    # Scripts to create visualizations
│
├── plots/
│   ├── exploratory/      # Quick EDA plots (not for publication)
│   └── publication/      # Publication-ready figures (high DPI)
│
├── docs/                 # Documentation files
├── reports/              # Generated reports (HTML, PDF, LaTeX)
├── results/              # Model outputs, predictions, metrics
└── config/               # Configuration files (YAML, JSON)
```

### Simple Template

Just the essentials:
- `data/` (raw, interim, processed)
- `src/`
- `plots/`
- `notebooks/`
- `README.md`, `.gitignore`

### Minimal Template

Bare minimum:
- `data/` (raw, processed)
- `src/`
- `README.md`

## Usage Examples

### Example 1: Create and Set Up a Project

```python
from mydropbox import get_dropbox, create_project
import xarray as xr

# Initialize
db = get_dropbox(personal_folder="Your Name")

# Create project
project = create_project(
    db.personal.projects,
    "soc_pco2_analysis_2026",
    template="full",
    description="Southern Ocean pCO2 trends from 2015-2025",
    author="Your Name"
)

# Download data to raw/
raw_file = project.data.raw / "soc_pco2_2015_2025.nc"
# ... download data to raw_file ...

# Process data
ds = xr.open_dataset(raw_file)
processed = ds.sel(latitude=slice(-60, -40))  # Southern Ocean only

# Save processed data
processed_file = project.save_dataset(
    processed,
    "soc_pco2_filtered.nc",
    location="processed"
)

print(f"Processed data saved to: {processed_file}")
```

### Example 2: Working with an Existing Project

```python
from mydropbox import get_dropbox
from mydropbox.projects import ProjectPaths

# Initialize
db = get_dropbox(personal_folder="Your Name")

# Open existing project
project = ProjectPaths(db.personal.projects / "soc_pco2_analysis_2026")

# Load processed data
import xarray as xr
ds = xr.open_dataset(project.data.processed / "soc_pco2_filtered.nc")

# Create a plot
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ds.pco2.mean(dim=['lat', 'lon']).plot(ax=ax)
ax.set_title("Southern Ocean pCO2 Time Series")

# Save to publication folder
project.save_figure(fig, "pco2_timeseries.png", location="publication", dpi=300)

print(f"Figure saved to: {project.plots.publication}")
```

### Example 3: Organizing Code in src/

Create reusable functions in your `src/` directory:

```python
# project/src/data/load_data.py
"""Functions to load and preprocess data."""

import xarray as xr
from pathlib import Path

def load_argo_data(data_dir: Path, year: int):
    """Load BGC-Argo data for a specific year."""
    file_path = data_dir / f"argo_{year}.nc"
    return xr.open_dataset(file_path)

def filter_southern_ocean(ds: xr.Dataset, lat_min: float = -60, lat_max: float = -40):
    """Filter dataset to Southern Ocean latitudes."""
    return ds.sel(latitude=slice(lat_min, lat_max))
```

Then use in notebooks or scripts:

```python
# project/notebooks/01_analysis.ipynb
import sys
sys.path.insert(0, '../src')

from data.load_data import load_argo_data, filter_southern_ocean

ds = load_argo_data(project.data.raw, 2025)
ds_filtered = filter_southern_ocean(ds)
```

### Example 4: List All Datasets

```python
# See what data you have
datasets = project.list_datasets(location="all", pattern="*.nc")

print("Raw datasets:")
for f in datasets["raw"]:
    print(f"  - {f.name}")

print("\nProcessed datasets:")
for f in datasets["processed"]:
    print(f"  - {f.name}")
```

### Example 5: Save Results

```python
import numpy as np
import pickle

# Train a model (example)
model_results = {
    'rmse': 0.23,
    'r2': 0.89,
    'coefficients': np.array([1.2, -0.5, 0.8])
}

# Save to results/
results_file = project.results / "model_v1_metrics.pkl"
with open(results_file, 'wb') as f:
    pickle.dump(model_results, f)

print(f"Results saved to: {results_file}")
```

## Best Practices

### 1. Keep Raw Data Immutable

```python
# ✓ GOOD: Read from raw, save to processed
raw_data = xr.open_dataset(project.data.raw / "original.nc")
processed = raw_data.mean(dim='time')
processed.to_netcdf(project.data.processed / "monthly_means.nc")

# ✗ BAD: Never overwrite raw data
# xr.open_dataset(project.data.raw / "original.nc").mean().to_netcdf(
#     project.data.raw / "original.nc"  # Don't do this!
# )
```

### 2. Use Interim for Multi-Step Processing

```python
# Step 1: Clean raw data → interim
raw = xr.open_dataset(project.data.raw / "sensor_data.nc")
cleaned = remove_outliers(raw)
cleaned.to_netcdf(project.data.interim / "cleaned.nc")

# Step 2: Add features → interim
with_features = add_derived_variables(cleaned)
with_features.to_netcdf(project.data.interim / "with_features.nc")

# Step 3: Final processing → processed
final = normalize_and_filter(with_features)
final.to_netcdf(project.data.processed / "analysis_ready.nc")
```

### 3. Separate Exploratory and Publication Plots

```python
# Quick exploration (lower quality, not version controlled)
fig_explore = quick_timeseries_plot(data)
project.save_figure(fig_explore, "quick_check.png", location="exploratory", dpi=100)

# Publication quality (high DPI, version controlled)
fig_pub = create_publication_figure(data)
project.save_figure(fig_pub, "figure1_flux.png", location="publication", dpi=300)
```

### 4. Document Your Code

Always update the README:

```python
# After creating your project, edit the README
readme_path = project.readme
# Edit manually or programmatically to describe:
# - What the project does
# - Data sources
# - How to reproduce results
# - Key findings
```

### 5. Use Configuration Files

```python
# Create a config file
import yaml

config = {
    'data_source': 'BGC-Argo',
    'latitude_range': [-60, -40],
    'years': [2015, 2020, 2025],
    'variables': ['pco2', 'temperature', 'salinity']
}

config_file = project.config / "analysis_config.yaml"
with open(config_file, 'w') as f:
    yaml.dump(config, f)

# Load config in your analysis
with open(config_file) as f:
    config = yaml.safe_load(f)
```

## Integration with Dropbox

The project structure works seamlessly with MyDropbox:

```python
from mydropbox import get_dropbox, create_project

db = get_dropbox(personal_folder="Your Name")

# Create project in your Dropbox
project = create_project(
    db.personal.projects,  # Projects folder in Dropbox
    "my_analysis"
)

# Access both Dropbox and project paths
group_data = db.group.datasets / "shared_observations.nc"  # Shared data
my_processed = project.data.processed / "my_analysis.nc"    # Your processed data

# Copy group data to your project
import shutil
shutil.copy(group_data, project.data.raw / "observations.nc")
```

## Common Workflows

### Workflow 1: Start a New Analysis

```python
from mydropbox import get_dropbox, create_project

# 1. Create project
db = get_dropbox(personal_folder="Your Name")
project = create_project(db.personal.projects, "my_new_project")
# 2. Add data to raw/
# 3. Create a notebook in notebooks/
# 4. Write processing code in src/
# 5. Save results to results/
# 6. Create publication figures in plots/publication/
```

### Workflow 2: Reproduce Someone's Analysis

```python
from mydropbox.projects import ProjectPaths

# Open their project
project = ProjectPaths("/path/to/their/project")

# Check what data they used
datasets = project.list_datasets("all")

# Run their analysis scripts
# Look in project.src for scripts
# Check project.readme for instructions
```

### Workflow 3: Share Your Work

```python
# Your project is already organized!
# Just share the project folder

# Others can access:
# - Your code in src/
# - Your processed data in data/processed/
# - Your figures in plots/publication/
# - Your documentation in README.md

# Raw data stays in data/raw/ (add to .gitignore if too large)
```

## Advanced Features

### Custom Metadata

```python
project.create_metadata(
    description="flux analysis using ML",
    author="Your Name",
    tags=["carbon-cycle", "machine-learning", "southern-ocean", "2026"]
)

# Creates project_metadata.json with timestamps and info
```

### Programmatic Access

```python
# Get all paths as a dictionary
paths = {
    'raw': project.data.raw,
    'processed': project.data.processed,
    'notebooks': project.notebooks,
    'src': project.src.base,
}

# Check if project exists
if project.base.exists():
    print("Project found!")
```

## Tips

### Recommended File Naming

```python
# Use descriptive names with dates/versions
"argo_bgc_2015_2025_v1.nc"
"soc_flux_monthly_processed_2026-01-28.nc"
"figure1_spatial_distribution_300dpi.png"
```

## FAQ

**Q: Can I customize the structure?**  
A: Yes! After creating a project, you can add your own folders:
```python
project.base / "manuscripts" ).mkdir(exist_ok=True)
(project.base / "presentations").mkdir(exist_ok=True)
```

**Q: What if I want to use `code/` instead of `src/`?**  
A: Just rename it:
```python
project.src.base.rename(project.base / "code")
```

**Q: Should I commit data to Git?**  
A: No for large files! The `.gitignore` is configured to exclude data folders. Only commit small reference files or metadata.

**Q: How do I share processed data with the group?**  
A: Copy to the group datasets folder:
```python
import shutil
shutil.copy(
    project.data.processed / "my_analysis.nc",
    db.group.datasets / "my_analysis.nc"
)
```

---

**For more examples, see** [the example](docs/examples/examples_projects.py) `examples_projects.py` 
