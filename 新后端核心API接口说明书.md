# 新后端核心 API 接口说明书

> **项目名称**: `student_behavior_ai_server` (智慧教育预警系统)  
> **技术栈**: FastAPI + SQLAlchemy + Pandas + LightGBM + SHAP + LLM  
> **Base URL**: `http://localhost:8000/api/v1`  
> **文档版本**: v1.0 · **日期**: 2026-03-08  
> **适用端**: 教师端 / 管理员端

---

## 0. 全局约定

### 0.1 统一响应结构

```json
{
  "status": "success",
  "data": { "..." },
  "meta": { "page": 1, "size": 20, "total": 256 }
}
```

### 0.2 错误响应

```json
HTTP 404
{ "detail": "学生 20230001 的特征数据尚未计算" }
```

### 0.3 风险等级判定规则

| 概率区间 | 风险等级 | 颜色建议 |
|----------|---------|---------|
| `risk_probability ≥ 0.7` | 高风险 | 🔴 `#ff4d4f` |
| `0.4 ≤ risk_probability < 0.7` | 中风险 | 🟡 `#faad14` |
| `risk_probability < 0.4` | 低风险 | 🟢 `#52c41a` |

### 0.4 聚类标签映射

| `cluster_label` | `cluster_name` |
|:---------------:|----------------|
| 1 | 奋斗学霸型 |
| 2 | 普通平庸型 |
| 3 | 游戏沉迷型 |
| 4 | 社交活跃型 |

---

## 模块一：全局数据大盘

---

### 1.1 风险总览统计卡片

> 用于大盘顶部的统计卡片（总人数、各等级人数、风险率、模型 AUC）

- **接口名称**: 风险总览统计
- **请求路径**: `GET /api/v1/analytics/overview`
- **请求参数**: 无
- **响应体示例**:

```json
{
  "status": "success",
  "data": {
    "total_students": 1200,
    "high_risk": { "count": 86, "ratio": 0.0717 },
    "medium_risk": { "count": 214, "ratio": 0.1783 },
    "low_risk": { "count": 900, "ratio": 0.7500 },
    "risk_rate": 0.25,
    "model_auc": 0.8347
  }
}
```

- **前端对接**: 4 张数字卡片，分别显示总人数和三个风险等级

---

### 1.2 四类行为模式聚类分布

> 用于饼图 / 柱状图展示 KMeans 聚类的 4 类行为群体

- **接口名称**: 聚类分布统计
- **请求路径**: `GET /api/v1/analytics/clusters`
- **请求参数**: 无
- **响应体示例**:

```json
{
  "status": "success",
  "data": [
    { "cluster_label": 1, "cluster_name": "奋斗学霸型", "count": 320, "ratio": 0.2667 },
    { "cluster_label": 2, "cluster_name": "普通平庸型", "count": 480, "ratio": 0.4000 },
    { "cluster_label": 3, "cluster_name": "游戏沉迷型", "count": 160, "ratio": 0.1333 },
    { "cluster_label": 4, "cluster_name": "社交活跃型", "count": 240, "ratio": 0.2000 }
  ],
  "meta": { "total_students": 1200 }
}
```

- **ECharts 饼图映射**: `name` ← `cluster_name`, `value` ← `count`

---

### 1.3 八维特征全校均值（雷达基准线）

> 用于雷达图的全校平均基准线，与单个学生对比

- **接口名称**: 全校特征均值
- **请求路径**: `GET /api/v1/analytics/feature-averages`
- **请求参数**: 无
- **响应体示例**:

```json
{
  "status": "success",
  "data": {
    "dimensions": [
      { "key": "academic",        "label": "学业基础",   "avg": 72.5 },
      { "key": "classroom",       "label": "课堂投入",   "avg": 81.3 },
      { "key": "online_learning", "label": "在线学习",   "avg": 65.8 },
      { "key": "library",         "label": "图书馆沉浸", "avg": 58.2 },
      { "key": "internet",        "label": "网络自律",   "avg": 55.0 },
      { "key": "routine",         "label": "作息规律",   "avg": 63.7 },
      { "key": "fitness",         "label": "体质运动",   "avg": 68.4 },
      { "key": "honor",           "label": "综合荣誉",   "avg": 40.1 }
    ]
  }
}
```

- **ECharts 雷达图映射**: `indicator` ← `[{name: label, max: 100}]`, 全校均值 `series.data` ← `[avg, avg, ...]`

---

## 模块二：风险预警与干预

---

### 2.1 风险学生分页列表

> 教师查看高/中/低风险学生列表，支持筛选、排序、分页

- **接口名称**: 风险学生列表
- **请求路径**: `GET /api/v1/warnings/students`
- **请求参数**:

| 参数 | 位置 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|:----:|--------|------|
| `risk_level` | Query | string | 否 | `all` | `high` / `medium` / `low` / `all` |
| `cluster_label` | Query | int | 否 | - | 按聚类标签筛选 (1~4) |
| `college` | Query | string | 否 | - | 按学院名称筛选 |
| `page` | Query | int | 否 | 1 | 页码 |
| `size` | Query | int | 否 | 20 | 每页条数 (上限100) |
| `sort_by` | Query | string | 否 | `risk_probability` | 排序字段 |
| `order` | Query | string | 否 | `desc` | `asc` / `desc` |

- **响应体示例**:

```json
{
  "status": "success",
  "data": [
    {
      "student_id": "20234350520",
      "college": "计算机学院",
      "major": "软件工程",
      "cluster_label": 3,
      "cluster_name": "游戏沉迷型",
      "risk_probability": 0.8734,
      "risk_level": "高风险",
      "gpa": 1.85,
      "fail_count": 4,
      "late_night_online_days": 45
    },
    {
      "student_id": "20234350521",
      "college": "计算机学院",
      "major": "网络工程",
      "cluster_label": 2,
      "cluster_name": "普通平庸型",
      "risk_probability": 0.7102,
      "risk_level": "高风险",
      "gpa": 2.10,
      "fail_count": 3,
      "late_night_online_days": 32
    }
  ],
  "meta": { "page": 1, "size": 20, "total": 86 }
}
```

- **前端对接**: 表格组件 + 分页器，点击行跳转至学生画像详情

---

### 2.2 聚类群体学生列表

> 点击某个聚类类别后，查看该群体下的全部学生

- **接口名称**: 按聚类查学生
- **请求路径**: `GET /api/v1/analytics/clusters/{label}/students`
- **请求参数**:

| 参数 | 位置 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|:----:|--------|------|
| `label` | Path | int | 是 | - | 聚类标签 1~4 |
| `page` | Query | int | 否 | 1 | 页码 |
| `size` | Query | int | 否 | 20 | 每页条数 |

- **响应体示例**:

```json
{
  "status": "success",
  "data": {
    "cluster_label": 3,
    "cluster_name": "游戏沉迷型",
    "students": [
      { "student_id": "20234350520", "college": "计算机学院", "major": "软件工程" },
      { "student_id": "20234350533", "college": "数学学院", "major": "应用数学" }
    ]
  },
  "meta": { "page": 1, "size": 20, "total": 160 }
}
```

---

## 模块三：学生全息画像

---

### 3.1 学生基本信息

> 画像页面顶部的个人信息卡片

- **接口名称**: 学生基本信息
- **请求路径**: `GET /api/v1/students/{student_id}`
- **请求参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|:----:|------|
| `student_id` | Path | string | 是 | 学号 |

- **响应体示例**:

```json
{
  "status": "success",
  "data": {
    "XH": "20234350520",
    "XB": "男",
    "MZMC": "汉族",
    "ZZMMMC": "共青团员",
    "CSRQ": "2003-05-20",
    "JG": "湖南长沙",
    "XSM": "计算机学院",
    "ZYM": "软件工程"
  }
}
```

---

### 3.2 学生八维特征雷达图数据

> 画像核心：返回 19 个原始指标 + 8 维归一化雷达图得分 + 聚类标签 + 风险概率

- **接口名称**: 学生行为特征
- **请求路径**: `GET /api/v1/students/{student_id}/features`
- **请求参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|:----:|------|
| `student_id` | Path | string | 是 | 学号 |

- **响应体示例**:

```json
{
  "status": "success",
  "data": {
    "student_id": "20234350520",
    "cluster_label": 3,
    "cluster_name": "游戏沉迷型",
    "risk_probability": 0.8734,
    "risk_level": "高风险",
    "raw_features": {
      "gpa": 1.85,
      "fail_count": 4,
      "edge_fail_rate": 0.35,
      "attendance_rate": 0.62,
      "skip_class_count": 18,
      "class_focus_rate": 0.45,
      "video_completion_rate": 0.30,
      "quiz_stability": 48.5,
      "forum_activeness": 2,
      "library_freq_per_week": 0.8,
      "avg_library_duration": 1.2,
      "daily_online_duration": 8.5,
      "late_night_online_days": 45,
      "early_rising_regularity": 0.25,
      "late_return_count": 22,
      "avg_pe_score": 58.0,
      "weekly_exercise_freq": 0.5,
      "total_scholarship_amount": 0,
      "has_status_warning": true
    },
    "radar_scores": [
      { "dimension": "学业基础",   "score": 25, "max": 100 },
      { "dimension": "课堂投入",   "score": 38, "max": 100 },
      { "dimension": "在线学习",   "score": 28, "max": 100 },
      { "dimension": "图书馆沉浸", "score": 22, "max": 100 },
      { "dimension": "网络自律",   "score": 15, "max": 100 },
      { "dimension": "作息规律",   "score": 20, "max": 100 },
      { "dimension": "体质运动",   "score": 35, "max": 100 },
      { "dimension": "综合荣誉",   "score": 5,  "max": 100 }
    ]
  }
}
```

- **ECharts 雷达图映射**:
  - `indicator` ← `radar_scores` 的 `[{name: dimension, max: max}]`
  - 个人得分 `series[0].data` ← `radar_scores` 的 `[score, score, ...]`
  - 全校均值 `series[1].data` ← 调用 `1.3` 接口获取

#### 八维得分计算口径

| 维度 | 原始指标 | 得分计算公式 (百分制) |
|------|---------|----------------------|
| 学业基础 | `gpa`, `fail_count`, `edge_fail_rate` | `gpa/4.5×50 + (1-fail_count/10)×30 + (1-edge_fail_rate)×20` |
| 课堂投入 | `attendance_rate`, `skip_class_count`, `class_focus_rate` | `attendance×40 + focus×40 + (1-skip/30)×20` |
| 在线学习 | `video_completion_rate`, `quiz_stability`, `forum_activeness` | `video×40 + quiz/100×40 + min(forum/20,1)×20` |
| 图书馆沉浸 | `library_freq_per_week`, `avg_library_duration` | `min(freq/5,1)×50 + min(duration/4,1)×50` |
| 网络自律 | `daily_online_duration`, `late_night_online_days` | `(1-min(online/10,1))×50 + (1-min(nights/60,1))×50` |
| 作息规律 | `early_rising_regularity`, `late_return_count` | `rising×60 + (1-min(late/30,1))×40` |
| 体质运动 | `avg_pe_score`, `weekly_exercise_freq` | `pe/100×60 + min(exercise/7,1)×40` |
| 综合荣誉 | `total_scholarship_amount`, `has_status_warning` | `min(scholarship/5000,1)×70 + (!warning×30)` |

---

## 模块四：大模型智能解释

---

### 4.1 SHAP 归因因子分析

> 返回 SHAP TreeExplainer 计算的 TOP 3 关键归因因子，前端渲染为水平条形图

- **接口名称**: SHAP 关键归因因子
- **请求路径**: `GET /api/v1/report/student/{student_id}/shap`
- **请求参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|:----:|------|
| `student_id` | Path | string | 是 | 学号 |

- **响应体示例**:

```json
{
  "status": "success",
  "data": {
    "student_id": "20234350520",
    "risk_score": 87.3,
    "top_factors": [
      {
        "feature": "late_night_online_days",
        "feature_cn": "深夜沉迷天数",
        "effect": "positive",
        "importance": 0.34
      },
      {
        "feature": "skip_class_count",
        "feature_cn": "逃课/迟到次数",
        "effect": "positive",
        "importance": 0.28
      },
      {
        "feature": "gpa",
        "feature_cn": "绩点(GPA)",
        "effect": "negative",
        "importance": 0.15
      }
    ]
  }
}
```

- **ECharts 水平条形图映射**:
  - `yAxis.data` ← `feature_cn`（从下到上排列）
  - `series.data` ← `importance`
  - 颜色逻辑：`effect === 'positive'` → 🔴 红色（推高风险），`'negative'` → 🟢 绿色（降低风险）

---

### 4.2 LLM 个性化评价报告

> 完整 Pipeline：DB 特征 → SHAP 归因 → LLM 生成自然语言报告  
> **⚠️ 响应耗时 3~10 秒**，前端需显示加载动画

- **接口名称**: 智能评价报告
- **请求路径**: `GET /api/v1/report/student/{student_id}`
- **请求参数**:

| 参数 | 位置 | 类型 | 必填 | 说明 |
|------|------|------|:----:|------|
| `student_id` | Path | string | 是 | 学号 |

- **响应体示例**:

```json
{
  "status": "success",
  "student_id": "20234350520",
  "cluster_name": "游戏沉迷型",
  "risk_assessment": {
    "risk_score": 87.3,
    "top_factors": [
      { "feature": "late_night_online_days", "feature_cn": "深夜沉迷天数", "effect": "positive", "importance": 0.34 },
      { "feature": "skip_class_count", "feature_cn": "逃课/迟到次数", "effect": "positive", "importance": 0.28 },
      { "feature": "gpa", "feature_cn": "绩点(GPA)", "effect": "negative", "importance": 0.15 }
    ]
  },
  "smart_report": "## 学生群体画像\n该学生被系统归类为「游戏沉迷型」群体。在8个行为维度中，网络自律指数和课堂投入度显著低于全校平均水平，学业风险概率高达 87.3%。\n\n## 核心风险指标解读\n1. **深夜沉迷天数 (45天)**: 这是影响该学生学业表现的最大因素。过去一个学期中，有近三分之一的日子存在深夜上网行为，严重影响次日课堂状态与精力恢复。\n2. **逃课/迟到次数 (18次)**: 缺勤频率远超班级均值(3次)，表明课堂参与意愿严重不足。\n3. **绩点 (1.85)**: 已低于学业警告线 2.0，如不及时干预，下学期面临学籍异动风险。\n\n## 建设性改进建议\n1. 建议辅导员安排一对一深度谈话，了解深夜上网的具体成因（游戏、社交、还是心理压力）。\n2. 推荐加入「学业互助计划」，由同专业高绩点同学进行每周一次的结对辅导。\n3. 引导安装手机使用时间管理工具（如Forest），逐步将熄灯后在线时长控制在30分钟以内。"
}
```

- **前端对接**: `smart_report` 为 Markdown 格式文本，需用 `v-html` 或 Markdown 渲染组件展示

---

### 4.3 模型训练触发（管理员操作）

> 管理员一键训练，训练 KMeans + LightGBM 并回写结果到数据库

- **接口名称**: 一键训练模型
- **请求路径**: `POST /api/v1/model/train`
- **请求参数**: 无（从 `behavior_feature` 表自动读取）
- **响应体示例**:

```json
{
  "status": "success",
  "clustering": {
    "n_clusters": 4,
    "inertia": 1523.45,
    "distribution": {
      "奋斗学霸型": 320,
      "普通平庸型": 480,
      "游戏沉迷型": 160,
      "社交活跃型": 240
    }
  },
  "risk_model": {
    "total_samples": 1200,
    "risk_students": 300,
    "safe_students": 900,
    "train_auc": 0.8347
  },
  "message": "已训练并回写 1200 条 cluster_label 和 risk_probability"
}
```

---

## 附录 A：八维特征字段字典

| 维度 | 字段名 | 中文名 | 类型 | 取值范围 |
|------|--------|--------|:----:|----------|
| 学业基础 | `gpa` | 绩点 | float | 0.5~4.5 |
| 学业基础 | `fail_count` | 挂科次数 | int | ≥0 |
| 学业基础 | `edge_fail_rate` | 及格边缘游离度 | float | 0~1 |
| 课堂投入 | `attendance_rate` | 全勤率 | float | 0~1 |
| 课堂投入 | `skip_class_count` | 逃课迟到次数 | int | ≥0 |
| 课堂投入 | `class_focus_rate` | 课堂专注度 | float | 0~1 |
| 在线学习 | `video_completion_rate` | 视频完成率 | float | 0~1 |
| 在线学习 | `quiz_stability` | 测验稳定度 | float | 10~100 |
| 在线学习 | `forum_activeness` | 论坛活跃度 | int | ≥0 |
| 图书馆沉浸 | `library_freq_per_week` | 周均进馆频次 | float | ≥0 |
| 图书馆沉浸 | `avg_library_duration` | 平均逗留时长(h) | float | ≥0 |
| 网络自律 | `daily_online_duration` | 日均在线时长(h) | float | ≥0 |
| 网络自律 | `late_night_online_days` | 深夜沉迷天数 | int | ≥0 |
| 作息规律 | `early_rising_regularity` | 早起规律性 | float | 0~1 |
| 作息规律 | `late_return_count` | 晚归次数 | int | ≥0 |
| 体质运动 | `avg_pe_score` | 体测均分 | float | 30~100 |
| 体质运动 | `weekly_exercise_freq` | 周均运动次数 | float | ≥0 |
| 综合荣誉 | `total_scholarship_amount` | 奖学金总额(元) | float | ≥0 |
| 综合荣誉 | `has_status_warning` | 学籍异动预警 | bool | true/false |

## 附录 B：ML 产出字段

| 字段名 | 中文名 | 类型 | 说明 |
|--------|--------|:----:|------|
| `cluster_label` | 聚类标签 | int | 1~4，见 §0.4 映射表 |
| `risk_probability` | 风险概率 | float | 0~1，见 §0.3 等级判定 |

## 附录 C：接口总览速查

| # | 模块 | 方法 | 路径 | 说明 |
|---|------|:----:|------|------|
| 1 | 大盘 | GET | `/analytics/overview` | 风险统计卡片 |
| 2 | 大盘 | GET | `/analytics/clusters` | 聚类分布饼图 |
| 3 | 大盘 | GET | `/analytics/feature-averages` | 全校均值雷达 |
| 4 | 预警 | GET | `/warnings/students` | 风险学生列表 |
| 5 | 预警 | GET | `/analytics/clusters/{label}/students` | 聚类反查 |
| 6 | 画像 | GET | `/students/{student_id}` | 基本信息 |
| 7 | 画像 | GET | `/students/{student_id}/features` | 八维雷达数据 |
| 8 | 报告 | GET | `/report/student/{student_id}/shap` | SHAP归因 |
| 9 | 报告 | GET | `/report/student/{student_id}` | LLM智能报告 |
| 10 | 管理 | POST | `/model/train` | 模型训练 |
