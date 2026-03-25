from pathlib import Path

from student_behavior_etl.config import build_default_paths


def test_build_default_paths_uses_fixed_repo_layout(tmp_path: Path) -> None:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()

    paths = build_default_paths(repo_root)

    assert paths.input_dir == repo_root / "数据集及类型"
    assert paths.output_dir == repo_root / "artifacts" / "semester_features"
    assert paths.output_csv == paths.output_dir / "v1_semester_features.csv"
    assert paths.output_warning_json == paths.output_dir / "v1_warnings.json"
