"""Tests for dropbox utility functions (dropbox/utils.py)."""

import importlib
import platform
import pytest

# Import via importlib to avoid the `dropbox = DropboxPaths(...)` instance in
# mydropbox/__init__.py shadowing the `mydropbox.dropbox` subpackage on Linux
# (where Python resolves attribute lookups on the package object rather than
# going through sys.modules when an editable install is active).
_utils = importlib.import_module("mydropbox.dropbox.utils")
check_sync_status = _utils.check_sync_status
evict_to_online_only = _utils.evict_to_online_only
auto_discover_paths = _utils.auto_discover_paths
_check_sync_sparse = _utils._check_sync_sparse


# ---------------------------------------------------------------------------
# Platform markers
# ---------------------------------------------------------------------------

macos_only = pytest.mark.skipif(
    platform.system() != "Darwin", reason="macOS-specific (com.dropbox.placeholder xattr)"
)
linux_only = pytest.mark.skipif(
    platform.system() != "Linux", reason="Linux-specific (sparse-file detection)"
)


# ---------------------------------------------------------------------------
# xattr helpers (macOS only)
# ---------------------------------------------------------------------------

def _xattr_libc():
    import ctypes, ctypes.util
    return ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)


def _set_placeholder_xattr(path):
    """Simulate an online-only file by setting com.dropbox.placeholder xattr."""
    libc = _xattr_libc()
    p = str(path).encode("utf-8", errors="surrogateescape")
    return libc.setxattr(p, b"com.dropbox.placeholder", b"\x00", 1, 0, 0) == 0


def _has_placeholder_xattr(path):
    libc = _xattr_libc()
    p = str(path).encode("utf-8", errors="surrogateescape")
    return libc.getxattr(p, b"com.dropbox.placeholder", None, 0, 0, 0) >= 0


def _remove_placeholder_xattr(path):
    libc = _xattr_libc()
    p = str(path).encode("utf-8", errors="surrogateescape")
    libc.removexattr(p, b"com.dropbox.placeholder", 0)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestCheckSyncStatus:

    # --- cross-platform basics ---

    def test_nonexistent_path(self, tmp_path):
        status = check_sync_status(tmp_path / "no_such_file.nc")
        assert status["exists_locally"] is False
        assert status["error"] is not None

    def test_existing_file_not_flagged_online_only(self, tmp_path):
        f = tmp_path / "real_file.txt"
        f.write_text("hello world")
        status = check_sync_status(f)
        assert status["exists_locally"] is True
        assert status["is_online_only"] is False

    def test_existing_directory(self, tmp_path):
        d = tmp_path / "mydir"
        d.mkdir()
        status = check_sync_status(d)
        assert status["exists_locally"] is True
        assert status["is_online_only"] is False

    # --- macOS: com.dropbox.placeholder xattr ---

    @macos_only
    def test_file_with_placeholder_xattr_is_online_only(self, tmp_path):
        """A file with com.dropbox.placeholder xattr must be detected as online-only."""
        f = tmp_path / "online_file.nc"
        f.write_bytes(b"")
        assert _set_placeholder_xattr(f), "setxattr failed"
        try:
            status = check_sync_status(f)
            assert status["is_online_only"] is True
            assert status["is_synced"] is False
        finally:
            _remove_placeholder_xattr(f)

    @macos_only
    def test_directory_with_placeholder_child_is_online_only(self, tmp_path):
        """A directory whose child has com.dropbox.placeholder must be online-only."""
        d = tmp_path / "online_dir"
        d.mkdir()
        f = d / "data.nc"
        f.write_bytes(b"")
        assert _set_placeholder_xattr(f), "setxattr failed"
        try:
            status = check_sync_status(d)
            assert status["is_online_only"] is True
            assert status["is_synced"] is False
        finally:
            _remove_placeholder_xattr(f)

    @macos_only
    def test_directory_with_placeholder_in_subdir(self, tmp_path):
        """Online-only detection must find placeholders in nested subdirectories."""
        d = tmp_path / "root_dir"
        sub = d / "subdir"
        sub.mkdir(parents=True)
        f = sub / "nested.nc"
        f.write_bytes(b"")
        assert _set_placeholder_xattr(f), "setxattr failed"
        try:
            status = check_sync_status(d)
            assert status["is_online_only"] is True
        finally:
            _remove_placeholder_xattr(f)

    @macos_only
    def test_empty_directory_is_always_synced(self, tmp_path):
        """An empty directory has no placeholders — must report is_synced=True."""
        d = tmp_path / "empty_dir"
        d.mkdir()
        status = check_sync_status(d)
        assert status["is_synced"] is True
        assert status["is_online_only"] is False

    @macos_only
    def test_download_if_online_triggers_coordinator(self, tmp_path):
        """download_if_online=True must invoke NSFileCoordinator and return downloaded=True.

        Note: the placeholder xattr is removed by the Dropbox daemon after it fetches
        content. In tmp_path (outside a Dropbox-watched folder) the daemon is not
        watching, so we only verify the trigger was invoked (downloaded=True).
        """
        f = tmp_path / "to_download.txt"
        f.write_text("content")
        assert _set_placeholder_xattr(f)
        try:
            status = check_sync_status(f, download_if_online=True)
            assert status["downloaded"] is True
            assert status["is_syncing"] is True
        finally:
            _remove_placeholder_xattr(f)

    @macos_only
    def test_download_on_directory_triggers_all_files(self, tmp_path):
        """download_if_online=True on a directory must trigger all nested placeholder
        files and return downloaded=True.
        """
        d = tmp_path / "dl_dir"
        sub = d / "sub"
        sub.mkdir(parents=True)
        files = [d / "a.txt", sub / "b.txt"]
        for f in files:
            f.write_text("hi")
            assert _set_placeholder_xattr(f)
        try:
            status = check_sync_status(d, download_if_online=True)
            assert status["downloaded"] is True
            assert status["is_syncing"] is True
        finally:
            for f in files:
                _remove_placeholder_xattr(f)

    # --- Linux: sparse-file heuristic ---

    @linux_only
    def test_sparse_file_is_online_only(self, tmp_path):
        """On Linux, a sparse file (st_size>0, st_blocks==0) is online-only.
        Tests _check_sync_sparse directly to bypass the Dropbox CLI layer.
        """
        f = tmp_path / "sparse.nc"
        with open(f, "wb") as fh:
            fh.seek(4096)
            fh.truncate()
        if f.stat().st_blocks != 0:
            pytest.skip("Filesystem does not support sparse files")
        result = _check_sync_sparse(f)
        assert result["is_online_only"] is True

    @linux_only
    def test_sparse_file_in_subdir_makes_dir_online_only(self, tmp_path):
        """On Linux, a directory with a nested sparse file must be online-only.
        Tests _check_sync_sparse directly to bypass the Dropbox CLI layer.
        """
        d = tmp_path / "sparse_dir"
        sub = d / "sub"
        sub.mkdir(parents=True)
        f = sub / "sparse.nc"
        with open(f, "wb") as fh:
            fh.seek(4096)
            fh.truncate()
        if f.stat().st_blocks != 0:
            pytest.skip("Filesystem does not support sparse files")
        result = _check_sync_sparse(d)
        assert result["is_online_only"] is True

    @linux_only
    def test_download_if_online_triggers_plain_read(self, tmp_path):
        """On Linux, download_if_online=True must open the file and return downloaded=True.

        Patches both _check_sync_via_cli (so the CLI shortcut is bypassed) and
        _check_sync_sparse to simulate an online-only file without needing a
        real sparse file or an installed Dropbox CLI.
        """
        import unittest.mock as mock
        f = tmp_path / "data.nc"
        f.write_text("content")
        online_only = {"is_synced": False, "is_online_only": True, "is_syncing": False}
        with mock.patch.object(_utils, "_check_sync_via_cli", return_value=None), \
             mock.patch.object(_utils, "_check_sync_sparse", return_value=online_only):
            status = check_sync_status(f, download_if_online=True)
        assert status["downloaded"] is True


class TestEvictToOnlineOnly:

    @macos_only
    def test_raises_not_implemented_on_macos(self, tmp_path):
        """evict_to_online_only must raise NotImplementedError on macOS."""
        f = tmp_path / "file.txt"
        f.write_text("hi")
        with pytest.raises(NotImplementedError, match="macOS"):
            evict_to_online_only(f)

    @linux_only
    def test_raises_file_not_found_when_no_cli(self, tmp_path, monkeypatch):
        """On Linux without the Dropbox CLI, must raise FileNotFoundError."""
        monkeypatch.setattr(_utils, "_LINUX_CLI_CANDIDATES", ["/nonexistent/dropbox"])
        f = tmp_path / "file.txt"
        f.write_text("hi")
        with pytest.raises(FileNotFoundError, match="Dropbox CLI not found"):
            evict_to_online_only(f)


class TestAutoDiscoverPaths:

    def test_discovers_subdirs(self, tmp_dropbox):
        paths = auto_discover_paths(tmp_dropbox / "group", max_depth=1)
        assert "datasets" in paths
        assert "group_notes" in paths

    def test_discovers_files_and_dirs(self, tmp_path):
        """auto_discover_paths returns both files and directories."""
        (tmp_path / "subdir").mkdir()
        (tmp_path / "file.txt").write_text("data")
        paths = auto_discover_paths(tmp_path, max_depth=1)
        assert "subdir" in paths
        assert "file_txt" in paths   # dots become underscores

    def test_nonexistent_base_returns_empty(self, tmp_path):
        paths = auto_discover_paths(tmp_path / "no_such_dir", max_depth=1)
        assert paths == {}

    def test_snake_case_conversion(self, tmp_path):
        (tmp_path / "My Folder Name").mkdir()
        paths = auto_discover_paths(tmp_path, max_depth=1)
        assert "my_folder_name" in paths
