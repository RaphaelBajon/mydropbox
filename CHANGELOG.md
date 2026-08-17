# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `auto_identify` option on `get_dropbox()` / `DropboxPaths` — resolves
  `personal_folder` automatically from the Dropbox account's display name via
  the official `dropbox` SDK, instead of requiring it to be passed or
  configured by hand. Opt-in only (default `False`); no-op when
  `personal_folder` is already provided. Requires
  `pip install mydropbox[sdk]` and a `MYDROPBOX_SDK_TOKEN` access token — see
  `docs/DROPBOX_SDK_SETUP.md`. Raises a clear error if the resolved account
  name doesn't match any folder on disk, rather than guessing.
- New `sdk` optional-dependency group (`dropbox`) in `pyproject.toml`.

## [0.2.1] - 2026-08-16

### Fixed
- Package-shipped `config/config.yaml` no longer hardcodes a real `PERSONAL_FOLDER` —
  it ships as `null` so installing the package never silently leaks one user's
  identity to teammates who haven't set up their own `~/.mydropbox.yaml`
- Labpc personal-folder resolution: the hardcoded `path_lab_fixed` name→username dict
  (a bare `KeyError` for any unlisted lab member) is replaced by a `labpc_users`
  mapping loaded from config, so new lab members are added via config, not source
- Site detection (`labpc` vs personal computer) no longer relies on fragile
  index-based `path.parts[1] == 'mnt'`; uses `base_path.is_relative_to(...)` against
  the known lab mount root instead
- `DropboxPaths` now warns (`warnings.warn`) instead of silently falling back to a
  probably-nonexistent path when Dropbox base-path auto-detection finds nothing
- Restored `MYDROPBOX_PERSONAL_FOLDER` / `MYDROPBOX_BASE_PATH` environment variable
  overrides in `load_config()` (highest priority, above the YAML file) — this existed
  before the 0.2.0 YAML rewrite and had been silently dropped
- `check_sync_status`'s return type annotation now uses `typing.Any` instead of the
  builtin `any`

### Changed
- README's "Config file" section now documents the actual YAML-based mechanism
  (`~/.mydropbox.yaml`) instead of a `mydropbox_config_template.py` module that never
  existed

### Removed
- `tests/test_mydropbox.py`, a pre-0.2.0 file left behind after its contents were
  split into `test_discoverable_paths.py` / `test_dropbox_paths.py` /
  `test_project_paths.py` / `test_utils.py`

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
