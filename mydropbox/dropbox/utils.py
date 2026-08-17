"""
Utility functions for MyDropbox.

Includes functions for checking Dropbox sync status, auto-discovering paths,
and converting folders to project structures.
"""

from pathlib import Path
from typing import Union, Optional, List, Dict, Any
import subprocess
import platform
import os


def check_sync_status(path: Union[str, Path], download_if_online: bool = False) -> Dict[str, Any]:
    """
    Check if a file or folder is synced locally or online-only in Dropbox.
    
    This function checks the Dropbox sync status and optionally downloads
    online-only files/folders.
    
    Args:
        path: Path to file or folder to check
        download_if_online: If True, attempt to download online-only content
        
    Returns:
        Dictionary with status information:
        {
            'path': Path object,
            'exists_locally': bool,
            'is_synced': bool,  # True if fully synced locally
            'is_online_only': bool,  # True if online-only (not downloaded)
            'is_syncing': bool,  # True if currently syncing
            'error': str or None,  # Error message if check failed
            'downloaded': bool,  # True if download was triggered
        }
    
    Notes:
        - **Downloading** (``download_if_online=True``) works automatically on
          macOS via ``NSFileCoordinator`` and on Linux via a plain file open.
        - **Evicting back to online-only** is NOT possible programmatically.
          Dropbox does not expose a public API for this.  Use Finder:
          right-click the file → Dropbox → Online only.
        - **Empty directories** always report ``is_synced=True``.  There are
          no files inside to mark as online-only, so the concept does not
          apply — an empty folder has nothing to download.

    Example:
        >>> status = check_sync_status(dropbox.personal.datasets / "large_file.nc")
        >>> if status['is_online_only']:
        ...     print("File is online-only, downloading...")
        ...     check_sync_status(path, download_if_online=True)
    """
    path = Path(path)
    
    result = {
        'path': path,
        'exists_locally': False,
        'is_synced': False,
        'is_online_only': False,
        'is_syncing': False,
        'error': None,
        'downloaded': False,
    }
    
    # Check if path exists at all
    if not path.exists():
        result['error'] = "Path does not exist"
        return result

    result['exists_locally'] = True

    try:
        # Try the Dropbox CLI first — most accurate source of truth
        cli_result = _check_sync_via_cli(path)
        if cli_result is not None:
            result.update(cli_result)
        else:
            # Fall back to OS-level heuristics
            result.update(_check_sync_sparse(path))

        # Trigger download if requested
        if download_if_online and result['is_online_only']:
            success = _trigger_download(path)
            result['downloaded'] = success
            if success:
                result['is_syncing'] = True
                result['is_online_only'] = False

    except Exception as e:
        result['error'] = str(e)

    return result


# Dropbox CLI locations to try in order
_DROPBOX_CLI_CANDIDATES = [
    "dropbox",  # in PATH
    os.path.expanduser("~/.dropbox-dist/dropboxd"),
    "/Applications/Dropbox.app/Contents/MacOS/dropbox",
    "/usr/local/bin/dropbox",
    "/usr/bin/dropbox",
]

# Linux-only CLI candidates for evict_to_online_only
_LINUX_CLI_CANDIDATES = [
    "dropbox",
    os.path.expanduser("~/.dropbox-dist/dropboxd"),
    "/usr/local/bin/dropbox",
    "/usr/bin/dropbox",
]


def _check_sync_via_cli(path: Path) -> Optional[Dict[str, bool]]:
    """Try ``dropbox filestatus <path>`` and parse the output.

    Returns a status dict only when the CLI is available **and** returns a
    recognised status string.  Returns ``None`` in all other cases so the
    caller falls back to sparse-file detection.

    Known Dropbox CLI statuses: "up to date", "syncing", "sync error",
    "unwatched", "selective sync excluded", "online only".
    """
    _KNOWN_STATUSES = {
        "up to date", "syncing", "sync error",
        "unwatched", "selective sync excluded", "online only",
    }

    for cli in _DROPBOX_CLI_CANDIDATES:
        try:
            proc = subprocess.run(
                [cli, "filestatus", str(path)],
                capture_output=True, text=True, timeout=5,
            )
            if proc.returncode != 0:
                continue
            # Output: "/path/to/file: up to date\n"
            raw = proc.stdout.strip().lower()
            # Strip the path prefix (everything up to and including the last colon)
            status = raw.split(":", maxsplit=1)[-1].strip()
            if status not in _KNOWN_STATUSES:
                # Binary exists but gave unrecognised/empty output — not a
                # proper Dropbox CLI; try the next candidate.
                continue
            return {
                'is_synced': status == "up to date",
                'is_online_only': "online" in status,
                'is_syncing': status == "syncing",
            }
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError, PermissionError):
            continue
    return None


def _has_dropbox_placeholder_xattr(path: Path) -> bool:
    """Return True if ``path`` has the ``com.dropbox.placeholder`` xattr.

    Dropbox sets this xattr on every file that is online-only (Smart Sync).
    It is typically NOT set on directories — individual files inside are
    marked instead.  An empty directory will always return False here.

    Uses ctypes to call the macOS ``getxattr(2)`` syscall directly; returns
    False on any error.
    """
    try:
        import ctypes, ctypes.util
        _libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)
        path_b = str(path).encode("utf-8", errors="surrogateescape")
        attr_b = b"com.dropbox.placeholder"
        result = _libc.getxattr(path_b, attr_b, None, 0, 0, 0)
        return result >= 0
    except Exception:
        return False


def _check_sync_sparse(path: Path) -> Dict[str, bool]:
    """Detect online-only paths via OS-level heuristics (macOS + Linux).

    macOS (Dropbox Smart Sync / File Provider)
    ------------------------------------------
    Dropbox sets the ``com.dropbox.placeholder`` extended attribute on every
    file that has not been downloaded locally.  Directories never get this
    xattr directly; to detect whether a directory's contents are online-only,
    we scan its immediate file children for the placeholder xattr.

    Note: ``SF_DATALESS`` and ``st_blocks == 0`` are NOT reliable on macOS
    APFS — the File Provider extension does not consistently set them.

    Linux (legacy Smart Sync)
    -------------------------
    Online-only files appear as sparse placeholders: ``st_size > 0`` but
    ``st_blocks == 0`` (no disk blocks allocated).  Directories cannot be
    detected without the CLI.

    Detecting *currently syncing* is not possible without the CLI.
    """
    try:
        if platform.system() == "Darwin":
            if path.is_file():
                is_online_only = _has_dropbox_placeholder_xattr(path)
            else:
                # Check the directory itself first (rare but possible),
                # then fall back to scanning immediate file children.
                # An empty directory has no files to mark as placeholders
                # so it will always report is_online_only=False — this is
                # correct: there is no content to download.
                if _has_dropbox_placeholder_xattr(path):
                    is_online_only = True
                else:
                    # Recursively scan all file descendants for placeholder xattr.
                    # An empty directory (or one with no files) always returns False.
                    is_online_only = any(
                        _has_dropbox_placeholder_xattr(child)
                        for child in path.rglob("*")
                        if child.is_file() and not child.name.startswith('.')
                    )
        elif path.is_file():
            # Linux: sparse-file heuristic; st_blocks is in 512-byte units
            st = path.stat()
            is_online_only = st.st_size > 0 and st.st_blocks == 0
        else:
            # Linux directories: recursively scan file descendants
            is_online_only = any(
                (f.stat().st_size > 0 and f.stat().st_blocks == 0)
                for f in path.rglob("*")
                if f.is_file() and not f.name.startswith('.')
            )

        return {
            'is_synced': not is_online_only,
            'is_online_only': is_online_only,
            'is_syncing': False,
        }
    except Exception:
        return _check_sync_fallback(path)


def _check_sync_fallback(path: Path) -> Dict[str, bool]:
    """Last-resort fallback: try to read the file to confirm it is local."""
    try:
        if path.is_file():
            with open(path, 'rb') as f:
                f.read(1)
        else:
            next(path.iterdir(), None)
        return {'is_synced': True, 'is_online_only': False, 'is_syncing': False}
    except (OSError, PermissionError):
        return {'is_synced': False, 'is_online_only': True, 'is_syncing': False}


def _trigger_download(path: Path) -> bool:
    """Trigger Dropbox Smart Sync download of an online-only path.

    On macOS, the correct way to hydrate a File Provider placeholder is via
    ``NSFileCoordinator`` — a coordinated read signals the File Provider
    extension to fetch the content.  Plain ``open()`` / ``read()`` bypasses
    the coordination layer and does NOT reliably hydrate placeholders.

    We invoke a tiny Swift one-liner via ``subprocess`` so we don't need
    PyObjC.  On Linux (legacy Smart Sync), a plain ``open()`` is sufficient
    because there is no File Provider layer.

    For directories, every immediate file child is triggered individually.
    Returns ``True`` if the trigger call succeeded without error.
    """
    if platform.system() == "Darwin":
        return _trigger_download_macos(path)

    # Linux: plain read, rglob for directories
    try:
        if path.is_file():
            with open(path, 'rb') as f:
                f.read(1)
        elif path.is_dir():
            for child in path.rglob("*"):
                try:
                    if child.is_file() and not child.name.startswith('.'):
                        with open(child, 'rb') as f:
                            f.read(1)
                except OSError:
                    pass
        return True
    except Exception:
        return False


def _trigger_download_macos(path: Path) -> bool:
    """Use NSFileCoordinator via a Swift subprocess to hydrate a placeholder.

    NSFileCoordinator is the macOS-sanctioned API for triggering File Provider
    downloads.  A coordinated read on a **file** causes the File Provider to
    fetch its content.  For **directories**, coordinating a read on the
    directory itself only retrieves the listing — the individual files inside
    must each be coordinated separately to actually hydrate them.
    """
    if path.is_dir():
        # Recursively collect all placeholder files under the directory
        children = [
            child for child in path.rglob("*")
            if child.is_file()
            and not child.name.startswith('.')
            and _has_dropbox_placeholder_xattr(child)
        ]
        if not children:
            return True  # nothing to download
        # Build a Swift snippet that coordinates a read on each file in turn
        paths_literal = "\n".join(f'    "{str(c)}",' for c in children)
        swift_code = f"""
import Foundation
let paths: [String] = [
{paths_literal}
]
for p in paths {{
    let url = URL(fileURLWithPath: p)
    let coordinator = NSFileCoordinator()
    var err: NSError?
    coordinator.coordinate(readingItemAt: url, options: .withoutChanges, error: &err) {{ u in
        _ = try? Data(contentsOf: u)
    }}
}}
"""
    else:
        # Single file
        swift_code = f"""
import Foundation
let url = URL(fileURLWithPath: "{str(path)}")
let coordinator = NSFileCoordinator()
var err: NSError?
coordinator.coordinate(readingItemAt: url, options: .withoutChanges, error: &err) {{ u in
    _ = try? Data(contentsOf: u)
}}
"""
    try:
        result = subprocess.run(
            ["swift", "-e", swift_code],
            capture_output=True, text=True, timeout=60,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        # swift not available — fall back to plain open
        try:
            if path.is_file():
                with open(path, 'rb') as f:
                    f.read(1)
            elif path.is_dir():
                for child in path.iterdir():
                    try:
                        if child.is_file():
                            with open(child, 'rb') as f:
                                f.read(1)
                    except OSError:
                        pass
            return True
        except Exception:
            return False


def evict_to_online_only(path: Union[str, Path]) -> bool:
    """Evict a locally-synced file or folder back to online-only (Smart Sync).

    **Linux only** — uses the Dropbox CLI ``dropbox smart-sync online-only``
    command which is available in the Linux Dropbox desktop client.

    **macOS** — Dropbox does not register as an Apple File Provider domain
    and exposes no public eviction API.  Use Finder instead:
    right-click → Dropbox → Online only.

    Args:
        path: File or folder to evict.

    Returns:
        ``True`` if the eviction command succeeded, ``False`` otherwise.

    Raises:
        NotImplementedError: On macOS, where programmatic eviction is not
            supported.
        FileNotFoundError: If the Dropbox CLI is not found on Linux.
    """
    path = Path(path)
    system = platform.system()

    if system == "Darwin":
        raise NotImplementedError(
            "Programmatic eviction is not supported on macOS. "
            "Use Finder: right-click the file → Dropbox → Online only."
        )

    if system != "Linux":
        raise NotImplementedError(f"evict_to_online_only is not supported on {system}.")

    # Linux: Dropbox CLI supports 'dropbox smart-sync online-only <path>'
    for cli in _LINUX_CLI_CANDIDATES:
        try:
            result = subprocess.run(
                [cli, "smart-sync", "online-only", str(path)],
                capture_output=True, text=True, timeout=15,
            )
            if result.returncode == 0:
                return True
            # Some versions use positional order: path first, then mode
            result2 = subprocess.run(
                [cli, "smart-sync", str(path), "online-only"],
                capture_output=True, text=True, timeout=15,
            )
            return result2.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            continue

    raise FileNotFoundError(
        "Dropbox CLI not found. Install the Dropbox desktop client and ensure "
        "'dropbox' is in your PATH."
    )


def auto_discover_paths(base_path: Union[str, Path], max_depth: int = 2) -> Dict[str, Path]:
    """
    Automatically discover all subdirectories and create path attributes.
    
    This function scans a directory and returns a dictionary of all subdirectories,
    converting folder names to valid Python attribute names.
    
    Args:
        base_path: Root directory to scan
        max_depth: Maximum depth to scan (default: 2)
                  1 = immediate children only
                  2 = children and grandchildren
                  
    Returns:
        Dictionary mapping attribute names to Path objects
        
    Example:
        >>> paths = auto_discover_paths(dropbox.group.base)
        >>> # Returns: {
        >>> #   'assorted_content': Path('.../Assorted content'),
        >>> #   'datasets': Path('.../Datasets'),
        >>> #   'group_notes': Path('.../Group_notes'),
        >>> # }
        
        >>> # Can be used to dynamically create attributes:
        >>> for name, path in paths.items():
        ...     setattr(my_object, name, path)
    """
    base_path = Path(base_path)
    discovered = {}
    
    if not base_path.exists() or not base_path.is_dir():
        return discovered
    
    def _scan_directory(directory: Path, current_depth: int = 1):
        """Recursively scan directory up to max_depth."""
        if current_depth > max_depth:
            return
        
        try:
            for item in directory.iterdir():
                if item.name.startswith('.'):
                    continue
                # Convert name to a valid Python identifier.
                # Dots in file extensions become underscores, e.g.
                # "cruise_2025.nc" -> "cruise_2025_nc".
                attr_name = _path_to_attribute_name(item.name)

                # Store path (files and directories alike)
                discovered[attr_name] = item

                # Recurse into directories if not at max depth
                if item.is_dir() and current_depth < max_depth:
                    _scan_directory(item, current_depth + 1)
                        
        except PermissionError:
            # Skip directories we can't access
            pass
    
    _scan_directory(base_path)
    return discovered


def _path_to_attribute_name(name: str) -> str:
    """
    Convert a folder name to a valid Python attribute name.
    
    Rules:
    - Convert spaces to underscores
    - Convert to lowercase
    - Remove special characters
    - Ensure it doesn't start with a number
    
    Examples:
        "Assorted content" -> "assorted_content"
        "Lab_Field_Data" -> "lab_field_data"
        "2023_06 SeAjusted pCO2" -> "seajusted_pco2_2023_06"
    """
    # Convert to lowercase
    name = name.lower()
    
    # Replace spaces and special chars with underscore
    name = name.replace(' ', '_')
    name = name.replace('-', '_')
    name = ''.join(c if c.isalnum() or c == '_' else '_' for c in name)
    
    # Remove multiple consecutive underscores
    while '__' in name:
        name = name.replace('__', '_')
    
    # Remove leading/trailing underscores
    name = name.strip('_')
    
    # If starts with a digit, prefix with 'num_' so the name is a valid
    # Python identifier while still hinting at the original folder name.
    # e.g. "2025_cruise" → "num_2025_cruise", "01_analysis" → "num_01_analysis"
    if name and name[0].isdigit():
        name = 'num_' + name

    return name


def create_dynamic_path_class(base_path: Union[str, Path], 
                              class_name: str = "DynamicPaths",
                              max_depth: int = 2):
    """
    Create a dynamic path class with auto-discovered attributes.
    
    This is useful when you want to access folders like:
    >>> paths = create_dynamic_path_class(some_folder)
    >>> paths.subfolder1.subfolder2
    
    Args:
        base_path: Root directory
        class_name: Name for the generated class
        max_depth: How deep to scan
        
    Returns:
        Class instance with discovered paths as attributes
        
    Example:
        >>> group = create_dynamic_path_class(dropbox.group.base, "GroupPaths")
        >>> group.datasets
        >>> group.collaborative_projects
    """
    base_path = Path(base_path)
    discovered = auto_discover_paths(base_path, max_depth=max_depth)
    
    # Create a dynamic class
    class DynamicPaths:
        def __init__(self):
            self.base = base_path
            
            # Add all discovered paths as attributes
            for attr_name, path in discovered.items():
                setattr(self, attr_name, path)
        
        def __repr__(self):
            return f"{class_name}(base='{self.base}')"
        
        def list_paths(self) -> List[str]:
            """List all available path attributes."""
            return [attr for attr in dir(self) 
                   if not attr.startswith('_') and attr != 'base' and attr != 'list_paths']
    
    # Change class name
    DynamicPaths.__name__ = class_name
    DynamicPaths.__qualname__ = class_name
    
    return DynamicPaths()


def convert_to_project(folder_path: Union[str, Path], 
                       template: str = "full",
                       auto_discover: bool = True) -> 'ProjectPaths':
    """
    Convert an existing folder into a ProjectPaths instance.
    
    This function takes any folder and treats it as a project, optionally
    creating missing structure and auto-discovering existing folders.
    
    Args:
        folder_path: Path to the folder to convert
        template: Project template to use if creating structure
                 ("full", "simple", "minimal")
        auto_discover: If True, auto-discover existing subfolders and add them
                      as attributes to the project
                      
    Returns:
        ProjectPaths instance
        
    Example:
        >>> # Convert an existing folder to a project
        >>> project = convert_to_project(
        ...     dropbox.personal.projects / "my_old_analysis",
        ...     template="simple",
        ...     auto_discover=True
        ... )
        >>> 
        >>> # Now access standard paths
        >>> project.data.raw
        >>> 
        >>> # AND any existing subfolders that were discovered
        >>> project.results_2025  # If "results_2025" folder exists
        >>> project.old_notebooks  # If "old_notebooks" folder exists
    """
    from .projects import ProjectPaths
    
    folder_path = Path(folder_path)
    
    # Create ProjectPaths instance
    project = ProjectPaths(folder_path, auto_create=False)
    
    # Create standard structure if folders don't exist
    if template:
        project.create_structure(template=template)
    
    # Auto-discover additional folders if requested
    if auto_discover:
        discovered = auto_discover_paths(folder_path, max_depth=1)
        
        # Add discovered paths as attributes (avoid overwriting existing ones)
        for attr_name, path in discovered.items():
            if not hasattr(project, attr_name):
                setattr(project, attr_name, path)
    
    return project


if __name__ == "__main__":
    # Demo
    print("=" * 60)
    print("MyDropbox Utility Functions Demo")
    print("=" * 60)
    
    from pathlib import Path
    import tempfile
    
    # Demo 1: Check sync status
    print("\n1. Check Sync Status")
    print("-" * 60)
    test_path = Path.home() / "Desktop"
    if test_path.exists():
        status = check_sync_status(test_path)
        print(f"Path: {status['path']}")
        print(f"Exists locally: {status['exists_locally']}")
        print(f"Is synced: {status['is_synced']}")
        print(f"Is online-only: {status['is_online_only']}")
    
    # Demo 2: Auto-discover paths
    print("\n2. Auto-Discover Paths")
    print("-" * 60)
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        (base / "folder1").mkdir()
        (base / "folder2").mkdir()
        (base / "Special Folder Name").mkdir()
        
        discovered = auto_discover_paths(base)
        print(f"Discovered {len(discovered)} folders:")
        for name, path in discovered.items():
            print(f"  {name} -> {path.name}")
    
    # Demo 3: Dynamic path class
    print("\n3. Create Dynamic Path Class")
    print("-" * 60)
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        (base / "data").mkdir()
        (base / "results").mkdir()
        (base / "plots").mkdir()
        
        paths = create_dynamic_path_class(base, "MyPaths")
        print(f"Created: {paths}")
        print(f"Available paths: {paths.list_paths()}")
        print(f"Access like: paths.{paths.list_paths()[0] if paths.list_paths() else 'data'}")
    
    print("\n" + "=" * 60)
