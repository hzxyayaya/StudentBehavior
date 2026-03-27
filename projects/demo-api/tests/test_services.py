import pytest

from student_behavior_demo_api.services import DemoApiStore


@pytest.fixture
def sample_store() -> DemoApiStore:
    return DemoApiStore()


def test_get_overview_by_term_returns_single_term_payload(sample_store) -> None:
    payload = sample_store.get_overview("2023-1")
    assert payload["student_count"] == 3


def test_get_model_summary_returns_stub_summary(sample_store) -> None:
    payload = sample_store.get_model_summary(term="2023-1")
    assert payload["risk_model"] == "stub-risk-rules"
