from pathlib import Path

import pytest

from student_behavior_demo_api.services import DemoApiStore


@pytest.fixture
def sample_store() -> DemoApiStore:
    artifact_root = (
        Path(__file__).resolve().parents[4]
        / "v1-model-stubs"
        / "artifacts"
        / "model_stubs"
    )
    return DemoApiStore(
        overview_path=artifact_root / "v1_overview_by_term.json",
        model_summary_path=artifact_root / "v1_model_summary.json",
        overview_term="2024-2",
    )


def test_get_overview_by_term_returns_single_term_payload(sample_store) -> None:
    payload = sample_store.get_overview("2024-2")
    assert payload["student_count"] == 179


def test_get_model_summary_returns_stub_summary(sample_store) -> None:
    payload = sample_store.get_model_summary(term="2024-2")
    assert payload["risk_model"] == "stub-risk-rules"
