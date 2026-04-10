# Phase 2 回归检查汇总

Last Updated: 2026-04-10

## 1. 文档目的

本汇总用于记录当前“真实去向分析链” Phase 2 的回归检查结果，区分：

- 已通过的 focused 回归
- 当前阶段已确认可用的能力
- 尚未扩展的后续方向

## 2. 已通过的 focused 回归

### analytics-db

- `uv run pytest tests/test_load_fact_destinations.py tests/test_build_demo_features_from_excels.py -q`
- 结果：`15 passed`

说明：

- 去向真值 loader 已通过
- 备用表头发现规则已通过
- DWXZ / DWXZMC 口径的体制内映射已通过
- 重复去向记录的业务优先级已通过

### model-stubs

- `uv run pytest tests/test_build_outputs.py -q`
- 结果：`18 passed`

说明：

- 去向字段已进入 student results
- 去向分布、专业去向摘要、群体去向关联已通过

### demo-api

- `uv run --all-groups --with pytest --with pandas pytest tests/test_services.py tests/test_api.py -q -k "development or destination or major_comparison or behavior_patterns"`
- 结果：`6 passed, 107 deselected`

说明：

- `/api/analytics/development`
- `/api/results/major-comparison`
- `/api/results/behavior-patterns`

去向相关接口已通过 focused 回归

### demo-web

- `npm run test -- tests/api.optional-fields.test.ts tests/flow.test.ts`
- 结果：`10 passed`

- `npm run build`
- 结果：通过

说明：

- `/development` 页面已接入真实去向分析字段
- 前端构建可用

## 3. 当前阶段结论

### 已实现

1. 去向真值已接入数据链
2. 去向标签已标准化
3. 去向统计分布已可输出
4. 专业去向对比已可输出
5. 群体去向关联已可输出
6. 前端发展分析页已展示真实去向结果

### 尚未完成

1. 去向预测模型
2. 更复杂的路径关联分析
3. 阶段文档最终收口与里程碑提交

## 4. 当前判断

Phase 2 已经达到“真实去向分析链最小闭环”状态。

当前系统不再只是：

- `去向真值暂未接入`

而是已经具备：

- 真实去向真值接入
- 去向分布展示
- 专业去向对比
- 群体去向关联分析

## 5. 推荐下一步

建议下一步二选一：

1. 提交当前 Phase 2 里程碑
2. 进入 Phase 3：真实 LLM 在线报告链
