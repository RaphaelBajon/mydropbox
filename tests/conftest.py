"""Shared pytest fixtures for the mydropbox test suite."""

import pytest


@pytest.fixture
def tmp_dropbox(tmp_path):
    """Create a minimal fake Dropbox directory tree with nested subdirectories."""
    group = tmp_path / "group"
    (group / "datasets" / "argo" / "floats_2025").mkdir(parents=True)
    (group / "datasets" / "argo" / "floats_2024").mkdir(parents=True)
    (group / "group_notes").mkdir(parents=True)
    (group / "collaborative_projects").mkdir(parents=True)

    personal = tmp_path / "My Name"
    (personal / "mycode").mkdir(parents=True)
    (personal / "datasets" / "processed").mkdir(parents=True)
    (personal / "projects" / "project_01" / "data").mkdir(parents=True)

    return tmp_path
