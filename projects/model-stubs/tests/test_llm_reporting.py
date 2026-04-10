from __future__ import annotations

from pathlib import Path

import pytest

from student_behavior_model_stubs.llm_reporting import DEFAULT_LLM_PROMPT_VERSION
from student_behavior_model_stubs.llm_reporting import DEFAULT_TEMPLATE_PROMPT_VERSION
from student_behavior_model_stubs.llm_reporting import LLMReportResult
from student_behavior_model_stubs.llm_reporting import LLMReportingError
from student_behavior_model_stubs.llm_reporting import LLMReportingSettings
from student_behavior_model_stubs.llm_reporting import build_report_payload_with_fallback
from student_behavior_model_stubs.llm_reporting import load_llm_reporting_settings
from student_behavior_model_stubs.templates import build_report_payload


def _template_payload() -> dict[str, object]:
    return build_report_payload(
        base_risk_score=61.0,
        risk_adjustment_score=4.0,
        adjusted_risk_score=65.0,
        risk_delta=3.5,
        risk_change_direction="rising",
        risk_level="一般风险",
        group_segment="课堂参与薄弱组",
        dimension_scores=[
            {
                "dimension": "学业基础表现",
                "dimension_code": "academic_base",
                "score": 0.32,
                "level": "low",
                "label": "学业基础预警",
                "metrics": [{"metric": "term_gpa", "label": "学期GPA", "value": 2.3}],
                "explanation": "学业基础表现处于学业基础预警，主要依据是学期GPA 2.3。",
                "provenance": {"has_caveated_metrics": False, "has_deferred_metrics": False},
            }
        ],
    )


def test_load_llm_reporting_settings_reads_env_file_without_requiring_real_key(
    tmp_path: Path,
) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "STUDENT_BEHAVIOR_LLM_ENABLED=true",
                "STUDENT_BEHAVIOR_LLM_PROVIDER=deepseek",
                "STUDENT_BEHAVIOR_LLM_BASE_URL=https://api.deepseek.com/v1",
                "STUDENT_BEHAVIOR_LLM_MODEL=deepseek-chat",
                "STUDENT_BEHAVIOR_LLM_PROMPT_VERSION=llm-report-v1",
                "STUDENT_BEHAVIOR_LLM_SOURCE_MODE=hybrid",
            ]
        ),
        encoding="utf-8",
    )

    settings = load_llm_reporting_settings(env_file=env_file, environ={})

    assert settings.enabled is True
    assert settings.provider == "deepseek"
    assert settings.base_url == "https://api.deepseek.com/v1"
    assert settings.model == "deepseek-chat"
    assert settings.api_key is None
    assert settings.source_mode == "hybrid"
    assert settings.prompt_version == "llm-report-v1"
    assert settings.is_configured is False


def test_build_report_payload_with_fallback_uses_template_when_api_key_is_missing() -> None:
    template_payload = _template_payload()
    settings = LLMReportingSettings(
        enabled=True,
        provider="deepseek",
        base_url="https://api.deepseek.com/v1",
        model="deepseek-chat",
        api_key=None,
        source_mode="hybrid",
        prompt_version=DEFAULT_LLM_PROMPT_VERSION,
        timeout_seconds=8.0,
    )

    payload = build_report_payload_with_fallback(
        template_payload=template_payload,
        llm_settings=settings,
    )

    assert payload["report_text"] == template_payload["report_text"]
    assert payload["report_source"] == "template"
    assert payload["prompt_version"] == DEFAULT_TEMPLATE_PROMPT_VERSION
    assert payload["report_generation"] == {
        "source": "template",
        "prompt_version": DEFAULT_TEMPLATE_PROMPT_VERSION,
        "fallback_reason": "missing_api_key",
        "provider": "deepseek",
        "model": "deepseek-chat",
        "requested_source": "hybrid",
        "requested_prompt_version": DEFAULT_LLM_PROMPT_VERSION,
    }


def test_build_report_payload_with_fallback_marks_hybrid_when_llm_succeeds() -> None:
    template_payload = _template_payload()
    settings = LLMReportingSettings(
        enabled=True,
        provider="openai-compatible",
        base_url="https://api.openai.example/v1",
        model="gpt-test",
        api_key="test-key",
        source_mode="hybrid",
        prompt_version="llm-report-v1",
        timeout_seconds=8.0,
    )

    payload = build_report_payload_with_fallback(
        template_payload=template_payload,
        llm_settings=settings,
        generate_llm_report=lambda request: LLMReportResult(
            report_text="LLM enhanced report",
            source="hybrid",
        ),
    )

    assert payload["report_text"] == "LLM enhanced report"
    assert payload["report_source"] == "hybrid"
    assert payload["prompt_version"] == "llm-report-v1"
    assert payload["report_generation"] == {
        "source": "hybrid",
        "prompt_version": "llm-report-v1",
        "fallback_reason": None,
        "provider": "openai-compatible",
        "model": "gpt-test",
        "requested_source": "hybrid",
        "requested_prompt_version": "llm-report-v1",
    }


def test_build_report_payload_with_fallback_reverts_to_template_when_llm_errors() -> None:
    template_payload = _template_payload()
    settings = LLMReportingSettings(
        enabled=True,
        provider="openai-compatible",
        base_url="https://api.openai.example/v1",
        model="gpt-test",
        api_key="test-key",
        source_mode="hybrid",
        prompt_version="llm-report-v1",
        timeout_seconds=8.0,
    )

    payload = build_report_payload_with_fallback(
        template_payload=template_payload,
        llm_settings=settings,
        generate_llm_report=lambda request: (_ for _ in ()).throw(
            LLMReportingError("provider request failed")
        ),
    )

    assert payload["report_text"] == template_payload["report_text"]
    assert payload["report_source"] == "template"
    assert payload["prompt_version"] == DEFAULT_TEMPLATE_PROMPT_VERSION
    assert payload["report_generation"]["fallback_reason"] == "provider_request_failed"


def test_build_report_payload_with_fallback_reverts_to_template_when_provider_raises_unexpected_exception() -> None:
    template_payload = _template_payload()
    settings = LLMReportingSettings(
        enabled=True,
        provider="openai-compatible",
        base_url="https://api.openai.example/v1",
        model="gpt-test",
        api_key="test-key",
        source_mode="hybrid",
        prompt_version="llm-report-v1",
        timeout_seconds=8.0,
    )

    payload = build_report_payload_with_fallback(
        template_payload=template_payload,
        llm_settings=settings,
        generate_llm_report=lambda request: (_ for _ in ()).throw(
            ValueError("provider exploded unexpectedly")
        ),
    )

    assert payload["report_text"] == template_payload["report_text"]
    assert payload["report_source"] == "template"
    assert payload["prompt_version"] == DEFAULT_TEMPLATE_PROMPT_VERSION
    assert payload["report_generation"]["fallback_reason"] == "provider_exploded_unexpectedly"


def test_load_llm_reporting_settings_accepts_template_source_mode(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "STUDENT_BEHAVIOR_LLM_ENABLED=true",
                "STUDENT_BEHAVIOR_LLM_PROVIDER=deepseek",
                "STUDENT_BEHAVIOR_LLM_BASE_URL=https://api.deepseek.com/v1",
                "STUDENT_BEHAVIOR_LLM_MODEL=deepseek-chat",
                "STUDENT_BEHAVIOR_LLM_SOURCE_MODE=template",
            ]
        ),
        encoding="utf-8",
    )

    settings = load_llm_reporting_settings(env_file=env_file, environ={})

    assert settings.source_mode == "template"


def test_build_report_payload_with_fallback_short_circuits_template_mode_without_online_call() -> None:
    template_payload = _template_payload()
    settings = LLMReportingSettings(
        enabled=True,
        provider="openai-compatible",
        base_url="https://api.openai.example/v1",
        model="gpt-test",
        api_key="test-key",
        source_mode="template",
        prompt_version="llm-report-v1",
        timeout_seconds=8.0,
    )

    payload = build_report_payload_with_fallback(
        template_payload=template_payload,
        llm_settings=settings,
        generate_llm_report=lambda request: (_ for _ in ()).throw(
            AssertionError("generator should not be called")
        ),
    )

    assert payload["report_text"] == template_payload["report_text"]
    assert payload["report_source"] == "template"
    assert payload["prompt_version"] == DEFAULT_TEMPLATE_PROMPT_VERSION
    assert payload["report_generation"] == {
        "source": "template",
        "prompt_version": DEFAULT_TEMPLATE_PROMPT_VERSION,
        "fallback_reason": None,
        "provider": None,
        "model": None,
        "requested_source": "template",
        "requested_prompt_version": DEFAULT_TEMPLATE_PROMPT_VERSION,
    }


@pytest.mark.parametrize("exception", [KeyboardInterrupt(), SystemExit(2)])
def test_build_report_payload_with_fallback_does_not_swallow_process_control_exceptions(
    exception: BaseException,
) -> None:
    template_payload = _template_payload()
    settings = LLMReportingSettings(
        enabled=True,
        provider="openai-compatible",
        base_url="https://api.openai.example/v1",
        model="gpt-test",
        api_key="test-key",
        source_mode="hybrid",
        prompt_version="llm-report-v1",
        timeout_seconds=8.0,
    )

    with pytest.raises(type(exception)):
        build_report_payload_with_fallback(
            template_payload=template_payload,
            llm_settings=settings,
            generate_llm_report=lambda request: (_ for _ in ()).throw(exception),
        )
