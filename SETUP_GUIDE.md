# Setup Guide for New Users

Welcome to MyDropbox! This guide will help you get started quickly.

## Step 1: Install the Library

```bash
# If your group has it on GitHub:
pip install git+https://github.com/raphaelbajon/mydropbox.git
```

## Step 2: Configure Your Personal Folder

You have 2 options to set your personal folder name:

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
   from mydropbox.config.mydropbox_config import PERSONAL_FOLDER
   from mydropbox import get_dropbox
   
   db = get_dropbox(personal_folder=PERSONAL_FOLDER)
   ```

4. **Important**: `mydropbox_config.py` is already in `.gitignore`, so your name won't be pushed to GitHub!

## Step 3: Test It Out

Create a test script:

```python
from mydropbox import get_dropbox

# Initialize (using Option A for this test)
db = get_dropbox(personal_folder="Your Name")  # Use YOUR actual name

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

## Next Steps

- Read the [README.md](README.md) for detailed usage examples
- Check [PROJECTS_GUIDE.md](PROJECTS_GUIDE.md) for a project setup
- See [examples.py](docs/examples/examples.py) for code examples
- Read [CONTRIBUTING.md](CONTRIBUTING.md) if you want to add features

