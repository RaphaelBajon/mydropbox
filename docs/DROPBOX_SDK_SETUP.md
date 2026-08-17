# Dropbox SDK auto-identify setup

`get_dropbox(auto_identify=True)` resolves `personal_folder` automatically from
your Dropbox account instead of requiring you to pass or configure it by hand.
It calls the official Dropbox API (`users_get_current_account`) to read your
account's display name, which is expected to match your personal folder name in
the group Dropbox (e.g. `"Raphaël Bajon"`).

This is entirely optional — everything else in `mydropbox` works exactly as
before without it.

## 1. Install the optional dependency

```bash
pip install mydropbox[sdk]
```

## 2. Get a Dropbox access token

You need an access token for your own Dropbox account with (at minimum)
`account_info.read` scope. In broad strokes, via the
[Dropbox App Console](https://www.dropbox.com/developers/apps):

1. Create a new app ("Scoped access", minimal permissions — just
   `account_info.read` is needed).
2. Enable that permission under the app's **Permissions** tab.
3. Generate an access token for your own account from the app's **Settings**
   tab.

**The exact console layout may have changed** since these instructions were
written — if a step doesn't match what you see, use the Dropbox API
documentation's current OAuth guide as the source of truth; the goal is just
"end up with a valid access token string for your account."

Treat the token like a password: don't commit it, don't share it with
teammates. Each lab member should generate their own.

## 3. Configure it

```bash
export MYDROPBOX_SDK_TOKEN="your-token-here"
```

(Add this to your shell profile so it persists across sessions.)

## 4. Use it

```python
from mydropbox import get_dropbox

db = get_dropbox(auto_identify=True)
db.personal.mycode
```

If your Dropbox account's display name doesn't exactly match your personal
folder's name on disk (nickname, accents, middle name, etc.), `auto_identify`
raises a clear error listing the folders it found instead of guessing — pass
`personal_folder=` explicitly in that case.
