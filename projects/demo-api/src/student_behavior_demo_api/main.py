from functools import lru_cache
from typing import Literal

from fastapi import FastAPI
from fastapi import Query
from fastapi import Request
from fastapi.responses import JSONResponse

from student_behavior_demo_api.models import (
    DemoLoginRequest,
    DemoLoginResponse,
    Envelope,
    MetaModel,
)
from student_behavior_demo_api.services import DemoApiStore


app = FastAPI(title="Student Behavior Demo API")


@lru_cache(maxsize=1)
def get_store() -> DemoApiStore:
    return DemoApiStore()


@app.exception_handler(FileNotFoundError)
async def handle_file_not_found(request: Request, _exc: FileNotFoundError) -> JSONResponse:
    return _error_envelope(
        status_code=500,
        message="artifacts unavailable",
        term=request.query_params.get("term"),
    )


@app.exception_handler(LookupError)
async def handle_lookup_error(request: Request, _exc: LookupError) -> JSONResponse:
    message = "student not found" if request.url.path.startswith("/api/students/") else "term not found"
    return _error_envelope(
        status_code=404,
        message=message,
        term=request.query_params.get("term"),
    )


@app.post("/api/auth/demo-login")
def demo_login(payload: DemoLoginRequest) -> Envelope[DemoLoginResponse]:
    return Envelope(
        code=200,
        message="OK",
        data=DemoLoginResponse(session_token="demo-token"),
        meta=MetaModel(request_id="demo-request"),
    )


@app.get("/api/analytics/overview")
def get_overview(term: str) -> Envelope[dict]:
    try:
        data = get_store().get_overview(term)
    except KeyError:
        return _error_envelope(status_code=404, message="term not found", term=term)
    except (FileNotFoundError, ValueError):
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    return Envelope(
        code=200,
        message="OK",
        data=data,
        meta=MetaModel(request_id="demo-request", term=term),
    )


@app.get("/api/analytics/quadrants")
def get_quadrants(term: str) -> Envelope[dict]:
    try:
        data = get_store().get_quadrants(term=term)
    except KeyError as exc:
        if _is_unknown_term_error(exc, term):
            return _error_envelope(status_code=404, message="term not found", term=term)
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    except (FileNotFoundError, ValueError):
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    return Envelope(
        code=200,
        message="OK",
        data=data,
        meta=MetaModel(request_id="demo-request", term=term),
    )


@app.get("/api/models/summary")
def get_models_summary(term: str | None = None) -> Envelope[dict]:
    try:
        data = get_store().get_model_summary(term=term)
    except (FileNotFoundError, ValueError):
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    return Envelope(
        code=200,
        message="OK",
        data=data,
        meta=MetaModel(request_id="demo-request", term=term),
    )


@app.get("/api/students/{student_id}/profile")
def get_student_profile(student_id: str, term: str) -> Envelope[dict]:
    try:
        data = get_store().get_student_profile(student_id=student_id, term=term)
    except KeyError:
        return _error_envelope(status_code=404, message="student not found", term=term)
    except (FileNotFoundError, ValueError):
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    return Envelope(
        code=200,
        message="OK",
        data=data,
        meta=MetaModel(request_id="demo-request", term=term),
    )


@app.get("/api/students/{student_id}/report")
def get_student_report(student_id: str, term: str) -> Envelope[dict]:
    try:
        data = get_store().get_student_report(student_id=student_id, term=term)
    except KeyError:
        return _error_envelope(status_code=404, message="student not found", term=term)
    except (FileNotFoundError, ValueError):
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    return Envelope(
        code=200,
        message="OK",
        data=data,
        meta=MetaModel(request_id="demo-request", term=term),
    )


@app.get("/api/warnings")
def get_warnings(
    term: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=200),
    risk_level: Literal["high", "medium", "low"] | None = None,
    quadrant_label: Literal["自律共鸣型", "被动守纪型", "脱节离散型", "情绪驱动型"] | None = None,
    major_name: str | None = None,
) -> Envelope[dict]:
    try:
        data = get_store().list_warnings(
            term=term,
            page=page,
            page_size=page_size,
            risk_level=risk_level,
            quadrant_label=quadrant_label,
            major_name=major_name,
        )
    except KeyError:
        return _error_envelope(status_code=404, message="term not found", term=term)
    except (FileNotFoundError, ValueError):
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    return Envelope(
        code=200,
        message="OK",
        data=data,
        meta=MetaModel(request_id="demo-request", term=term),
    )


def _error_envelope(status_code: int, message: str, term: str | None = None) -> JSONResponse:
    payload = Envelope(
        code=status_code,
        message=message,
        data={},
        meta=MetaModel(request_id="demo-request", term=term),
    )
    return JSONResponse(status_code=status_code, content=payload.model_dump())


def _is_unknown_term_error(exc: KeyError, term: str) -> bool:
    return len(exc.args) == 1 and exc.args[0] == term
