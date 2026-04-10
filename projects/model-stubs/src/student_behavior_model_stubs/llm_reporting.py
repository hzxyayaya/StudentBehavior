from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
import json
import os
from pathlib import Path
from urllib import error, request


DEFAULT_TEMPLATE_PROMPT_VERSION = "template-report-v1"
DEFAULT_LLM_PROMPT_VERSION = "llm-report-v1"
_VALID_REPORT_SOURCES = {"template", "llm", "hybrid"}


class LLMReportingError(RuntimeError):
    """Raised when the LLM reporting boundary cannot produce a report."""


@dataclass(frozen=True)
class LLMReportingSettings:
    enabled: bool
    provider: str | None
    base_url: str | None
    model: str | None
    api_key: str | None
    source_mode: str
    prompt_version: str
    timeout_seconds: float

    @property
    def is_configured(self) -> bool:
        return bool(
            self.enabled
            and self.provider
            and self.base_url
            and self.model
            and self.api_key
        )


@dataclass(frozen=True)
class LLMReportRequest:
    settings: LLMReportingSettings
    template_payload: Mapping[str, object]


@dataclass(frozen=True)
class LLMReportResult:
    report_text: str
    source: str


def _module_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _clean_text(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _parse_bool(value: str | None, *, default: bool) -> bool:
    cleaned = _clean_text(value)
    if cleaned is None:
        return default
    return cleaned.lower() in {"1", "true", "yes", "on"}


def _parse_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        values[key] = value.strip().strip('"').strip("'")
    return values


def load_llm_reporting_settings(
    *,
    env_file: Path | None = None,
    environ: Mapping[str, str] | None = None,
) -> LLMReportingSettings:
    resolved_env_file = env_file if env_file is not None else _module_project_root() / ".env"
    file_values = _parse_env_file(resolved_env_file)
    runtime_environ = dict(os.environ if environ is None else environ)

    def _read(name: str) -> str | None:
        value = runtime_environ.get(name)
        if value is None:
            value = file_values.get(name)
        return _clean_text(value)

    source_mode = (_read("STUDENT_BEHAVIOR_LLM_SOURCE_MODE") or "hybrid").lower()
    if source_mode not in _VALID_REPORT_SOURCES:
        source_mode = "hybrid"

    timeout_raw = _read("STUDENT_BEHAVIOR_LLM_TIMEOUT_SECONDS")
    try:
        timeout_seconds = float(timeout_raw) if timeout_raw is not None else 8.0
    except ValueError:
        timeout_seconds = 8.0

    return LLMReportingSettings(
        enabled=_parse_bool(_read("STUDENT_BEHAVIOR_LLM_ENABLED"), default=False),
        provider=_read("STUDENT_BEHAVIOR_LLM_PROVIDER") or "openai-compatible",
        base_url=_read("STUDENT_BEHAVIOR_LLM_BASE_URL"),
        model=_read("STUDENT_BEHAVIOR_LLM_MODEL"),
        api_key=_read("STUDENT_BEHAVIOR_LLM_API_KEY"),
        source_mode=source_mode,
        prompt_version=_read("STUDENT_BEHAVIOR_LLM_PROMPT_VERSION")
        or DEFAULT_LLM_PROMPT_VERSION,
        timeout_seconds=max(timeout_seconds, 1.0),
    )


def build_template_report_generation_metadata() -> dict[str, object]:
    return {
        "source": "template",
        "prompt_version": DEFAULT_TEMPLATE_PROMPT_VERSION,
        "fallback_reason": None,
        "provider": None,
        "model": None,
        "requested_source": "template",
        "requested_prompt_version": DEFAULT_TEMPLATE_PROMPT_VERSION,
    }


def _with_generation_metadata(
    payload: Mapping[str, object],
    *,
    source: str,
    prompt_version: str,
    fallback_reason: str | None,
    provider: str | None,
    model: str | None,
    requested_source: str,
    requested_prompt_version: str,
) -> dict[str, object]:
    updated = dict(payload)
    updated["report_source"] = source
    updated["prompt_version"] = prompt_version
    updated["report_generation"] = {
        "source": source,
        "prompt_version": prompt_version,
        "fallback_reason": fallback_reason,
        "provider": provider,
        "model": model,
        "requested_source": requested_source,
        "requested_prompt_version": requested_prompt_version,
    }
    return updated


def _fallback_reason(settings: LLMReportingSettings) -> str:
    if not settings.provider:
        return "missing_provider"
    if not settings.base_url:
        return "missing_base_url"
    if not settings.model:
        return "missing_model"
    if not settings.api_key:
        return "missing_api_key"
    return "llm_unavailable"


def _normalize_error_reason(message: str) -> str:
    cleaned = "_".join(part for part in message.lower().replace("-", " ").split() if part)
    return cleaned or "provider_error"


def _build_llm_messages(template_payload: Mapping[str, object], settings: LLMReportingSettings) -> list[dict[str, str]]:
    report_goal = "润色并增强模板报告" if settings.source_mode == "hybrid" else "生成完整学生风险报告"
    report_context = {
        "risk_level": template_payload.get("risk_level"),
        "top_risk_factors": template_payload.get("top_risk_factors"),
        "top_protective_factors": template_payload.get("top_protective_factors"),
        "intervention_plan": template_payload.get("intervention_plan"),
        "base_risk_explanation": template_payload.get("base_risk_explanation"),
        "behavior_adjustment_explanation": template_payload.get("behavior_adjustment_explanation"),
        "risk_change_explanation": template_payload.get("risk_change_explanation"),
        "template_report_text": template_payload.get("report_text"),
    }
    return [
        {
            "role": "system",
            "content": (
                "你是学生学业风险预警报告助手。"
                "只能基于输入事实进行总结，不做医学或心理学诊断，"
                "输出必须稳定、克制、可执行。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"任务：{report_goal}。\n"
                "请保留事实口径和风险等级，不要新增未提供的数据。\n"
                f"prompt_version={settings.prompt_version}\n"
                f"source_mode={settings.source_mode}\n"
                f"context={json.dumps(report_context, ensure_ascii=False)}"
            ),
        },
    ]


def _extract_message_content(content: object) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if not isinstance(item, Mapping):
                continue
            text = item.get("text")
            if isinstance(text, str) and text.strip():
                parts.append(text.strip())
        return "\n".join(parts).strip()
    return ""


def _default_generate_llm_report(request_payload: LLMReportRequest) -> LLMReportResult:
    settings = request_payload.settings
    if not settings.is_configured:
        raise LLMReportingError(_fallback_reason(settings))

    base_url = settings.base_url.rstrip("/")
    endpoint = (
        base_url
        if base_url.endswith("/chat/completions")
        else f"{base_url}/chat/completions"
    )
    payload = {
        "model": settings.model,
        "messages": _build_llm_messages(request_payload.template_payload, settings),
        "temperature": 0.2,
    }
    request_data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request_headers = {
        "Authorization": f"Bearer {settings.api_key}",
        "Content-Type": "application/json",
    }
    api_request = request.Request(
        endpoint,
        data=request_data,
        headers=request_headers,
        method="POST",
    )
    try:
        with request.urlopen(api_request, timeout=settings.timeout_seconds) as response:
            response_body = response.read().decode("utf-8")
    except error.HTTPError as exc:
        raise LLMReportingError(f"http_{exc.code}") from exc
    except error.URLError as exc:
        raise LLMReportingError("network_unavailable") from exc
    except TimeoutError as exc:
        raise LLMReportingError("request_timeout") from exc

    try:
        response_payload = json.loads(response_body)
        choices = response_payload["choices"]
        message = choices[0]["message"]
        report_text = _extract_message_content(message.get("content"))
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise LLMReportingError("invalid_provider_response") from exc

    if not report_text:
        raise LLMReportingError("empty_provider_response")

    return LLMReportResult(report_text=report_text, source=settings.source_mode)


def build_report_payload_with_fallback(
    *,
    template_payload: Mapping[str, object],
    llm_settings: LLMReportingSettings | None = None,
    generate_llm_report: Callable[[LLMReportRequest], LLMReportResult] | None = None,
) -> dict[str, object]:
    settings = llm_settings if llm_settings is not None else load_llm_reporting_settings()
    base_payload = dict(template_payload)

    if not settings.enabled:
        return _with_generation_metadata(
            base_payload,
            source="template",
            prompt_version=DEFAULT_TEMPLATE_PROMPT_VERSION,
            fallback_reason=None,
            provider=None,
            model=None,
            requested_source="template",
            requested_prompt_version=DEFAULT_TEMPLATE_PROMPT_VERSION,
        )

    if settings.source_mode == "template":
        return _with_generation_metadata(
            base_payload,
            source="template",
            prompt_version=DEFAULT_TEMPLATE_PROMPT_VERSION,
            fallback_reason=None,
            provider=None,
            model=None,
            requested_source="template",
            requested_prompt_version=DEFAULT_TEMPLATE_PROMPT_VERSION,
        )

    if not settings.is_configured:
        return _with_generation_metadata(
            base_payload,
            source="template",
            prompt_version=DEFAULT_TEMPLATE_PROMPT_VERSION,
            fallback_reason=_fallback_reason(settings),
            provider=settings.provider,
            model=settings.model,
            requested_source=settings.source_mode,
            requested_prompt_version=settings.prompt_version,
        )

    llm_request = LLMReportRequest(settings=settings, template_payload=base_payload)
    generator = generate_llm_report or _default_generate_llm_report
    try:
        result = generator(llm_request)
    except LLMReportingError as exc:
        return _with_generation_metadata(
            base_payload,
            source="template",
            prompt_version=DEFAULT_TEMPLATE_PROMPT_VERSION,
            fallback_reason=_normalize_error_reason(str(exc)),
            provider=settings.provider,
            model=settings.model,
            requested_source=settings.source_mode,
            requested_prompt_version=settings.prompt_version,
        )
    except Exception as exc:
        return _with_generation_metadata(
            base_payload,
            source="template",
            prompt_version=DEFAULT_TEMPLATE_PROMPT_VERSION,
            fallback_reason=_normalize_error_reason(str(exc)),
            provider=settings.provider,
            model=settings.model,
            requested_source=settings.source_mode,
            requested_prompt_version=settings.prompt_version,
        )

    if result.source not in _VALID_REPORT_SOURCES - {"template"}:
        return _with_generation_metadata(
            base_payload,
            source="template",
            prompt_version=DEFAULT_TEMPLATE_PROMPT_VERSION,
            fallback_reason="invalid_llm_source",
            provider=settings.provider,
            model=settings.model,
            requested_source=settings.source_mode,
            requested_prompt_version=settings.prompt_version,
        )

    report_text = result.report_text.strip()
    if not report_text:
        return _with_generation_metadata(
            base_payload,
            source="template",
            prompt_version=DEFAULT_TEMPLATE_PROMPT_VERSION,
            fallback_reason="empty_llm_report",
            provider=settings.provider,
            model=settings.model,
            requested_source=settings.source_mode,
            requested_prompt_version=settings.prompt_version,
        )

    updated_payload = dict(base_payload)
    updated_payload["report_text"] = report_text
    return _with_generation_metadata(
        updated_payload,
        source=result.source,
        prompt_version=settings.prompt_version,
        fallback_reason=None,
        provider=settings.provider,
        model=settings.model,
        requested_source=settings.source_mode,
        requested_prompt_version=settings.prompt_version,
    )
