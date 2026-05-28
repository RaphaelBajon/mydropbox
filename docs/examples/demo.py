"""
MyDropbox interactive demo.

Run with:
    python docs/examples/demo.py
"""

from mydropbox import get_dropbox

print("MyDropbox Library Demo")
print("=" * 50)

# Example 1: Group-only access
print("\n--- Example 1: Group Access Only ---")
db_group = get_dropbox()
print(f"Base path: {db_group.base_path}")
print(f"Group datasets: {db_group.group.datasets}")
print(f"Personal paths available: {db_group.personal is not None}")

# Example 2: With personal folder
print("\n--- Example 2: With Personal Folder ---")
personal_name = input("Enter your personal folder name in the shared Dropbox: ")
db = get_dropbox(personal_folder=personal_name)
print(f"Base path: {db.base_path}")

print("\n--- Group Paths ---")
print(f"Datasets:    {db.group.datasets}")
print(f"Group notes: {db.group.group_notes}")

if db.personal:
    print("\n--- Personal Paths ---")
    for name, path in db.personal.get_all_paths().items():
        print(f"  {name}: {path}")
