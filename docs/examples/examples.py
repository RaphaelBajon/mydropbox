"""
examples_dropbox.py — MyDropbox path access examples.

Run with:
    python docs/examples/examples.py
"""

from mydropbox import get_dropbox, check_sync_status


# ── 1. Basic path access ──────────────────────────────────────────────────────

db = get_dropbox(personal_folder="Your Name")

# Group folders
print(db.group.datasets)           # .../UHM_Ocean_BGC_Group/datasets
print(db.group.group_notes)

# Personal folders
print(db.personal.mycode)          # .../Your Name/mycode
print(db.personal.projects)

# Build a file path (returns a plain pathlib.Path)
data_file = db.group.datasets / "cruise_2025.nc"
script    = db.personal.mycode / "analysis" / "compute_flux.py"


# ── 2. Discover deeper sub-folders ───────────────────────────────────────────

# Default discovery depth is 2 levels.  Drill deeper on demand:
db.group.datasets.expand(2)
print(db.group.datasets.argo.floats_2025)   # accessible after expand


# ── 3. Standard pathlib operations ───────────────────────────────────────────

if data_file.exists():
    print(f"size: {data_file.stat().st_size / 1e6:.1f} MB")

nc_files = list(db.personal.datasets.glob("*.nc"))
all_scripts = list(db.personal.mycode.rglob("*.py"))


# ── 4. Sync status and download ───────────────────────────────────────────────

status = check_sync_status(data_file)
# {'exists_locally': bool, 'is_synced': bool, 'is_online_only': bool, ...}

if status['is_online_only']:
    # Trigger Dropbox Smart Sync download (macOS: NSFileCoordinator; Linux: file open)
    check_sync_status(data_file, download_if_online=True)
    print("Download triggered — wait for Dropbox to finish, then re-run.")
else:
    pass  # import xarray as xr; ds = xr.open_dataset(data_file)


# ── 5. Writing portable shared code ──────────────────────────────────────────

def load_flux_data():
    """Load carbon flux data — works for any group member with the library installed."""
    filename = f"test.nc"
    filepath = db.group.datasets / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Not found: {filename}")
    import xarray as xr
    return xr.open_dataset(filepath)

