# Architecture Baseline

Last Updated: 2026-03-20

## 当前系统概况

当前项目不是纯文档，也不是只有数据集。它已经包含一套学生行为分析系统的前端、后端、模型文件和说明文档。

## 已识别的主系统

### 1. 前端

- 目录: `student_behavior_frontend`
- 技术栈: Vue 3、Vite、Pinia、Vue Router、ECharts、Axios、TypeScript
- 页面视图: 登录、仪表盘、预警中心、学生画像、设置页
- 当前信号: 文档说明中提到部分 store 仍以 mock 逻辑为主，需要后端集成确认

### 2. 后端

- 目录: `student_behavior_ai_server`
- 技术栈: FastAPI、SQLAlchemy、Pandas、LightGBM、SHAP、OpenAI
- 结构包含: 配置层、数据库层、模型层、schema、服务层、API 路由层
- 当前信号: 已有模型文件和测试脚本，但环境与数据库状态未核验

### 3. 数据与模型

- 数据目录: `数据集及类型`
- 数据形式: 多个 Excel 文件及对应字段说明文档
- 模型目录: `student_behavior_ai_server/data/models`
- 当前信号: 数据资产丰富，适合做新版特征映射和样本回放，但是否全量保留尚未确认

### 4. 文档资产

已存在的高价值文档包括:

- `ARCHITECTURE_MANUAL.md`
- `前端架构与交互资产说明书.md`
- `新前端开发蓝图与组件设计文档.md`
- `新后端核心API接口说明书.md`
- `CODE_REVIEW_REPORT.md`
- `修复进展说明.md`
- `student_behavior_analysis_plan.md`

## 当前架构判断

- 系统已有明确业务方向: 学生行为分析、风险预警、画像、模型训练、AI 报告
- 当前最缺的不是“功能说明书”，而是“哪部分要继承进新版”的统一基线
- 用户已明确下一步是删除旧实现并重写，因此现阶段更不应直接改代码，而应先完成现状提取和重写范围收敛
- 旧代码在当前阶段的角色是“信息来源”和“回溯样本”，不是直接演进对象

## 进入下一阶段前需要澄清

1. 新版是否必须保留现有前后端分层形态
2. 数据集是继续沿用，还是只保留字段语义
3. AI 报告、SHAP 和聚类训练是否属于首批必做范围
4. 现有中文说明文档中哪一份是最可信的业务基线
