# Phase 1 回归检查汇总

Last Updated: 2026-04-09

## 1. 文档目的

本汇总用于记录当前“真实模型训练链” Phase 1 的回归检查结果，区分：

- 已通过的 focused 回归
- 尚未收口的全量失败
- 当前可以给出的阶段性结论

## 2. 已通过的 focused 回归

### analytics-db

- `uv run pytest tests/test_build_student_term_features.py tests/test_build_demo_features_from_excels.py -q`
- 结果：`9 passed`

### model-stubs

- `uv run pytest tests/test_model_registry.py -q`
- 结果：`8 passed`

- `uv run pytest tests/test_train_risk_model.py -q`
- 结果：`4 passed`

- `uv run pytest tests/test_evaluate_risk_model.py -q`
- 结果：`5 passed`

- `uv run pytest tests/test_build_outputs.py -q -k build_model_summary`
- 结果：`6 passed`

### demo-api

- `uv run --all-groups --with pytest --with pandas pytest tests/test_api.py -q -k "models_summary or result_model_summary"`
- 结果：`4 passed`

### demo-web

- `npm run test -- tests/api.test.ts tests/flow.test.ts`
- 结果：`16 passed`

- `npm run test -- tests/api.test.ts tests/flow.test.ts tests/router.test.ts tests/warnings-layout.test.ts tests/warnings-query.test.ts tests/motion-budget.test.ts`
- 结果：`36 passed`

- `npm run build`
- 结果：通过

## 3. 全量回归状态

### model-stubs

全量运行：

- `uv run pytest -q`

结果：

- `83 passed`

说明：

- `model-stubs` 当前全量测试已收口

### demo-api

全量运行：

- `uv run --all-groups --with pytest --with pandas pytest tests/test_services.py tests/test_api.py -q`

结果：

- `109 passed`

说明：

- `demo-api` 当前 API 与 service 主测试面已收口

## 4. 当前阶段判断

### 可以确认的结论

1. 真实模型训练链的核心骨架已经打通：
   - 标签
   - 训练命令
   - 评估命令
   - 模型摘要
   - API 模型摘要
   - 前端模型信息展示

2. 当前链路已经不再只是静态 `auc` + `stub-*` 展示方案

3. Focused regression 层面，当前新增能力是可运行、可验证的

### 仍然不能直接宣布的结论

还不能直接宣布：

- 风险主结果已经完全由真实训练模型替代
- 前端已经完整消费并展示所有训练链结果
- Phase 1 所有文档、接口、页面都已统一到最终口径

## 5. 推荐下一步

建议下一步按以下顺序推进：

1. 刷新文档中的模型摘要与回归状态说明
2. 决定是否提交当前 Phase 1 里程碑
3. 再进入 Phase 2：真实去向分析链
