# Utilities Guide

## `check_sync_status()` — Check Dropbox sync state

Checks whether a file or folder is synced locally, online-only, or currently syncing.

```python
from mydropbox import get_dropbox, check_sync_status

db = get_dropbox(personal_folder="Your Name")

status = check_sync_status(db.personal.datasets / "large_data.nc")
# {
#   'path': Path,
#   'exists_locally': bool,
#   'is_synced': bool,
#   'is_online_only': bool,
#   'is_syncing': bool,
#   'error': str | None,
#   'downloaded': bool,
# }

# Download if online-only
if status['is_online_only']:
    check_sync_status(db.personal.datasets / "large_data.nc", download_if_online=True)
```

**Before processing a large file:**
```python
data_file = db.personal.datasets / "50gb_output.nc"
status = check_sync_status(data_file)

if not status['is_synced']:
    check_sync_status(data_file, download_if_online=True)
    print("Sync triggered — wait for Dropbox to finish before re-running.")
else:
    ds = xr.open_dataset(data_file)
```

---

## `auto_discover_paths()` — Manual path discovery

Called automatically on `get_dropbox()`, but available directly if you need it for a custom path:

```python
from mydropbox.dropbox.utils import auto_discover_paths

discovered = auto_discover_paths(some_path, max_depth=1)
# {"my_data": Path(".../My Data"), "results_2026": Path(".../Results 2026"), ...}
```

Folder names are converted to valid snake_case Python identifiers:

| Folder name | Attribute |
|-------------|-----------|
| `My Data` | `my_data` |
| `2023_Results` | `results_2023` |
| `Lab-Field Data` | `lab_field_data` |
| `Project #1` | `project_1` |
