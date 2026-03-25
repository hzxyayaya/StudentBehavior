# Dev Startup

Last Updated: 2026-03-20

## 目标

为后续 agent 提供最小可执行的启动入口，优先用于“读取现状”和“验证基础可运行性”，不是保证生产就绪。

## 前端

工作目录: `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_frontend`

已发现脚本:

- `npm run dev`
- `npm run build`
- `npm run preview`

最小启动步骤:

```powershell
cd C:\Users\Orion\Desktop\StudentBehavior\student_behavior_frontend
npm install
npm run dev
```

## 后端

工作目录: `C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server`

已发现:

- `pyproject.toml`
- `uv.lock`
- `main.py`
- `app/main.py`

最小启动步骤:

```powershell
cd C:\Users\Orion\Desktop\StudentBehavior\student_behavior_ai_server
uv sync
uv run uvicorn app.main:app --reload
```

## 启动前注意

- 后端可能依赖 `.env` 中的数据库和 API Key 配置
- 当前未确认数据库是否已初始化
- `tests/` 中存在数据库与 LLM 相关脚本，但尚未执行验证

## 当前结论

- 前后端都具备基本启动入口
- 但缺少一份经过验证的“可复现启动结果”
- 如果下一轮要做重写前核验，应先补一轮启动验证并记录结果到 `docs/session-progress.md`
