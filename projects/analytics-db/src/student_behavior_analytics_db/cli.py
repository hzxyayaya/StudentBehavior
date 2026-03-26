from __future__ import annotations

from pathlib import Path
from typing import Sequence

from .config import build_default_paths


def resolve_checkout_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / ".git").exists():
            return parent
    raise RuntimeError("unable to locate checkout root")


def bootstrap() -> None:
    build_default_paths(resolve_checkout_root())


def main(argv: Sequence[str] | None = None) -> int:
    args = list(argv or [])
    if not args:
        return 0
    if args[0] == "bootstrap":
        bootstrap()
        return 0
    return 2
