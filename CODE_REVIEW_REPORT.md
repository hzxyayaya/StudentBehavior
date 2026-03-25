# StudentBehavior Code Review Report

## Scope

- 审查范围：
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_frontend`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server`
- 审查基准：
  - 仅以当前 Vue 3 + FastAPI 实际代码、配置、路由、类型、运行行为为准
  - 不把 `C:\Users\Orion\Desktop\StudentBehavior\ARCHITECTURE_MANUAL.md` 作为当前实现依据
- 本次还额外对照了 `C:\Users\Orion\Desktop\StudentBehavior\修复进展说明.md`，用于判断“已修复项”是否已经真实落到代码

## System Summary

- 前端当前是 Vue 3 + Pinia + Vue Router + Axios，`src/utils/request.ts` 负责统一注入 token，并对默认 `{ status, data, meta }` 响应做自动解包。
- 后端当前是 FastAPI + SQLAlchemy + MySQL，暴露 `/api/v1/auth`、`/students`、`/warnings`、`/analytics`、`/features`、`/model`、`/report` 等接口。
- 模型链路目前仍是：
  - `features/compute` 生成 `behavior_feature`
  - `model/train` 训练 KMeans + LightGBM 并回写 `cluster_label` / `risk_probability`
  - `report/student/{id}/shap` 输出 SHAP
  - `report/student/{id}` 调用 LLM 生成报告
- 对照 `修复进展说明.md` 后，已确认以下修复已经真实落地：
  - 前端登录恢复已改为调用 `/auth/me`
  - `401` 时会同步清理前端内存登录态
  - 预警页筛选已改为以 Store 为主
  - 训练面板已改为真实调用 `/model/train`
  - 监控大屏已补充错误提示
- 但也确认还有几项关键问题仍未完成：
  - 后端鉴权依赖没有真正挂到业务路由
  - 模拟特征开关只存在于配置，未真正拦截接口行为
  - LLM 失败仍被包装成业务成功
  - 大屏 `model_auc` 契约仍未和后端对齐

## Findings

### F1
- 标题：后端业务路由仍然基本处于未鉴权状态
- 严重级别：`P0`
- 问题描述：
  后端虽然已经新增了 `get_current_user`、`require_admin` 和 `/auth/me`，但这些依赖没有挂接到主要业务路由。认证能力存在，实际保护没有落地。
- 影响：
  任何能访问服务的人都可以在未登录状态下直接读取学生数据、预警列表，甚至调用模型训练接口。
- 证据：
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\api\v1\auth.py:91`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\api\v1\auth.py:114`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\api\v1\auth.py:154`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\api\v1\model.py:19`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\api\v1\report.py:49`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\api\v1\student.py:92`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\api\v1\warnings.py:30`
  - 实测：未带 token 调用 `/api/v1/model/metrics`、`/api/v1/model/train`、`/api/v1/warnings/students`、`/api/v1/students/` 都返回 `200`
- 修复建议：
  - 给所有读接口挂 `Depends(get_current_user)`
  - 给 `/features/compute`、`/model/train` 这类写/管理接口挂 `Depends(require_admin)`
  - 不要只保留 `/auth/me` 一个鉴权示例接口，必须把安全依赖应用到真实业务入口

### F2
- 标题：认证配置已迁入配置层，但默认值仍是硬编码弱凭据和自定义 token 方案
- 严重级别：`P1`
- 问题描述：
  当前密钥和 demo 账号虽然从 `auth.py` 挪到了 `config.py`，但默认值仍然是源码内硬编码，且 token 仍是手写签名格式，不是成熟 JWT/session 方案。
- 影响：
  当前实现仍然容易被源码泄露、默认凭据滥用、伪造 token 等问题影响。只是“从业务文件迁走”，不等于安全问题已经解决。
- 证据：
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\core\config.py:14`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\core\config.py:16`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\core\config.py:20`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\api\v1\auth.py:49`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\api\v1\auth.py:64`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\api\v1\auth.py:123`
- 修复建议：
  - 把默认 demo 用户和密钥彻底移出源码默认值，改为 `.env` 或部署注入
  - 密码改为哈希存储
  - 用标准 JWT 库或成熟 session 方案替代当前手写 token

### F3
- 标题：LLM 失败语义仍然错误，失败会被当成成功报告返回
- 严重级别：`P1`
- 问题描述：
  `llm_service` 捕获异常后直接返回错误字符串；上层 `/report/student/{student_id}` 和 `/report/generate` 仍返回 `status: success`。
- 影响：
  前端无法区分“真实报告”和“报错文本”，业务层会把异常结果当成正常报告展示，导致误判。
- 证据：
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\services\llm_service.py:55`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\services\llm_service.py:70`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\api\v1\report.py:72`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\api\v1\report.py:77`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\api\v1\report.py:92`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\api\v1\report.py:97`
- 修复建议：
  - `llm_service` 失败时抛异常，不返回伪报告
  - 接口层对 LLM 错误返回显式失败状态或 5xx/4xx
  - 前端只在明确成功时展示 `smart_report`

### F4
- 标题：模拟特征开关尚未真正生效，特征工程仍会直接写入随机数据
- 严重级别：`P1`
- 问题描述：
  `config.py` 里已经有 `ALLOW_SYNTHETIC_FEATURES = False`，但 `feature_engineering.py` 并没有读取这个开关；`/features/compute` 仍然会直接生成随机特征并写入数据库。
- 影响：
  当前模型训练、风险概率、SHAP 和 LLM 报告仍可能建立在伪造行为数据上。配置项名义上存在，实际上没有形成保护。
- 证据：
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\core\config.py:27`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\api\v1\features.py:13`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\services\feature_engineering.py:13`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\services\feature_engineering.py:61`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\services\feature_engineering.py:75`
- 修复建议：
  - 在 `/features/compute` 或 `compute_all_features` 入口显式检查 `ALLOW_SYNTHETIC_FEATURES`
  - 默认关闭时直接拒绝执行并返回明确错误
  - 若确实要保留 demo 流程，建议单独做 demo 模式或 demo 数据库

### F5
- 标题：监控大屏 `model_auc` 契约仍未和后端对齐
- 严重级别：`P2`
- 问题描述：
  前端仍然期待 `analytics/overview` 返回 `model_auc`，只是现在对缺失做了兜底；后端 `overview` 依旧不返回该字段。
- 影响：
  页面不会崩，但会稳定显示 `0.0000`，造成“模型指标正常但看起来像零值”的误导。
- 证据：
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_frontend\src\types\api.d.ts:13`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_frontend\src\stores\dashboard.ts:31`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_frontend\src\stores\dashboard.ts:34`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_frontend\src\views\DashboardView.vue:19`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\api\v1\analytics.py:20`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\api\v1\analytics.py:46`
- 修复建议：
  - 要么由 `/analytics/overview` 返回真实 `model_auc`
  - 要么改前端通过 `/model/metrics` 获取模型状态
  - 要么暂时移除这个卡片，避免展示伪零值

### F6
- 标题：自动化测试和运行文档仍存在明显缺口
- 严重级别：`P2`
- 问题描述：
  后端项目依旧没有 `pytest` 依赖，`uv run pytest` 无法执行。现有“测试”仍主要是打印脚本而非断言测试。同时数据库脚本中的默认库名和密码口径仍不一致。
- 影响：
  当前修复无法通过稳定的自动化回归验证，安全改造、接口改造和前后端契约调整都容易反复回退。
- 证据：
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\pyproject.toml:7`
  - 实测：`uv run pytest` 失败，原因是 `pytest` 未安装
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\tests\test_db.py:11`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\tests\test_llm.py:12`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\tests\create_db.py:4`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\tests\create_db.py:10`
  - `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server\app\core\config.py:11`
- 修复建议：
  - 把 `pytest` 纳入项目依赖并建立最小断言测试
  - 统一数据库默认库名、密码、初始化脚本说明
  - 至少补三类回归：
    - 鉴权路由回归
    - 前后端接口契约回归
    - 模型训练/报告失败路径回归

## Open Questions / Assumptions

- `修复进展说明.md` 中“后端 `/api/v1/warnings/students` 可正常返回”这一条从接口可达性角度看属实，但它当前是未鉴权可访问的 `200`，不能等同于“安全修复已完成”。
- 我没有用真实数据库做全量业务回归，因此不对“学生数据是否完整、训练结果是否业务可信”下绝对结论；这部分仍属于待验证假设。
- 我没有验证真实 OpenAI Key 下的成功报告生成，只验证了代码路径与错误处理逻辑。
- 前端登录恢复改造已经落地，但这只是把“前端伪造登录”修掉了，不代表后端权限已经闭环。

## Recommended Fix Order

1. 先把后端鉴权真正挂到业务路由，尤其是 `/students`、`/warnings`、`/report`、`/features/compute`、`/model/train`
2. 修复 LLM 失败语义，避免“错误文本伪装成成功报告”
3. 让 `ALLOW_SYNTHETIC_FEATURES` 真正生效，阻止随机特征在默认配置下写库
4. 收敛认证默认值，移除源码内弱默认凭据和手写 token 方案
5. 修正大屏模型指标契约，消除 `model_auc` 伪零值
6. 补最小自动化回归和统一环境脚本

## Testing Gaps

- 已运行前端构建：`npm run build` 通过，但仍有超大 chunk 警告，`FeatureRadarChart` 相关产物超过 1 MB。
- 已做后端接口级静态验证：
  - `/api/v1/auth/me` 未带 token 返回 `401`
  - `/api/v1/model/metrics` 未带 token 返回 `200`
  - `/api/v1/model/train` 未带 token 返回 `200`
  - `/api/v1/warnings/students` 未带 token 返回 `200`
  - `/api/v1/students/` 未带 token 返回 `200`
- 未完成自动化测试：
  - `uv run pytest` 无法执行，因为项目环境中没有 `pytest`
- 未完成的验证：
  - 基于真实 MySQL 数据的完整训练链路
  - 基于真实 LLM 凭据的成功报告链路
  - 前端页面级交互回归

## Review Method

- 读取并复核了前端请求层、API 封装、Pinia stores、路由守卫、登录页、预警页、训练面板、监控大屏等关键模块。
- 读取并复核了后端入口、配置、鉴权、学生、预警、分析、特征工程、模型训练、报告生成和 LLM 服务。
- 对照阅读了 `C:\Users\Orion\Desktop\StudentBehavior\修复进展说明.md`，并以实际代码为准核对修复是否落地。
- 运行了以下验证：
  - `npm run build`
  - `uv run pytest`
  - 使用 FastAPI `TestClient` 验证部分接口返回码
- 未把旧版 Spring Boot 架构文档作为判断依据。
