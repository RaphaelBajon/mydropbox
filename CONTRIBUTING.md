# Contributing to MyDropbox

Thanks for your interest in improving this library! This guide will help you contribute effectively.

## Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/raphaelbajon/mydropbox.git
   cd mydropbox
   ```

2. **Install in development mode**
   ```bash
   pip install -e .
   ```

3. **Make your changes**
   - Edit files in `mydropbox/`
   - Update documentation if needed
   - Add examples if you're adding new features

## How to Contribute

### Reporting Issues

If you find a bug or have a suggestion:
1. Check if the issue already exists
2. Open a new issue with:
   - Clear description of the problem
   - Steps to reproduce (if it's a bug)
   - Your environment (OS, Python version)
   - Suggested solution (if you have one)

### Adding New Features

1. **Before you start**, open an issue to discuss the feature
2. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**:
   - Add the feature to `mydropbox/__init__.py`
   - Update `README.md` with usage examples
   - Update `CHANGELOG.md` under `[Unreleased]`
4. **Test your changes**:
   ```bash
   pytest tests/
   ```
5. **Commit with clear messages**:
   ```bash
   git commit -m "Add feature: [brief description]"
   ```
6. **Push and create a Pull Request**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Code Style

- Follow PEP 8
- Use clear, descriptive variable names
- Add docstrings to functions (summary + Args + Returns)
- Use type hints where appropriate

## Adding New Paths

Paths are auto-discovered — no code changes needed. Any new subfolder in Dropbox will be accessible as an attribute after calling `expand()` or reloading:

```python
db.group.datasets.expand(1)   # refresh one level deep
db.group.datasets.my_new_folder  # now available
```

If you're adding support for a completely new Dropbox root (e.g. a second shared group folder), edit `mydropbox/dropbox/group_path.py` or `personal_path.py` and update `README.md`.

4. **Update CHANGELOG.md** under `[Unreleased]` → `Added`

## Version Updates

When ready to release, follow the steps in [CHANGELOG.md](CHANGELOG.md):

1. **Update version** in `pyproject.toml`
2. **Update CHANGELOG.md** — move items from `[Unreleased]` to a new `## [X.Y.Z] - YYYY-MM-DD` section
3. **Tag and push**:
   ```bash
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin main --tags
   ```

This project uses [Semantic Versioning](https://semver.org/): MAJOR.MINOR.PATCH.

## Testing

Before submitting: `pytest tests/`

---

Thank you for contributing to the UHM Ocean BGC Group dropbox!
