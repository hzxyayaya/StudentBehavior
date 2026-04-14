from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Sequence

from .config import build_default_paths
from .build_demo_features_from_excels import build_demo_features_from_excels
from .sqlite_runtime import build_sqlite_runtime_db


def resolve_checkout_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists():
            return parent
    raise RuntimeError("unable to locate checkout root")


def bootstrap() -> None:
    build_default_paths(resolve_checkout_root())


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        return 0
    if args[0] == "bootstrap":
        bootstrap()
        return 0
    if args[0] == "build-demo-features":
        parser = argparse.ArgumentParser(prog="analytics-db build-demo-features")
        parser.add_argument(
            "--skip-heavy-sources",
            action="store_true",
            help="skip heavyweight source workbooks during feature rebuild",
        )
        parsed_args = parser.parse_args(args[1:])
        repo_root = resolve_checkout_root()
        summary = build_demo_features_from_excels(
            repo_root=repo_root,
            include_heavy_sources=not parsed_args.skip_heavy_sources,
        )
        print(f"data_dir={summary['data_dir']}")
        print(f"output_csv={summary['output_csv']}")
        print(f"row_count={summary['row_count']}")
        return 0
    if args[0] == "build-runtime-sqlite":
        parser = argparse.ArgumentParser(prog="analytics-db build-runtime-sqlite")
        parser.add_argument("--sqlite-path", type=Path)
        parsed_args = parser.parse_args(args[1:])
        repo_root = resolve_checkout_root()
        summary = build_sqlite_runtime_db(repo_root=repo_root, sqlite_path=parsed_args.sqlite_path)
        print(f"sqlite_path={summary['sqlite_path']}")
        print(f"student_term_features_count={summary['student_term_features_count']}")
        print(f"student_results_count={summary['student_results_count']}")
        print(f"student_reports_count={summary['student_reports_count']}")
        print(f"model_summary_count={summary['model_summary_count']}")
        print(f"overview_count={summary['overview_count']}")
        print(f"warnings_count={summary['warnings_count']}")
        return 0
    return 2
