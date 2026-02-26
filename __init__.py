"""
MyDropbox - A library for managing UHM Ocean BGC Group Dropbox paths

This library provides easy access to commonly used paths in the research group's
Dropbox structure, making it easier to write portable and maintainable code.

Author: Raphaël Bajon
"""

__version__ = "0.1.0"
__author__ = "Raphaël Bajon"
__license__ = "MIT"

# Import project management
from .project import ProjectPaths, create_project
# Import dropbox management
from .dropbox import get_dropbox, DropboxPaths, PersonalPaths, GroupPaths
from .config.loadconfig import _load_config


__all__ = [
    "DropboxPaths",
    "ProjectPaths",
    "create_project",
    "get_dropbox",
    "GroupPaths",
    "PersonalPaths",
    "dropbox",
]


# Initialize default dropbox instance
_config = _load_config()
dropbox = get_dropbox(
    base_path=_config["base_path"],
    personal_folder=_config["personal_folder"]
)


if __name__ == "__main__":
    # Demo usage
    print("MyDropbox Library Demo")
    print("=" * 50)
    
    # Example 1: Group-only access (no personal folder specified)
    print("\n--- Example 1: Group Access Only ---")
    db_group = get_dropbox()
    print(f"Base path: {db_group.base_path}")
    print(f"Group datasets: {db_group.group.datasets}")
    print(f"Personal paths available: {db_group.personal is not None}")
    
    # Example 2: With personal folder
    print("\n--- Example 2: With Personal Folder ---")
    db = get_dropbox(personal_folder=str(input('Please enter your folder personal name of the shared dropbox path: ')))
    print(f"Base path: {db.base_path}")
    
    print("\n--- Group Paths ---")
    print(f"Datasets: {db.group.datasets}")
    print(f"Group notes: {db.group.group_notes}")
    
    if db.personal:
        print("\n--- Personal Paths ---")
        print(f"My code: {db.personal.mycode}")
        print(f"Datasets: {db.personal.datasets}")
        print(f"Projects: {db.personal.projects}")
        print(f"Papers: {db.personal.papers}")
    
    print("\n--- Usage Examples ---")
    print("# Import and use (group only):")
    print("from mydropbox import dropbox")
    print("shared_data = dropbox.group.datasets / 'observations.nc'")
    print("\n# With personal folder:")
    print("from mydropbox import get_dropbox")
    print("db = get_dropbox(personal_folder='Your Name')")
    print("my_data = db.personal.datasets / 'my_data.nc'")
    print("\n# Or set a default in your scripts:")
    print("db = get_dropbox(personal_folder='Your Name')")
    print("# Then use db throughout your code")
