# V1 API Contract

Status: Current

Last Updated: 2026-03-28

## 0. Current Artifact Baseline

当前 API 读取的离线产物已经基于真实 Excel 特征重建过一轮：

- `artifacts/semester_features/v1_semester_features.csv`: `2905` 行
- `artifacts/model_stubs/v1_student_results.csv`: `2905` 行
- 当前总览产物中的风险分布：
  - `high = 0`
  - `medium = 50`
  - `low = 2855`

这意味着：

- Demo 的“底层输入特征”已经主要来自真实数据
- 但 API 返回中的风险相关字段仍然是规则版结果，不应解释为正式模型预测

本文档描述当前主工作区 `projects/demo-api` 的真实接口口径，供前端联调、代码审查和交接文档引用。

## 1. Response Envelope

```json
{
  "code": 200,
  "message": "OK",
  "data": {},
  "meta": {
    "request_id": "demo-request",
    "term": "2024-2"
  }
}
```

统一规则：

- 成功响应：`code = 200`
- 学期或学生不存在：HTTP `404`，同时 `code = 404`
- 产物缺失或不可用：HTTP `500`，同时 `code = 500`

## 2. Shared Fields

- `risk_level`: `high` / `medium` / `low`
- `group_segment`: 系统输出的行为模式或群体标签

说明：

- 旧实现中的 `quadrant_label` 仅作为历史兼容字段存在
- 新接口、新页面和新结果层不应再把 `quadrant_label` 作为主字段

## 3. Real Demo Values

当前真实联调值：

- `term`: `2023-2`、`2024-1`、`2024-2`
- 示例学生：`pjwrqxbj901`

以下旧值不要继续使用：

- `2023-1`
- `20230001`

## 4. Endpoints

### POST `/api/auth/demo-login`

Request:

```json
{
  "username": "demo_admin",
  "password": "demo_only",
  "role": "manager"
}
```

Response `data`:

```json
{
  "session_token": "demo-token"
}
```

说明：

- 当前接口只返回固定演示 token
- 不返回 `user_id`、`display_name`、`role`

### GET `/api/analytics/overview?term=2024-2`

Response `data`:

```json
{
  "student_count": 179,
  "risk_distribution": [
    { "risk_level": "high", "count": 12 },
    { "risk_level": "medium", "count": 34 },
    { "risk_level": "low", "count": 133 }
  ],
  "group_distribution": [
    { "group_segment": "学习投入稳定组", "count": 45 },
    { "group_segment": "课堂参与薄弱组", "count": 51 },
    { "group_segment": "作息失衡风险组", "count": 39 },
    { "group_segment": "综合发展优势组", "count": 44 }
  ],
  "major_risk_summary": [
    { "major_name": "计算机科学与技术", "high_risk_count": 5, "student_count": 18 }
  ],
  "trend_summary": [
    { "term": "2024-1", "high_risk_count": 10 },
    { "term": "2024-2", "high_risk_count": 12 }
  ]
}
```

### GET `/api/analytics/groups?term=2024-2`

Response `data`:

```json
{
  "groups": [
    {
      "group_segment": "作息失衡风险组",
      "student_count": 39,
      "avg_risk_probability": 0.81,
      "top_factors": [
        { "dimension": "课堂学习投入", "explanation": "课堂参与偏低与风险升高相关" }
      ]
    }
  ]
}
```

### GET `/api/warnings?term=2024-2&page=1&page_size=20&risk_level=high`

可选查询参数：

- `page`
- `page_size`
- `risk_level`
- `group_segment`
- `major_name`

Response `data`:

```json
{
  "items": [
    {
      "student_id": "pjwrqxbj901",
      "student_name": "示例学生",
      "major_name": "计算机科学与技术",
      "group_segment": "作息失衡风险组",
      "risk_level": "high",
      "risk_probability": 0.82
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 12
}
```

### GET `/api/students/{student_id}/profile?term=2024-2`

Response `data`:

```json
{
  "student_id": "pjwrqxbj901",
  "student_name": "示例学生",
  "major_name": "计算机科学与技术",
  "group_segment": "作息失衡风险组",
  "risk_level": "high",
  "risk_probability": 0.82,
  "dimension_scores": [
    { "dimension": "课堂学习投入", "score": 0.26 }
  ],
  "trend": [
    { "term": "2024-2", "risk_probability": 0.82 }
  ]
}
```

### GET `/api/students/{student_id}/report?term=2024-2`

Response `data`:

```json
{
  "top_factors": [
    {
      "dimension": "课堂学习投入",
      "explanation": "课堂参与下降与风险升高相关",
      "direction": "up",
      "impact": 0.21
    }
  ],
  "intervention_advice": [
    "安排阶段性学习跟踪"
  ],
  "report_text": "当前学生处于较高风险。"
}
```

### GET `/api/models/summary?term=2024-2`

Response `data`:

```json
{
  "cluster_method": "stub-quadrant-rules",
  "risk_model": "stub-risk-rules",
  "target_label": "综合测评低等级风险",
  "auc": 0.81,
  "updated_at": "2026-03-28T12:00:00+08:00"
}
```

### Planned Analytics Endpoints

后续建议补强以下接口，以完整承接 4 类分析任务和 10 个系统输出：

- `GET /api/analytics/groups`
- `GET /api/analytics/trends`
- `GET /api/analytics/majors`
- `GET /api/analytics/directions`

## 5. Error Semantics

- 学期不存在：`message = "term not found"`
- 学生不存在：`message = "student not found"`
- 产物缺失：
  - `overview artifact unavailable`
  - `model summary artifact unavailable`
  - `student results artifact unavailable`
  - `student reports artifact unavailable`
  - 或统一退化为 `artifacts unavailable`

## 6. Stub Boundary

以下字段仍是 stub/规则版结果，不要在前端文案、PR 描述或汇报材料中误称为正式模型结果：

- `risk_probability`
- `risk_level`
- `quadrant_label`
- `top_factors`
- `intervention_advice`
- `report_text`
- `cluster_method`
- `risk_model`
- `target_label`

若当前历史实现中仍返回 `quadrant_label`，应视为兼容性字段，而不是新的冻结业务表达。
