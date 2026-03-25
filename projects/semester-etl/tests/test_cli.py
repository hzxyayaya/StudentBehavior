from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from student_behavior_etl.cli import main, run_build
from student_behavior_etl.config import DefaultPaths


def _make_paths(base_dir: Path) -> DefaultPaths:
    input_dir = base_dir / "数据集及类型"
    output_dir = base_dir / "artifacts" / "semester_features"
    return DefaultPaths(
        input_dir=input_dir,
        output_dir=output_dir,
        output_csv=output_dir / "v1_semester_features.csv",
        output_warning_json=output_dir / "v1_warnings.json",
    )


def test_run_build_writes_csv_and_warning_json(tmp_path: Path) -> None:
    paths = _make_paths(tmp_path)
    paths.input_dir.mkdir(parents=True)

    pd.DataFrame([{"XH": "stu-1", "ZYM": "信息安全"}]).to_excel(
        paths.input_dir / "学生基本信息.xlsx",
        index=False,
    )
    pd.DataFrame([{"XH": "stu-1", "XN": "2023-2024", "XQ": 1}]).to_excel(
        paths.input_dir / "考勤汇总.xlsx",
        index=False,
    )
    pd.DataFrame(
        [
            {
                "XSBH": "stu-1",
                "XN": None,
                "XQ": None,
                "TJNY": "2023-03-01",
                "SWLJSC": 9.5,
            }
        ]
    ).to_excel(paths.input_dir / "上网统计.xlsx", index=False)

    summary = run_build(paths)

    csv_df = pd.read_csv(paths.output_csv)
    warning_payload = json.loads(paths.output_warning_json.read_text(encoding="utf-8"))

    assert list(csv_df.columns) == [
        "student_id",
        "term_key",
        "major_name",
        "attendance_record_count",
        "internet_duration_sum",
    ]
    assert warning_payload["degraded_sources"][0]["source_file"] == "上网统计.xlsx"
    assert summary["rows_written"] == 1
    assert summary["sources_read"] == [
        "学生基本信息.xlsx",
        "考勤汇总.xlsx",
        "上网统计.xlsx",
    ]
    assert summary["internet_source_degraded"] is True
    assert summary["dropped_attendance_rows"] == 0


def test_run_build_marks_internet_source_used_when_frozen_term_fields_exist(
    tmp_path: Path,
) -> None:
    paths = _make_paths(tmp_path)
    paths.input_dir.mkdir(parents=True)

    pd.DataFrame([{"XH": "stu-1", "ZYM": "信息安全"}]).to_excel(
        paths.input_dir / "学生基本信息.xlsx",
        index=False,
    )
    pd.DataFrame([{"XH": "stu-1", "XN": "2023-2024", "XQ": 1}]).to_excel(
        paths.input_dir / "考勤汇总.xlsx",
        index=False,
    )
    pd.DataFrame(
        [{"XSBH": "stu-1", "XN": "2023-2024", "XQ": 1, "TJNY": "2023-03-01", "SWLJSC": 9.5}]
    ).to_excel(paths.input_dir / "上网统计.xlsx", index=False)

    summary = run_build(paths)
    warning_payload = json.loads(paths.output_warning_json.read_text(encoding="utf-8"))

    assert summary["internet_source_degraded"] is False
    assert warning_payload["source_file_status"][2]["status"] == "used"


def test_run_build_hard_fails_when_required_source_is_missing(tmp_path: Path) -> None:
    paths = _make_paths(tmp_path)
    paths.input_dir.mkdir(parents=True)

    pd.DataFrame([{"XH": "stu-1", "ZYM": "信息安全"}]).to_excel(
        paths.input_dir / "学生基本信息.xlsx",
        index=False,
    )
    pd.DataFrame([{"XH": "stu-1", "XN": "2023-2024", "XQ": 1}]).to_excel(
        paths.input_dir / "考勤汇总.xlsx",
        index=False,
    )

    with pytest.raises(FileNotFoundError):
        run_build(paths)


def test_main_build_uses_cwd_default_paths(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    input_dir = tmp_path / "数据集及类型"
    input_dir.mkdir(parents=True)

    pd.DataFrame([{"XH": "stu-1", "ZYM": "信息安全"}]).to_excel(
        input_dir / "学生基本信息.xlsx",
        index=False,
    )
    pd.DataFrame([{"XH": "stu-1", "XN": "2023-2024", "XQ": 1}]).to_excel(
        input_dir / "考勤汇总.xlsx",
        index=False,
    )
    pd.DataFrame(
        [{"XSBH": "stu-1", "XN": "2023-2024", "XQ": 1, "TJNY": "2023-03-01", "SWLJSC": 9.5}]
    ).to_excel(input_dir / "上网统计.xlsx", index=False)

    monkeypatch.chdir(tmp_path)

    exit_code = main(["build"])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "rows_written=1" in captured.out
