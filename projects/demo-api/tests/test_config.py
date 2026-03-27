from pathlib import Path

from student_behavior_demo_api.config import build_default_settings


def test_build_default_settings_uses_repo_bound_artifact_paths() -> None:
    repo_root = Path(r"C:\Users\Orion\Desktop\StudentBehavior")
    settings = build_default_settings(repo_root)
    assert settings.artifacts_root == repo_root / "artifacts" / "model_stubs"
    assert settings.student_results_csv == settings.artifacts_root / "v1_student_results.csv"
    assert settings.demo_token == "demo-token"
