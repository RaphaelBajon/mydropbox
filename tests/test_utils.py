"""Tests for dropbox utility functions (dropbox/utils.py)."""

import pytest


class TestCheckSyncStatus:
    def test_nonexistent_path(self, tmp_path):
        from mydropbox.dropbox.utils import check_sync_status

        status = check_sync_status(tmp_path / "no_such_file.nc")
        assert status["exists_locally"] is False
        assert status["error"] is not None

    def test_existing_file_not_flagged_online_only(self, tmp_path):
        from mydropbox.dropbox.utils import check_sync_status

        f = tmp_path / "real_file.txt"
        f.write_text("hello world")

        status = check_sync_status(f)
        assert status["exists_locally"] is True
        assert status["is_online_only"] is False

    def test_existing_directory(self, tmp_path):
        from mydropbox.dropbox.utils import check_sync_status

        d = tmp_path / "mydir"
        d.mkdir()

        status = check_sync_status(d)
        assert status["exists_locally"] is True
        assert status["is_online_only"] is False


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

    def test_nonexistent_base_returns_empty(self, tmp_path):
        from mydropbox.dropbox.utils import auto_discover_paths

        paths = auto_discover_paths(tmp_path / "no_such_dir", max_depth=1)
        assert paths == {}

    def test_snake_case_conversion(self, tmp_path):
        from mydropbox.dropbox.utils import auto_discover_paths

        (tmp_path / "My Folder Name").mkdir()
        paths = auto_discover_paths(tmp_path, max_depth=1)
        assert "my_folder_name" in paths
