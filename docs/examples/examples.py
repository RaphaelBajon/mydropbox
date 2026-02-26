"""
Example usage of the MyDropbox library for Southern Ocean Carbon research
"""

from mydropbox import dropbox, get_dropbox
from pathlib import Path


def example_1_basic_usage():
    """Basic path access."""
    print("=" * 60)
    print("Example 1: Basic Usage")
    print("=" * 60)
    
    # Access your personal folders
    print(f"My datasets: {dropbox.personal.datasets}")
    print(f"My code: {dropbox.personal.mycode}")
    print(f"My projects: {dropbox.personal.projects}")
    
    # Access group folders
    print(f"\nGroup datasets: {dropbox.group.datasets}")
    print(f"Group notes: {dropbox.group.group_notes}")


def example_2_data_loading():
    """Example of loading data with error handling."""
    print("\n" + "=" * 60)
    print("Example 2: Data Loading with Error Handling")
    print("=" * 60)
    
    # Simulate loading a dataset
    data_file = dropbox.personal.datasets / "soc_carbon_flux_2025.nc"
    
    if data_file.exists():
        print(f"✓ Found: {data_file}")
        # In real code: ds = xr.open_dataset(data_file)
    else:
        print(f"✗ Not found: {data_file}")
        print("  -> Create this file or check the path")


def example_3_project_structure():
    """Create a project directory structure."""
    print("\n" + "=" * 60)
    print("Example 3: Creating Project Structure")
    print("=" * 60)
    
    project_name = "antarctic_carbon_budget_2026"
    project_dir = dropbox.personal.projects / project_name
    
    print(f"Project directory: {project_dir}")
    
    # Define subdirectories
    subdirs = ["data", "figures", "notebooks", "scripts", "results"]
    
    for subdir in subdirs:
        full_path = project_dir / subdir
        # In real usage, you'd actually create these:
        # full_path.mkdir(parents=True, exist_ok=True)
        print(f"  - {subdir}/  -> {full_path}")


def example_4_cross_platform():
    """Demonstrate cross-platform compatibility."""
    print("\n" + "=" * 60)
    print("Example 4: Cross-Platform Paths")
    print("=" * 60)
    
    # Path objects handle Windows/Mac/Linux differences automatically
    script_path = dropbox.personal.mycode / "analysis" / "compute_flux.py"
    
    print(f"Script path: {script_path}")
    print(f"Path type: {type(script_path)}")
    print(f"As string: {str(script_path)}")
    print(f"As POSIX: {script_path.as_posix()}")  # Always uses forward slashes


def example_5_file_operations():
    """Common file operations."""
    print("\n" + "=" * 60)
    print("Example 5: Common File Operations")
    print("=" * 60)
    
    code_dir = dropbox.personal.mycode
    
    print(f"Code directory: {code_dir}")
    
    # List Python files (simulation - won't actually execute)
    print("\nSearching for Python files:")
    print(f"  Command: list(code_dir.glob('*.py'))")
    print(f"  Command: list(code_dir.rglob('*.py'))  # Recursive")
    
    # Check file properties
    example_file = code_dir / "example_script.py"
    print(f"\nFile operations for: {example_file}")
    print(f"  .exists()  -> Check if file exists")
    print(f"  .is_file() -> Check if it's a file")
    print(f"  .is_dir()  -> Check if it's a directory")
    print(f"  .stat()    -> Get file statistics")
    print(f"  .name      -> Get filename: 'example_script.py'")
    print(f"  .stem      -> Get name without extension: 'example_script'")
    print(f"  .suffix    -> Get extension: '.py'")


def example_6_utilities():
    """Useful utility functions."""
    print("\n" + "=" * 60)
    print("Example 6: Utility Functions")
    print("=" * 60)
    
    def get_latest_dataset(pattern="soc_flux_*.nc"):
        """Get the most recent dataset matching a pattern."""
        datasets_dir = dropbox.personal.datasets
        matching_files = list(datasets_dir.glob(pattern))
        
        if not matching_files:
            return None
        
        # Sort by modification time
        latest = max(matching_files, key=lambda p: p.stat().st_mtime)
        return latest
    
    print("Function: get_latest_dataset()")
    print("  Purpose: Find the most recent file matching a pattern")
    print("  Usage: latest = get_latest_dataset('soc_flux_*.nc')")
    
    
    def organize_by_date(source_dir, dest_dir):
        """Organize files into year/month folders."""
        print("\nFunction: organize_by_date()")
        print("  Purpose: Organize files by creation date")
        print("  Structure: dest_dir/YYYY/MM/filename")


def example_7_sharing_code():
    """Example of portable code for sharing."""
    print("\n" + "=" * 60)
    print("Example 7: Writing Portable Code")
    print("=" * 60)
    
    code_template = '''
def load_flux_data(year, month):
    """
    Load carbon flux data for a specific month.
    Works for anyone in the group with the library installed.
    """
    from mydropbox import dropbox
    
    filename = f"carbon_flux_{year}_{month:02d}.nc"
    filepath = dropbox.group.datasets / filename
    
    if not filepath.exists():
        raise FileNotFoundError(f"Data not found: {filename}")
    
    return xr.open_dataset(filepath)

# Use it
ds = load_flux_data(2025, 6)  # June 2025
    '''
    
    print("Portable code template:")
    print(code_template)


def main():
    """Run all examples."""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 12 + "MyDropbox Library Examples" + " " * 20 + "║")
    print("║" + " " * 8 + "Southern Ocean Carbon Cycle Research" + " " * 13 + "║")
    print("╚" + "=" * 58 + "╝")
    
    example_1_basic_usage()
    example_2_data_loading()
    example_3_project_structure()
    example_4_cross_platform()
    example_5_file_operations()
    example_6_utilities()
    example_7_sharing_code()
    
    print("\n" + "=" * 60)
    print("For more information, see README.md")
    print("=" * 60)


if __name__ == "__main__":
    main()
