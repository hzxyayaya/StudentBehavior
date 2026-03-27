from pathlib import Path

import pytest

from student_behavior_demo_api.services import DemoApiStore


@pytest.fixture
def sample_store(tmp_path: Path) -> DemoApiStore:
    artifact_root = (
        Path(__file__).resolve().parents[4]
        / "v1-model-stubs"
        / "artifacts"
        / "model_stubs"
    )
    warnings_path = tmp_path / "v1_student_results.csv"
    warnings_path.write_text(
        "\ufeffstudent_id,term_key,student_name,major_name,quadrant_label,risk_probability,risk_level,dimension_scores_json\n"
        '20230002,2023-1,Alice,软件工程,情绪驱动型,0.92,high,"[]"\n'
        '20230001,2023-1,Bob,软件工程,被动守纪型,0.81,medium,"[]"\n'
        '20230003,2024-1,Carol,软件工程,自律共鸣型,0.65,low,"[]"\n',
        encoding="utf-8",
    )
    return DemoApiStore(
        overview_path=artifact_root / "v1_overview_by_term.json",
        model_summary_path=artifact_root / "v1_model_summary.json",
        overview_term="2024-2",
        warnings_path=warnings_path,
    )


def test_get_overview_by_term_returns_single_term_payload(sample_store) -> None:
    payload = sample_store.get_overview("2024-2")
    assert payload["student_count"] == 179


def test_get_model_summary_returns_stub_summary(sample_store) -> None:
    payload = sample_store.get_model_summary(term="2024-2")
    assert payload["risk_model"] == "stub-risk-rules"


def test_list_warnings_filters_by_term_and_risk_level(sample_store) -> None:
    payload = sample_store.list_warnings(term="2023-1", risk_level="high")
    assert payload["total"] == 1
    assert payload["items"][0]["risk_level"] == "high"


def test_list_warnings_sorts_by_risk_probability_desc_then_student_id(sample_store) -> None:
    payload = sample_store.list_warnings(term="2023-1", page=1, page_size=2)
    assert [item["student_id"] for item in payload["items"]] == ["20230002", "20230001"]


def test_list_warnings_raises_for_unknown_term(sample_store) -> None:
    with pytest.raises(KeyError, match="2099-1"):
        sample_store.list_warnings(term="2099-1")


def test_missing_default_artifact_resolution_only_uses_current_worktree(tmp_path: Path) -> None:
    current_artifact_root = tmp_path / "artifacts" / "model_stubs"
    sibling_artifact_root = tmp_path.parent / "v1-model-stubs" / "artifacts" / "model_stubs"
    sibling_artifact_root.mkdir(parents=True)
    (sibling_artifact_root / "v1_overview_by_term.json").write_text("{}", encoding="utf-8")
    (sibling_artifact_root / "v1_model_summary.json").write_text("{}", encoding="utf-8")

    with pytest.raises(FileNotFoundError):
        DemoApiStore(repo_root=tmp_path)
