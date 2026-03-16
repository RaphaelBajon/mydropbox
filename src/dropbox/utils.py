"""
Utility functions for MyDropbox.

Includes functions for checking Dropbox sync status, auto-discovering paths,
and converting folders to project structures.
"""

from pathlib import Path
from typing import Union, Optional, List, Dict
import subprocess
import platform
import os


def check_sync_status(path: Union[str, Path], download_if_online: bool = False) -> Dict[str, any]:
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
    
    # Get platform-specific Dropbox attributes
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            # Check extended attributes for Dropbox status
            result.update(_check_sync_macos(path))
            
        elif system == "Windows":
            # Check file attributes on Windows
            result.update(_check_sync_windows(path))
            
        elif system == "Linux":
            # Check extended attributes on Linux
            result.update(_check_sync_linux(path))
            
        else:
            result['error'] = f"Unsupported platform: {system}"
            return result
        
        # If download requested and file is online-only, trigger download
        if download_if_online and result['is_online_only']:
            success = _trigger_download(path)
            result['downloaded'] = success
            if success:
                result['is_syncing'] = True
                result['is_online_only'] = False
                
    except Exception as e:
        result['error'] = str(e)
    
    return result


def _check_sync_macos(path: Path) -> Dict[str, bool]:
    """Check Dropbox sync status on macOS using xattr."""
    try:
        import xattr
        
        # Dropbox uses extended attributes to mark file status
        # com.dropbox.attributes contains sync status
        attrs = xattr.xattr(path)
        
        # Check for Dropbox-specific attributes
        dropbox_attrs = [attr for attr in attrs if b'dropbox' in attr.lower()]
        
        # If file has content, it's synced
        # Online-only files have minimal local presence
        if path.is_file():
            size = path.stat().st_size
            # Files < 1KB are likely placeholders (online-only)
            is_online_only = size < 1024 and len(dropbox_attrs) > 0
        else:
            # For directories, check if children are accessible
            is_online_only = False
            
        return {
            'is_synced': not is_online_only,
            'is_online_only': is_online_only,
            'is_syncing': False,
        }
        
    except ImportError:
        # xattr not available, fall back to file size check
        return _check_sync_fallback(path)
    except Exception:
        return _check_sync_fallback(path)


def _check_sync_windows(path: Path) -> Dict[str, bool]:
    """Check Dropbox sync status on Windows."""
    try:
        import win32api
        import win32con
        
        # Get file attributes
        attrs = win32api.GetFileAttributes(str(path))
        
        # Check for offline/sparse file attributes
        is_online_only = bool(attrs & win32con.FILE_ATTRIBUTE_OFFLINE)
        
        return {
            'is_synced': not is_online_only,
            'is_online_only': is_online_only,
            'is_syncing': False,
        }
        
    except ImportError:
        # win32api not available, fall back
        return _check_sync_fallback(path)
    except Exception:
        return _check_sync_fallback(path)


def _check_sync_linux(path: Path) -> Dict[str, bool]:
    """Check Dropbox sync status on Linux using extended attributes."""
    try:
        import xattr
        
        attrs = xattr.xattr(path)
        dropbox_attrs = [attr for attr in attrs if b'dropbox' in attr.lower()]
        
        # Similar logic to macOS
        if path.is_file():
            size = path.stat().st_size
            is_online_only = size < 1024 and len(dropbox_attrs) > 0
        else:
            is_online_only = False
            
        return {
            'is_synced': not is_online_only,
            'is_online_only': is_online_only,
            'is_syncing': False,
        }
        
    except ImportError:
        return _check_sync_fallback(path)
    except Exception:
        return _check_sync_fallback(path)


def _check_sync_fallback(path: Path) -> Dict[str, bool]:
    """
    Fallback sync check when platform-specific methods unavailable.
    Uses heuristics based on file size and accessibility.
    """
    try:
        if path.is_file():
            # Try to read first byte to ensure file is accessible
            with open(path, 'rb') as f:
                f.read(1)
            is_synced = True
        else:
            # For directories, check if we can list contents
            list(path.iterdir())
            is_synced = True
            
        return {
            'is_synced': is_synced,
            'is_online_only': False,
            'is_syncing': False,
        }
        
    except (OSError, PermissionError):
        # If we can't access it, assume online-only
        return {
            'is_synced': False,
            'is_online_only': True,
            'is_syncing': False,
        }


def _trigger_download(path: Path) -> bool:
    """
    Trigger download of online-only file/folder.
    
    Returns:
        True if download triggered successfully, False otherwise
    """
    try:
        # On most systems, simply accessing the file triggers download
        if path.is_file():
            # Open file to trigger sync
            with open(path, 'rb') as f:
                f.read(1)
        else:
            # For directories, list contents to trigger sync
            list(path.iterdir())
        
        return True
        
    except Exception:
        return False


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
                if item.is_dir():
                    # Convert folder name to valid attribute name
                    attr_name = _path_to_attribute_name(item.name)
                    
                    # Store path
                    discovered[attr_name] = item
                    
                    # Recurse if not at max depth
                    if current_depth < max_depth:
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
    
    # If starts with number, move it to end
    if name and name[0].isdigit():
        # Find where numbers end
        i = 0
        while i < len(name) and name[i].isdigit():
            i += 1
        if i < len(name):
            name = name[i:] + '_' + name[:i]
        else:
            name = 'folder_' + name
    
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
