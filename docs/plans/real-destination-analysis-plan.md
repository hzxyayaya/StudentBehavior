# 真实去向分析全链路方案

Last Updated: 2026-04-08

## 1. 目标

将当前“发展方向与去向关联分析”从半占位状态升级为真实数据驱动链路。

当前系统已经有：

- `/development` 页面
- `/api/analytics/development`
- `/api/results/major-comparison`

但仍存在显式占位：

- `去向真值暂未接入`

本方案目标是去掉这一占位，形成真实去向分析闭环。

## 2. 总体策略

第一版不追求复杂预测模型，优先落地：

1. 去向真值接入
2. 去向标签标准化
3. 去向分布统计
4. 行为与去向关联分析

如果时间允许，再增加：

5. 去向预测模型

## 3. 数据接入

### 3.1 优先检查源表

优先确认当前数据中是否存在：

- 毕业去向
- 升学/就业/出国/考公/待定
- 单位类型
- 去向类别

### 3.2 建议新增 loader

在 `projects/analytics-db` 中新增类似：

- `load_fact_destinations.py`

其职责：

- 读取去向原始表
- 标准化 student_id
- 标准化去向类别
- 输出学生级去向真值记录

## 4. 去向标签定义

建议第一版先统一成少量稳定类别：

- 升学
- 企业就业
- 体制内
- 出国/出境
- 待定/其他

并保留：

- `destination_label_raw`
- `destination_label_normalized`

## 5. 分析链路

### 5.1 最小可落地链路

先做真实统计和关联：

- 去向类别分布
- 专业/学院去向分布
- 群体标签与去向差异
- 选课路径与去向关联

### 5.2 可选增强链路

如果时间够，再补：

- 去向预测模型
- 去向类别概率输出

## 6. 后端接入

### 6.1 analytics-db

在学期或学生聚合层补充：

- `destination_label`
- `destination_source`

### 6.2 model-stubs

增加真实去向分析结果产物，例如：

- `destination_distribution`
- `major_destination_summary`
- `group_destination_summary`

### 6.3 demo-api

扩充：

- `/api/analytics/development`
- `/api/results/major-comparison`

建议新增字段：

- `destination_distribution`
- `destination_segments`
- `major_destination_comparison`
- `behavior_destination_association`

## 7. 前端展示

当前 `/development` 页面可直接升级，不需要重做结构。

建议新增或替换为：

- 去向类别分布图
- 专业去向对比
- 群体标签与去向差异
- 选课路径 / 行为模式与去向关联

## 8. 最小成功标准

这条链完成后，至少要满足：

1. 系统不再显示“去向真值暂未接入”
2. 去向类别来自真实数据
3. 页面至少有真实统计与对比
4. 接口可返回真实去向相关字段

## 9. 当前建议

如果时间有限，先做：

- 去向真值接入
- 去向统计分布
- 专业/群体对比

不要一开始就做复杂去向预测模型。

## 10. 当前 Phase 2 进度

截至当前版本，Phase 2 已推进到以下程度：

### 已完成

1. `analytics-db`
   - 已新增 `load_fact_destinations.py`
   - 已接入真实源表 `毕业去向.xlsx`
   - 已输出：
     - `destination_label`
     - `destination_source`
   - 已保留原始去向、单位性质、行业等字段
2. `analytics-db` 特征产物
   - 去向真值已进入当前导出的学期特征/演示特征 artifact
3. `model-stubs`
   - 已将 `destination_label`
   - `destination_source`
   透传到学生结果
   - 已新增：
     - `destination_distribution`
     - `major_destination_summary`
     - `group_destination_association`
4. `demo-api`
   - `/api/analytics/development`
   - `/api/results/major-comparison`
   - `/api/results/behavior-patterns`
   已支持真实去向分析字段透出
5. `demo-web`
   - `/development`
   已优先展示真实去向分布、专业去向对比、群体去向关联

### 当前尚未完成

1. 还没有补去向预测模型
2. 还没有补更复杂的“选课路径与去向关联”分析
3. 还没有刷新该阶段的最终文档和阶段里程碑提交

### 当前判断

Phase 2 已经从“页面占位”推进到“真实去向真值接入 + 统计/关联结果可展示”的状态，已经达到最小闭环版本。
