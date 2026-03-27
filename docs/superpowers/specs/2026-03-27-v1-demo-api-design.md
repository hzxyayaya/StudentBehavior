# V1 Demo API 设计

Status: Draft for implementation planning

Last Updated: 2026-03-27

## 1. 文档目的

本文档用于冻结 `V1-IMPL-003` 的 Demo API 设计，作为后续 `projects/demo-api` 实现、前端联调和演示验收的共同基线。

这一步的目标不是建设正式后端系统，而是：

- 读取已经生成好的离线结果产物
- 按冻结的 API contract 返回稳定 JSON
- 打通“结果层 -> 接口层 -> 页面层”的展示闭环
- 为后续接入真实数据库、真实模型和正式认证预留清晰边界

## 2. 设计结论

V1 应新增独立子项目 `projects/demo-api`，职责仅限于：

- 读取 `artifacts/model_stubs` 下的离线结果文件
- 对结果做最小必要的筛选、分页、聚合和格式转换
- 按 `v1-api-contract.md` 返回统一 envelope
- 提供最轻量的 `demo-login` 固定返回

因此，`demo-api` 是只读接口层，不是模型服务层，也不是数据库服务层。

## 3. 上下游边界

### 3.1 上游输入

`demo-api` 首版只依赖 `projects/model-stubs` 产出的离线文件：

- `artifacts/model_stubs/v1_student_results.csv`
- `artifacts/model_stubs/v1_student_reports.jsonl`
- `artifacts/model_stubs/v1_overview_by_term.json`
- `artifacts/model_stubs/v1_model_summary.json`
- `artifacts/model_stubs/v1_warnings.json`

其中核心输入是：

- `v1_student_results.csv`
- `v1_student_reports.jsonl`
- `v1_overview_by_term.json`
- `v1_model_summary.json`

`v1_warnings.json` 首版主要用于服务健康和数据摘要校验，不作为页面主数据源。

### 3.2 下游消费者

`demo-api` 的下游只面向：

- 前端 Demo 页面
- 本地接口联调
- 演示和答辩环境

首版不承担：

- 正式用户系统
- 正式鉴权授权
- 数据库写入
- 在线模型推理

### 3.3 分层职责

- `projects/semester-etl`：原始 Excel -> 初始学期级结果
- `projects/analytics-db`：标准化事实/维度 -> `student_term_features`
- `projects/model-stubs`：`student_term_features` -> 风险/分层/解释/建议/总览结果文件
- `projects/demo-api`：读取结果文件并对外提供 HTTP 接口

## 4. 为什么当前阶段先做只读文件 API

当前项目最需要的是完整 Demo 闭环，而不是进一步增加底层复杂度。

如果现在直接做正式后端系统，会同时引入以下额外不稳定因素：

- 数据库在线查询接口尚未冻结
- 正式认证、会话、权限体系不在当前主线范围
- 真实模型尚未替换到位
- 页面还缺少可以稳定消费的接口

因此 V1 先做只读文件 API 的原因是：

- 让前端不再直接依赖静态 mock
- 让字段命名、分页、筛选、错误行为先稳定
- 后续替换数据源时尽量不动页面
- 把复杂度控制在“只读产物 + contract 对齐”这一层

## 5. 项目结构

建议新建：

- `projects/demo-api/pyproject.toml`
- `projects/demo-api/src/student_behavior_demo_api/config.py`
- `projects/demo-api/src/student_behavior_demo_api/models.py`
- `projects/demo-api/src/student_behavior_demo_api/loaders.py`
- `projects/demo-api/src/student_behavior_demo_api/services.py`
- `projects/demo-api/src/student_behavior_demo_api/main.py`
- `projects/demo-api/tests/...`

推荐职责拆分：

- `config.py`
  - 默认结果目录
  - 分页默认值
  - demo token
- `models.py`
  - Pydantic 请求/响应模型
  - 统一 response envelope
- `loaders.py`
  - 读取 CSV / JSON / JSONL
  - 文件存在性和字段完整性校验
- `services.py`
  - term 过滤
  - 分页
  - `profile` / `report` / `quadrants` 组装
- `main.py`
  - FastAPI app
  - 路由注册
  - 异常处理

## 6. 技术选型

首版建议使用：

- Python 3.12+
- `uv`
- `fastapi`
- `uvicorn`
- `pydantic`
- `pandas`
- `pytest`

选择 FastAPI 的原因：

- 路由和响应模型定义更清晰
- 后续联调和接口文档更方便
- 对当前这种“小型只读 API” 足够轻量

## 7. 首版接口范围

首版固定实现以下 6 个核心接口和 1 个最轻登录接口。

### 7.1 POST `/api/auth/demo-login`

用途：

- 让前端登录流程先跑通

首版策略：

- 接收 `username`、`password`、`role`
- 不做真实认证
- 固定返回 demo 账号信息和固定 token

冻结要求：

- 返回结构必须符合 `v1-api-contract.md`
- 不引入数据库 session
- 不引入 JWT

### 7.2 GET `/api/analytics/overview`

主要来源：

- `v1_overview_by_term.json`

返回：

- `student_count`
- `risk_distribution`
- `quadrant_distribution`
- `major_risk_summary`
- `trend_summary`

冻结要求：

- 必须按 `term` 返回单学期总览
- 若 `term` 不存在，明确报错，不伪装为空结果

### 7.3 GET `/api/analytics/quadrants`

主要来源：

- `v1_student_results.csv`
- `v1_student_reports.jsonl`
- 可辅助读取 `v1_overview_by_term.json`

返回：

- `quadrants`
  - `quadrant_label`
  - `student_count`
  - `avg_risk_probability`
  - `top_factors`

首版聚合策略：

- 对当前 `term` 的学生结果按 `quadrant_label` 分组
- `student_count` 为组内人数
- `avg_risk_probability` 为组内平均值
- `top_factors` 由该象限学生报告中的 `top_factors` 频次汇总得到

首版不做复杂文本聚类或语义归并。

### 7.4 GET `/api/warnings`

主要来源：

- `v1_student_results.csv`

支持参数：

- `term`
- `page`
- `page_size`
- `risk_level`
- `quadrant_label`
- `major_name`

返回：

- `items`
- `page`
- `page_size`
- `total`

冻结要求：

- 默认按 `risk_probability desc, student_id asc` 排序
- 所有筛选都在内存数据上完成
- 分页逻辑在 service 层实现，不在路由层堆逻辑

### 7.5 GET `/api/students/{student_id}/profile`

主要来源：

- `v1_student_results.csv`

返回：

- `student_id`
- `student_name`
- `major_name`
- `quadrant_label`
- `risk_level`
- `risk_probability`
- `dimension_scores`
- `trend`

首版组装策略：

- 当前学期主记录来自 `student_results`
- `dimension_scores_json` 解包为数组
- `trend` 从同一学生跨学期结果中组装

冻结要求：

- `dimension_scores` 字段名必须与 contract 保持一致
- `trend` 按时间顺序返回

### 7.6 GET `/api/students/{student_id}/report`

主要来源：

- `v1_student_reports.jsonl`

返回：

- `top_factors`
- `intervention_advice`
- `report_text`

冻结要求：

- 只按 `student_id + term` 精确定位
- 不从别的文件临时拼装解释字段

### 7.7 GET `/api/models/summary`

主要来源：

- `v1_model_summary.json`

返回：

- `cluster_method`
- `risk_model`
- `target_label`
- `auc`
- `updated_at`

首版策略：

- 接受 `term` 参数
- 但摘要文件仍为全局单文件
- 不按 term 分文件维护

## 8. 与冻结 API Contract 的映射要求

`demo-api` 的核心要求不是重新设计接口，而是忠实实现冻结 contract。

必须对齐：

- Response envelope:
  - `code`
  - `message`
  - `data`
  - `meta`
- `risk_level` 枚举：
  - `high`
  - `medium`
  - `low`
- `quadrant_label` 枚举：
  - `自律共鸣型`
  - `被动守纪型`
  - `脱节离散型`
  - `情绪驱动型`

首版允许的轻量转换：

- `dimension_scores_json` -> `dimension_scores`
- `student_reports.jsonl` 中的记录解包为接口结构
- 对 overview / quadrants 做有限的 service 组装

首版不允许的行为：

- 自行更改字段名
- 自行追加未冻结字段
- 用不存在的真实模型名替换 `stub` 结果来源

## 9. 错误处理

首版错误处理保持简单且一致。

### 9.1 文件缺失

若所需产物文件不存在：

- 返回 `500`
- `message` 明确指出缺失的产物类型
- 不伪装为空数据

### 9.2 请求 term 不存在

若请求的 `term` 不存在于当前结果中：

- 返回 `404`

### 9.3 请求 student 不存在

若请求的 `student_id + term` 组合不存在：

- 返回 `404`

### 9.4 参数非法

例如：

- `page <= 0`
- `page_size <= 0`
- 非法枚举值

返回：

- `422`

### 9.5 错误响应 envelope

即使错误，也保持统一 envelope：

```json
{
  "code": 1001,
  "message": "term not found",
  "data": {},
  "meta": {
    "request_id": "req_demo_001",
    "term": "2023-1"
  }
}
```

## 10. 缓存策略

首版不引入 Redis 或外部缓存。

推荐策略：

- 服务启动时读取一次结果文件
- 将结果缓存在进程内
- 请求阶段只做只读查询

后续若需要支持热刷新，可再增加显式 reload 机制，但不属于本次实现范围。

## 11. 测试策略

首版按 3 层测试。

### 11.1 Loader 测试

覆盖：

- CSV / JSON / JSONL 读取成功
- 缺文件时报错
- 字段缺失时报错

### 11.2 Service 测试

覆盖：

- `overview` 按 term 返回
- `warnings` 筛选和分页
- `profile` 解包 `dimension_scores_json`
- `report` 按 `student_id + term` 返回
- `quadrants` 聚合人数、均值和因子

### 11.3 API 集成测试

使用 FastAPI `TestClient`：

- 覆盖 6 个核心接口
- 断言统一 envelope
- 覆盖 `404 / 422 / 500`

## 12. 首版验收标准

若满足以下条件，则认为首版 `demo-api` 达成目标：

- `uv run --project projects/demo-api uvicorn student_behavior_demo_api.main:app --reload` 能启动
- 首版接口全部可调用
- 响应字段与 `v1-api-contract.md` 对齐
- `warnings` 支持分页和筛选
- `profile` 包含趋势和维度分数
- `report` 包含解释和建议
- `overview` 和 `quadrants` 能支撑总览页和群体页
- loader、service、API 测试可跑通
- 缺产物时错误行为明确

## 13. 明确不在本次范围内的内容

以下内容不属于 `V1-IMPL-003`：

- 正式用户体系
- JWT / refresh token
- 数据库读写
- 在线模型推理
- 结果重新计算
- WebSocket 或实时推送
- 生产级缓存和部署编排

## 14. 后续替换路径

当前首版的核心目标是让接口边界先稳定。

后续增强时，优先替换以下内部实现，而不推翻对外接口：

- 将文件 loader 替换为数据库/对象存储读取
- 将 `stub` 风险结果替换为正式模型结果
- 将规则型解释和建议替换为正式解释链路
- 将最轻 `demo-login` 替换为正式认证机制

这样可以保证：

- 前端页面尽量少改
- contract 尽量不改
- Demo 可以快速演化到正式系统
