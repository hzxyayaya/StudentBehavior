from typing import Generic, TypeVar

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class MetaModel(BaseModel):
    request_id: str = Field(description="请求唯一标识")
    term: str | None = Field(default=None, description="当前接口对应的学期标识")


T = TypeVar("T")


class Envelope(BaseModel, Generic[T]):
    code: int = Field(description="业务状态码，200 表示成功")
    message: str = Field(description="接口状态说明")
    data: T
    meta: MetaModel = Field(description="响应元信息")


class DemoLoginRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "demo_admin",
                "password": "demo_only",
                "role": "manager",
            }
        }
    )

    username: str = Field(description="演示登录用户名")
    password: str = Field(description="演示登录密码")
    role: str = Field(description="演示账号角色")


class DemoLoginResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_token": "demo-token",
            }
        }
    )

    session_token: str = Field(description="演示登录成功后返回的会话令牌")
