"""Integration tests against the real Dropbox folder.

These tests are skipped automatically when the real Dropbox tree is not
present on the machine (CI, other users' laptops, etc.).
They verify that the actual folder structure is discovered correctly.
"""

import pytest
from pathlib import Path

from mydropbox import dropbox, get_dropbox
from mydropbox.dropbox.base_path import DiscoverablePaths
from mydropbox.config.loadconfig import load_config


# ---------------------------------------------------------------------------
# Skip guard — skip the whole module if the real Dropbox base doesn't exist
# ---------------------------------------------------------------------------

_config = load_config()
_real_base = Path(_config["base_path"]) if _config.get("base_path") else None

# Try auto-detected path used by get_dropbox() when base_path is None
if _real_base is None or not _real_base.exists():
    # Replicate the auto-detection logic to find out where Dropbox lives
    import os
    _candidates = [
        Path.home() / "UHM_Ocean_BGC_Group Dropbox",
        Path("/mnt/md0/group_data/UHM_Ocean_BGC_Group Dropbox"),
        Path.home() / "Dropbox" / "UHM_Ocean_BGC_Group Dropbox",
        Path.home() / "Library" / "CloudStorage" / "Dropbox" / "UHM_Ocean_BGC_Group Dropbox",
    ]
    for _p in _candidates:
        if _p.exists():
            _real_base = _p
            break

_real_dropbox_missing = _real_base is None or not _real_base.exists()

pytestmark = pytest.mark.skipif(
    _real_dropbox_missing,
    reason="Real Dropbox folder not found on this machine",
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def db():
    """Return a DropboxPaths instance pointing at the real Dropbox."""
    return get_dropbox(
        base_path=str(_real_base),
        personal_folder=_config.get("personal_folder"),
        group_depth=1,       # keep it shallow so tests are fast
        personal_depth=1,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestRealDropboxBase:
    def test_base_path_exists(self, db):
        assert db.base_path.exists()
        assert db.base_path.is_dir()

    def test_group_is_discoverable(self, db):
        assert isinstance(db.group, DiscoverablePaths)
        assert db.group._path.exists()

    def test_group_has_children(self, db):
        """At least one sub-folder should be discovered under group."""
        children = db.group.get_all_paths()
        assert len(children) > 0, "No sub-folders discovered under group/"

    def test_group_children_exist_on_disk(self, db):
        for name, node in db.group.get_all_paths().items():
            assert node._path.exists(), f"group.{name} path does not exist: {node._path}"

    def test_default_dropbox_instance(self):
        """The module-level ``dropbox`` object must point at a real folder."""
        assert dropbox.base_path.exists()
        assert isinstance(dropbox.group, DiscoverablePaths)


class TestRealPersonalPaths:
    def test_personal_configured(self, db):
        if db.personal is None:
            pytest.skip("No personal_folder configured in config.yaml")

    def test_personal_exists(self, db):
        if db.personal is None:
            pytest.skip("No personal_folder configured")
        assert db.personal._path.exists()

    def test_personal_has_children(self, db):
        if db.personal is None:
            pytest.skip("No personal_folder configured")
        children = db.personal.get_all_paths()
        assert len(children) > 0, "No sub-folders discovered under personal/"

    def test_personal_children_exist_on_disk(self, db):
        if db.personal is None:
            pytest.skip("No personal_folder configured")
        for name, node in db.personal.get_all_paths().items():
            assert node._path.exists(), f"personal.{name} does not exist: {node._path}"


class TestRealPathlib:
    def test_group_pathlib_exists(self, db):
        assert db.group.exists()
        assert db.group.is_dir()

    def test_group_truediv(self, db):
        result = db.group / "nonexistent_test_file.txt"
        assert isinstance(result, Path)

    def test_group_str(self, db):
        assert str(db.group) == str(db.group._path)

    def test_expand_discovers_deeper(self, db):
        """expand(2) on group should reveal grandchildren."""
        # Work on a fresh instance so we don't mutate the shared fixture
        fresh = get_dropbox(
            base_path=str(_real_base),
            group_depth=1,
            personal_depth=0,
        )
        # Before expand: grandchildren not loaded
        for child in fresh.group.get_all_paths().values():
            assert child._max_depth == 0
        # After expand: grandchildren present for at least one child
        fresh.group.expand(2)
        found_grandchild = any(
            len(child.get_all_paths()) > 0
            for child in fresh.group.get_all_paths().values()
            if child._path.exists()
        )
        assert found_grandchild, "expand(2) found no grandchildren under any group sub-folder"
