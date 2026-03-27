from pathlib import Path

from student_behavior_model_stubs.config import build_default_paths


def test_build_default_paths_uses_project_bound_locations() -> None:
    repo_root = Path(r"C:\Users\Orion\Desktop\StudentBehavior")
    paths = build_default_paths(repo_root)
    assert paths.output_dir == repo_root / "artifacts" / "model_stubs"
    assert paths.student_results_csv == paths.output_dir / "v1_student_results.csv"
    assert paths.student_reports_jsonl == paths.output_dir / "v1_student_reports.jsonl"
    assert paths.overview_json == paths.output_dir / "v1_overview_by_term.json"
    assert paths.model_summary_json == paths.output_dir / "v1_model_summary.json"
    assert paths.warnings_json == paths.output_dir / "v1_warnings.json"
