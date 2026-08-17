"""Optional Dropbox-API-based identity resolution.

Used by ``get_dropbox(auto_identify=True)`` to resolve ``personal_folder``
automatically from the currently authenticated Dropbox account instead of
requiring it to be passed or configured by hand.

Requires the official ``dropbox`` SDK (``pip install mydropbox[sdk]``) and a
personal access token in the ``MYDROPBOX_SDK_TOKEN`` environment variable.
This module is never imported at package import time — it's only touched
when ``auto_identify=True`` is actually used, so the SDK being uninstalled
or unconfigured has no effect on normal usage.
"""

import os


class SdkNotAvailableError(RuntimeError):
    """The ``dropbox`` SDK package is not installed."""


class SdkNotConfiguredError(RuntimeError):
    """The ``dropbox`` SDK is installed but no access token is configured."""


def _build_client():
    try:
        import dropbox
    except ImportError as exc:
        raise SdkNotAvailableError(
            "auto_identify=True requires the 'dropbox' SDK, which isn't "
            "installed. Install it with: pip install mydropbox[sdk]"
        ) from exc

    token = os.getenv("MYDROPBOX_SDK_TOKEN")
    if not token:
        raise SdkNotConfiguredError(
            "auto_identify=True requires a Dropbox access token. Set the "
            "MYDROPBOX_SDK_TOKEN environment variable — see "
            "docs/DROPBOX_SDK_SETUP.md for how to generate one."
        )
    return dropbox.Dropbox(token, timeout=10)


def resolve_personal_folder(client=None) -> str:
    """Return the display name of the currently authenticated Dropbox account.

    This is expected to match the account holder's personal folder name
    within the group Dropbox (e.g. "Raphaël Bajon"). Pass ``client`` to use
    an already-constructed ``dropbox.Dropbox`` instance (mainly for tests);
    otherwise one is built from ``MYDROPBOX_SDK_TOKEN``.
    """
    if client is None:
        client = _build_client()
        import dropbox  # SDK import is guaranteed to succeed: _build_client() just did it

        try:
            account = client.users_get_current_account()
        except dropbox.exceptions.AuthError as exc:
            raise RuntimeError(
                "Dropbox rejected MYDROPBOX_SDK_TOKEN (invalid or expired). "
                "Regenerate a token and update MYDROPBOX_SDK_TOKEN — see "
                "docs/DROPBOX_SDK_SETUP.md."
            ) from exc
        except dropbox.exceptions.ApiError as exc:
            raise RuntimeError(f"Dropbox API error while identifying account: {exc}") from exc
    else:
        # Injected client (tests) — no dependency on the real SDK being installed.
        account = client.users_get_current_account()

    return account.name.display_name
