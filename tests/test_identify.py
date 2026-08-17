"""Tests for mydropbox.identify (Dropbox-SDK-based auto-identification)."""

import sys

import pytest

from mydropbox import identify


class _FakeName:
    def __init__(self, display_name):
        self.display_name = display_name


class _FakeAccount:
    def __init__(self, display_name):
        self.name = _FakeName(display_name)


class _FakeClient:
    def __init__(self, display_name):
        self._display_name = display_name

    def users_get_current_account(self):
        return _FakeAccount(self._display_name)


class TestResolvePersonalFolderWithInjectedClient:
    def test_returns_display_name(self):
        client = _FakeClient("Jane Doe")
        assert identify.resolve_personal_folder(client=client) == "Jane Doe"

    def test_does_not_require_dropbox_sdk_installed(self, monkeypatch):
        """An injected client must work even if the real SDK can't be imported."""
        monkeypatch.setitem(sys.modules, "dropbox", None)
        client = _FakeClient("Jane Doe")
        assert identify.resolve_personal_folder(client=client) == "Jane Doe"


class TestBuildClientErrors:
    def test_sdk_not_available_raises_typed_error(self, monkeypatch):
        monkeypatch.setitem(sys.modules, "dropbox", None)
        with pytest.raises(identify.SdkNotAvailableError, match="pip install mydropbox\\[sdk\\]"):
            identify.resolve_personal_folder()

    def test_sdk_not_configured_raises_typed_error(self, monkeypatch):
        pytest.importorskip("dropbox")
        monkeypatch.delenv("MYDROPBOX_SDK_TOKEN", raising=False)
        with pytest.raises(identify.SdkNotConfiguredError, match="MYDROPBOX_SDK_TOKEN"):
            identify.resolve_personal_folder()
