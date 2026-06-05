# Projects Guide

The `projects` module gives every research project a standard folder structure and helper methods to save data and figures.

## Quick Start

```python
from mydropbox import get_dropbox, create_project

db = get_dropbox(personal_folder="Your Name")

project = create_project(
    base_path=db.personal.projects,
    name="antarctic_carbon_2026",
    template="full",          # "full" | "simple" | "minimal"
    description="Antarctic carbon flux analysis",
    author="Your Name",
)

# Standard paths are immediately available
project.data.raw / "argo_floats.nc"
project.plots.publication / "figure1.png"
project.src.models / "flux_model.py"
```

## Project Structure

### Templates

| Template | Creates |
|----------|---------|
| `full` (default) | `data/`, `src/`, `plots/`, `notebooks/`, `docs/`, `reports/`, `results/`, `config/` |
| `simple` | `data/`, `src/`, `plots/`, `notebooks/` |
| `minimal` | `data/` (raw + processed), `src/` |

### Full layout

```
project_name/
├── data/
│   ├── raw/          # original, immutable data — never overwrite
│   ├── interim/      # intermediate processing steps
│   └── processed/    # analysis-ready data
├── src/
│   ├── data/         # download / generate data
│   ├── features/     # feature engineering
│   ├── models/       # model training
│   └── visualization/
├── plots/
│   ├── exploratory/  # quick EDA plots
│   └── publication/  # high-DPI publication figures
├── notebooks/
├── docs/
├── reports/
├── results/
├── config/
├── README.md
└── .gitignore        # pre-configured to exclude data/ and exploratory plots
```

## Saving Data and Figures

```python
import xarray as xr
import matplotlib.pyplot as plt

# Save an xarray dataset (auto-detects type: xarray / pandas / numpy / torch)
project.save_dataset(ds, "soc_filtered.nc", location="processed")

# Save a figure
fig, ax = plt.subplots()
ax.plot(time, flux)
project.save_figure(fig, "flux_timeseries.png", location="publication", dpi=300)

# Or use pathlib directly — both work
ds.to_netcdf(project.data.processed / "soc_filtered.nc")
plt.savefig(project.plots.exploratory / "quick_check.png", dpi=100)
```

## Open an Existing Project

```python
from mydropbox.project.projects import ProjectPaths

project = ProjectPaths(db.personal.projects / "antarctic_carbon_2026")
ds = xr.open_dataset(project.data.processed / "soc_filtered.nc")
```

## Discovery and expand()

Sub-directories created after project initialisation can be discovered on demand:

```python
project.data.processed.expand(1)         # refresh processed/
project.src.models.expand(2)             # go 2 levels deep in src/models/
project.expand(2)                        # refresh all three sub-trees at once
```

## List Datasets

```python
files = project.list_datasets(location="all", pattern="*.nc")
# returns {"raw": [...], "interim": [...], "processed": [...]}
# locations that don't exist are simply omitted
```

## FAQ

**Can I add custom folders?**
```python
(project.base / "manuscripts").mkdir(exist_ok=True)
project.expand(1)   # pick up the new folder
project.manuscripts / "draft_v2.docx"
```

**How do I share processed data with the group?**
```python
import shutil
shutil.copy(
    project.data.processed / "soc_filtered.nc",
    db.group.datasets / "soc_filtered.nc",
)
```
