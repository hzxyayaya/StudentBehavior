from pathlib import Path

import student_behavior_analytics_db.cli as cli
from student_behavior_analytics_db.config import build_default_paths


def test_cli_bootstrap_uses_project_root_not_cwd(tmp_path: Path, monkeypatch) -> None:
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    monkeypatch.chdir(outside_dir)

    captured: dict[str, Path] = {}

    def fake_build_default_paths(repo_root: Path):
        captured["repo_root"] = repo_root
        return build_default_paths(repo_root)

    monkeypatch.setattr(cli, "build_default_paths", fake_build_default_paths)

    assert cli.main(["bootstrap"]) == 0
    assert captured["repo_root"] == Path(cli.__file__).resolve().parents[2]
