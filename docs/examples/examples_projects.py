"""
examples_projects.py — MyDropbox project module examples.

Run with:
    python docs/examples/examples_projects.py
"""

import tempfile
from pathlib import Path

import xarray as xr
import matplotlib.pyplot as plt
import numpy as np

from mydropbox import get_dropbox, create_project
from mydropbox.project.projects import ProjectPaths


db = get_dropbox(personal_folder="Your Name")


# ── 1. Create a new project ───────────────────────────────────────────────────

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


# ── 2. Open an existing project ───────────────────────────────────────────────

project = ProjectPaths(db.personal.projects / "antarctic_carbon_2026")
ds = xr.open_dataset(project.data.processed / "soc_filtered.nc")


# ── 3. Save data ──────────────────────────────────────────────────────────────

# auto-detects type: xarray / pandas / numpy / torch
project.save_dataset(ds, "soc_filtered.nc", location="processed")

# or use pathlib directly
ds.to_netcdf(project.data.processed / "soc_filtered.nc")


# ── 4. Save figures ───────────────────────────────────────────────────────────

fig, ax = plt.subplots()
ax.plot(np.random.randn(100))

project.save_figure(fig, "quick_check.png",      location="exploratory", dpi=100)
project.save_figure(fig, "flux_timeseries.png",  location="publication",  dpi=300)
plt.close(fig)


# ── 5. Discover sub-folders added after creation ──────────────────────────────

(project.base / "manuscripts").mkdir(exist_ok=True)
project.expand(1)
project.manuscripts / "draft_v2.docx"


# ── 6. Share processed data with the group ────────────────────────────────────

import shutil
shutil.copy(
    project.data.processed / "soc_filtered.nc",
    db.group.datasets / "soc_filtered.nc",
)



def example_7_integration_with_dropbox():
    """Example 7: Integration with MyDropbox."""
    print("\n" + "=" * 60)
    print("Example 7: MyDropbox Integration")
    print("=" * 60)
    
    print("\nCode example:")
    print("""
from mydropbox import get_dropbox, create_project

# Initialize Dropbox
db = get_dropbox(personal_folder="Your Name")

# Create project in your Dropbox projects folder
project = create_project(
    base_path=db.personal.projects,
    name="my_research_2026",
    template="full"
)

# Now you can use both:
# - db.group.datasets (shared group data)
# - project.data.raw (your project's raw data)

# Example: Copy group data to your project
import shutil
shutil.copy(
    db.group.datasets / "shared_observations.nc",
    project.data.raw / "observations.nc"
)
    """)


def example_8_real_workflow():
    """Example 8: Real-world workflow."""
    print("\n" + "=" * 60)
    print("Example 8: Complete Research Workflow")
    print("=" * 60)
    
    print("\nTypical Southern Ocean Carbon Research Workflow:")
    print("""
# 1. Create project
from mydropbox import get_dropbox, create_project
db = get_dropbox(personal_folder="Your Name")
project = create_project(
    db.personal.projects,
    "soc_flux_analysis_2026",
    template="full",
    description="Carbon flux analysis for Southern Ocean",
    author="Your Name"
)

# 2. Add raw data
import xarray as xr
import shutil

# Copy from group or download
shutil.copy(
    db.group.datasets / "argo_bgc_2025.nc",
    project.data.raw / "argo_bgc_2025.nc"
)

# 3. Process data
ds = xr.open_dataset(project.data.raw / "argo_bgc_2025.nc")

# Clean
ds_clean = ds.where(ds.quality_flag == 1)
ds_clean.to_netcdf(project.data.interim / "argo_qc.nc")

# Add features
ds_featured = compute_carbon_flux(ds_clean)
ds_featured.to_netcdf(project.data.interim / "argo_with_flux.nc")

# Final processing
ds_final = ds_featured.sel(latitude=slice(-60, -40))
project.save_dataset(ds_final, "soc_flux_final.nc", location="processed")

# 4. Analyze in notebook
# Open: project.notebooks / "01_analysis.ipynb"

# 5. Create figures
import matplotlib.pyplot as plt
fig = create_flux_map(ds_final)
project.save_figure(fig, "figure1_flux_map.png", 
                   location="publication", dpi=300)

# 6. Save results
results = compute_flux_statistics(ds_final)
results.to_csv(project.results / "flux_stats.csv")

# 7. Document
# Edit project.readme to describe analysis

# 8. Share
# Push project folder to Git (data excluded by .gitignore)
# Share processed data with group if needed
    """)


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "MyDropbox Project Management Examples" + " " * 11 + "║")
    print("╚" + "=" * 58 + "╝")
    
    example_1_create_new_project()
    example_2_access_existing_project()
    example_3_save_dataset()
    example_4_save_figures()
    example_5_list_datasets()
    example_6_project_templates()
    example_7_integration_with_dropbox()
    example_8_real_workflow()
    
    print("\n" + "=" * 60)
    print("For detailed documentation, see PROJECTS_GUIDE.md")
    print("=" * 60)


if __name__ == "__main__":
    main()
