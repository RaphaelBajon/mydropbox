"""Tests for mydropbox.config.loadconfig.load_config."""

import importlib

import pytest

_loadconfig = importlib.import_module("mydropbox.config.loadconfig")
load_config = _loadconfig.load_config


@pytest.fixture
def isolated_config(tmp_path, monkeypatch):
    """Point config lookup at an empty tmp_path so the real ~/.mydropbox.yaml
    (or the package default) never leaks into these tests."""
    monkeypatch.setattr(_loadconfig.Path, "home", staticmethod(lambda: tmp_path))
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("MYDROPBOX_PERSONAL_FOLDER", raising=False)
    monkeypatch.delenv("MYDROPBOX_BASE_PATH", raising=False)
    return tmp_path


class TestDefaults:
    def test_no_user_config_no_env_leaves_personal_data_unset(self, isolated_config):
        """With no ~/.mydropbox.yaml or ./mydropbox.yaml, load_config() falls through to
        the package-shipped config.yaml. personal_folder/base_path must stay None there
        (no identity leak) even though labpc_users (non-private, shared lab data) is
        still populated by design — see TestLabpcUsers for that behavior in isolation."""
        config = load_config()
        assert config["personal_folder"] is None
        assert config["base_path"] is None


class TestEnvVarOverride:
    def test_env_personal_folder_used_with_no_file(self, isolated_config, monkeypatch):
        monkeypatch.setenv("MYDROPBOX_PERSONAL_FOLDER", "Env Name")
        assert load_config()["personal_folder"] == "Env Name"

    def test_env_base_path_used_with_no_file(self, isolated_config, monkeypatch):
        monkeypatch.setenv("MYDROPBOX_BASE_PATH", "/env/path")
        assert load_config()["base_path"] == "/env/path"

    def test_env_wins_over_yaml_file(self, isolated_config, monkeypatch):
        (isolated_config / ".mydropbox.yaml").write_text(
            "dropbox:\n  PERSONAL_FOLDER: 'File Name'\n"
        )
        monkeypatch.setenv("MYDROPBOX_PERSONAL_FOLDER", "Env Name")
        assert load_config()["personal_folder"] == "Env Name"

    def test_yaml_used_when_no_env(self, isolated_config):
        (isolated_config / ".mydropbox.yaml").write_text(
            "dropbox:\n  PERSONAL_FOLDER: 'File Name'\n"
        )
        assert load_config()["personal_folder"] == "File Name"


class TestLabpcUsers:
    def test_parses_labpc_users_section(self, isolated_config):
        (isolated_config / ".mydropbox.yaml").write_text(
            "dropbox:\n  PERSONAL_FOLDER: 'File Name'\n"
            "labpc_users:\n  Jane Doe: jane\n  John Roe: john\n"
        )
        assert load_config()["labpc_users"] == {"Jane Doe": "jane", "John Roe": "john"}

    def test_defaults_to_empty_dict_when_absent(self, isolated_config):
        (isolated_config / ".mydropbox.yaml").write_text(
            "dropbox:\n  PERSONAL_FOLDER: 'File Name'\n"
        )
        assert load_config()["labpc_users"] == {}
