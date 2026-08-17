"""Tests for labpc site detection and personal-path resolution (dropbox_path.py).

Uses a fake ``tmp_path`` tree shaped like the real lab PC mount
(``<root>/group_data/UHM_Ocean_BGC_Group Dropbox`` for the group,
``<root>/<username>/UHM_Ocean_BGC_Group Dropbox/<Name>`` for personal folders,
siblings under the same mount root) so tests don't depend on the real
``/mnt/md0`` mount or real lab usernames.
"""

import importlib
import warnings
from pathlib import Path

import pytest

# Import via importlib to avoid the `dropbox = DropboxPaths(...)` instance in
# mydropbox/__init__.py shadowing the `mydropbox.dropbox` subpackage (see the
# same workaround in tests/test_utils.py).
dropbox_path_module = importlib.import_module("mydropbox.dropbox.dropbox_path")
get_dropbox = dropbox_path_module.get_dropbox


@pytest.fixture
def fake_lab_tree(tmp_path, monkeypatch):
    """Build a fake lab mount and point _LAB_MOUNT_ROOT at it."""
    lab_root = tmp_path / "mnt" / "md0"
    group_base = lab_root / "group_data" / "UHM_Ocean_BGC_Group Dropbox"
    (group_base / "datasets").mkdir(parents=True)

    personal_base = lab_root / "raph" / "UHM_Ocean_BGC_Group Dropbox" / "Raphaël Bajon"
    (personal_base / "mycode").mkdir(parents=True)

    monkeypatch.setattr(dropbox_path_module, "_LAB_MOUNT_ROOT", lab_root)
    monkeypatch.setattr(
        dropbox_path_module,
        "load_config",
        lambda: {"personal_folder": None, "base_path": None,
                  "labpc_users": {"Raphaël Bajon": "raph"}},
    )
    return group_base


class TestLabpcDetection:
    def test_configured_for_labpc(self, fake_lab_tree):
        db = get_dropbox(base_path=str(fake_lab_tree))
        assert db._configure_for_labpc is True
        assert db._configure_for_persopc is False

    def test_personopc_regression_guard(self, tmp_dropbox):
        """A normal (non-/mnt) base_path must still be treated as a personal computer."""
        db = get_dropbox(base_path=str(tmp_dropbox / "group"))
        assert db._configure_for_labpc is False
        assert db._configure_for_persopc is True


class TestLabpcPersonalResolution:
    def test_resolves_known_user(self, fake_lab_tree):
        db = get_dropbox(base_path=str(fake_lab_tree), personal_folder="Raphaël Bajon")
        expected = fake_lab_tree.parent.parent / "raph" / "UHM_Ocean_BGC_Group Dropbox" / "Raphaël Bajon"
        assert db.personal._path == expected
        assert db.personal._path.exists()

    def test_unknown_user_raises_value_error(self, fake_lab_tree):
        with pytest.raises(ValueError, match="No labpc username configured"):
            get_dropbox(base_path=str(fake_lab_tree), personal_folder="Someone New")


class TestBasePathAutoDetectWarning:
    def test_warns_when_nothing_found(self, monkeypatch):
        monkeypatch.setattr(Path, "exists", lambda self: False)
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            get_dropbox()
        assert any("Could not auto-detect the Dropbox base path" in str(w.message) for w in caught)
