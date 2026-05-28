# Setup Guide

## 1. Install

```bash
pip install git+https://github.com/raphaelbajon/mydropbox.git
# or locally
git clone https://github.com/raphaelbajon/mydropbox.git && pip install -e mydropbox
```

## 2. Configure your personal folder

**Option A — inline (simple)**
```python
from mydropbox import get_dropbox
db = get_dropbox(personal_folder="Your Name")
```

**Option B — config file (recommended for shared code)**
```bash
cp mydropbox_config_template.py mydropbox_config.py
# edit mydropbox_config.py and set PERSONAL_FOLDER = "Your Name"
```
```python
from mydropbox.config.mydropbox_config import PERSONAL_FOLDER
from mydropbox import get_dropbox
db = get_dropbox(personal_folder=PERSONAL_FOLDER)
```
`mydropbox_config.py` is already in `.gitignore` — your name won't be committed.

## 3. Verify

```python
from mydropbox import get_dropbox
db = get_dropbox(personal_folder="Your Name")

print(db.group.datasets)           # → .../group/datasets
print(db.group.datasets.exists())  # → True
print(db.personal.mycode)          # → .../Your Name/mycode
```

## Next steps

- [README.md](README.md) — full API overview
- [PROJECTS_GUIDE.md](PROJECTS_GUIDE.md) — project structure management
- [docs/examples/](docs/examples/) — runnable examples
