from fastapi import FastAPI
from fastapi.responses import JSONResponse

from student_behavior_demo_api.models import (
    DemoLoginRequest,
    DemoLoginResponse,
    Envelope,
    MetaModel,
)
from student_behavior_demo_api.services import DemoApiStore


app = FastAPI(title="Student Behavior Demo API")
store = DemoApiStore()


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
        data = store.get_overview(term)
    except KeyError:
        return _error_envelope(status_code=404, message="term not found", term=term)
    return Envelope(
        code=200,
        message="OK",
        data=data,
        meta=MetaModel(request_id="demo-request", term=term),
    )


@app.get("/api/models/summary")
def get_models_summary(term: str | None = None) -> Envelope[dict]:
    return Envelope(
        code=200,
        message="OK",
        data=store.get_model_summary(term=term),
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
