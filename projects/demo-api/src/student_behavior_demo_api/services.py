from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from student_behavior_demo_api.loaders import validate_model_summary_payload
from student_behavior_demo_api.loaders import validate_overview_payload


class DemoApiStore:
    def __init__(
        self,
        overview_payload: Mapping[str, Any] | None = None,
        model_summary_payload: Mapping[str, Any] | None = None,
    ) -> None:
        default_overview_payload = {
            "term_buckets": {
                "2023-1": {
                    "student_count": 3,
                    "risk_distribution": {},
                    "quadrant_distribution": {},
                    "major_risk_summary": [],
                    "trend_summary": [],
                }
            }
        }
        default_model_summary_payload = {
            "cluster_method": "stub-cluster",
            "risk_model": "stub-risk-rules",
            "target_label": "risk_flag",
            "auc": 0.5,
            "updated_at": "2024-01-01T00:00:00Z",
        }

        self._overview_payload = validate_overview_payload(
            overview_payload or default_overview_payload
        )
        self._model_summary_payload = validate_model_summary_payload(
            model_summary_payload or default_model_summary_payload
        )

    def get_overview(self, term: str) -> dict[str, Any]:
        term_buckets = self._overview_payload["term_buckets"]
        if term not in term_buckets:
            raise KeyError(term)
        return dict(term_buckets[term])

    def get_model_summary(self, term: str | None = None) -> dict[str, Any]:
        return dict(self._model_summary_payload)
