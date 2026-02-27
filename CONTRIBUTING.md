# Contributing to MyDropbox

Thanks for your interest in improving this library! This guide will help you contribute effectively.

## Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/[GROUP_GITHUB]/mydropbox.git
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
   python examples.py
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

- Follow PEP 8 style guidelines
- Use clear, descriptive variable names
- Add docstrings to all classes and functions
- Keep functions focused and simple
- Use type hints where appropriate

Example:
```python
def get_data_path(filename: str) -> Path:
    """
    Get the full path to a dataset file.
    
    Args:
        filename: Name of the dataset file
        
    Returns:
        Full Path object to the dataset
        
    Example:
        >>> path = get_data_path("flux_2025.nc")
    """
    return dropbox.personal.datasets / filename
```

## Adding New Paths

If you need to add new folders to the library:

1. **For personal paths**, edit the `PersonalPaths` class:
   ```python
   class PersonalPaths:
       def __init__(self, base_path: Path):
           self.base = base_path
           # Add your new path here
           self.new_folder = self.base / "new_folder_name"
   ```

2. **For group paths**, edit the `GroupPaths` class similarly

3. **Update README.md** to document the new path

4. **Update CHANGELOG.md** under `[Unreleased]` → `Added`

## Version Updates

When you're ready to release a new version:

1. **Update version number** in:
   - `setup.py` (line: `version="X.Y.Z"`)
   - `mydropbox/__init__.py` (add `__version__ = "X.Y.Z"`)

2. **Update CHANGELOG.md**:
   - Move items from `[Unreleased]` to a new version section
   - Add the date: `## [X.Y.Z] - YYYY-MM-DD`

3. **Create a git tag**:
   ```bash
   git tag -a v0.1.0 -m "Release version 0.1.0"
   git push origin v0.1.0
   ```

## Version Numbering

Use [Semantic Versioning](https://semver.org/):
- **MAJOR** (X.0.0): Breaking changes (incompatible API changes)
- **MINOR** (0.X.0): New features (backwards compatible)
- **PATCH** (0.0.X): Bug fixes (backwards compatible)

Examples:
- `0.1.0` → `0.1.1`: Fixed a bug
- `0.1.1` → `0.2.0`: Added new helper functions
- `0.2.0` → `1.0.0`: Changed the API structure

## Testing

Before submitting:
1. Run the examples: `python docs/examples/examples.py` (:sleeping:)
2. Test in your own scripts
3. Check that paths resolve correctly
4. Verify cross-platform compatibility if possible

## Questions?

- Open an issue for questions
- Discuss in group meetings
- Check the README.md for documentation

## Code of Conduct

- Be respectful and constructive
- Help others learn and improve
- Focus on the science and the code
- Have fun! 🌊

---

Thank you for contributing to the UHM Ocean BGC Group dropbox! 🙏
