from pathlib import Path

import student_behavior_analytics_db.cli as cli
from student_behavior_analytics_db.config import build_default_paths


def _find_checkout_root(path: Path) -> Path:
    for parent in path.resolve().parents:
        if (parent / ".git").exists():
            return parent
    raise AssertionError("checkout root not found")


def test_cli_bootstrap_uses_checkout_root_from_package_location(
    tmp_path: Path, monkeypatch
) -> None:
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    monkeypatch.chdir(outside_dir)

    captured: dict[str, Path] = {}

    def fake_build_default_paths(repo_root: Path):
        captured["repo_root"] = repo_root
        return build_default_paths(repo_root)

    monkeypatch.setattr(cli, "build_default_paths", fake_build_default_paths)

    assert cli.main(["bootstrap"]) == 0
    expected_root = _find_checkout_root(Path(cli.__file__))

    assert captured["repo_root"] == expected_root
    assert captured["repo_root"] != Path.cwd()
    assert captured["repo_root"] != Path(cli.__file__).resolve().parents[2]
