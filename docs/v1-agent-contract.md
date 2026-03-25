# V1 Agent Contract

Status: Draft

Last Updated: 2026-03-25

## Purpose

本文档定义 V1 阶段各角色 agent 的职责边界、输入输出契约、依赖顺序和冻结规则，供协作执行使用。

本文档依赖 `docs/v1-frozen-baseline.md`。如与基线冲突，以基线为准。

## Roles

V1 默认分为 5 类职责：

1. Data Agent
2. Model Agent
3. Backend Agent
4. Frontend Agent
5. Documentation Agent

## Shared Rules

- 所有 agent 输出都必须显式标注 `Frozen`、`Draft`、`待确认` 三种状态之一。
- 未经确认的字段、阈值、映射和页面文案不得写成既定事实。
- 任何新增能力都必须说明它映射到哪一个分析成果。
- 接口字段命名、页面术语和报告术语必须统一使用四象限标签和风险等级，不直接暴露聚类编号。

## Data Agent Contract

### Responsibility

- 识别并整理 V1 所需最小数据源集合
- 建立学号统一规则
- 形成学期级特征宽表
- 输出标签对齐前的清洗结果说明

### Required Outputs

- 数据源清单
- 字段映射表
- 学号统一规则
- 学期级特征宽表 schema
- 标签对齐说明
- 缺失值与异常值处理说明

### Handoff To

- 向 Model Agent 提供可训练特征宽表和标签字段
- 向 Backend Agent 提供稳定数据 schema
- 向 Documentation Agent 提供数据字典和清洗规则

### Must Not Decide Alone

- 风险等级阈值
- 四象限业务命名
- 页面展示形式

## Model Agent Contract

### Responsibility

- 基于特征宽表完成聚类、标签映射、风险预测、解释输出和建议骨架设计
- 保证模型结果可被后端接口和前端页面消费

### Required Outputs

- 聚类输入特征清单
- 四象限映射规则
- 风险模型训练配置
- 模型评估指标
- 单学生解释输出格式
- 干预建议规则骨架

### Handoff To

- 向 Backend Agent 提供可服务化的模型输入输出契约
- 向 Frontend Agent 提供页面需要的结果字段
- 向 Documentation Agent 提供模型说明与限制

### Must Not Decide Alone

- 新增未在基线中定义的页面
- 将实验性模型替换为新的 V1 主路线

## Backend Agent Contract

### Responsibility

- 提供页面最小闭环所需接口
- 保证风险、群体、个体、解释、建议在 student_id 维度可串联
- 为训练、分析和报告能力提供可调用服务

### Minimum API Domains

- analytics
- warnings
- students
- report
- model
- auth

### Minimum API Capabilities

- 总览统计与趋势摘要
- 四象限群体列表与群体下学生列表
- 风险学生筛选与分页
- 学生基础信息与画像特征
- SHAP 或等价解释结果
- 个性化报告或建议文本
- 模型训练触发与指标返回

### Handoff To

- 向 Frontend Agent 提供稳定接口 contract
- 向 Documentation Agent 提供 API spec 和错误语义

### Must Not Decide Alone

- 擅自改写业务标签命名
- 用技术内部字段替代业务字段

## Frontend Agent Contract

### Responsibility

- 围绕“总览 -> 群体 -> 预警 -> 个体”主路径组织页面
- 保证页面结构直接对应 8 个分析成果
- 将技术结果转换为管理者可读表达

### Minimum Deliverables

- 登录页
- 总览仪表盘
- 群体分析页
- 风险预警页
- 学生个体画像页

### Page-Level Contract

- 总览页：展示风险分布、四象限分布、组织维度对比、趋势摘要
- 群体页：展示四象限定义、群体差异、群体风险结构、下钻入口
- 预警页：支持按风险等级、四象限、组织维度筛选
- 个体页：展示画像、风险、解释、趋势、建议

### Must Not Decide Alone

- 改写风险等级规则
- 发明未被模型或后端提供的新分析结果

## Documentation Agent Contract

### Responsibility

- 维护基线文档、专项文档、任务板和验收标准
- 标出已冻结、待确认和超范围项
- 在文档间维护依赖关系

### Required Outputs

- architecture / baseline
- contract / API spec
- task board / checklist
- integration plan
- assumptions / open questions register

## Recommended Execution Order

1. Documentation Agent 冻结基线
2. Data Agent 冻结最小数据 schema
3. Model Agent 冻结模型输入输出
4. Backend Agent 冻结 API contract
5. Frontend Agent 完成页面闭环
6. Documentation Agent 回写验收结果和残余风险

## Acceptance Gates

以下条件全部成立，才可视为 V1 闭环成立：

- 8 个分析成果均有明确载体页面、接口或报告输出
- 风险预测能返回概率和等级
- 四象限结果能下钻到学生级
- 个体页能同时展示画像、解释和建议
- 至少 1 条数据到页面的演示链路可复现

## Assumptions

- 当前优先级是建立稳定协作基线，而不是立即验证历史实现。
- 各 agent 可以在不改变基线决策的前提下补充实现细节。

## Open Questions

- 最小数据源集合尚未冻结。
- API 返回 envelope 是否统一，待确认。
- 错误码、鉴权方式、分页参数标准待确认。

## Out of Scope

- 详细数据库物理设计
- 生产环境部署编排
- 非 V1 角色权限矩阵
