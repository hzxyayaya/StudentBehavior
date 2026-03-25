from __future__ import annotations


def validate_required_columns(actual_columns: list[str], required_columns: set[str]) -> None:
    missing = sorted(required_columns - set(actual_columns))
    if missing:
        raise ValueError(f"missing required columns: {', '.join(missing)}")
