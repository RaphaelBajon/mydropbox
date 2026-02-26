# MyDropbox Configuration Template
# Copy this file to your home directory or project directory and customize it

"""
Configuration for MyDropbox library.

This file allows you to set your personal folder name without exposing it in Git.
"""

# Your personal folder name within the group Dropbox
# Example: "John Doe", "Jane Smith", etc.
PERSONAL_FOLDER = ""

# Optional: Custom Dropbox base path (usually auto-detected)
DROPBOX_BASE_PATH = None

# Usage in your scripts:
# ----------------------
# Option 1: Import from config
# from mydropbox_config import PERSONAL_FOLDER
# from mydropbox import get_dropbox
# db = get_dropbox(personal_folder=PERSONAL_FOLDER)

# Option 2: Set directly in your scripts
# from mydropbox import get_dropbox
# db = get_dropbox(personal_folder="Your Name")

# Option 3: Use environment variable
# import os
# from mydropbox import get_dropbox
# db = get_dropbox(personal_folder=os.getenv("DROPBOX_PERSONAL_FOLDER"))
