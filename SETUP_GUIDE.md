# Setup Guide

## 1. Install

```bash
pip install git+https://github.com/raphaelbajon/mydropbox.git
```

Or clone locally for development:
```bash
git clone https://github.com/raphaelbajon/mydropbox.git && pip install -e mydropbox
```

## 2. Verify

```python
from mydropbox import get_dropbox
db = get_dropbox(personal_folder="Your Name")

print(db.group.datasets)           # → .../group/datasets
print(db.group.datasets.exists())  # → True
print(db.personal.mycode)          # → .../Your Name/mycode
```

See [README.md](README.md) for configuration options and the full API.
