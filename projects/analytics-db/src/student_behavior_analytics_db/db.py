from __future__ import annotations

from pathlib import Path


def build_database_path(project_root: Path) -> Path:
    return project_root / "data" / "analytics.db"
