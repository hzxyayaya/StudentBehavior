# Git Harness

Last Updated: 2026-03-20

## 当前事实

- `C:\Users\Orion\Desktop\StudentBehavior` 已初始化为 Git 仓库。
- 当前默认分支为 `main`。
- 当前尚无首个提交，因此还没有可恢复的稳定 checkpoint。

## 当前阶段约束

- 在完成首次提交之前，所有文档和实现结论都只能视为工作草稿。

## 建议的最小 Git 规则

1. 首次提交只提交“现状提取”和“文档初始化”产物，不混入大规模重写代码。
2. 后续分支统一使用 `codex/` 前缀，例如 `codex/rewrite-baseline`。
3. 每次进入新的实现批次前，先记录一个可恢复 checkpoint。
4. handoff 时必须更新 `docs/session-progress.md`，说明最近完成、当前阻塞和下一步。

## 推荐 checkpoint 节点

- `baseline/extracted-current-state`: 现状提取完成
- `baseline/rewrite-scope-confirmed`: 重写范围确认完成
- `impl/<feature-name>`: 单功能实现完成并可验证

## handoff 最低要求

- 更新 `docs/feature-backlog.json`
- 更新 `docs/session-progress.md`
- 标注本轮依赖的文档
- 标注是否存在未验证假设

## 前置条件未满足时的处理

- 如果仍未创建首个提交，不进入高风险改写或大规模删除。
- 如果用户希望立即继续实现，先显式接受“无 checkpoint 风险”，否则暂停到基线提交完成。
