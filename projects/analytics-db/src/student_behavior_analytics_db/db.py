from __future__ import annotations

import re
from pathlib import Path


SCHEMA_SQL_FILENAMES = (
    "001_create_dimensions.sql",
    "002_create_fact_tables.sql",
    "003_create_student_term_features.sql",
    "004_indexes.sql",
)


def build_database_path(project_root: Path) -> Path:
    return project_root / "data"


def get_schema_sql_files(project_root: Path) -> tuple[Path, ...]:
    sql_dir = project_root / "sql"
    return tuple(sql_dir / filename for filename in SCHEMA_SQL_FILENAMES)


def collect_schema_table_names(project_root: Path) -> set[str]:
    table_names: set[str] = set()
    for sql_file in get_schema_sql_files(project_root):
        table_names.update(_extract_table_names(sql_file.read_text(encoding="utf-8")))
    return table_names


def _extract_table_names(sql_text: str) -> set[str]:
    pattern = re.compile(
        r"(?im)^\s*create\s+table\s+(?:if\s+not\s+exists\s+)?([a-z_][a-z0-9_]*)\s*\("
    )
    return {match.group(1) for match in pattern.finditer(sql_text)}
