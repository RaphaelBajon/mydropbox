"""Tests for DropboxPaths / get_dropbox (dropbox_path.py)."""

import pytest

from mydropbox import identify
from mydropbox.dropbox.base_path import DiscoverablePaths
from mydropbox.dropbox.dropbox_path import get_dropbox


class TestGetDropbox:
    def test_no_personal_folder(self, tmp_dropbox):
        db = get_dropbox(base_path=str(tmp_dropbox))
        assert db.personal is None
        assert db.group is not None

    def test_with_personal_folder(self, tmp_dropbox):
        db = get_dropbox(base_path=str(tmp_dropbox), personal_folder="My Name")
        assert db.personal is not None
        assert db.personal.name == "My Name"

    def test_repr(self, tmp_dropbox):
        db = get_dropbox(base_path=str(tmp_dropbox))
        assert "DropboxPaths" in repr(db)


class TestDepthParams:
    def test_group_depth_one_no_grandchildren(self, tmp_dropbox):
        """group_depth=1: immediate children of base_path discovered, not deeper."""
        db = get_dropbox(
            base_path=str(tmp_dropbox),
            personal_folder="My Name",
            group_depth=1,
        )
        # "group" and "My Name" are immediate children of tmp_dropbox
        assert isinstance(db.group.group, DiscoverablePaths)
        # "datasets" under "group/" is NOT eagerly discovered at depth=1
        assert "datasets" not in db.group.group.__dict__

    def test_personal_depth_three(self, tmp_dropbox):
        """personal_depth=3: three levels under personal folder are discovered."""
        db = get_dropbox(
            base_path=str(tmp_dropbox),
            personal_folder="My Name",
            personal_depth=3,
        )
        assert isinstance(db.personal.projects.project_01.data, DiscoverablePaths)

    def test_independent_group_and_personal_depths(self, tmp_dropbox):
        db = get_dropbox(
            base_path=str(tmp_dropbox),
            personal_folder="My Name",
            group_depth=1,
            personal_depth=3,
        )
        assert isinstance(db.group.group, DiscoverablePaths)
        assert "datasets" not in db.group.group.__dict__
        assert isinstance(db.personal.projects.project_01.data, DiscoverablePaths)


class TestAutoIdentify:
    def test_explicit_personal_folder_skips_resolver(self, tmp_dropbox, monkeypatch):
        """auto_identify=True must be a no-op when personal_folder is already given."""
        def _boom():
            raise AssertionError("resolve_personal_folder should not have been called")

        monkeypatch.setattr(identify, "resolve_personal_folder", _boom)
        db = get_dropbox(base_path=str(tmp_dropbox), personal_folder="My Name", auto_identify=True)
        assert db.personal.name == "My Name"

    def test_resolves_personal_folder_via_sdk(self, tmp_dropbox, monkeypatch):
        monkeypatch.setattr(identify, "resolve_personal_folder", lambda: "My Name")
        db = get_dropbox(base_path=str(tmp_dropbox), auto_identify=True)
        assert db.personal.name == "My Name"
        assert db.personal._path == tmp_dropbox / "My Name"

    def test_mismatch_between_resolved_name_and_disk_raises(self, tmp_dropbox, monkeypatch):
        monkeypatch.setattr(identify, "resolve_personal_folder", lambda: "Nobody Here")
        with pytest.raises(RuntimeError, match="auto_identify resolved your Dropbox account name"):
            get_dropbox(base_path=str(tmp_dropbox), auto_identify=True)

    def test_auto_identify_false_ignores_missing_personal_folder(self, tmp_dropbox):
        """Default behavior (auto_identify=False) is unaffected: no personal_folder -> None."""
        db = get_dropbox(base_path=str(tmp_dropbox))
        assert db.personal is None
