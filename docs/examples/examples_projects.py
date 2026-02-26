"""
Example usage of the MyDropbox Projects module for research organization
"""

from mydropbox import get_dropbox, create_project
from mydropbox.projects import ProjectPaths
from pathlib import Path
import tempfile


def example_1_create_new_project():
    """Example 1: Create a new project with full structure."""
    print("=" * 60)
    print("Example 1: Creating a New Project")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Simulate creating in Dropbox projects folder
        base_path = Path(tmpdir)
        
        # Create the project
        project = create_project(
            base_path=base_path,
            name="antarctic_carbon_flux_2026",
            template="full",
            description="Analysis of Antarctic carbon flux using BGC-Argo and satellite data",
            author="Research Team"
        )
        
        print(f"\nProject created: {project.base.name}")
        print(f"Location: {project.base}")
        print(f"\nKey directories:")
        print(f"  Raw data:         {project.data.raw}")
        print(f"  Processed data:   {project.data.processed}")
        print(f"  Source code:      {project.src.base}")
        print(f"  Notebooks:        {project.notebooks}")
        print(f"  Publication plots: {project.plots.publication}")
        print(f"\nFiles created:")
        print(f"  ✓ README.md")
        print(f"  ✓ .gitignore")
        print(f"  ✓ project_metadata.json")


def example_2_access_existing_project():
    """Example 2: Access an existing project."""
    print("\n" + "=" * 60)
    print("Example 2: Accessing an Existing Project")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        
        # Create a project first
        create_project(base_path, "my_analysis", template="simple")
        
        # Later, access it
        project = ProjectPaths(base_path / "my_analysis")
        
        print(f"\nOpened project: {project}")
        print(f"\nAvailable paths:")
        print(f"  project.data.raw")
        print(f"  project.data.interim")
        print(f"  project.data.processed")
        print(f"  project.src.base")
        print(f"  project.notebooks")
        print(f"  project.plots.base")


def example_3_save_dataset():
    """Example 3: Save datasets to appropriate locations."""
    print("\n" + "=" * 60)
    print("Example 3: Saving Datasets")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        project = create_project(Path(tmpdir), "data_processing", template="simple")
        
        # Simulate different data processing stages
        print("\nData processing workflow:")
        print("\n1. Raw data (original, immutable)")
        print(f"   Save to: {project.data.raw}")
        print("   Example: argo_floats_raw_2026.nc")
        
        print("\n2. Interim data (cleaned, but not final)")
        print(f"   Save to: {project.data.interim}")
        print("   Example: argo_floats_qc.nc")
        
        print("\n3. Processed data (analysis-ready)")
        print(f"   Save to: {project.data.processed}")
        print("   Example: argo_floats_monthly_means.nc")
        
        # Example with pandas
        try:
            import pandas as pd
            df = pd.DataFrame({'flux': [1.2, 1.5, 1.3], 'temp': [15, 16, 15.5]})
            saved_path = project.save_dataset(df, "example_data.csv", location="processed")
            print(f"\n✓ Saved example data to: {saved_path}")
        except ImportError:
            print("\n(pandas not available, skipping save example)")


def example_4_save_figures():
    """Example 4: Save figures to exploratory vs publication folders."""
    print("\n" + "=" * 60)
    print("Example 4: Saving Figures")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        project = create_project(Path(tmpdir), "visualization", template="full")
        
        print("\nFigure organization:")
        print("\n1. Exploratory plots (quick checks, lower quality)")
        print(f"   Save to: {project.plots.exploratory}")
        print("   Example: quick_scatter.png (100 DPI)")
        print("   Note: Add to .gitignore (not for publication)")
        
        print("\n2. Publication plots (high quality, version controlled)")
        print(f"   Save to: {project.plots.publication}")
        print("   Example: figure1_flux_map.png (300 DPI)")
        print("   Note: Keep in Git, use for papers")
        
        # Example with matplotlib
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            fig, ax = plt.subplots()
            ax.plot(np.random.randn(100))
            ax.set_title("Example Plot")
            
            # Save exploratory
            exp_path = project.save_figure(fig, "test_exploratory.png", 
                                          location="exploratory", dpi=100)
            print(f"\n✓ Saved exploratory: {exp_path.name}")
            
            # Save publication
            pub_path = project.save_figure(fig, "test_publication.png", 
                                          location="publication", dpi=300)
            print(f"✓ Saved publication: {pub_path.name}")
            
            plt.close(fig)
        except ImportError:
            print("\n(matplotlib not available, skipping figure examples)")


def example_5_list_datasets():
    """Example 5: List all datasets in a project."""
    print("\n" + "=" * 60)
    print("Example 5: Listing Datasets")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        project = create_project(Path(tmpdir), "data_inventory", template="simple")
        
        # Create some dummy files
        (project.data.raw / "file1.nc").touch()
        (project.data.raw / "file2.nc").touch()
        (project.data.processed / "analysis1.nc").touch()
        (project.data.processed / "analysis2.csv").touch()
        
        # List all NetCDF files
        datasets = project.list_datasets(location="all", pattern="*.nc")
        
        print("\nNetCDF datasets in project:")
        for location, files in datasets.items():
            if files:
                print(f"\n{location.upper()}:")
                for f in files:
                    print(f"  - {f.name}")


def example_6_project_templates():
    """Example 6: Different project templates."""
    print("\n" + "=" * 60)
    print("Example 6: Project Templates")
    print("=" * 60)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        
        # Minimal template
        print("\n1. MINIMAL Template (data + src only)")
        minimal = create_project(base, "minimal_project", template="minimal")
        print(f"   Created: {len(list(minimal.base.rglob('*')))} files/folders")
        
        # Simple template
        print("\n2. SIMPLE Template (essentials)")
        simple = create_project(base, "simple_project", template="simple")
        print(f"   Created: {len(list(simple.base.rglob('*')))} files/folders")
        
        # Full template
        print("\n3. FULL Template (complete data science structure)")
        full = create_project(base, "full_project", template="full")
        print(f"   Created: {len(list(full.base.rglob('*')))} files/folders")
        
        print("\nRecommendations:")
        print("  - Use MINIMAL for quick scripts")
        print("  - Use SIMPLE for most analyses")
        print("  - Use FULL for major projects or publications")


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
