# Utility Functions Guide

MyDropbox includes powerful utility functions for advanced features like checking sync status, auto-discovering paths, and converting folders to projects.

## Function 1: `check_sync_status()` - Check Dropbox Sync

Check if files/folders are synced locally or online-only, and optionally download them.

### Usage

```python
from mydropbox import get_dropbox, check_sync_status

db = get_dropbox(personal_folder="Your Name")

# Check if a large dataset is synced
status = check_sync_status(db.personal.datasets / "large_argo_data.nc")

print(f"Synced locally: {status['is_synced']}")
print(f"Online-only: {status['is_online_only']}")
print(f"Currently syncing: {status['is_syncing']}")

# Download if online-only
if status['is_online_only']:
    print("Downloading...")
    check_sync_status(
        db.personal.datasets / "large_argo_data.nc",
        download_if_online=True
    )
```

### Return Value

```python
{
    'path': Path,              # Path that was checked
    'exists_locally': bool,    # True if path exists
    'is_synced': bool,         # True if fully synced locally
    'is_online_only': bool,    # True if online-only (not downloaded)
    'is_syncing': bool,        # True if currently syncing
    'error': str or None,      # Error message if check failed
    'downloaded': bool,        # True if download was triggered
}
```

### Use Cases

**1. Check before processing large files:**
```python
data_file = db.personal.datasets / "50gb_model_output.nc"
status = check_sync_status(data_file)

if not status['is_synced']:
    print("Data not synced yet, downloading...")
    check_sync_status(data_file, download_if_online=True)
    print("Please wait for sync to complete before processing")
else:
    # Process the file
    ds = xr.open_dataset(data_file)
```

**2. Batch check entire directory:**
```python
import xarray as xr

def check_and_load(file_path):
    """Load file, downloading if needed."""
    status = check_sync_status(file_path)
    
    if status['is_online_only']:
        print(f"Downloading {file_path.name}...")
        check_sync_status(file_path, download_if_online=True)
        return None  # Wait for sync
    
    return xr.open_dataset(file_path)

# Check multiple files
datasets_dir = db.personal.datasets
for nc_file in datasets_dir.glob("*.nc"):
    ds = check_and_load(nc_file)
    if ds:
        print(f"Loaded: {nc_file.name}")
```

**3. Smart data pipeline:**
```python
def ensure_synced(path, timeout=300):
    """Ensure file is synced before continuing."""
    import time
    
    status = check_sync_status(path, download_if_online=True)
    
    start_time = time.time()
    while status['is_syncing'] or status['is_online_only']:
        if time.time() - start_time > timeout:
            raise TimeoutError(f"Sync timeout for {path}")
        
        time.sleep(5)
        status = check_sync_status(path)
    
    return status['is_synced']

# Use in pipeline
if ensure_synced(data_file):
    process_data(data_file)
```

## Function 2: `auto_discover_paths()` - Auto-Discover Subfolders

Automatically discover all subfolders and convert names to Python attributes.

### Usage

```python
from mydropbox import get_dropbox, auto_discover_paths

db = get_dropbox(personal_folder="Your Name")

# Discover all folders in your personal directory
discovered = auto_discover_paths(db.personal.base, max_depth=1)

print("Discovered folders:")
for attr_name, path in discovered.items():
    print(f"  {attr_name}: {path}")
```

### Output Example

```python
{
    'admin': Path('.../admin'),
    'datasets': Path('.../datasets'),
    'meeting': Path('.../meeting'),
    'mycode': Path('.../mycode'),
    'new_folder_2026': Path('.../New Folder 2026'),  # Auto-converted!
    'special_data': Path('.../Special Data'),        # Auto-converted!
}
```

### Name Conversion Rules

Folder names are automatically converted to valid Python attributes:

| Folder Name | Attribute Name |
|-------------|----------------|
| "My Data" | `my_data` |
| "2023_Results" | `results_2023` |
| "Lab-Field_Data" | `lab_field_data` |
| "Project #1" | `project_1` |

### Use Cases

**1. Dynamically access any subfolder:**
```python
# Instead of manually defining every folder
paths = auto_discover_paths(db.personal.projects)

# Access any project folder
for name, path in paths.items():
    print(f"Project: {name}")
    if (path / "README.md").exists():
        print(f"  Has README")
```

**2. Create flexible path classes:**
```python
from mydropbox import create_dynamic_path_class

# Create a class that auto-discovers all folders
my_projects = create_dynamic_path_class(
    db.personal.projects,
    class_name="MyProjects"
)

# Now access any project folder as an attribute!
my_projects.antarctic_flux_2026
my_projects.ml_carbon_model
my_projects.summer_2025_analysis

# List all available projects
print(my_projects.list_paths())
```

**3. Update existing classes with new folders:**
```python
class MyPaths:
    def __init__(self, base):
        self.base = base
        
        # Manually defined paths
        self.data = base / "data"
        self.code = base / "code"
        
        # Auto-discover any other folders
        self._add_discovered_paths()
    
    def _add_discovered_paths(self):
        discovered = auto_discover_paths(self.base, max_depth=1)
        for name, path in discovered.items():
            if not hasattr(self, name):
                setattr(self, name, path)
```

## Function 3: `convert_to_project()` - Convert Folder to Project

Convert any existing folder into a structured project with auto-discovery.

### Usage

```python
from mydropbox import get_dropbox, convert_to_project

db = get_dropbox(personal_folder="Your Name")

# Convert an existing folder to a project
project = convert_to_project(
    db.personal.base / "my_old_analysis",
    template="simple",      # Add standard structure
    auto_discover=True      # Discover existing folders
)

# Access standard project paths
project.data.raw
project.data.processed
project.notebooks
project.src

# AND access any existing folders that were discovered
project.old_results_2024    # If this folder existed
project.backup_data         # If this folder existed
```

### Parameters

- **folder_path**: Path to convert
- **template**: `"full"`, `"simple"`, `"minimal"`, or `None`
  - If template specified, creates missing standard folders
  - If `None`, only discovers existing structure
- **auto_discover**: If `True`, adds all existing subfolders as attributes

### Use Cases

**1. Upgrade old project to new structure:**
```python
# You have an old project with random folders
old_project_path = db.personal.projects / "2023_carbon_analysis"

# Convert it to use new structure
project = convert_to_project(
    old_project_path,
    template="full",        # Add standard folders if missing
    auto_discover=True      # Keep access to old folders
)

# Now you have both:
# Standard structure
project.data.processed / "final_analysis.nc"

# Old folders still accessible
project.preliminary_results / "old_plot.png"
project.draft_paper / "manuscript_v1.docx"
```

**2. Organize messy directory:**
```python
# Start with messy directory
messy_dir = db.personal.base / "random_stuff"

# Convert and organize
project = convert_to_project(messy_dir, template="simple")

# Move files to proper locations
for file in project.base.glob("*.nc"):
    file.rename(project.data.raw / file.name)

for file in project.base.glob("*.ipynb"):
    file.rename(project.notebooks / file.name)
```

**3. Create project from shared folder:**
```python
# Someone shared a folder with you
shared_folder = db.group.collaborative_projects / "team_analysis"

# Convert to your project structure
my_version = convert_to_project(
    db.personal.projects / "team_analysis_copy",
    template="full",
    auto_discover=False  # Don't auto-discover, use standard structure
)

# Copy data from shared folder
import shutil
shutil.copytree(
    shared_folder / "data",
    my_version.data.raw,
    dirs_exist_ok=True
)
```

## Combined Examples

### Example 1: Complete Workflow

```python
from mydropbox import (
    get_dropbox,
    check_sync_status,
    convert_to_project,
)

# Initialize
db = get_dropbox(personal_folder="Your Name")

# 1. Check if shared data is synced
shared_data = db.group.datasets / "large_argo_dataset.nc"
status = check_sync_status(shared_data, download_if_online=True)

if status['is_synced']:
    # 2. Convert your project folder to structured project
    project = convert_to_project(
        db.personal.projects / "argo_analysis_2026",
        template="full",
        auto_discover=True
    )
    
    # 3. Copy data to project
    import shutil
    shutil.copy(shared_data, project.data.raw / "argo_dataset.nc")
    
    # 4. Process data
    import xarray as xr
    ds = xr.open_dataset(project.data.raw / "argo_dataset.nc")
    processed = ds.sel(latitude=slice(-60, -40))
    
    # 5. Save to project
    project.save_dataset(processed, "soc_argo.nc", location="processed")
    
    print("✓ Workflow complete!")
```

### Example 2: Auto-Discovering Personal Workspace

```python
from mydropbox import get_dropbox, create_dynamic_path_class

db = get_dropbox(personal_folder="Your Name")

# Create dynamic access to ALL your personal folders
my_workspace = create_dynamic_path_class(
    db.personal.base,
    class_name="MyWorkspace",
    max_depth=2  # Include subfolders
)

# List everything
print("Available folders:")
for path_name in my_workspace.list_paths():
    print(f"  my_workspace.{path_name}")

# Access anything
my_workspace.datasets
my_workspace.projects
my_workspace.summer_2025_fieldwork  # Any folder you create!
```

### Example 3: Smart Data Manager

```python
from mydropbox import get_dropbox, check_sync_status, auto_discover_paths

class SmartDataManager:
    def __init__(self, dropbox_instance):
        self.db = dropbox_instance
        
    def get_available_datasets(self):
        """Get all synced datasets."""
        datasets_dir = self.db.personal.datasets
        available = []
        
        for nc_file in datasets_dir.glob("*.nc"):
            status = check_sync_status(nc_file)
            if status['is_synced']:
                available.append(nc_file)
        
        return available
    
    def ensure_project_structure(self, project_name):
        """Ensure project has proper structure."""
        from mydropbox import convert_to_project
        
        project_path = self.db.personal.projects / project_name
        if not project_path.exists():
            project_path.mkdir(parents=True)
        
        return convert_to_project(project_path, template="full")

# Use it
manager = SmartDataManager(db)
datasets = manager.get_available_datasets()
project = manager.ensure_project_structure("new_analysis")
```

## Platform Compatibility

### `check_sync_status()`
- ✅ macOS: Uses extended attributes (xattr)
- ✅ Windows: Uses Win32 API
- ✅ Linux: Uses extended attributes
- ⚠️  Fallback: File size heuristics if platform-specific methods unavailable

### `auto_discover_paths()` & `convert_to_project()`
- ✅ All platforms: Pure Python, no platform-specific code

## Tips

1. **Use auto-discovery sparingly** - Only when you have dynamic folders
2. **Check sync before large operations** - Avoid errors with online-only files
3. **Combine functions** - They work great together!
4. **Enable auto_discover in classes** - Add `auto_discover=True` to GroupPaths/PersonalPaths

## Troubleshooting

**"Can't determine sync status"**
- Platform-specific libraries may not be installed
- Install: `pip install xattr` (Mac/Linux) or `pip install pywin32` (Windows)
- Fallback method still works but is less accurate

**"Auto-discovery finds too many folders"**
- Adjust `max_depth` parameter
- Use `max_depth=1` for immediate children only

**"Attribute name conflicts"**
- Auto-discovered names won't overwrite existing attributes
- Check with `hasattr()` before setting

---

**See also:**
- [PROJECTS_GUIDE.md](PROJECTS_GUIDE.md) - Project structure details
- [README.md](README.md) - Main documentation
