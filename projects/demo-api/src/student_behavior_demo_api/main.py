from fastapi import FastAPI
from fastapi import HTTPException

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
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="term not found") from exc
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
