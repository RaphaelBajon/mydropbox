# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **PROJECT MANAGEMENT MODULE**: New `mydropbox.projects` module for standardized project structures
  - `ProjectPaths` class for managing research project directories
  - `create_project()` function to create projects with templates
  - Three templates: "full" (complete data science), "simple" (essentials), "minimal" (basic)
  - Automatic directory creation following best practices (Cookiecutter Data Science)
  - Helper methods: `save_dataset()`, `save_figure()`, `list_datasets()`
  - Auto-generated README.md, .gitignore, and project metadata
  - Standardized structure: data/{raw,interim,processed}, src/, notebooks/, plots/, etc.
  - See `PROJECTS_GUIDE.md` for complete documentation

### Changed
- **PRIVACY IMPROVEMENT**: Personal folder name is now configurable via `personal_folder` parameter
  - Prevents exposing personal names in GitHub repositories
  - `get_dropbox(personal_folder="Your Name")` required for personal paths
  - Default `dropbox` instance now has `personal=None` for group-only access
  - See `mydropbox_config_template.py` for configuration examples

### Planned
- Add support for custom folder configurations
- Add helper functions for common file operations
- Integration with xarray for netCDF file handling

## [0.1.0] - 2026-01-28

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
- `PersonalPaths` class for accessing personal folders:
  - admin, datasets, meeting, mycode, papers, phd
  - projects, slides, soc_tools, team, utils
  - Special pCO2 adjusted data folder
- Convenience function `get_dropbox()` for quick access
- Default `dropbox` instance for direct import
- Full documentation in README.md
- Comprehensive examples in examples.py
- Cross-platform path support using pathlib
- MIT License

### Features
- Auto-detection of Dropbox location across different platforms
- Support for custom Dropbox paths
- Clean, intuitive API for path access
- Type-safe using pathlib.Path objects
- Fully documented with examples

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
