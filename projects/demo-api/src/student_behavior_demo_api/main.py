from functools import lru_cache
from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from fastapi import Query
from fastapi import Request
from fastapi.responses import JSONResponse
from scalar_fastapi import get_scalar_api_reference

from student_behavior_demo_api.models import (
    DemoLoginRequest,
    DemoLoginResponse,
    Envelope,
    MetaModel,
)
from student_behavior_demo_api.services import DemoApiStore


app = FastAPI(
    title="Student Behavior Demo API",
    description="学生行为分析演示后端，提供风险预警、学业轨迹、画像分层与发展方向等接口。",
    version="0.1.0",
    openapi_tags=[
        {"name": "认证", "description": "演示登录与会话相关接口。"},
        {"name": "总览分析", "description": "学期级总览与八维分析概览接口。"},
        {"name": "画像分层", "description": "学生群体分层、群体画像与群体主导因子接口。"},
        {"name": "轨迹分析", "description": "学业轨迹演化、关键行为因子与重点学生样本接口。"},
        {"name": "发展分析", "description": "专业对比、群体方向标签与发展方向关联分析接口。"},
        {"name": "模型说明", "description": "聚类与风险模型摘要说明接口。"},
        {"name": "学生画像", "description": "单个学生的学期画像与风险趋势接口。"},
        {"name": "学生报告", "description": "单个学生的个性化报告与干预建议接口。"},
        {"name": "风险预警", "description": "学期级风险预警分页与筛选接口。"},
        {"name": "结果输出", "description": "按比赛要求拆分的 8~10 个结果输出接口。"},
    ],
)


def _example_meta(term: str | None = None) -> dict[str, str | None]:
    return {
        "request_id": "demo-request",
        "term": term,
    }


def _error_example(message: str, term: str | None = None) -> dict:
    return {
        "code": 404 if message == "term not found" or message == "student not found" else 500,
        "message": message,
        "data": {},
        "meta": _example_meta(term),
    }


def _response_examples(success_example: dict, *, term: str | None = None) -> dict:
    return {
        200: {
            "description": "成功返回示例",
            "content": {
                "application/json": {
                    "example": success_example,
                }
            },
        },
        404: {
            "description": "未找到资源示例",
            "content": {
                "application/json": {
                    "example": _error_example("term not found", term),
                }
            },
        },
        500: {
            "description": "产物不可用示例",
            "content": {
                "application/json": {
                    "example": _error_example("artifacts unavailable", term),
                }
            },
        },
    }


@lru_cache(maxsize=1)
def get_store() -> DemoApiStore:
    return DemoApiStore()


@app.exception_handler(FileNotFoundError)
async def handle_file_not_found(request: Request, exc: FileNotFoundError) -> JSONResponse:
    return _error_envelope(
        status_code=500,
        message=_missing_artifact_message(exc),
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


@app.get("/scalar", include_in_schema=False)
def scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title="Student Behavior Demo API - Scalar",
    )


@app.post(
    "/api/auth/demo-login",
    tags=["认证"],
    summary="演示账号登录",
    description="返回固定的演示会话令牌，用于前端演示流程，不进行真实鉴权。",
    responses={
        200: {
            "description": "成功返回示例",
            "content": {
                "application/json": {
                    "example": {
                        "code": 200,
                        "message": "OK",
                        "data": {"session_token": "demo-token"},
                        "meta": _example_meta(),
                    }
                }
            },
        }
    },
)
def demo_login(payload: DemoLoginRequest) -> Envelope[DemoLoginResponse]:
    return Envelope(
        code=200,
        message="OK",
        data=DemoLoginResponse(session_token="demo-token"),
        meta=MetaModel(request_id="demo-request"),
    )


@app.get(
    "/api/analytics/overview",
    tags=["总览分析"],
    summary="获取学期总览分析",
    description="返回指定学期的总览指标，包括风险分布、八维摘要、群体分布与风险因子概览。",
    responses=_response_examples(
        {
            "code": 200,
            "message": "OK",
            "data": {
                "student_count": 220,
                "risk_distribution": {"high": 0, "medium": 49, "low": 171},
                "risk_band_distribution": {"高风险": 0, "较高风险": 12, "一般风险": 37, "低风险": 171},
                "dimension_summary": [
                    {"dimension": "学业基础表现", "average_score": 0.7, "label": "学业基础稳健"},
                    {"dimension": "课堂学习投入", "average_score": 0.28, "label": "课堂投入积极"},
                ],
            },
            "meta": _example_meta("2024-2"),
        },
        term="2024-2",
    ),
)
def get_overview(
    term: str = Query(description="学期标识，例如 2024-2", examples=["2024-2"]),
) -> Envelope[dict]:
    try:
        data = get_store().get_overview(term)
    except KeyError:
        return _error_envelope(status_code=404, message="term not found", term=term)
    except FileNotFoundError as exc:
        return _error_envelope(status_code=500, message=_missing_artifact_message(exc), term=term)
    except ValueError:
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    return Envelope(
        code=200,
        message="OK",
        data=data,
        meta=MetaModel(request_id="demo-request", term=term),
    )


@app.get(
    "/api/analytics/groups",
    tags=["画像分层"],
    summary="获取学生画像与群体分层分析",
    description="返回指定学期的群体分层结果，包括群体规模、平均风险分、风险变化摘要与群体主导因子。",
    responses=_response_examples(
        {
            "code": 200,
            "message": "OK",
            "data": {
                "groups": [
                    {
                        "group_segment": "作息失衡风险组",
                        "student_count": 220,
                        "avg_risk_probability": 0.4787,
                        "avg_risk_score": 24.47,
                    }
                ]
            },
            "meta": _example_meta("2024-2"),
        },
        term="2024-2",
    ),
)
def get_groups(
    term: str = Query(description="学期标识，例如 2024-2", examples=["2024-2"]),
) -> Envelope[dict]:
    try:
        data = get_store().get_groups(term=term)
    except KeyError as exc:
        if _is_unknown_term_error(exc, term):
            return _error_envelope(status_code=404, message="term not found", term=term)
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    except FileNotFoundError as exc:
        return _error_envelope(status_code=500, message=_missing_artifact_message(exc), term=term)
    except ValueError:
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    return Envelope(
        code=200,
        message="OK",
        data=data,
        meta=MetaModel(request_id="demo-request", term=term),
    )


@app.get(
    "/api/analytics/trajectory",
    tags=["轨迹分析"],
    summary="获取学业轨迹演化与关键行为分析",
    description="返回指定学期的学期风险轨迹、关键行为因子、当前维度摘要、重点群体变化与重点学生样本。",
    responses=_response_examples(
        {
            "code": 200,
            "message": "OK",
            "data": {
                "term": "2024-2",
                "risk_trend_summary": [
                    {"term": "2024-1", "avg_risk_score": 52.1, "high_risk_count": 4},
                    {"term": "2024-2", "avg_risk_score": 47.9, "high_risk_count": 0},
                ],
                "key_factors": [
                    {"feature": "academic_base", "feature_cn": "学业基础表现", "count": 220, "importance": 0.69}
                ],
                "student_samples": [
                    {"student_id": "pjxyqwbk686", "risk_level": "较高风险", "risk_probability": 0.74}
                ],
            },
            "meta": _example_meta("2024-2"),
        },
        term="2024-2",
    ),
)
def get_trajectory_analysis(
    term: str = Query(description="学期标识，例如 2024-2", examples=["2024-2"]),
) -> Envelope[dict]:
    try:
        data = get_store().get_trajectory_analysis(term=term)
    except KeyError:
        return _error_envelope(status_code=404, message="term not found", term=term)
    except FileNotFoundError as exc:
        return _error_envelope(status_code=500, message=_missing_artifact_message(exc), term=term)
    except ValueError:
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    return Envelope(
        code=200,
        message="OK",
        data=data,
        meta=MetaModel(request_id="demo-request", term=term),
    )


@app.get(
    "/api/analytics/development",
    tags=["发展分析"],
    summary="获取发展方向与去向关联分析",
    description="返回指定学期的专业对比、群体方向标签、方向解释链路，以及真实毕业去向分布与群体关联分析。",
    responses=_response_examples(
        {
            "code": 200,
            "message": "OK",
            "data": {
                "term": "2024-2",
                "major_comparison": [
                    {"major_name": "智能科学与技术", "high_risk_count": 3, "student_count": 28}
                ],
                "destination_distribution": {"升学": 18, "企业就业": 9},
                "major_destination_summary": [
                    {
                        "major_name": "智能科学与技术",
                        "student_count": 28,
                        "destination_student_count": 7,
                        "top_destination_label": "升学",
                        "top_destination_count": 4,
                        "destination_distribution": {"升学": 4, "企业就业": 3},
                    }
                ],
                "group_destination_association": [
                    {
                        "group_segment": "作息失衡风险组",
                        "destination_label": "升学",
                        "student_count": 6,
                        "group_student_count": 21,
                        "share_within_group": 0.2857,
                    }
                ],
                "group_direction_segments": [
                    {"group_segment": "作息失衡风险组", "direction_label": "偏向 课堂学习投入", "avg_risk_score": 24.47}
                ],
                "disclaimer": "去向分析已接入真实毕业去向数据；无匹配数据时相关字段返回空结果",
            },
            "meta": _example_meta("2024-2"),
        },
        term="2024-2",
    ),
)
def get_development_analysis(
    term: str = Query(description="学期标识，例如 2024-2", examples=["2024-2"]),
) -> Envelope[dict]:
    try:
        data = get_store().get_development_analysis(term=term)
    except KeyError:
        return _error_envelope(status_code=404, message="term not found", term=term)
    except FileNotFoundError as exc:
        return _error_envelope(status_code=500, message=_missing_artifact_message(exc), term=term)
    except ValueError:
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    return Envelope(
        code=200,
        message="OK",
        data=data,
        meta=MetaModel(request_id="demo-request", term=term),
    )


@app.get(
    "/api/models/summary",
    tags=["模型说明"],
    summary="获取模型摘要说明",
    description="返回当前演示系统使用的聚类与风险模型摘要，包括目标标签、AUC 与更新时间。",
    responses=_response_examples(
        {
            "code": 200,
            "message": "OK",
            "data": {
                "cluster_method": "stub-eight-dimension-group-rules",
                "risk_model": "stub-eight-dimension-risk-rules",
                "target_label": "学期级八维学业风险",
                "auc": 0.8347,
                "updated_at": "2026-04-02T11:58:27",
            },
            "meta": _example_meta("2024-2"),
        },
        term="2024-2",
    ),
)
def get_models_summary(
    term: str | None = Query(default=None, description="可选的学期标识，例如 2024-2", examples=["2024-2"]),
) -> Envelope[dict]:
    try:
        data = get_store().get_model_summary(term=term)
    except FileNotFoundError as exc:
        return _error_envelope(status_code=500, message=_missing_artifact_message(exc), term=term)
    except ValueError:
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    return Envelope(
        code=200,
        message="OK",
        data=data,
        meta=MetaModel(request_id="demo-request", term=term),
    )


@app.get(
    "/api/results/individual-profile",
    tags=["结果输出"],
    summary="获取学生个体画像结果",
    description="按结果口径输出学生个体画像，复用学生画像接口中的学生级风险与八维结果。",
)
def get_result_individual_profile(
    student_id: str = Query(description="学生学号"),
    term: str = Query(description="学期标识，例如 2024-2", examples=["2024-2"]),
) -> Envelope[dict]:
    try:
        data = get_store().get_result_individual_profile(student_id=student_id, term=term)
    except KeyError as exc:
        return _handle_result_lookup_error(exc, term=term, student_id=student_id)
    except FileNotFoundError as exc:
        return _error_envelope(status_code=500, message=_missing_artifact_message(exc), term=term)
    except ValueError:
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    return Envelope(code=200, message="OK", data=data, meta=MetaModel(request_id="demo-request", term=term))


@app.get(
    "/api/results/group-profile",
    tags=["结果输出"],
    summary="获取学生群体画像结果",
    description="按结果口径输出群体画像与分层结果，复用群体分层接口。",
)
def get_result_group_profile(
    term: str = Query(description="学期标识，例如 2024-2", examples=["2024-2"]),
) -> Envelope[dict]:
    try:
        data = get_store().get_result_group_profile(term=term)
    except KeyError as exc:
        return _handle_result_lookup_error(exc, term=term)
    except FileNotFoundError as exc:
        return _error_envelope(status_code=500, message=_missing_artifact_message(exc), term=term)
    except ValueError:
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    return Envelope(code=200, message="OK", data=data, meta=MetaModel(request_id="demo-request", term=term))


@app.get(
    "/api/results/behavior-patterns",
    tags=["结果输出"],
    summary="获取四类行为模式识别结果",
    description="按结果口径输出行为模式识别结果，基于群体标签分布和群体主导因子汇总行为模式。",
)
def get_result_behavior_patterns(
    term: str = Query(description="学期标识，例如 2024-2", examples=["2024-2"]),
) -> Envelope[dict]:
    try:
        data = get_store().get_result_behavior_patterns(term=term)
    except KeyError as exc:
        return _handle_result_lookup_error(exc, term=term)
    except FileNotFoundError as exc:
        return _error_envelope(status_code=500, message=_missing_artifact_message(exc), term=term)
    except ValueError:
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    return Envelope(code=200, message="OK", data=data, meta=MetaModel(request_id="demo-request", term=term))


@app.get(
    "/api/results/risk-probability",
    tags=["结果输出"],
    summary="获取学业风险概率分层结果",
    description="按结果口径输出风险概率分层与风险档位人数分布。",
)
def get_result_risk_probability(
    term: str = Query(description="学期标识，例如 2024-2", examples=["2024-2"]),
) -> Envelope[dict]:
    try:
        data = get_store().get_result_risk_probability(term=term)
    except KeyError as exc:
        return _handle_result_lookup_error(exc, term=term)
    except FileNotFoundError as exc:
        return _error_envelope(status_code=500, message=_missing_artifact_message(exc), term=term)
    except ValueError:
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    return Envelope(code=200, message="OK", data=data, meta=MetaModel(request_id="demo-request", term=term))


@app.get(
    "/api/results/risk-warning-level",
    tags=["结果输出"],
    summary="获取风险等级预警结果",
    description="按结果口径输出四档预警人数统计和高优先级预警样本。",
)
def get_result_risk_warning_level(
    term: str = Query(description="学期标识，例如 2024-2", examples=["2024-2"]),
) -> Envelope[dict]:
    try:
        data = get_store().get_result_risk_warning_level(term=term)
    except KeyError as exc:
        return _handle_result_lookup_error(exc, term=term)
    except FileNotFoundError as exc:
        return _error_envelope(status_code=500, message=_missing_artifact_message(exc), term=term)
    except ValueError:
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    return Envelope(code=200, message="OK", data=data, meta=MetaModel(request_id="demo-request", term=term))


@app.get(
    "/api/results/key-factors",
    tags=["结果输出"],
    summary="获取关键影响因子解释结果",
    description="按结果口径输出当前学期的关键风险因子摘要与重点关注因子。",
)
def get_result_key_factors(
    term: str = Query(description="学期标识，例如 2024-2", examples=["2024-2"]),
) -> Envelope[dict]:
    try:
        data = get_store().get_result_key_factors(term=term)
    except KeyError as exc:
        return _handle_result_lookup_error(exc, term=term)
    except FileNotFoundError as exc:
        return _error_envelope(status_code=500, message=_missing_artifact_message(exc), term=term)
    except ValueError:
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    return Envelope(code=200, message="OK", data=data, meta=MetaModel(request_id="demo-request", term=term))


@app.get(
    "/api/results/intervention-advice",
    tags=["结果输出"],
    summary="获取个性化干预建议结果",
    description="按结果口径输出指定学生在指定学期的干预建议与报告摘要。",
)
def get_result_intervention_advice(
    student_id: str = Query(description="学生学号"),
    term: str = Query(description="学期标识，例如 2024-2", examples=["2024-2"]),
) -> Envelope[dict]:
    try:
        data = get_store().get_result_intervention_advice(student_id=student_id, term=term)
    except KeyError as exc:
        return _handle_result_lookup_error(exc, term=term, student_id=student_id)
    except FileNotFoundError as exc:
        return _error_envelope(status_code=500, message=_missing_artifact_message(exc), term=term)
    except ValueError:
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    return Envelope(code=200, message="OK", data=data, meta=MetaModel(request_id="demo-request", term=term))


@app.get(
    "/api/results/term-trend",
    tags=["结果输出"],
    summary="获取学期趋势分析结果",
    description="按结果口径输出学期风险趋势变化摘要。",
)
def get_result_term_trend(
    term: str = Query(description="学期标识，例如 2024-2", examples=["2024-2"]),
) -> Envelope[dict]:
    try:
        data = get_store().get_result_term_trend(term=term)
    except KeyError as exc:
        return _handle_result_lookup_error(exc, term=term)
    except FileNotFoundError as exc:
        return _error_envelope(status_code=500, message=_missing_artifact_message(exc), term=term)
    except ValueError:
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    return Envelope(code=200, message="OK", data=data, meta=MetaModel(request_id="demo-request", term=term))


@app.get(
    "/api/results/major-comparison",
    tags=["结果输出"],
    summary="获取专业与学院群体对比结果",
    description="按结果口径输出专业维度的风险对比结果。",
)
def get_result_major_comparison(
    term: str = Query(description="学期标识，例如 2024-2", examples=["2024-2"]),
) -> Envelope[dict]:
    try:
        data = get_store().get_result_major_comparison(term=term)
    except KeyError as exc:
        return _handle_result_lookup_error(exc, term=term)
    except FileNotFoundError as exc:
        return _error_envelope(status_code=500, message=_missing_artifact_message(exc), term=term)
    except ValueError:
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    return Envelope(code=200, message="OK", data=data, meta=MetaModel(request_id="demo-request", term=term))


@app.get(
    "/api/results/model-summary",
    tags=["结果输出"],
    summary="获取模型摘要说明结果",
    description="按结果口径输出模型摘要，供比赛指标中的模型说明结果直接使用。",
)
def get_result_model_summary(
    term: str = Query(description="学期标识，例如 2024-2", examples=["2024-2"]),
) -> Envelope[dict]:
    try:
        data = get_store().get_result_model_summary(term=term)
    except FileNotFoundError as exc:
        return _error_envelope(status_code=500, message=_missing_artifact_message(exc), term=term)
    except ValueError:
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    return Envelope(code=200, message="OK", data=data, meta=MetaModel(request_id="demo-request", term=term))


@app.get(
    "/api/students/{student_id}/profile",
    tags=["学生画像"],
    summary="获取学生个体画像",
    description="返回指定学生在指定学期的风险信息、八维结果与学期趋势，用于学生级画像展示。",
    responses=_response_examples(
        {
            "code": 200,
            "message": "OK",
            "data": {
                "student_id": "pjxyqwbk686",
                "student_name": "pjxyqwbk686",
                "risk_level": "较高风险",
                "risk_probability": 0.74,
                "dimension_scores": [{"dimension": "学业基础表现", "score": 0.31, "label": "学业基础预警"}],
            },
            "meta": _example_meta("2024-2"),
        },
        term="2024-2",
    ),
)
def get_student_profile(
    student_id: str,
    term: str = Query(description="学期标识，例如 2024-2", examples=["2024-2"]),
) -> Envelope[dict]:
    try:
        data = get_store().get_student_profile(student_id=student_id, term=term)
    except KeyError:
        return _error_envelope(status_code=404, message="student not found", term=term)
    except FileNotFoundError as exc:
        return _error_envelope(status_code=500, message=_missing_artifact_message(exc), term=term)
    except ValueError:
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    return Envelope(
        code=200,
        message="OK",
        data=data,
        meta=MetaModel(request_id="demo-request", term=term),
    )


@app.get(
    "/api/students/{student_id}/report",
    tags=["学生报告"],
    summary="获取学生个性化报告",
    description="返回指定学生在指定学期的风险解释、主导因子、干预建议与报告文本。",
    responses=_response_examples(
        {
            "code": 200,
            "message": "OK",
            "data": {
                "risk_level": "较高风险",
                "top_factors": [{"dimension": "学业基础表现", "importance": 0.69}],
                "intervention_advice": ["优先补齐高风险课程与课堂投入"],
                "report_text": "当前学生处于较高风险，需要优先关注学业基础与课堂投入。",
            },
            "meta": _example_meta("2024-2"),
        },
        term="2024-2",
    ),
)
def get_student_report(
    student_id: str,
    term: str = Query(description="学期标识，例如 2024-2", examples=["2024-2"]),
) -> Envelope[dict]:
    try:
        data = get_store().get_student_report(student_id=student_id, term=term)
    except KeyError:
        return _error_envelope(status_code=404, message="student not found", term=term)
    except FileNotFoundError as exc:
        return _error_envelope(status_code=500, message=_missing_artifact_message(exc), term=term)
    except ValueError:
        return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
    return Envelope(
        code=200,
        message="OK",
        data=data,
        meta=MetaModel(request_id="demo-request", term=term),
    )


@app.get(
    "/api/warnings",
    tags=["风险预警"],
    summary="获取学业风险预警列表",
    description="返回指定学期的风险预警学生分页列表，支持按风险等级、群体、专业与风险变化方向筛选。",
    responses=_response_examples(
        {
            "code": 200,
            "message": "OK",
            "data": {
                "items": [
                    {
                        "student_id": "pjxyqwbk686",
                        "student_name": "pjxyqwbk686",
                        "risk_level": "较高风险",
                        "risk_probability": 0.74,
                    }
                ],
                "page": 1,
                "page_size": 20,
                "total": 49,
            },
            "meta": _example_meta("2024-2"),
        },
        term="2024-2",
    ),
)
def get_warnings(
    term: str = Query(description="学期标识，例如 2024-2", examples=["2024-2"]),
    page: int = Query(default=1, ge=1, description="分页页码，从 1 开始"),
    page_size: int = Query(default=20, ge=1, le=200, description="每页条数，范围 1-200"),
    risk_level: Literal["high", "medium", "low", "高风险", "较高风险", "一般风险", "低风险"] | None = Query(
        default=None,
        description="按风险等级筛选，支持高风险、较高风险、一般风险、低风险，以及 high/medium/low",
    ),
    group_segment: str | None = Query(default=None, min_length=1),
    major_name: str | None = Query(default=None, description="按专业名称筛选"),
    risk_change_direction: Literal["rising", "steady", "falling"] | None = Query(
        default=None,
        description="按风险变化方向筛选，rising 为上升，steady 为持平，falling 为下降",
    ),
) -> Envelope[dict]:
    try:
        data = get_store().list_warnings(
            term=term,
            page=page,
            page_size=page_size,
            risk_level=risk_level,
            group_segment=group_segment,
            major_name=major_name,
            risk_change_direction=risk_change_direction,
        )
    except KeyError:
        return _error_envelope(status_code=404, message="term not found", term=term)
    except FileNotFoundError as exc:
        return _error_envelope(status_code=500, message=_missing_artifact_message(exc), term=term)
    except ValueError:
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


def _missing_artifact_message(exc: FileNotFoundError) -> str:
    if not exc.args:
        return "artifacts unavailable"

    artifact_name = Path(str(exc.args[0])).name
    if artifact_name == "v1_overview_by_term.json":
        return "overview artifact unavailable"
    if artifact_name == "v1_model_summary.json":
        return "model summary artifact unavailable"
    if artifact_name == "v1_student_results.csv":
        return "student results artifact unavailable"
    if artifact_name == "v1_student_reports.jsonl":
        return "student reports artifact unavailable"
    if artifact_name:
        return f"{artifact_name} unavailable"
    return "artifacts unavailable"


def _is_unknown_term_error(exc: KeyError, term: str) -> bool:
    return len(exc.args) == 1 and exc.args[0] == term


def _is_unknown_student_error(exc: KeyError, student_id: str, term: str) -> bool:
    return len(exc.args) == 1 and exc.args[0] == (student_id, term)


def _handle_result_lookup_error(exc: KeyError, *, term: str, student_id: str | None = None) -> JSONResponse:
    if student_id is not None and _is_unknown_student_error(exc, student_id, term):
        return _error_envelope(status_code=404, message="student not found", term=term)
    if _is_unknown_term_error(exc, term):
        return _error_envelope(status_code=404, message="term not found", term=term)
    return _error_envelope(status_code=500, message="artifacts unavailable", term=term)
