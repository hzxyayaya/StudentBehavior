# 项目交接说明

Last Updated: 2026-03-31

## 0. 2026-03-28 Real-Data Update

当前仓库已经不再只依赖极简 `semester-etl` 产物来驱动 Demo。

- `projects/analytics-db` 新增了 `analytics-db build-demo-features`
- 该命令会从仓库根目录下的真实 Excel 数据源生成 `artifacts/semester_features/v1_semester_features.csv`
- 默认纳入的真实源是：
  - `学生基本信息.xlsx`
  - `学生成绩.xlsx`
  - `考勤汇总.xlsx`
  - `本科生综合测评.xlsx`
  - `学生选课信息.xlsx`
- 为了控制构建时间，`学生签到记录.xlsx`、`课堂任务参与.xlsx`、`跑步打卡.xlsx`、`图书馆打卡记录.xlsx`、`学生作业提交记录.xlsx`、`考试提交记录.xlsx`、`讨论记录.xlsx` 当前没有作为默认输入

当前仓库内已经重建好的真实特征产物：

- `artifacts/semester_features/v1_semester_features.csv`
- 行数：`2905`
- 学期分布：
  - `2023-2`: `2440`
  - `2024-1`: `290`
  - `2024-2`: `175`

注意：

- “输入特征”已经主要来自真实 Excel
- 但 `risk_probability`、`risk_level`、`group_segment`、`top_factors`、`intervention_advice`、`report_text` 仍然是 `model-stubs` 的规则版输出，不是正式模型

## 1. 文档目的

本文档用于帮助新的开发者、协作者或 AI 代理快速接手本项目，明确当前项目状态、代码边界、推荐阅读顺序和后续协作方式。

本文档优先回答 4 个问题：

1. 当前项目已经推进到哪里
2. 哪些能力已经稳定，哪些内容仍在独立分支或待合并状态
3. 新接手者应该先看什么、先跑什么、先确认什么
4. 当前最合理的后续工作是什么

## 2. 项目目标

本项目围绕“四类学生行为分析任务”展开：

1. 学业风险动态感知与预警
2. 学业轨迹演化与关键行为分析
3. 学生个体画像与群体分层分析
4. 发展方向与去向关联分析

当前 V1 的主演示任务是：

- 学业风险动态感知与预警

其余任务在 V1 中主要作为支撑能力出现，通过趋势、分层、画像和摘要帮助解释主演示任务，不要求在当前阶段都做成完整独立系统。

## 3. 建议优先阅读的文档

新接手者先读这些文档，不要先看零散代码：

1. `.worktrees/p0-foundation/docs/v1-delivery-board.md`
2. `.worktrees/p0-foundation/docs/v1-risk-label-freeze.md`
3. `.worktrees/p0-foundation/docs/v1-semester-feature-schema.md`
4. `docs/v1-api-contract.md`
5. `docs/analysis-task-priority.md`
6. `docs/v1-demo-runbook.md`

如果需要看最近新增的设计与计划，再读：

1. `docs/superpowers/specs/2026-03-27-v1-model-stubs-design.md`
2. `docs/superpowers/plans/2026-03-27-v1-model-stubs.md`
3. `docs/superpowers/plans/2026-03-28-v1-demo-hardening.md`
4. `docs/superpowers/specs/2026-03-28-v1-demo-web-design.md`
5. `docs/superpowers/plans/2026-03-28-v1-demo-web.md`

## 4. 当前项目结构

当前仓库按独立子项目组织，不建议把后续功能重新堆回根目录。

主工作区中的子项目：

- `projects/semester-etl`
  - 作用：从原始 Excel 读取数据，生成学期宽表
- `projects/analytics-db`
  - 作用：构建分析数据库底座与 `student_term_features`
- `projects/model-stubs`
  - 作用：基于 `student_term_features` 生成离线结果文件
- `projects/demo-api`
  - 作用：读取离线结果文件，对外提供只读 API

当前尚未合并到 `main` 的前端实现：

- 分支：`codex/v1-demo-web`
- 在当前 Codex 工作区中，对应目录为 `.worktrees/v1-demo-web/projects/demo-web`
- 作用：Vue 3 前端 Demo 子项目 `projects/demo-web`

## 5. 当前主线状态

当前 `main` 上已经稳定的内容：

- `semester-etl`
- `analytics-db`
- `model-stubs`
- `demo-api`

当前 `main` 上已经验证通过的内容：

- `projects/model-stubs` 测试通过
- `projects/demo-api` 测试通过

当前不在 `main` 的内容：

- Vue 3 前端 `projects/demo-web`
- 它目前仍在分支 `codex/v1-demo-web` 上，不应假设已经合并回主线

## 6. 当前已知真实口径

V1 Demo 当前真实可用的联调值：

- `term`：`2023-2`、`2024-1`、`2024-2`
- 默认学期：`2024-2`
- 示例学生：`pjwrqxbj901`

以下旧示例值当前不要继续使用：

- `2023-1`
- `20230001`

真实 API 契约请以 `docs/v1-api-contract.md` 为准，不再沿用旧的 `code = 0` 或旧登录返回结构。

## 7. 当前仍然是 Stub 的内容

以下结果仍然是 stub 或规则版，不要在页面文案、汇报材料或 PR 描述中误称为正式模型结果：

- `risk_probability`
- `risk_level`
- `group_segment`
- `top_factors`
- `intervention_advice`
- `report_text`
- `cluster_method`
- `risk_model`
- `target_label`

补充说明：

- 当前历史命名里仍可能出现 `quadrant_label` 或 `/quadrants`
- 但新的推荐口径已经统一为“行为模式识别 / 群体分层”
- 当前主线实现应优先使用 `group_segment` 和 `/api/analytics/groups`

## 8. 当前前端分支状态

`codex/v1-demo-web` 分支已经完成的能力：

- 演示登录与真实 `demo-login` 返回结构对齐
- 总览、群体分层、风险预警、学生个体 4 个主页面
- 总览页到预警页、群体页到预警页、预警页到学生页的主链路下钻
- 预警页筛选条件写回 URL，并在刷新后恢复
- 学生页返回预警列表时保留筛选上下文
- 全局 `DemoStatusBar` 统一提示真实 API / 演示口径 / stub 边界
- 前端测试与构建已跑通
- 前端已切换为 `/groups` 页面和 `group_segment` 筛选语义，`/quadrants` 仅保留兼容跳转

当前前端边界：

- 前端只消费 `demo-api`
- 不直接读取 `artifacts/`
- 不直接读取 Excel
- 不直接连接数据库
- 页面可以展示 stub 字段，但不能把它们写成正式模型结论

当前推荐的前端业务表达是：

- 4 类分析任务
- 10 个系统输出
- 群体分析采用“行为模式识别 / 群体分层”

不再建议把“四象限”作为系统对外主表达。

## 9. 当前推荐运行顺序

整条 Demo 主链路按以下顺序理解：

1. `projects/semester-etl`
2. `projects/analytics-db`
3. `projects/model-stubs`
4. `projects/demo-api`
5. `projects/demo-web`（当前在独立分支）

推荐最小验证命令：

```powershell
uv run --project projects/semester-etl pytest projects/semester-etl/tests -q
uv run --project projects/analytics-db pytest projects/analytics-db/tests -q
uv run --project projects/model-stubs pytest projects/model-stubs/tests -q
uv run --project projects/demo-api pytest projects/demo-api/tests -q
```

如果需要联调 API，再启动：

```powershell
uv run --project projects/demo-api uvicorn student_behavior_demo_api.main:app --reload
```

如果需要联调前端：

```powershell
cd .worktrees/v1-demo-web/projects/demo-web
npm install
npm run test
npm run build
npm run dev
```

## 10. GitHub 管理建议

后续协作建议固定为以下流程：

1. `main` 只保留已验证通过的稳定实现
2. 每个独立任务先开 issue
3. 每个独立任务使用单独分支
4. 先有 spec，再有 implementation plan，再开始开发
5. 开发完成后走 PR，再合并到 `main`

推荐 GitHub labels：

- `foundation`
- `backend`
- `frontend`
- `data`
- `docs`
- `stub`
- `needs-review`

推荐里程碑：

- `V1 Demo`
- `Post-Demo Hardening`
- `Model Upgrade`

## 11. 新接手者的工作流程

不要让新接手者一上来直接写代码。推荐流程如下：

1. 先阅读第 3 节列出的冻结文档和 runbook
2. 再跑现有测试或构建
3. 再确认当前主线与分支状态
4. 输出“项目理解报告”
5. 明确本轮要做的单一任务
6. 针对该任务补或更新 spec
7. 再写 implementation plan
8. 最后才进入编码

## 12. 接手时必须先回答的问题

新接手者在开始开发前，必须先回答这些问题：

1. 当前主演示任务是什么
2. 哪些结果仍然是 stub
3. 当前真实可用的 `term` 是哪些
4. 当前前端是否已经在主线
5. `demo-api` 是否直接连数据库
6. `model-stubs` 的输入来源是什么
7. 当前最准确的 API 契约写在哪里
8. 当前下一步最合理的任务是什么

如果这些问题答不清楚，不应该直接开始改代码。

## 13. 推荐下一步任务

当前最合理的下一步不是继续大幅扩功能，而是先完成收口工作：

- 同步交接文档、runbook、前端 spec/plan 与真实实现
- 以 PR 审查视角复查 `codex/v1-demo-web`
- 决定是否将前端分支整理后合并

如果继续做前端编码，优先级更高的是：

- 补页面级交互测试
- 统一整理提交说明与演示说明
- 修正文档中的历史 API 口径，避免后续接手者误用

## 14. 可以直接发给接手者的 Prompt

### Prompt A：先理解项目，不写代码

```text
你现在不是来直接写代码的。你的第一任务是完整理解这个项目，并用中文输出一份“可接手开发”的项目理解报告。

项目根目录：
.

请按下面顺序工作：

1. 先阅读这些文档：
- .worktrees/p0-foundation/docs/v1-delivery-board.md
- .worktrees/p0-foundation/docs/v1-risk-label-freeze.md
- .worktrees/p0-foundation/docs/v1-semester-feature-schema.md
- docs/v1-api-contract.md
- docs/analysis-task-priority.md
- docs/v1-demo-runbook.md
- docs/handoff.md

2. 再阅读当前子项目：
- projects/semester-etl
- projects/analytics-db
- projects/model-stubs
- projects/demo-api

3. 如果要接前端，再确认 `codex/v1-demo-web` 分支或对应 worktree 的状态。

4. 最后用中文输出：
- 项目在解决什么问题
- 当前 V1 已完成什么
- 当前还没完成什么
- 现有子项目各自职责是什么
- 当前主线 Demo 是怎么跑通的
- 哪些字段/结果仍然是 stub
- 下一步最合理的开发任务是什么

注意：
- 先不要改代码
- 不要创建文件
- 不要直接开始实现
- 如果发现文档和代码不一致，要单独列出
```

### Prompt B：执行单一任务

```text
你现在负责执行一个单独任务，不要扩范围，不要顺手重构其他模块。

任务目标：
<在这里写具体任务>

执行要求：
1. 先阅读相关 spec 和 plan
2. 先总结你理解到的边界
3. 只修改与该任务直接相关的文件
4. 写代码前先明确验收标准
5. 完成后必须运行相关测试或构建命令
6. 输出时必须说明：
- 改了什么
- 为什么这样改
- 跑了什么验证
- 还有哪些限制
```

### Prompt C：代码审查

```text
请你以代码审查模式检查这个任务是否已经达到可合并状态。

重点不是总结，而是找问题。请优先检查：
- 是否偏离 spec
- 是否引入未验证假设
- 是否遗漏测试
- 是否和 API contract 不一致
- 是否把 stub 结果误写成正式模型结果
- 是否改动了不该改的项目边界

输出格式：
1. Findings
2. Residual Risks
3. Merge Recommendation
```

### Prompt D：前端接手

```text
你现在接手前端 Demo 开发。请先确认当前前端是否已经在主线，还是在独立分支。

项目根目录：
.

请按以下顺序工作：

1. 阅读：
- docs/handoff.md
- docs/v1-demo-runbook.md
- docs/v1-api-contract.md
- docs/superpowers/specs/2026-03-28-v1-demo-web-design.md
- docs/superpowers/plans/2026-03-28-v1-demo-web.md

2. 确认：
- 当前前端技术栈是 Vue 3
- 当前真实 `term` 是 `2023-2`、`2024-1`、`2024-2`
- 当前默认学期应为 `2024-2`

3. 在开始编码前，用中文给出：
- 你的理解
- 当前边界
- 本轮准备做什么
- 验收标准

4. 然后再进入实现。
```

## 15. 交接前建议补的最后一步

如果要正式把仓库交给别人，建议先做一次仓库收口：

1. 处理当前未跟踪文档
2. 决定是否把 `projects/demo-api/uv.lock` 纳入版本管理
3. 决定 `codex/v1-demo-web` 是否继续保留独立分支，还是整理后合并
4. 把 `docs/handoff.md`、`docs/v1-demo-runbook.md` 和 `docs/v1-api-contract.md` 一起提交

## 16. 当前结论

这个项目现在已经不是“只有一堆文档和零散脚本”的状态，而是已经具备：

- 数据清洗层
- 分析数据库层
- 结果生成层
- 只读 API 层
- 独立前端分支与可演示主链路

后续接手者最需要的不是“自由发挥”，而是按已有边界继续推进，并且先把文档和实现对齐。
