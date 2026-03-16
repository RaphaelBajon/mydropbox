"""
Group paths module for MyDropbox.

Manages paths to shared group folders within the Dropbox.
"""

from pathlib import Path
from typing import Dict
import os


class GroupPaths:
    """
    Access to group shared folders.
    
    This class wraps a Path object and automatically discovers all subdirectories,
    making them accessible as attributes. Behaves like a Path through delegation.
    """
    
    def __init__(self, base_path):
        """
        Initialize group paths with auto-discovery.
        
        Args:
            base_path: Base path to the group Dropbox folder
        """
        # Store the path
        self._path = Path(base_path)
        
        # Auto-discover all folders
        self._discover_all_paths()
    
    def _discover_all_paths(self):
        """Automatically discover and add all subdirectories as attributes."""
        from .utils import auto_discover_paths
        
        # Discover all folders (only immediate children, depth=1)
        discovered = auto_discover_paths(self._path, max_depth=1)
        
        # Add all paths as attributes
        for attr_name, path in discovered.items():
            setattr(self, attr_name, path)
    
    def get_all_paths(self) -> Dict[str, Path]:
        """
        Get all available paths as a dictionary.
        
        Returns:
            Dictionary mapping attribute names to Path objects
        """
        return {
            name: getattr(self, name)
            for name in dir(self)
            if not name.startswith('_') 
            and name != 'get_all_paths'
            and isinstance(getattr(self, name), Path)
        }
    
    # Delegate Path methods to self._path
    def __truediv__(self, other):
        """Support / operator: db.group / 'subfolder'"""
        return self._path / other
    
    def __str__(self):
        """String representation"""
        return str(self._path)
    
    def __repr__(self):
        num_paths = len(self.get_all_paths())
        return f"GroupPaths('{self._path}', {num_paths} folders)"
    
    def __fspath__(self):
        """Support os.PathLike protocol - allows use anywhere Path is expected"""
        return str(self._path)
    
    # Delegate common Path methods
    def exists(self):
        return self._path.exists()
    
    def is_dir(self):
        return self._path.is_dir()
    
    def is_file(self):
        return self._path.is_file()
    
    def iterdir(self):
        return self._path.iterdir()
    
    def glob(self, pattern):
        return self._path.glob(pattern)
    
    def rglob(self, pattern):
        return self._path.rglob(pattern)
    
    @property
    def name(self):
        return self._path.name
    
    @property
    def parent(self):
        return self._path.parent
    
    @property
    def stem(self):
        return self._path.stem
    
    @property
    def suffix(self):
        return self._path.suffix
    
    def mkdir(self, *args, **kwargs):
        return self._path.mkdir(*args, **kwargs)
    
    def rename(self, target):
        return self._path.rename(target)
    
    def resolve(self, *args, **kwargs):
        return self._path.resolve(*args, **kwargs)
    
    # Make it work like a Path in most contexts
    def __eq__(self, other):
        if isinstance(other, GroupPaths):
            return self._path == other._path
        return self._path == other
    
    def __hash__(self):
        return hash(self._path)