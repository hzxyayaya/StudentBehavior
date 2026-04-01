<template>
  <section class="status-bar panel">
    <div class="panel-inner status-inner">
      <div class="status-copy">
        <p class="eyebrow">演示状态</p>
        <strong>当前页面消费真实 `demo-api`，但风险等级、风险概率、群体分层、影响因子和模型摘要仍为 stub/规则版结果。</strong>
        <p class="muted">推荐联调学期：2023-2、2024-1、2024-2；默认学期：2024-2；示例学生：pjwrqxbj901。</p>
      </div>
      <div class="status-tags">
        <span class="tag cool">真实 API</span>
        <span class="tag">演示口径</span>
        <span class="tag">Stub 字段未替模</span>
      </div>
    </div>
  </section>
</template>

<style scoped>
.status-bar {
  background:
    linear-gradient(135deg, rgba(255, 248, 235, 0.92), rgba(247, 243, 255, 0.9)),
    radial-gradient(circle at top right, rgba(255, 190, 92, 0.18), transparent 30%);
  border: 1px solid rgba(191, 120, 31, 0.14);
}

.status-inner {
  display: grid;
  gap: 16px;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
}

.status-copy {
  display: grid;
  gap: 6px;
}

.status-copy p,
.status-copy strong {
  margin: 0;
}

.status-tags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

@media (max-width: 960px) {
  .status-inner {
    grid-template-columns: 1fr;
  }

  .status-tags {
    justify-content: flex-start;
  }
}
</style>
