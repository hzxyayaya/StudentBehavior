from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DefaultPaths:
    output_dir: Path
    student_results_csv: Path
    student_reports_jsonl: Path
    overview_json: Path
    model_summary_json: Path
    warnings_json: Path


def build_default_paths(repo_root: Path) -> DefaultPaths:
    output_dir = repo_root / "artifacts" / "model_stubs"
    return DefaultPaths(
        output_dir=output_dir,
        student_results_csv=output_dir / "v1_student_results.csv",
        student_reports_jsonl=output_dir / "v1_student_reports.jsonl",
        overview_json=output_dir / "v1_overview.json",
        model_summary_json=output_dir / "v1_model_summary.json",
        warnings_json=output_dir / "v1_warnings.json",
    )
