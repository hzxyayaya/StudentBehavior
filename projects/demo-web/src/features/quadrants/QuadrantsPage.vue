<template>
  <AppShell>
    <section class="panel">
      <div class="panel-inner stack">
        <p class="eyebrow">群体分层</p>
        <h2 class="title">行为模式分层</h2>
        <p class="muted">按重点群体标签概览当前学期的群体状态，支撑后续预警筛查与学生下钻。</p>
      </div>
    </section>

    <LoadingState v-if="query.isLoading.value" label="正在加载群体分层..." />
    <ErrorState v-else-if="query.error.value" title="群体分层加载失败" :description="errorMessage" @retry="query.refetch()" />
    <EmptyState
      v-else-if="groups.length === 0"
      title="当前学期暂无群体分层结果"
      description="请切换到真实联调学期后重试。"
    />
    <section v-else class="group-grid">
      <article v-for="item in groups" :key="item.group_segment" class="panel group-card">
        <div class="panel-inner stack">
          <div class="group-head">
            <h3>{{ item.group_segment }}</h3>
            <span class="tag">{{ item.student_count }} 人</span>
          </div>
          <div class="group-metric">
            <span class="muted">平均风险概率</span>
            <strong>{{ formatRisk(item.avg_risk_probability) }}</strong>
          </div>
          <div class="stack">
            <p class="muted">群体平均八维得分</p>
            <div v-for="dimension in item.avg_dimension_scores" :key="dimension.dimension" class="dimension-row">
              <div class="dimension-meta">
                <div class="dimension-copy">
                  <strong>{{ dimension.dimension }}</strong>
                  <span class="muted">{{ dimension.label ?? '待补充' }}</span>
                </div>
                <div class="dimension-score">
                  <span class="tag" :class="dimensionTagClass(dimension.level)">
                    {{ dimensionLevelText(dimension.level) }}
                  </span>
                  <span class="muted">{{ Math.round(dimension.score * 100) }}分</span>
                </div>
              </div>
              <p class="muted dimension-explanation">
                {{ dimension.explanation ?? '当前维度尚未提供完整校准结果' }}
              </p>
              <div class="dimension-track">
                <div class="dimension-fill" :style="{ width: `${dimension.score * 100}%` }"></div>
              </div>
              <div v-if="dimension.metrics?.length" class="dimension-tags">
                <span v-for="metric in dimension.metrics?.slice(0, 2) ?? []" :key="metric.metric" class="tag">
                  {{ metric.metric }} {{ formatMetric(metric) }}
                </span>
              </div>
              <div v-else class="muted">暂无指标</div>
            </div>
          </div>
          <div class="stack">
            <p class="muted">主导因子</p>
            <div v-for="factor in item.top_factors" :key="factor.dimension" class="factor-row">
              <div class="factor-head">
                <strong>{{ factor.dimension }}</strong>
                <span v-if="factor.label" class="tag">{{ factor.label }}</span>
              </div>
              <span class="muted">{{ factor.explanation }}</span>
              <div v-if="factor.metrics?.length" class="factor-tags">
                <span v-for="metric in factor.metrics?.slice(0, 2) ?? []" :key="metric.metric" class="tag">
                  {{ metric.metric }} {{ formatMetric(metric) }}
                </span>
              </div>
            </div>
          </div>
          <RouterLink
            class="btn secondary link-btn"
            :to="{
              path: '/warnings',
              query: { term, group_segment: item.group_segment },
            }"
          >
            查看该群体预警
          </RouterLink>
        </div>
      </article>
    </section>
  </AppShell>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { RouterLink } from 'vue-router'

import { useTermStore } from '@/app/term'
import AppShell from '@/components/layout/AppShell.vue'
import EmptyState from '@/components/state/EmptyState.vue'
import ErrorState from '@/components/state/ErrorState.vue'
import LoadingState from '@/components/state/LoadingState.vue'
import { getGroups } from '@/lib/api'
import { formatApiErrorMessage, formatRisk } from '@/lib/format'

const termStore = useTermStore()
const query = useQuery({
  queryKey: computed(() => ['groups', termStore.term.value]),
  queryFn: () => getGroups(termStore.term.value),
})

const groups = computed(() => query.data.value?.groups ?? [])
const term = computed(() => termStore.term.value)
const errorMessage = computed(() => formatApiErrorMessage(query.error.value, '当前群体分层数据暂不可用，请稍后重试'))

function dimensionLevelText(level?: string) {
  if (!level) return '待补充'
  if (level === 'high') return '高'
  if (level === 'medium') return '中'
  return '低'
}

function dimensionTagClass(level?: string) {
  if (!level) return 'pending'
  if (level === 'high') return 'hot'
  if (level === 'medium') return 'warn'
  return 'cool'
}

function formatMetric(metric: { display?: string; value: number | string }) {
  return metric.display || String(metric.value)
}
</script>

<style scoped>
.group-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.group-card {
  min-height: 280px;
}

.group-head,
.group-metric {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.factor-row {
  display: grid;
  gap: 6px;
  padding: 12px 0;
  border-top: 1px solid rgba(28, 34, 56, 0.08);
}

.dimension-row {
  display: grid;
  gap: 6px;
}

.dimension-meta {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.dimension-copy {
  display: grid;
  gap: 4px;
}

.dimension-score {
  display: grid;
  gap: 6px;
  justify-items: end;
  white-space: nowrap;
}

.dimension-explanation {
  margin: 0;
}

.tag.pending {
  color: #667085;
  border-color: #d0d5dd;
  background: #f2f4f7;
}

.dimension-track {
  height: 10px;
  border-radius: 999px;
  background: #eef2f7;
  overflow: hidden;
}

.dimension-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #ff8746 0%, #ff4b00 100%);
}

.dimension-tags,
.factor-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.factor-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.link-btn {
  justify-self: start;
}

@media (max-width: 960px) {
  .group-grid {
    grid-template-columns: 1fr;
  }
}
</style>
