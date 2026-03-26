from pathlib import Path

import pytest

from student_behavior_analytics_db.cli import main
from student_behavior_analytics_db.config import build_default_paths


def test_cli_bootstrap_command_and_default_paths(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    paths = build_default_paths(repo_root)

    assert paths.project_root == repo_root / "projects" / "analytics-db"
    assert paths.src_dir == paths.project_root / "src"
    assert paths.tests_dir == paths.project_root / "tests"
    assert main(["bootstrap"]) == 0
