from pathlib import Path

import student_behavior_analytics_db.cli as cli
import student_behavior_analytics_db.db as db
from student_behavior_analytics_db.config import build_default_paths


def _find_checkout_root(path: Path) -> Path:
    for parent in path.resolve().parents:
        if (parent / ".git").exists():
            return parent
    raise AssertionError("checkout root not found")


def test_cli_bootstrap_uses_checkout_root_from_package_location(
    tmp_path: Path, monkeypatch
) -> None:
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    monkeypatch.chdir(outside_dir)

    captured: dict[str, Path] = {}

    def fake_build_default_paths(repo_root: Path):
        captured["repo_root"] = repo_root
        return build_default_paths(repo_root)

    monkeypatch.setattr(cli, "build_default_paths", fake_build_default_paths)

    assert cli.main(["bootstrap"]) == 0
    expected_root = _find_checkout_root(Path(cli.__file__))

    assert captured["repo_root"] == expected_root
    assert captured["repo_root"] != Path.cwd()
    assert captured["repo_root"] != Path(cli.__file__).resolve().parents[2]


EXPECTED_TABLES = {
    "students",
    "terms",
    "courses",
    "majors",
    "student_course_enrollments",
    "student_grade_records",
    "student_attendance_records",
    "student_signin_events",
    "student_assignment_submissions",
    "student_exam_submissions",
    "student_task_participation",
    "student_discussion_events",
    "student_library_visits",
    "student_running_events",
    "student_evaluation_labels",
    "student_term_features",
}

EXPECTED_SQL_FILES = [
    "001_create_dimensions.sql",
    "002_create_fact_tables.sql",
    "003_create_student_term_features.sql",
    "004_indexes.sql",
]


def test_schema_scaffold_defines_expected_tables() -> None:
    project_root = Path(db.__file__).resolve().parents[2]
    sql_dir = project_root / "sql"
    fact_sql = (sql_dir / "002_create_fact_tables.sql").read_text(encoding="utf-8")
    mart_sql = (sql_dir / "003_create_student_term_features.sql").read_text(
        encoding="utf-8"
    )
    schema_sql_files = db.get_schema_sql_files(project_root)
    schema_sql_names = [path.name for path in schema_sql_files]

    assert db.collect_schema_table_names(project_root) == EXPECTED_TABLES
    assert schema_sql_names == sorted(schema_sql_names)
    assert set(EXPECTED_SQL_FILES).issubset(schema_sql_names)
    assert all((sql_dir / name).exists() for name in EXPECTED_SQL_FILES)
    assert "source_file text not null" in fact_sql
    assert "source_row_hash text not null" in fact_sql
    assert "primary key (student_id, term_key)" in mart_sql


def test_extract_table_names_handles_quoted_and_schema_qualified_tables() -> None:
    sql_text = """
        create table if not exists public."Student_Events" (
            id integer primary key
        );

        create table "analytics"."term_features" (
            id integer primary key
        );
    """

    assert db._extract_table_names(sql_text) == {"Student_Events", "term_features"}


def test_cli_build_demo_features_defaults_to_full_build(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_resolve_checkout_root() -> Path:
        return Path("C:/demo-repo")

    def fake_build_demo_features_from_excels(*, repo_root: Path, include_heavy_sources: bool = True):
        captured["repo_root"] = repo_root
        captured["include_heavy_sources"] = include_heavy_sources
        return {"data_dir": "demo-data", "output_csv": "demo-output.csv", "row_count": 3}

    monkeypatch.setattr(cli, "resolve_checkout_root", fake_resolve_checkout_root)
    monkeypatch.setattr(cli, "build_demo_features_from_excels", fake_build_demo_features_from_excels)

    assert cli.main(["build-demo-features"]) == 0
    assert captured == {"repo_root": Path("C:/demo-repo"), "include_heavy_sources": True}


def test_cli_build_demo_features_can_skip_heavy_source_build(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_resolve_checkout_root() -> Path:
        return Path("C:/demo-repo")

    def fake_build_demo_features_from_excels(*, repo_root: Path, include_heavy_sources: bool = True):
        captured["repo_root"] = repo_root
        captured["include_heavy_sources"] = include_heavy_sources
        return {"data_dir": "demo-data", "output_csv": "demo-output.csv", "row_count": 3}

    monkeypatch.setattr(cli, "resolve_checkout_root", fake_resolve_checkout_root)
    monkeypatch.setattr(cli, "build_demo_features_from_excels", fake_build_demo_features_from_excels)

    assert cli.main(["build-demo-features", "--skip-heavy-sources"]) == 0
    assert captured == {"repo_root": Path("C:/demo-repo"), "include_heavy_sources": False}
