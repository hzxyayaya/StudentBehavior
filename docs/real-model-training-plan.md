# 真实模型训练链落地方案

Last Updated: 2026-04-08

## 1. 目标

当前项目已经具备完整的演示链路，但模型层仍存在明显的规则化和静态摘要痕迹，例如：

- `risk_model` 仍为 `stub-*`
- `auc` 仍为固定值
- 风险结果主要来自规则链而非真实训练产物

因此，本方案的目标是：

1. 将学业风险预测从静态规则摘要升级为真实训练与评估链路
2. 让模型摘要接口和前端模型信息卡读取真实训练结果
3. 保留现有规则链作为 fallback，而不是一次性推翻现有系统

## 2. 总体策略

不重做架构，沿用当前分层：

- `projects/analytics-db`
  - 负责训练样本与标签构建
- `projects/model-stubs`
  - 升级为真实训练、评估与推理产物层
- `projects/demo-api`
  - 读取真实评估摘要并暴露接口
- `projects/demo-web`
  - 只展示真实训练结果，不承担训练逻辑

## 3. 当前问题

当前模型链路的主要问题包括：

1. `auc` 为静态摘要值，不是实时评估结果
2. `risk_model` 和 `cluster_method` 仍带有 `stub-*` 命名
3. 风险等级结果与模型摘要之间缺少真实训练产物连接
4. 页面展示的“模型信息”无法经受答辩中的训练细节追问

## 4. 第一阶段：风险标签定义

在真实训练前，必须先固定一版版本化标签规则。

### 4.1 推荐主任务

优先只做一个主任务：

- 学期级学业风险预测

### 4.2 推荐标签来源

优先从当前已经稳定接入的真实字段中构造监督标签：

- `term_gpa`
- `failed_course_count`
- `borderline_course_count`
- `failed_course_ratio`
- 综合测评等级
- 学籍异动类信号

### 4.3 推荐标签形式

建议先同时保留两种：

1. 二分类标签
   - `risk_label_binary`
   - 风险 / 非风险
2. 分层标签
   - `risk_label_level`
   - 高风险 / 较高风险 / 一般风险 / 低风险

### 4.4 推荐最小规则

先定义一版可答辩、可复现的业务规则，例如：

- 若挂科门数较高，则记为风险
- 若 GPA 低于阈值，则记为风险
- 若边缘课程数较高，则上调风险
- 若综合测评明显偏低，则上调风险

最终应额外输出：

- `label_source`
- `label_rule_version`

## 5. 第二阶段：训练样本构建

### 5.1 输入来源

训练输入直接来自：

- `artifacts/semester_features/v1_semester_features.csv`

### 5.2 特征选择原则

优先使用当前已稳定接入的学期级特征：

- 学业基础
- 课堂投入
- 在线学习
- 图书馆行为
- 网络作息
- 作息规律
- 体质运动
- 荣誉与异动

### 5.3 约束

- 不要一开始把高缺失字段全部纳入训练
- 先使用当前最稳定、最可解释的特征列
- 输出一份显式的训练特征清单

建议产物：

- `feature_columns.json`

## 6. 第三阶段：训练模块设计

建议在 `projects/model-stubs` 中新增真实训练模块，而不是把训练逻辑硬塞进现有 `build_outputs.py`。

### 6.1 建议文件

- `projects/model-stubs/src/student_behavior_model_stubs/train_risk_model.py`
- `projects/model-stubs/src/student_behavior_model_stubs/evaluate_risk_model.py`
- `projects/model-stubs/src/student_behavior_model_stubs/model_registry.py`

### 6.2 模块职责

#### `train_risk_model.py`

- 读取学期特征表
- 加载标签字段
- 划分训练集 / 验证集 / 测试集
- 训练真实风险模型
- 保存模型文件

#### `evaluate_risk_model.py`

- 读取测试集
- 生成 AUC / Accuracy / Recall / F1 等指标
- 输出评估摘要

#### `model_registry.py`

- 统一模型路径
- 统一版本号
- 统一产物命名
- 统一元数据格式

## 7. 第四阶段：模型选择

本项目当前阶段不建议从深度学习起步。

### 7.1 推荐顺序

1. `LightGBM`
2. `RandomForest` 或 `XGBoost`
3. 规则基线作为对照

### 7.2 推荐首选

建议首选：

- `LightGBM`

原因：

- 更适合当前表格型特征
- 训练成本低
- 结果更容易稳定
- 更容易给出可解释指标

## 8. 第五阶段：训练集划分

### 8.1 推荐策略

避免同一学生不同学期同时进入训练和测试，优先考虑：

- 按学生划分 train / valid / test

### 8.2 推荐比例

- 训练集：70%
- 验证集：15%
- 测试集：15%

### 8.3 必须记录的信息

训练后必须能输出：

- `train_sample_count`
- `valid_sample_count`
- `test_sample_count`
- `split_strategy`

## 9. 第六阶段：训练产物设计

建议新增训练产物目录，例如：

- `artifacts/model_training/`

### 9.1 建议产物

- `risk_model.pkl` 或 `risk_model.txt`
- `risk_metrics.json`
- `feature_importance.csv`
- `training_config.json`

### 9.2 `risk_metrics.json` 建议字段

- `model_name`
- `task_type`
- `target_label`
- `auc`
- `accuracy`
- `precision`
- `recall`
- `f1`
- `train_sample_count`
- `test_sample_count`
- `feature_count`
- `trained_at`

## 10. 第七阶段：接入当前产物链

### 10.1 现有问题

当前 `projects/model-stubs/src/student_behavior_model_stubs/build_outputs.py` 中包含静态模型摘要常量：

- `_MODEL_SUMMARY_AUC = 0.8347`

### 10.2 目标改法

将模型摘要改为：

1. 优先读取真实评估产物
2. 读不到时再回退到 stub 逻辑

### 10.3 好处

- 不破坏现有 demo 主流程
- 不会因为训练产物缺失导致系统整体崩掉
- 便于答辩时明确说明“当前模型摘要来源”

## 11. 第八阶段：demo-api 接入

`projects/demo-api` 中以下接口需要切换到读取真实训练摘要：

- `/api/models/summary`
- `/api/results/model-summary`

### 11.1 建议新增返回字段

- `risk_model`
- `target_label`
- `auc`
- `accuracy`
- `recall`
- `f1`
- `train_sample_count`
- `test_sample_count`
- `updated_at`
- `source`

其中：

- `source = trained`
- 或 `source = stub`

## 12. 第九阶段：前端展示改法

前端不需要大改，只需要让模型信息卡从真实模型摘要中读取数据。

### 12.1 建议展示字段

- 模型名称
- 目标标签
- AUC
- Accuracy
- Recall / F1
- 训练样本数
- 测试样本数
- 更新时间
- 模型来源

### 12.2 建议展示逻辑

- 若 `source = trained`
  - 明确显示“真实训练模型”
- 若 `source = stub`
  - 明确显示“规则基线 / 演示摘要”

## 13. 第十阶段：验证标准

这条链完成后，至少要满足以下标准：

1. 有真实训练命令可以执行
2. 有真实评估产物可以输出
3. `demo-api` 能返回真实模型摘要
4. 前端模型信息模块能显示真实训练结果
5. 文档中能明确说明：
   - 标签如何定义
   - 特征如何选择
   - 数据如何划分
   - 指标如何计算

## 14. 最小实施顺序

### Phase 1

- 在 `analytics-db` 中增加风险标签字段
- 重新生成带标签的学期特征表

### Phase 2

- 在 `model-stubs` 中增加训练与评估脚本
- 训练一个真实风险模型
- 输出模型与评估产物

### Phase 3

- 改 `build_outputs.py` 与模型摘要逻辑
- 改 `demo-api` 的模型摘要接口

### Phase 4

- 改前端模型信息展示
- 补文档与答辩口径

## 15. 当前建议

如果只启动一个真实链路，建议优先从这一条开始：

- 真实风险标签定义
- 真实训练与评估
- 真实模型摘要输出

原因：

- 它能最快提升项目可信度
- 它会直接影响答辩中最容易被追问的部分
- 它比去向分析和在线 LLM 链路更适合作为第一条真实化改造主线

## 16. 下一步

建议下一步继续补一份配套文档：

- 风险标签定义方案

该文档应明确：

- 标签规则
- 阈值来源
- 标签版本号
- 哪些字段参与打标
- 哪些字段只是解释用，不参与监督标签生成

## 17. 当前 Phase 1 进度

截至当前版本，Phase 1 已完成到以下程度：

### 已完成

1. `analytics-db`
   - 已新增显式风险标签字段：
     - `risk_label_binary`
     - `risk_label_level`
     - `label_source`
     - `label_rule_version`
2. `model-stubs`
   - 已新增训练产物注册模块
   - 已新增 `train-risk-model` 训练命令
   - 已新增 `evaluate-risk-model` 评估命令
   - 评估已支持 held-out / persisted split 信号
   - `build_model_summary()` 已支持：
     - 优先读取真实训练指标
     - 读不到时回退到 stub
     - `source = trained | stub`
3. `demo-api`
   - `/api/models/summary`
   - `/api/results/model-summary`
   已能透出真实训练摘要扩展字段，并保持 legacy stub 兼容
4. `demo-web`
   - 总览页模型信息模块已可显示：
     - `source`
     - `accuracy`
     - `precision`
     - `recall`
     - `f1`
     - 样本数

### 尚未完成

1. 训练链尚未真正接入 `build_outputs` 之外的完整业务主路径
   - 风险结果本身仍未完全由真实训练模型替代
2. 前端目前只消费了“模型摘要扩展字段”，并未把真实训练模型输出全面作用到风险主结果
3. 尚未提交本轮改动，也尚未固化为阶段里程碑提交

### 当前判断

Phase 1 的“真实模型训练链骨架”已经搭起来了，而且 `model-stubs` 与 `demo-api` 的核心全量回归已经收口；但它仍未达到“真实训练结果全面替换风险主产物”的最终状态。
