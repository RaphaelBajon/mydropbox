"""Tests for DropboxPaths / get_dropbox (dropbox_path.py)."""

import pytest

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
