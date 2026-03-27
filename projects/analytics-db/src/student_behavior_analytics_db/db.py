from __future__ import annotations

import re
from pathlib import Path


def build_database_path(project_root: Path) -> Path:
    return project_root / "data"


def get_schema_sql_files(project_root: Path) -> tuple[Path, ...]:
    sql_dir = project_root / "sql"
    return tuple(sorted(sql_dir.glob("*.sql"), key=lambda path: path.name))


def collect_schema_table_names(project_root: Path) -> set[str]:
    table_names: set[str] = set()
    for sql_file in get_schema_sql_files(project_root):
        table_names.update(_extract_table_names(sql_file.read_text(encoding="utf-8")))
    return table_names


def _extract_table_names(sql_text: str) -> set[str]:
    pattern = re.compile(
        r'(?im)^\s*create\s+table\s+(?:if\s+not\s+exists\s+)?'
        r'(?:(?:[a-z_][a-z0-9_]*|"[^"]+")\s*\.\s*)*'
        r'(?P<table>[a-z_][a-z0-9_]*|"[^"]+")\s*\('
    )
    return {
        match.group("table").strip('"')
        for match in pattern.finditer(sql_text)
    }
