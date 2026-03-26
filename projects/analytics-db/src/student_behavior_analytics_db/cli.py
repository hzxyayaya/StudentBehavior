from __future__ import annotations

from pathlib import Path
from typing import Sequence

from .config import build_default_paths


def main(argv: Sequence[str] | None = None) -> int:
    args = list(argv or [])
    if not args:
        return 0
    if args[0] == "bootstrap":
        build_default_paths(Path.cwd())
        return 0
    return 2
