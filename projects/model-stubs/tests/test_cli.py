from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pytest

import student_behavior_model_stubs.cli as cli_module
from student_behavior_model_stubs.reporting import build_warnings_payload


def _find_checkout_root(path: Path) -> Path:
    for parent in path.resolve().parents:
        if (parent / ".git").exists():
            return parent
    raise AssertionError("checkout root not found")


def test_build_warnings_payload_uses_runtime_generated_at() -> None:
    fixed_now = datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    payload = build_warnings_payload(
        input_row_count=1,
        output_row_count=1,
        dropped_row_count=0,
        null_metric_summary={"avg_course_score": 0, "failed_course_count": 1},
        notes=["build completed"],
        now=fixed_now,
    )

    assert payload["generated_at"] == "2024-01-02T03:04:05Z"
    assert payload["generated_at"] != "generated_at"
    assert payload["null_metric_summary"] == {
        "avg_course_score": 0,
        "failed_course_count": 1,
        "attendance_normal_rate": 0,
        "sign_event_count": 0,
        "selected_course_count": 0,
        "library_visit_count": 0,
    }


def test_run_build_defaults_to_checkout_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_csv = tmp_path / "features.csv"
    input_csv.write_text(
        "student_id,term_key,major_name,risk_label,avg_course_score,failed_course_count,"
        "attendance_normal_rate,sign_event_count,selected_course_count,library_visit_count\n"
        "20230001,2023-1,软件工程,1,61,2,0.42,3,4,1\n",
        encoding="utf-8",
    )
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    monkeypatch.chdir(outside_dir)

    captured: dict[str, Path] = {}

    def fake_build_default_paths(repo_root: Path):
        captured["repo_root"] = repo_root
        return cli_module.DefaultPaths(
            output_dir=tmp_path / "artifacts" / "model_stubs",
            student_results_csv=tmp_path / "artifacts" / "model_stubs" / "v1_student_results.csv",
            student_reports_jsonl=tmp_path / "artifacts" / "model_stubs" / "v1_student_reports.jsonl",
            overview_json=tmp_path / "artifacts" / "model_stubs" / "v1_overview_by_term.json",
            model_summary_json=tmp_path / "artifacts" / "model_stubs" / "v1_model_summary.json",
            warnings_json=tmp_path / "artifacts" / "model_stubs" / "v1_warnings.json",
        )

    monkeypatch.setattr(cli_module, "build_default_paths", fake_build_default_paths)

    cli_module.run_build(input_csv)

    expected_root = _find_checkout_root(Path(cli_module.__file__))
    assert captured["repo_root"] == expected_root
    assert captured["repo_root"] != Path.cwd()


def test_main_build_writes_all_expected_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    input_csv = tmp_path / "features.csv"
    output_dir = tmp_path / "artifacts" / "model_stubs"

    pd.DataFrame(
        [
            {
                "student_id": "20230001",
                "term_key": "2023-1",
                "major_name": "软件工程",
                "risk_label": 1,
                "avg_course_score": 61.0,
                "failed_course_count": 2,
                "attendance_normal_rate": 0.42,
                "sign_event_count": 3,
                "selected_course_count": 4,
                "library_visit_count": 1,
            }
        ]
    ).to_csv(input_csv, index=False, encoding="utf-8")

    fixed_now = datetime(2024, 1, 2, 3, 4, 5, tzinfo=timezone.utc)
    original_run_build = cli_module.run_build

    def _fixed_run_build(
        features_csv: Path,
        output_dir: Path | None = None,
        *,
        warnings_now: datetime | None = None,
    ) -> dict[str, object]:
        del warnings_now
        return original_run_build(features_csv, output_dir, warnings_now=fixed_now)

    monkeypatch.setattr(cli_module, "run_build", _fixed_run_build)

    exit_code = cli_module.main(["build", str(input_csv), "--output-dir", str(output_dir)])

    assert exit_code == 0

    student_results_csv = output_dir / "v1_student_results.csv"
    student_reports_jsonl = output_dir / "v1_student_reports.jsonl"
    overview_json = output_dir / "v1_overview_by_term.json"
    model_summary_json = output_dir / "v1_model_summary.json"
    warnings_json = output_dir / "v1_warnings.json"

    for path in [
        student_results_csv,
        student_reports_jsonl,
        overview_json,
        model_summary_json,
        warnings_json,
    ]:
        assert path.exists()

    results = pd.read_csv(student_results_csv)
    reports = [
        json.loads(line)
        for line in student_reports_jsonl.read_text(encoding="utf-8").splitlines()
        if line
    ]
    overview = json.loads(overview_json.read_text(encoding="utf-8"))
    model_summary = json.loads(model_summary_json.read_text(encoding="utf-8"))
    warnings = json.loads(warnings_json.read_text(encoding="utf-8"))

    assert list(results["student_id"].astype(str)) == ["20230001"]
    assert reports == [
        {
            "student_id": "20230001",
            "term_key": "2023-1",
            "top_factors": [
                {
                    "feature": "behavior_activity",
                    "feature_cn": "学习行为活跃度",
                    "effect": "positive",
                    "importance": 0.69,
                },
                {
                    "feature": "routine_resource_use",
                    "feature_cn": "生活规律与资源使用",
                    "effect": "positive",
                    "importance": 0.64,
                },
                {
                    "feature": "class_engagement",
                    "feature_cn": "课堂学习投入",
                    "effect": "positive",
                    "importance": 0.55,
                },
            ],
            "intervention_advice": [
                "建议先聚焦课堂参与和作息稳定，按周观察变化趋势。",
                "把学习任务拆成小步执行，并保留固定的反馈节奏。",
                "继续维持已有的正向行为，同时减少波动较大的环节。",
            ],
            "report_text": (
                "## 学生群体画像\n"
                "该学生被系统归类为「情绪驱动型」群体，当前风险等级为 中风险。\n\n"
                "## 核心风险指标解读\n"
                "1. **学习行为活跃度**: 当前维度得分为 0.12，属于需要优先关注的弱项。\n"
                "2. **生活规律与资源使用**: 当前维度得分为 0.23，属于需要优先关注的弱项。\n"
                "3. **课堂学习投入**: 当前维度得分为 0.39，属于需要优先关注的弱项。\n\n"
                "## 建设性改进建议\n"
                "1. 建议先聚焦课堂参与和作息稳定，按周观察变化趋势。\n"
                "2. 把学习任务拆成小步执行，并保留固定的反馈节奏。\n"
                "3. 继续维持已有的正向行为，同时减少波动较大的环节。"
            ),
        }
    ]
    assert overview["student_count"] == 1
    assert model_summary == {
        "cluster_method": "stub-quadrant-rules",
        "risk_model": "stub-risk-rules",
        "target_label": "综合测评低等级风险",
        "auc": 0.8347,
        "updated_at": model_summary["updated_at"],
    }
    assert warnings["generated_at"] == "2024-01-02T03:04:05Z"
    assert warnings["input_row_count"] == 1
    assert warnings["output_row_count"] == 1
    assert warnings["dropped_row_count"] == 0
    assert warnings["null_metric_summary"] == {
        "avg_course_score": 0,
        "failed_course_count": 0,
        "attendance_normal_rate": 0,
        "sign_event_count": 0,
        "selected_course_count": 0,
        "library_visit_count": 0,
    }
    assert warnings["notes"] == ["build completed"]
