"""Tests for DiscoverablePaths base class (base_path.py)."""

import os
from pathlib import Path

import pytest

from mydropbox.dropbox.base_path import DiscoverablePaths
from mydropbox.dropbox.group_path import GroupPaths
from mydropbox.dropbox.personal_path import PersonalPaths


class TestInheritance:
    def test_group_paths_is_subclass(self):
        assert issubclass(GroupPaths, DiscoverablePaths)

    def test_personal_paths_is_subclass(self):
        assert issubclass(PersonalPaths, DiscoverablePaths)


class TestDiscovery:
    def test_auto_discovery(self, tmp_dropbox):
        gp = GroupPaths(tmp_dropbox / "group")
        paths = gp.get_all_paths()

        assert "datasets" in paths
        assert "group_notes" in paths
        assert "collaborative_projects" in paths
        assert all(isinstance(v, DiscoverablePaths) for v in paths.values())

    def test_recursive_chaining_group(self, tmp_dropbox):
        """With max_depth=None the full tree is available at any depth."""
        gp = GroupPaths(tmp_dropbox / "group", max_depth=None)

        assert isinstance(gp.datasets, DiscoverablePaths)
        assert isinstance(gp.datasets.argo, DiscoverablePaths)
        assert isinstance(gp.datasets.argo.floats_2025, DiscoverablePaths)
        assert gp.datasets.argo.floats_2025._path == (
            tmp_dropbox / "group" / "datasets" / "argo" / "floats_2025"
        )

    def test_recursive_chaining_personal(self, tmp_dropbox):
        pp = PersonalPaths(tmp_dropbox / "My Name", max_depth=None)

        assert isinstance(pp.projects.project_01.data, DiscoverablePaths)
        assert pp.projects.project_01.data._path == (
            tmp_dropbox / "My Name" / "projects" / "project_01" / "data"
        )


class TestExpand:
    def test_expand_from_depth_zero(self, tmp_dropbox):
        """expand(1) on a depth-0 node discovers immediate children."""
        gp = GroupPaths(tmp_dropbox / "group", max_depth=0)
        assert gp.get_all_paths() == {}
        gp.expand(1)
        assert isinstance(gp.datasets, DiscoverablePaths)

    def test_expand_does_not_affect_siblings(self, tmp_dropbox):
        """expanding one branch leaves other nodes unchanged."""
        gp = GroupPaths(tmp_dropbox / "group", max_depth=1)
        # datasets child exists but has no grandchildren yet
        assert "argo" not in gp.datasets.__dict__
        gp.datasets.expand(1)
        assert isinstance(gp.datasets.argo, DiscoverablePaths)
        # sibling branch is untouched
        assert "argo" not in gp.group_notes.__dict__

    def test_expand_returns_self_for_chaining(self, tmp_dropbox):
        """expand() returns self so you can chain attribute access."""
        gp = GroupPaths(tmp_dropbox / "group", max_depth=1)
        node = gp.datasets.expand(2).argo
        assert isinstance(node, DiscoverablePaths)
        assert isinstance(node.floats_2025, DiscoverablePaths)

    def test_expand_depth_two(self, tmp_dropbox):
        """expand(2) on a leaf node reaches two extra levels."""
        gp = GroupPaths(tmp_dropbox / "group", max_depth=0)
        gp.expand(3)
        assert isinstance(gp.datasets.argo.floats_2025, DiscoverablePaths)

    def test_expand_idempotent(self, tmp_dropbox):
        """Calling expand() twice doesn't break already-discovered paths."""
        gp = GroupPaths(tmp_dropbox / "group", max_depth=1)
        gp.datasets.expand(1)
        gp.datasets.expand(1)
        assert isinstance(gp.datasets.argo, DiscoverablePaths)


class TestMaxDepth:
    def test_depth_zero_no_children(self, tmp_dropbox):
        """max_depth=0 must not discover any children."""
        gp = GroupPaths(tmp_dropbox / "group", max_depth=0)
        assert gp.get_all_paths() == {}

    def test_depth_one_no_grandchildren(self, tmp_dropbox):
        """max_depth=1 discovers children but not grandchildren."""
        gp = GroupPaths(tmp_dropbox / "group", max_depth=1)
        assert isinstance(gp.datasets, DiscoverablePaths)
        assert "argo" not in gp.datasets.__dict__

    def test_depth_two_has_grandchildren(self, tmp_dropbox):
        """max_depth=2 (default) discovers children and grandchildren."""
        gp = GroupPaths(tmp_dropbox / "group", max_depth=2)
        assert isinstance(gp.datasets.argo, DiscoverablePaths)
        assert "floats_2025" not in gp.datasets.argo.__dict__

    def test_depth_three_has_great_grandchildren(self, tmp_dropbox):
        gp = GroupPaths(tmp_dropbox / "group", max_depth=3)
        assert isinstance(gp.datasets.argo.floats_2025, DiscoverablePaths)

    def test_depth_none_unlimited(self, tmp_dropbox):
        gp = GroupPaths(tmp_dropbox / "group", max_depth=None)
        assert isinstance(gp.datasets.argo.floats_2025, DiscoverablePaths)


class TestPathInterface:
    def test_truediv_root(self, tmp_dropbox):
        gp = GroupPaths(tmp_dropbox / "group")
        result = gp / "new_subdir"
        assert isinstance(result, Path)
        assert result == tmp_dropbox / "group" / "new_subdir"

    def test_truediv_chained(self, tmp_dropbox):
        """/ operator at any chained level returns a plain Path."""
        gp = GroupPaths(tmp_dropbox / "group")
        result = gp.datasets.argo / "my_file.nc"
        assert isinstance(result, Path)
        assert result == tmp_dropbox / "group" / "datasets" / "argo" / "my_file.nc"

    def test_str(self, tmp_dropbox):
        gp = GroupPaths(tmp_dropbox / "group")
        assert str(gp) == str(tmp_dropbox / "group")

    def test_fspath(self, tmp_dropbox):
        gp = GroupPaths(tmp_dropbox / "group")
        assert os.fspath(gp) == str(tmp_dropbox / "group")

    def test_equality(self, tmp_dropbox):
        gp1 = GroupPaths(tmp_dropbox / "group")
        gp2 = GroupPaths(tmp_dropbox / "group")
        assert gp1 == gp2

    def test_repr_group(self, tmp_dropbox):
        gp = GroupPaths(tmp_dropbox / "group")
        r = repr(gp)
        assert r.startswith("GroupPaths(")
        assert "folders" in r

    def test_repr_personal(self, tmp_dropbox):
        pp = PersonalPaths(tmp_dropbox / "My Name")
        r = repr(pp)
        assert r.startswith("PersonalPaths(")
        assert "folders" in r

    def test_pathlib_delegation(self, tmp_dropbox):
        """Any pathlib.Path method not explicitly defined must still work."""
        gp = GroupPaths(tmp_dropbox / "group")

        assert gp.exists()
        assert gp.is_dir()
        assert not gp.is_file()
        assert gp.name == "group"
        assert gp.stem == "group"
        assert gp.suffix == ""
        assert gp.parent == tmp_dropbox
        assert len(list(gp.iterdir())) > 0
        assert isinstance(list(gp.rglob("*.nc")), list)
        assert gp.resolve() == (tmp_dropbox / "group").resolve()
