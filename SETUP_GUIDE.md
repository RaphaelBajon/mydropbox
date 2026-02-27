# Setup Guide for New Users

Welcome to MyDropbox! This guide will help you get started quickly.

## Step 1: Install the Library

```bash
# If your group has it on GitHub:
pip install git+https://github.com/raphaelbajon/mydropbox.git
```

## Step 2: Configure Your Personal Folder

You have three options to set your personal folder name:

### Option A: Direct in Code (Simplest)

Just specify your name when you use it:

```python
from mydropbox import get_dropbox

db = get_dropbox(personal_folder="Your Name")  # Replace with YOUR name
data = db.personal.datasets / "my_file.nc"
```

**Pros**: Simple, no extra files  
**Cons**: Your name is in your code (might be shared)

### Option B: Config File (Recommended)

1. **Copy the template**:
   ```bash
   cp mydropbox_config_template.py mydropbox_config.py
   ```

2. **Edit `mydropbox_config.py`**:
   ```python
   PERSONAL_FOLDER = "Your Actual Name"  # Change this!
   ```

3. **Use in your code**:
   ```python
   from config.mydropbox_config import PERSONAL_FOLDER
   from mydropbox import get_dropbox
   
   db = get_dropbox(personal_folder=PERSONAL_FOLDER)
   ```

4. **Important**: `mydropbox_config.py` is already in `.gitignore`, so your name won't be pushed to GitHub!

**Pros**: Private, not shared in Git  
**Cons**: One extra file

## Step 3: Test It Out

Create a test script:

```python
from mydropbox import get_dropbox

# Initialize (using Option A for this test)
db = get_dropbox(personal_folder="Your Name")  # Use YOUR actual name!

# Test group paths
print("Group datasets folder:", db.group.datasets)
print("Exists?", db.group.datasets.exists())

# Test personal paths
if db.personal:
    print("\nPersonal datasets folder:", db.personal.datasets)
    print("Exists?", db.personal.datasets.exists())
    print("Personal code folder:", db.personal.mycode)
    print("Exists?", db.personal.mycode.exists())
else:
    print("\nNo personal folder configured")
```

Run it:
```bash
python test_mydropbox.py
```

You should see your Dropbox paths printed out!

## Step 4: Use It in Your Work

### In Jupyter Notebooks

At the top of your notebook:

```python
from config.mydropbox_config import PERSONAL_FOLDER
from mydropbox import get_dropbox
import xarray as xr

# Initialize once
db = get_dropbox(personal_folder=PERSONAL_FOLDER)

# Now use it throughout your notebook
ds = xr.open_dataset(db.personal.datasets / "my_data.nc")
```

### In Scripts

```python
#!/usr/bin/env python
"""My analysis script"""

from config.mydropbox_config import PERSONAL_FOLDER
from mydropbox import get_dropbox


def main():
    db = get_dropbox(personal_folder=PERSONAL_FOLDER)

    # Your code here
    data_file = db.personal.datasets / "flux_data.nc"
    # ...


if __name__ == "__main__":
    main()
```

## Common Issues

### "ModuleNotFoundError: No module named 'mydropbox'"

The package isn't installed. Run:
```bash
pip install -e /path/to/mydropbox_package
```

### "ModuleNotFoundError: No module named 'mydropbox_config'"

You're using Option B but haven't created `mydropbox_config.py`. Either:
- Create it from the template, OR
- Use Option A (direct specification) instead

### "AttributeError: 'NoneType' object has no attribute 'datasets'"

You're trying to access `db.personal` but didn't specify `personal_folder`. Use:
```python
db = get_dropbox(personal_folder="Your Name")
```

### Paths don't exist

Make sure:
1. Your Dropbox folder name is correct (check in Finder/Explorer)
2. Your personal folder name matches exactly (including spaces, accents, etc.)
3. Dropbox is actually synced to your computer

## Next Steps

- Read the [README.md](README.md) for detailed usage examples
- Check [QUICKREF.md](QUICKREF.md) for a quick reference
- See [examples.py](docs/examples/examples.py) for code examples
- Read [CONTRIBUTING.md](CONTRIBUTING.md) if you want to add features

## Getting Help

- Check if your issue is in "Common Issues" above
- Look at the examples in [examples.py](docs/examples/examples.py)
- Ask your colleagues in the group
- Open an issue on GitHub

---

**Welcome to the group dropbox library! Happy coding! 🌊**
