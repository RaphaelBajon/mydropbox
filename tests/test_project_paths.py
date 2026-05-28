"""Tests for ProjectPaths / create_project (project/projects.py)."""

import pytest


class TestCreateProject:
    def test_full_template(self, tmp_path):
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

    def test_simple_template(self, tmp_path):
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "simple_project", template="simple")

        assert project.data.raw.exists()
        assert project.notebooks.exists()
        assert not project.docs.exists()  # not in simple template

    def test_minimal_template(self, tmp_path):
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "minimal_project", template="minimal")

        assert project.data.raw.exists()
        assert project.data.processed.exists()
        assert not project.data.interim.exists()  # not in minimal template

    def test_invalid_template_raises(self, tmp_path):
        from mydropbox.project.projects import ProjectPaths

        project = ProjectPaths(tmp_path / "proj")
        with pytest.raises(ValueError, match="Unknown template"):
            project.create_structure(template="typo")

    def test_repr(self, tmp_path):
        from mydropbox.project.projects import ProjectPaths

        p = ProjectPaths(tmp_path / "my_project")
        assert "my_project" in repr(p)


class TestSaveDataset:
    def test_xarray(self, tmp_path):
        pytest.importorskip("xarray")
        import xarray as xr
        import numpy as np
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "xr_project", template="minimal")
        ds = xr.Dataset({"temp": (["x"], np.array([1.0, 2.0, 3.0]))})
        out = project.save_dataset(ds, "test.nc", location="processed")
        assert out.exists()

    def test_numpy(self, tmp_path):
        import numpy as np
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "np_project", template="minimal")
        arr = np.array([1, 2, 3])
        out = project.save_dataset(arr, "test.npy", location="processed")
        assert out.exists()
        assert list(np.load(out)) == [1, 2, 3]

    def test_unknown_type_raises(self, tmp_path):
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "bad_project", template="minimal")
        with pytest.raises(TypeError):
            project.save_dataset(object(), "test.bin", location="processed")

    def test_invalid_location_raises(self, tmp_path):
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "loc_project", template="minimal")
        with pytest.raises(ValueError):
            project.save_dataset([], "test.csv", location="bad_location")


class TestSaveFigure:
    def test_save_to_publication(self, tmp_path):
        pytest.importorskip("matplotlib")
        import matplotlib.pyplot as plt
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "fig_project", template="full")
        fig, _ = plt.subplots()
        out = project.save_figure(fig, "test.png", location="publication", dpi=72)
        plt.close(fig)
        assert out.exists()

    def test_plt_savefig_directly(self, tmp_path):
        """plt.savefig() works when passed a project path directly."""
        pytest.importorskip("matplotlib")
        import matplotlib.pyplot as plt
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "direct_fig_project", template="full")
        fig, ax = plt.subplots()
        ax.plot([0, 1], [0, 1])
        # project.plots.exploratory is a Path-like object; savefig must accept it
        out = project.plots.exploratory / "quick_check.png"
        plt.savefig(out, dpi=72)
        plt.close(fig)
        assert out.exists()


class TestToNetcdfDirectly:
    def test_ds_to_netcdf_directly(self, tmp_path):
        """xr.Dataset.to_netcdf() works when passed a project path directly."""
        pytest.importorskip("xarray")
        import numpy as np
        import xarray as xr
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "direct_nc_project", template="minimal")
        ds = xr.Dataset({"sst": (["lat", "lon"], np.zeros((3, 4)))})
        out = project.data.processed / "sst.nc"
        ds.to_netcdf(out)
        assert out.exists()
        # Round-trip check
        loaded = xr.open_dataset(out)
        assert "sst" in loaded


class TestListDatasets:
    def test_list_raw(self, tmp_path):
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "list_project", template="full")
        (project.data.raw / "a.nc").touch()
        (project.data.raw / "b.nc").touch()

        result = project.list_datasets(location="raw", pattern="*.nc")
        assert len(result["raw"]) == 2

    def test_list_minimal_no_crash(self, tmp_path):
        """list_datasets(location='all') must not crash when interim is absent."""
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "minimal_list", template="minimal")
        result = project.list_datasets(location="all")
        # interim dir was never created — key must be absent, not an error
        assert "interim" not in result
        assert "raw" in result
        assert "processed" in result

class TestProjectExpand:
    def test_data_expand_discovers_subdirs(self, tmp_path):
        """DataPaths.expand() discovers sub-dirs created after init."""
        from mydropbox.dropbox.base_path import DiscoverablePaths
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "exp_proj", template="full")
        # Add a new nested folder after project creation
        new_dir = project.data.processed / "cruise_2025"
        new_dir.mkdir()
        # Without expand, the new dir is not yet an attribute
        assert "cruise_2025" not in project.data.processed.__dict__
        project.data.processed.expand(1)
        assert isinstance(project.data.processed.cruise_2025, DiscoverablePaths)

    def test_plots_expand_returns_self_for_chaining(self, tmp_path):
        from mydropbox.dropbox.base_path import DiscoverablePaths
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "chain_proj", template="full")
        (project.plots.exploratory / "argo").mkdir()
        node = project.plots.exploratory.expand(1).argo
        assert isinstance(node, DiscoverablePaths)

    def test_project_expand_refreshes_sub_trees(self, tmp_path):
        """ProjectPaths.expand() re-discovers data / src / plots sub-trees."""
        from mydropbox.dropbox.base_path import DiscoverablePaths
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "refresh_proj", template="full")
        (project.src.models / "v2").mkdir()
        project.expand(2)
        assert isinstance(project.src.models.v2, DiscoverablePaths)

    def test_src_expand_does_not_break_standard_attrs(self, tmp_path):
        """Standard attrs (data, features, …) stay accessible after expand()."""
        from mydropbox.project.projects import create_project

        project = create_project(tmp_path, "attrs_proj", template="full")
        project.src.expand(1)
        # Standard subdirs should still resolve correctly
        assert project.src.models.exists()
        assert project.src.features.exists()
