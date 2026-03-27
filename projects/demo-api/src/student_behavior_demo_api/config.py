from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DemoApiSettings:
    artifacts_root: Path
    student_results_csv: Path
    student_reports_jsonl: Path
    overview_json: Path
    model_summary_json: Path
    warnings_json: Path
    default_page: int
    default_page_size: int
    demo_token: str


def build_default_settings(repo_root: Path) -> DemoApiSettings:
    artifacts_root = repo_root / "artifacts" / "model_stubs"
    return DemoApiSettings(
        artifacts_root=artifacts_root,
        student_results_csv=artifacts_root / "v1_student_results.csv",
        student_reports_jsonl=artifacts_root / "v1_student_reports.jsonl",
        overview_json=artifacts_root / "overview.json",
        model_summary_json=artifacts_root / "model_summary.json",
        warnings_json=artifacts_root / "warnings.json",
        default_page=1,
        default_page_size=20,
        demo_token="demo-token",
    )
