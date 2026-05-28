"""
Tests for mydropbox package.

Run with:
    pytest tests/test_mydropbox.py -v
"""

import tempfile
import shutil
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def tmp_dropbox(tmp_path):
    """Create a minimal fake Dropbox directory tree."""
    group = tmp_path / "group"
    (group / "datasets").mkdir(parents=True)
    (group / "group_notes").mkdir(parents=True)
    (group / "collaborative_projects").mkdir(parents=True)

    personal = tmp_path / "My Name"
    (personal / "mycode").mkdir(parents=True)
    (personal / "datasets").mkdir(parents=True)
    (personal / "projects").mkdir(parents=True)

    return tmp_path


# ---------------------------------------------------------------------------
# DiscoverablePaths base class
# ---------------------------------------------------------------------------

class TestDiscoverablePaths:
    def test_inherits_into_group_paths(self, tmp_dropbox):
        from mydropbox.dropbox.base_path import DiscoverablePaths
        from mydropbox.dropbox.group_path import GroupPaths

        assert issubclass(GroupPaths, DiscoverablePaths)

    def test_inherits_into_personal_paths(self):
        from mydropbox.dropbox.base_path import DiscoverablePaths
        from mydropbox.dropbox.personal_path import PersonalPaths

        assert issubclass(PersonalPaths, DiscoverablePaths)

    def test_auto_discovery(self, tmp_dropbox):
        from mydropbox.dropbox.group_path import GroupPaths

        gp = GroupPaths(tmp_dropbox / "group")
        paths = gp.get_all_paths()

        assert "datasets" in paths
        assert "group_notes" in paths
        assert "collaborative_projects" in paths

    def test_truediv_operator(self, tmp_dropbox):
        from mydropbox.dropbox.group_path import GroupPaths

        gp = GroupPaths(tmp_dropbox / "group")
        result = gp / "new_subdir"
        assert isinstance(result, Path)
        assert result == tmp_dropbox / "group" / "new_subdir"

    def test_str(self, tmp_dropbox):
        from mydropbox.dropbox.group_path import GroupPaths

        gp = GroupPaths(tmp_dropbox / "group")
        assert str(gp) == str(tmp_dropbox / "group")

    def test_fspath(self, tmp_dropbox):
        import os
        from mydropbox.dropbox.group_path import GroupPaths

        gp = GroupPaths(tmp_dropbox / "group")
        assert os.fspath(gp) == str(tmp_dropbox / "group")

    def test_equality(self, tmp_dropbox):
        from mydropbox.dropbox.group_path import GroupPaths

        gp1 = GroupPaths(tmp_dropbox / "group")
        gp2 = GroupPaths(tmp_dropbox / "group")
        assert gp1 == gp2

    def test_repr_group(self, tmp_dropbox):
        from mydropbox.dropbox.group_path import GroupPaths

        gp = GroupPaths(tmp_dropbox / "group")
        r = repr(gp)
        assert r.startswith("GroupPaths(")
        assert "folders" in r

    def test_repr_personal(self, tmp_dropbox):
        from mydropbox.dropbox.personal_path import PersonalPaths

        pp = PersonalPaths(tmp_dropbox / "My Name")
        r = repr(pp)
        assert r.startswith("PersonalPaths(")
        assert "folders" in r

    def test_exists(self, tmp_dropbox):
        from mydropbox.dropbox.group_path import GroupPaths

        gp = GroupPaths(tmp_dropbox / "group")
        assert gp.exists()

    def test_is_dir(self, tmp_dropbox):
        from mydropbox.dropbox.group_path import GroupPaths

        gp = GroupPaths(tmp_dropbox / "group")
        assert gp.is_dir()

    def test_name_property(self, tmp_dropbox):
        from mydropbox.dropbox.group_path import GroupPaths

        gp = GroupPaths(tmp_dropbox / "group")
        assert gp.name == "group"


# ---------------------------------------------------------------------------
# DropboxPaths / get_dropbox
# ---------------------------------------------------------------------------

class TestDropboxPaths:
    def test_get_dropbox_no_personal(self, tmp_dropbox):
        from mydropbox.dropbox.dropbox_path import get_dropbox

        db = get_dropbox(base_path=str(tmp_dropbox))
        assert db.personal is None
        assert db.group is not None

    def test_get_dropbox_with_personal(self, tmp_dropbox):
        from mydropbox.dropbox.dropbox_path import get_dropbox

        db = get_dropbox(base_path=str(tmp_dropbox), personal_folder="My Name")
        assert db.personal is not None
        assert db.personal.name == "My Name"

    def test_repr(self, tmp_dropbox):
        from mydropbox.dropbox.dropbox_path import get_dropbox

        db = get_dropbox(base_path=str(tmp_dropbox))
        assert "DropboxPaths" in repr(db)


# ---------------------------------------------------------------------------
# ProjectPaths / create_project
# ---------------------------------------------------------------------------

class TestProjectPaths:
    def test_create_project_full(self, tmp_path):
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "test_project", template="full")

        assert project.base.exists()
        assert project.data.raw.exists()
        assert project.data.interim.exists()
        assert project.data.processed.exists()
        assert project.notebooks.exists()
        assert project.src.base.exists()
        assert project.plots.exploratory.exists()
        assert project.plots.publication.exists()
        assert project.docs.exists()
        assert project.readme.exists()
        assert project.gitignore.exists()

    def test_create_project_simple(self, tmp_path):
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "simple_project", template="simple")

        assert project.data.raw.exists()
        assert project.notebooks.exists()
        assert not project.docs.exists()  # not in simple template

    def test_create_project_minimal(self, tmp_path):
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "minimal_project", template="minimal")

        assert project.data.raw.exists()
        assert project.data.processed.exists()
        assert not project.data.interim.exists()  # not in minimal template

    def test_save_dataset_xarray(self, tmp_path):
        pytest.importorskip("xarray")
        import xarray as xr
        import numpy as np
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "xr_project", template="minimal")

        ds = xr.Dataset({"temp": (["x"], np.array([1.0, 2.0, 3.0]))})
        out = project.save_dataset(ds, "test.nc", location="processed")
        assert out.exists()

    def test_save_dataset_numpy(self, tmp_path):
        pytest.importorskip("numpy")
        import numpy as np
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "np_project", template="minimal")

        arr = np.array([1, 2, 3])
        out = project.save_dataset(arr, "test.npy", location="processed")
        assert out.exists()
        loaded = np.load(out)
        assert list(loaded) == [1, 2, 3]

    def test_save_dataset_unknown_type_raises(self, tmp_path):
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "bad_project", template="minimal")

        with pytest.raises(TypeError):
            project.save_dataset(object(), "test.bin", location="processed")

    def test_save_dataset_invalid_location_raises(self, tmp_path):
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "loc_project", template="minimal")

        with pytest.raises(ValueError):
            project.save_dataset([], "test.csv", location="bad_location")

    def test_save_figure(self, tmp_path):
        pytest.importorskip("matplotlib")
        import matplotlib.pyplot as plt
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "fig_project", template="full")

        fig, _ = plt.subplots()
        out = project.save_figure(fig, "test.png", location="publication", dpi=72)
        plt.close(fig)
        assert out.exists()

    def test_repr(self, tmp_path):
        from mydropbox.project.projects import ProjectPaths

        p = ProjectPaths(tmp_path / "my_project")
        assert "my_project" in repr(p)

    def test_list_datasets(self, tmp_path):
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "list_project", template="full")
        (project.data.raw / "a.nc").touch()
        (project.data.raw / "b.nc").touch()

        result = project.list_datasets(location="raw", pattern="*.nc")
        assert len(result["raw"]) == 2


# ---------------------------------------------------------------------------
# check_sync_status
# ---------------------------------------------------------------------------

class TestCheckSyncStatus:
    def test_nonexistent_path(self, tmp_path):
        from mydropbox.dropbox.utils import check_sync_status

        status = check_sync_status(tmp_path / "no_such_file.nc")
        assert status["exists_locally"] is False
        assert status["error"] is not None

    def test_existing_file(self, tmp_path):
        from mydropbox.dropbox.utils import check_sync_status

        f = tmp_path / "real_file.txt"
        f.write_text("hello world")

        status = check_sync_status(f)
        assert status["exists_locally"] is True
        # A locally-written file should NOT be flagged as online-only
        assert status["is_online_only"] is False

    def test_existing_directory(self, tmp_path):
        from mydropbox.dropbox.utils import check_sync_status

        d = tmp_path / "mydir"
        d.mkdir()

        status = check_sync_status(d)
        assert status["exists_locally"] is True
        assert status["is_online_only"] is False


# ---------------------------------------------------------------------------
# auto_discover_paths
# ---------------------------------------------------------------------------

class TestAutoDiscoverPaths:
    def test_discovers_subdirs(self, tmp_dropbox):
        from mydropbox.dropbox.utils import auto_discover_paths

        paths = auto_discover_paths(tmp_dropbox / "group", max_depth=1)
        assert "datasets" in paths
        assert "group_notes" in paths

    def test_skips_files(self, tmp_path):
        from mydropbox.dropbox.utils import auto_discover_paths

        (tmp_path / "subdir").mkdir()
        (tmp_path / "file.txt").write_text("data")

        paths = auto_discover_paths(tmp_path, max_depth=1)
        assert "subdir" in paths
        assert "file" not in paths

    def test_nonexistent_base(self, tmp_path):
        from mydropbox.dropbox.utils import auto_discover_paths

        paths = auto_discover_paths(tmp_path / "no_such_dir", max_depth=1)
        assert paths == {}

    def test_snake_case_conversion(self, tmp_path):
        from mydropbox.dropbox.utils import auto_discover_paths

        (tmp_path / "My Folder Name").mkdir()
        paths = auto_discover_paths(tmp_path, max_depth=1)
        assert "my_folder_name" in paths
