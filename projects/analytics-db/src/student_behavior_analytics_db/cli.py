from __future__ import annotations

from pathlib import Path
from typing import Sequence

from .config import build_default_paths


def resolve_project_root() -> Path:
    return Path(__file__).resolve().parents[6]


def bootstrap() -> None:
    build_default_paths(resolve_project_root())


def main(argv: Sequence[str] | None = None) -> int:
    args = list(argv or [])
    if not args:
        return 0
    if args[0] == "bootstrap":
        bootstrap()
        return 0
    return 2
