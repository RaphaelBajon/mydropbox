from pathlib import Path
from typing import Optional
import os
import warnings

from .group_path import GroupPaths
from .personal_path import PersonalPaths
from ..config.loadconfig import load_config

# Root of the lab PC mount. Personal Dropbox folders live at
# ``_LAB_MOUNT_ROOT / <username> / "UHM_Ocean_BGC_Group Dropbox" / <Personal Folder Name>``,
# a sibling of ``group_data`` (which holds the shared group Dropbox).
_LAB_MOUNT_ROOT = Path("/mnt/md0")


def _raise_auto_identify_mismatch(parent_dir: Path, resolved_name: str):
    try:
        existing = sorted(p.name for p in parent_dir.iterdir() if p.is_dir())
    except OSError:
        existing = []
    raise RuntimeError(
        f"auto_identify resolved your Dropbox account name to '{resolved_name}', but no "
        f"folder with that exact name exists under '{parent_dir}'. Existing folders: "
        f"{existing}. If your account name differs from your folder name, pass "
        "personal_folder= explicitly instead of auto_identify=True."
    )


class DropboxPaths:
    """
    Main class for accessing Dropbox folder paths.

    Attributes:
        base_path: Root path to the Dropbox folder
        group: Access to group shared folders
        personal: Access to personal folders (if personal_folder is specified)
    """

    def __init__(self, base_path: Optional[str] = None, personal_folder: Optional[str] = None,
                 group_depth: Optional[int] = 2, personal_depth: Optional[int] = 2,
                 auto_identify: bool = False):
        """
        Initialize Dropbox paths.

        Args:
            base_path: Custom base path to Dropbox. If None, tries to auto-detect
                      or uses ~/Dropbox/UHM_Ocean_BGC_Group Dropbox
            personal_folder: Name of your personal folder within the group Dropbox.
                           If None, personal paths will not be initialized (unless
                           auto_identify resolves one). Example: "John Doe", etc.
            group_depth: How many directory levels to discover eagerly under
                        ``db.group``.  1 = immediate children only (fastest);
                        2 = children + grandchildren (default);  None = full tree.
            personal_depth: Same as ``group_depth`` but for ``db.personal``.
            auto_identify: If True and personal_folder wasn't given, resolve it
                          automatically via the Dropbox SDK (requires
                          ``pip install mydropbox[sdk]`` and MYDROPBOX_SDK_TOKEN).
                          No-op if personal_folder was already provided. See
                          ``mydropbox.identify`` / docs/DROPBOX_SDK_SETUP.md.
        """
        auto_identified = False
        if personal_folder is None and auto_identify:
            from ..identify import resolve_personal_folder
            personal_folder = resolve_personal_folder()
            auto_identified = True

        self._base_path_found = False
        if base_path is None:
            # Try common Dropbox locations
            possible_paths = [
                # personal computer options
                Path.home() / "UHM_Ocean_BGC_Group Dropbox",
                Path.home() / "Dropbox" / "UHM_Ocean_BGC_Group Dropbox",
                Path.home() / "Library" / "CloudStorage" / "Dropbox" / "UHM_Ocean_BGC_Group Dropbox",
                Path("/Users") / os.getenv("USER", "") / "Dropbox" / "UHM_Ocean_BGC_Group Dropbox",
                Path("/Users") / os.getenv("USER", "") / "UHM_Ocean_BGC_Group Dropbox",
                # labpc option
                Path("/mnt/md0/group_data/UHM_Ocean_BGC_Group Dropbox"),
            ]

            for path in possible_paths:
                if path.exists():
                    self.base_path = path
                    self._base_path_found = True
                    break
            else:
                # Default fallback
                self.base_path = Path.home() / "Dropbox" / "UHM_Ocean_BGC_Group Dropbox"
                warnings.warn(
                    "Could not auto-detect the Dropbox base path. Checked: "
                    f"{[str(p) for p in possible_paths]}. Falling back to "
                    f"'{self.base_path}', which may not exist. Pass base_path= "
                    "explicitly, or set MYDROPBOX_BASE_PATH / ~/.mydropbox.yaml.",
                    stacklevel=2,
                )
        else:
            self.base_path = Path(base_path)

        # Initialize group paths (always available)
        self.group = GroupPaths(self.base_path, max_depth=group_depth)

        self._configure_for_labpc = self.base_path.is_relative_to(_LAB_MOUNT_ROOT)
        self._configure_for_persopc = not self._configure_for_labpc

        # Initialize personal paths only if personal_folder is specified
        if personal_folder is not None and self._configure_for_persopc:
            personal_path = self.base_path / personal_folder
            if auto_identified and not personal_path.exists():
                _raise_auto_identify_mismatch(self.base_path, personal_folder)
            self.personal = PersonalPaths(personal_path, max_depth=personal_depth)
        elif personal_folder is not None and self._configure_for_labpc:
            # On labpc, personal folders are a sibling of group_data:
            # /mnt/md0/<username>/UHM_Ocean_BGC_Group Dropbox/<Personal Folder Name>
            labpc_users = load_config().get("labpc_users", {})
            if personal_folder not in labpc_users:
                raise ValueError(
                    f"No labpc username configured for personal_folder='{personal_folder}'. "
                    f"Known names: {sorted(labpc_users)}. Add yourself to the 'labpc_users' "
                    "section of ~/.mydropbox.yaml (or the package config.yaml)."
                )
            username = labpc_users[personal_folder]
            personal_path = (
                self.base_path.parent.parent / username / "UHM_Ocean_BGC_Group Dropbox" / personal_folder
            )
            if auto_identified and not personal_path.exists():
                _raise_auto_identify_mismatch(personal_path.parent, personal_folder)
            self.personal = PersonalPaths(personal_path, max_depth=personal_depth)
        else:
            self.personal = None

    def __repr__(self):
        personal_info = f", personal_folder='{self.personal}'" if self.personal else ""
        return f"DropboxPaths(base_path='{self.base_path}'{personal_info})"


# Convenience function for quick access
def get_dropbox(base_path: Optional[str] = None, personal_folder: Optional[str] = None,
                group_depth: Optional[int] = 2, personal_depth: Optional[int] = 2,
                auto_identify: bool = False) -> DropboxPaths:
    """
    Convenience function to get a DropboxPaths instance.

    Args:
        base_path: Optional custom base path.
        personal_folder: Name of your personal folder (e.g., "Your Name").
        group_depth: Levels of subdirectories to discover under ``db.group``.
                     1 = immediate children (fastest); 2 = default; None = full tree.
        personal_depth: Same as ``group_depth`` but for ``db.personal``.
        auto_identify: If True and personal_folder wasn't given, resolve it via
                       the Dropbox SDK instead. See docs/DROPBOX_SDK_SETUP.md.

    Returns:
        DropboxPaths instance

    Example:
        >>> db = get_dropbox(personal_folder="John Doe")
        >>> db = get_dropbox(personal_folder="John Doe", group_depth=1, personal_depth=3)
        >>> db = get_dropbox(auto_identify=True)  # personal_folder resolved via Dropbox SDK
    """
    return DropboxPaths(
        base_path, personal_folder, group_depth=group_depth, personal_depth=personal_depth,
        auto_identify=auto_identify,
    )
