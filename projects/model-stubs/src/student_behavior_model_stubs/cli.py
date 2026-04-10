from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from student_behavior_model_stubs.build_outputs import build_model_summary
from student_behavior_model_stubs.build_outputs import build_overview_by_term
from student_behavior_model_stubs.build_outputs import build_student_reports
from student_behavior_model_stubs.build_outputs import build_student_results
from student_behavior_model_stubs.config import DefaultPaths
from student_behavior_model_stubs.config import build_default_paths
from student_behavior_model_stubs.evaluate_risk_model import evaluate_risk_model
from student_behavior_model_stubs.io import read_features
from student_behavior_model_stubs.reporting import build_warnings_from_features
from student_behavior_model_stubs.train_risk_model import train_risk_model


def resolve_checkout_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists():
            return parent
    raise RuntimeError("unable to locate checkout root")


def _build_paths(output_dir: Path) -> DefaultPaths:
    return DefaultPaths(
        output_dir=output_dir,
        student_results_csv=output_dir / "v1_student_results.csv",
        student_reports_jsonl=output_dir / "v1_student_reports.jsonl",
        overview_json=output_dir / "v1_overview_by_term.json",
        model_summary_json=output_dir / "v1_model_summary.json",
        warnings_json=output_dir / "v1_warnings.json",
    )


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict[str, object]]) -> None:
    text = "\n".join(json.dumps(record, ensure_ascii=False) for record in records)
    if text:
        text += "\n"
    path.write_text(text, encoding="utf-8")


def run_build(
    features_csv: Path,
    output_dir: Path | None = None,
    *,
    warnings_now: datetime | None = None,
) -> dict[str, object]:
    features = read_features(features_csv)
    paths = (
        _build_paths(output_dir)
        if output_dir is not None
        else build_default_paths(resolve_checkout_root())
    )

    student_results = build_student_results(features)
    student_reports = build_student_reports(student_results)
    overview = build_overview_by_term(student_results)
    model_summary = build_model_summary(now=datetime.now().replace(microsecond=0))
    warnings = build_warnings_from_features(
        features,
        output_row_count=int(len(student_results)),
        dropped_row_count=int(len(features) - len(student_results)),
        notes=["build completed"],
        now=warnings_now,
    )

    paths.output_dir.mkdir(parents=True, exist_ok=True)
    student_results.to_csv(paths.student_results_csv, index=False, encoding="utf-8-sig")
    _write_jsonl(paths.student_reports_jsonl, student_reports)
    _write_json(paths.overview_json, overview)
    _write_json(paths.model_summary_json, model_summary)
    _write_json(paths.warnings_json, warnings)

    return {
        "input_row_count": int(len(features)),
        "output_row_count": int(len(student_results)),
        "dropped_row_count": int(len(features) - len(student_results)),
        "student_results_csv": str(paths.student_results_csv),
        "student_reports_jsonl": str(paths.student_reports_jsonl),
        "overview_json": str(paths.overview_json),
        "model_summary_json": str(paths.model_summary_json),
        "warnings_json": str(paths.warnings_json),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="student-behavior-stubs")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("features_csv", type=Path)
    build_parser.add_argument("--output-dir", type=Path)

    train_parser = subparsers.add_parser("train-risk-model")
    train_parser.add_argument("features_csv", type=Path)
    train_parser.add_argument("--output-dir", type=Path)

    evaluate_parser = subparsers.add_parser("evaluate-risk-model")
    evaluate_parser.add_argument("features_csv", type=Path)
    evaluate_parser.add_argument("model_artifact", type=Path)
    evaluate_parser.add_argument("--output-dir", type=Path)

    args = parser.parse_args(argv)
    if args.command == "build":
        summary = run_build(args.features_csv, args.output_dir)
        print(f"input_row_count={summary['input_row_count']}")
        print(f"output_row_count={summary['output_row_count']}")
        print(f"dropped_row_count={summary['dropped_row_count']}")
        print(f"student_results_csv={summary['student_results_csv']}")
        print(f"student_reports_jsonl={summary['student_reports_jsonl']}")
        print(f"overview_json={summary['overview_json']}")
        print(f"model_summary_json={summary['model_summary_json']}")
        print(f"warnings_json={summary['warnings_json']}")
        return 0
    if args.command == "train-risk-model":
        summary = train_risk_model(args.features_csv, args.output_dir)
        print(f"split_strategy={summary['split_strategy']}")
        print(f"feature_count={summary['feature_count']}")
        print(f"train_sample_count={summary['train_sample_count']}")
        print(f"valid_sample_count={summary['valid_sample_count']}")
        print(f"test_sample_count={summary['test_sample_count']}")
        print(f"model_path={summary['model_path']}")
        print(f"metrics_path={summary['metrics_path']}")
        print(f"feature_importance_path={summary['feature_importance_path']}")
        print(f"training_config_path={summary['training_config_path']}")
        return 0
    if args.command == "evaluate-risk-model":
        summary = evaluate_risk_model(args.features_csv, args.model_artifact, args.output_dir)
        print(f"sample_count={summary['sample_count']}")
        print(f"positive_sample_count={summary['positive_sample_count']}")
        print(f"negative_sample_count={summary['negative_sample_count']}")
        print(f"auc={summary['auc']}")
        print(f"accuracy={summary['accuracy']}")
        print(f"precision={summary['precision']}")
        print(f"recall={summary['recall']}")
        print(f"f1={summary['f1']}")
        print(f"trained_at={summary['trained_at']}")
        print(f"evaluated_at={summary['evaluated_at']}")
        print(f"model_path={summary['model_path']}")
        print(f"metrics_path={summary['metrics_path']}")
        print(f"feature_importance_path={summary['feature_importance_path']}")
        return 0
    return 1
