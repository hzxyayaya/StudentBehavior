from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AnalyticsDBPaths:
    project_root: Path
    src_dir: Path
    tests_dir: Path


def build_default_paths(repo_root: Path) -> AnalyticsDBPaths:
    project_root = repo_root / "projects" / "analytics-db"
    return AnalyticsDBPaths(
        project_root=project_root,
        src_dir=project_root / "src",
        tests_dir=project_root / "tests",
    )
