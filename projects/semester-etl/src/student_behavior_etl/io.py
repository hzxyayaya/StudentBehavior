from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def validate_required_columns(actual_columns: list[str], required_columns: set[str]) -> None:
    missing = sorted(required_columns - set(actual_columns))
    if missing:
        raise ValueError(f"missing required columns: {', '.join(missing)}")


def read_excel_required(path: Path, required_columns: set[str]) -> pd.DataFrame:
    if not Path(path).is_file():
        raise FileNotFoundError(path)

    frame = pd.read_excel(path)
    validate_required_columns(list(frame.columns), required_columns)
    return frame


def write_warning_json(path: Path, payload: dict[str, object]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
