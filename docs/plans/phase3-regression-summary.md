# Phase 3 回归检查汇总

Last Updated: 2026-04-10

## 1. 文档目的

本汇总用于记录当前“真实 LLM 在线报告链” Phase 3 的回归检查结果，区分：

- 已通过的 focused 回归
- 当前阶段已经具备的能力
- 尚未完成的最后接入项

## 2. 已通过的 focused 回归

### model-stubs

- `uv run pytest tests/test_llm_reporting.py tests/test_templates.py tests/test_build_outputs.py tests/test_cli.py -q`
- 结果：`39 passed`

说明：

- LLM 边界模块可用
- 模板兜底可用
- `template / hybrid / llm` 模式可用
- 报告元数据可产出

### demo-api

- `uv run --all-groups --with pytest --with pandas pytest tests/test_services.py tests/test_api.py -q -k "student_report or intervention_advice or report_source or prompt_version"`
- 结果：`7 passed, 109 deselected`

说明：

- 学生报告接口已透出报告来源与版本信息
- 干预建议结果接口已透出报告来源与版本信息

### demo-web

- `npm run test -- tests/api.test.ts tests/flow.test.ts`
- 结果：`18 passed`

- `npm run build`
- 结果：通过

说明：

- 学生报告页已展示报告来源相关元数据
- 无元数据时页面仍可正常工作

### 真实在线调用验收

- 在 `projects/model-stubs/.env` 中提供真实 DeepSeek 配置后，
  使用 `uv run python -` 直接调用 `build_report_payload_with_fallback(...)`
- 结果：
  - 成功返回在线生成结果
  - `report_source = hybrid`
  - `prompt_version = llm-report-v1`
  - `fallback_reason = None`

说明：

- 当前链路已不仅是“可接入”
- 而是已经完成了一次真实在线调用验收

## 3. 当前阶段结论

### 已实现

1. 已建立真实在线 LLM 调用边界
2. 已保留模板兜底
3. 已支持报告来源标记
4. 已支持 prompt 版本透出
5. 已支持报告生成元数据透出
6. 前端已能展示这些元数据

### 尚未完成

1. 真实 provider 使用文档还未整理成最终版
2. 阶段里程碑还未提交

## 4. 当前判断

Phase 3 已达到“真实 DeepSeek 在线调用已跑通、可提交里程碑”的状态。

当前系统已经不再只是模板报告，而是：

- 模板兜底
- 在线 LLM 边界
- 来源可解释
- 页面可展示

## 5. 推荐下一步

建议下一步二选一：

1. 先提交当前 Phase 3 里程碑
2. 继续补 DeepSeek 使用文档与最终提交流程
