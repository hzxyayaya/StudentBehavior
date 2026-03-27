from typing import Generic, TypeVar

from pydantic import BaseModel


class MetaModel(BaseModel):
    request_id: str
    term: str | None = None


T = TypeVar("T")


class Envelope(BaseModel, Generic[T]):
    code: int
    message: str
    data: T
    meta: MetaModel


class DemoLoginRequest(BaseModel):
    username: str
    password: str
    role: str


class DemoLoginResponse(BaseModel):
    session_token: str
