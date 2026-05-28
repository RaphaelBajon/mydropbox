# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-05-28

### Added
- `DiscoverablePaths` base class shared by `GroupPaths` and `PersonalPaths` — eliminates duplication and provides a single extension point
- Recursive directory discovery: every subdirectory is a `DiscoverablePaths` instance, enabling chained access (`db.group.datasets.argo.floats_2025`)
- `max_depth` parameter on `get_dropbox()` (`group_depth`, `personal_depth`) to control eager discovery depth at startup (default: 2)
- `expand(depth)` method on every node — drill deeper into a specific branch at runtime without re-scanning the whole tree
- Full `pathlib.Path` API at every level via transparent `__getattr__` delegation
- `DataPaths`, `PlotPaths`, `SourcePaths` now inherit `DiscoverablePaths` — `expand()` works on project sub-trees too
- `ProjectPaths` inherits `DiscoverablePaths` with a typed `_discover_all_paths()` override; custom folders added after creation are auto-discovered
- `template` parameter on `ProjectPaths.__init__` when `auto_create=True`
- `environment.yml` and `environment-dev.yml` conda environment files

### Fixed
- `_check_sync_macos`: replaced fragile size heuristic with sparse-file detection (`st_blocks`); fixed `bytes`/`str` mismatch in xattr lookup
- `save_dataset`: numpy and torch branches now use `np.save()` / `torch.save()` correctly
- `create_structure()` raises `ValueError` on unknown template names instead of silently falling through to `"full"`
- `list_datasets()` no longer crashes when a data sub-directory was not created by the chosen template
- `create_metadata()` writes with explicit `utf-8` encoding

### Changed
- `requires-python` bumped to `>=3.12`
- `pyproject.toml` dependencies split into `[science]` and `[dev]` optional groups
- Tests split from a single `test_mydropbox.py` into focused files: `test_discoverable_paths.py`, `test_dropbox_paths.py`, `test_project_paths.py`, `test_utils.py`

## [0.1.0] - 2026-03-16

### Added
- Initial release of MyDropbox library
- `DropboxPaths` main class with auto-detection of Dropbox location
- `GroupPaths` class for accessing shared group folders:
  - Assorted content
  - Collaborative projects
  - Datasets
  - Group notes
  - Lab/Field data
  - Ocean reports
- `PersonalPaths` class for accessing personal folders
- Convenience function `get_dropbox()` for quick access
- Default `dropbox` instance for direct import
- Comprehensive examples in examples.py
- Cross-platform path support using pathlib

- **PROJECT MANAGEMENT MODULE**: New `mydropbox.projects` module for standardized project structures
  - `ProjectPaths` class for managing research project directories
  - `create_project()` function to create projects with templates
  - Three templates: "full" (complete data science), "simple" (essentials), "minimal" (basic)
  - Automatic directory creation following best practices (Cookiecutter Data Science)
  - Auto-generated README.md, .gitignore, and project metadata
  - Standardized structure: data/{raw,interim,processed}, src/, notebooks/, plots/, etc.
  - See `PROJECTS_GUIDE.md` for complete documentation
- **PRIVACY IMPROVEMENT**: Personal folder name is also configurable via `personal_folder` parameter

### Features
- Auto-detection of Dropbox location across different platforms
- Support for custom Dropbox paths
- Clean, intuitive API for path access
- Type-safe using pathlib.Path objects

---

## Version Numbering

This project uses [Semantic Versioning](https://semver.org/):
- **MAJOR** version for incompatible API changes
- **MINOR** version for added functionality (backwards compatible)
- **PATCH** version for backwards compatible bug fixes

Example: `0.1.0`
- `0` = Major version (initial development)
- `1` = Minor version (first release)
- `0` = Patch version (no patches yet)
