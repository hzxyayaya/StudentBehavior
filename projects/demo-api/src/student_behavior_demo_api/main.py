from fastapi import FastAPI

from student_behavior_demo_api.models import (
    DemoLoginRequest,
    DemoLoginResponse,
    Envelope,
    MetaModel,
)


app = FastAPI(title="Student Behavior Demo API")


@app.post("/api/auth/demo-login")
def demo_login(payload: DemoLoginRequest) -> Envelope[DemoLoginResponse]:
    return Envelope(
        code=200,
        message="OK",
        data=DemoLoginResponse(session_token="demo-token"),
        meta=MetaModel(request_id="demo-request"),
    )
