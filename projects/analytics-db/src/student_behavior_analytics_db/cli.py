from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

from .config import build_default_paths
from .build_demo_features_from_excels import build_demo_features_from_excels


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
        repo_root = resolve_checkout_root()
        summary = build_demo_features_from_excels(repo_root=repo_root)
        print(f"data_dir={summary['data_dir']}")
        print(f"output_csv={summary['output_csv']}")
        print(f"row_count={summary['row_count']}")
        return 0
    return 2
