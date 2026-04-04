<template>
  <AppShell>
    <section class="panel">
      <div class="panel-inner stack">
        <p class="eyebrow">学业轨迹演化与关键行为分析</p>
        <h2 class="title">学期风险轨迹与关键行为</h2>
        <p class="muted">结合学期风险趋势、当前高频触发因子与重点群体变化，观察风险如何演化以及哪些行为在当前学期最关键。</p>
      </div>
    </section>

    <LoadingState v-if="trajectoryQuery.isLoading.value" label="正在加载学业轨迹..." />
    <ErrorState v-else-if="hasError" title="学业轨迹加载失败" :description="errorMessage" @retry="retry" />
    <EmptyState
      v-else-if="trajectoryRows.length === 0 && factorRows.length === 0 && groups.length === 0"
      title="当前学期暂无轨迹分析结果"
      description="请切换到有真实轨迹数据的学期后重试。"
    />
    <template v-else>
      <section class="trajectory-grid">
        <article class="panel">
          <div class="panel-inner stack">
            <div class="section-head">
              <h3>学期风险轨迹</h3>
              <span class="tag cool">{{ term }}</span>
            </div>
            <div v-if="trajectoryRows.length === 0" class="muted">暂无学期轨迹数据</div>
            <div v-for="row in trajectoryRows" :key="row.term" class="trend-row">
              <div>
                <strong>{{ row.term }}</strong>
                <div class="muted">高风险人数 {{ row.high_risk_count }}</div>
              </div>
              <div class="trend-meta">
                <strong>{{ row.avg_risk_score.toFixed(1) }}</strong>
                <span class="tag">{{ riskChangeText(row.risk_change_direction) }}</span>
              </div>
            </div>
          </div>
        </article>

        <article class="panel">
          <div class="panel-inner stack">
            <h3>关键行为因子</h3>
            <div v-if="factorRows.length === 0" class="muted">暂无关键因子</div>
            <div v-for="item in factorRows" :key="item.feature" class="factor-row">
              <div>
                <strong>{{ item.feature_cn ?? item.feature }}</strong>
                <div class="muted">触发 {{ item.count }} 次</div>
              </div>
              <strong>{{ item.importance.toFixed(2) }}</strong>
            </div>
          </div>
        </article>
      </section>

      <section class="trajectory-grid">
        <article class="panel">
          <div class="panel-inner stack">
            <h3>当前学期关键维度</h3>
            <div v-if="dimensionRows.length === 0" class="muted">暂无维度摘要</div>
            <div v-for="item in dimensionRows" :key="item.dimension" class="dimension-row">
              <div>
                <strong>{{ item.dimension }}</strong>
                <div class="muted">{{ item.label ?? '待补充' }}</div>
              </div>
              <strong>{{ displayDimensionScore(item) }}</strong>
            </div>
          </div>
        </article>

        <article class="panel">
          <div class="panel-inner stack">
            <h3>重点群体变化</h3>
            <div v-if="groups.length === 0" class="muted">暂无群体变化数据</div>
            <div v-for="group in groups" :key="group.group_segment" class="group-row">
              <div>
                <strong>{{ group.group_segment }}</strong>
                <div class="muted">{{ group.student_count }} 人</div>
              </div>
              <div class="stack compact align-end">
                <strong>{{ formatRisk(group.avg_risk_probability) }}</strong>
                <span class="muted">{{ dominantRiskChange(group.risk_change_summary) }}</span>
                <span class="muted">{{ leadingFactor(group) }}</span>
              </div>
            </div>
          </div>
        </article>
      </section>

      <section class="panel">
        <div class="panel-inner stack">
          <div class="section-head">
            <h3>重点学生样本轨迹</h3>
            <span class="muted">当前学期高风险学生样本与主导行为链路</span>
          </div>
          <div v-if="warningRows.length === 0" class="muted">暂无重点学生样本</div>
          <RouterLink
            v-for="item in warningRows"
            :key="item.student_id"
            class="sample-row"
            :to="{
              path: `/students/${item.student_id}`,
              query: { term, source: 'warnings', risk_level: item.risk_level },
            }"
          >
            <div class="sample-main">
              <strong>{{ item.student_name }}</strong>
              <div class="muted">{{ item.major_name }} · {{ item.group_segment }}</div>
            </div>
            <div class="sample-metrics">
              <span class="tag">{{ formatWarningLevel(item.risk_level) }}</span>
              <strong>{{ formatRisk(item.risk_probability) }}</strong>
              <span class="muted">{{ sampleFactorText(item) }}</span>
            </div>
          </RouterLink>
        </div>
      </section>
    </template>
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
import { getTrajectoryAnalysis } from '@/lib/api'
import { formatApiErrorMessage, formatRisk, formatRiskLevel } from '@/lib/format'
import type { TrajectoryAnalysisData, WarningsData } from '@/lib/types'

const termStore = useTermStore()

const trajectoryQuery = useQuery({
  queryKey: computed(() => ['trajectory-analysis', termStore.term.value]),
  queryFn: () => getTrajectoryAnalysis(termStore.term.value),
})

const term = computed(() => termStore.term.value)
const trajectoryRows = computed(() => trajectoryQuery.data.value?.risk_trend_summary ?? [])
const factorRows = computed(() => (trajectoryQuery.data.value?.key_factors ?? []).slice(0, 5))
const dimensionRows = computed(() => (trajectoryQuery.data.value?.current_dimensions ?? []).slice(0, 4))
const groups = computed(() => (trajectoryQuery.data.value?.group_changes ?? []).slice(0, 4))
const warningRows = computed(() => (trajectoryQuery.data.value?.student_samples ?? []).slice(0, 5))
const hasError = computed(() => Boolean(trajectoryQuery.error.value))
const errorMessage = computed(() =>
  formatApiErrorMessage(
    trajectoryQuery.error.value,
    '当前学业轨迹数据暂不可用，请稍后重试',
  ),
)

function retry() {
  trajectoryQuery.refetch()
}

function displayDimensionScore(item: { average_score?: number; score?: number }) {
  const value = typeof item.average_score === 'number' ? item.average_score : item.score
  if (typeof value !== 'number') return '待补充'
  return value <= 1 ? `${Math.round(value * 100)}分` : `${Math.round(value)}分`
}

function dominantRiskChange(summary?: Partial<Record<'rising' | 'steady' | 'falling', number>>) {
  if (!summary) return '暂无变化摘要'
  const entries = Object.entries(summary)
  if (entries.length === 0) return '暂无变化摘要'
  const top = entries.sort((a, b) => (b[1] ?? 0) - (a[1] ?? 0))[0]
  if (!top) return '暂无变化摘要'
  return `${riskChangeText(top[0] as 'rising' | 'steady' | 'falling')} ${top[1] ?? 0} 人`
}

function leadingFactor(group: TrajectoryAnalysisData['group_changes'][number]) {
  return group.top_factors[0]?.dimension ?? '暂无主导因子'
}

function riskChangeText(direction?: 'rising' | 'steady' | 'falling') {
  if (direction === 'rising') return '上升'
  if (direction === 'falling') return '下降'
  return '持平'
}

function formatWarningLevel(level: string) {
  return formatRiskLevel(level as WarningsData['items'][number]['risk_level'])
}

function sampleFactorText(item: WarningsData['items'][number]) {
  const parts = item.top_risk_factors.slice(0, 2).map((factor) => factor.feature_cn ?? factor.feature)
  return parts.join(' / ') || '暂无关键因子'
}
</script>

<style scoped>
.trajectory-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.section-head,
.trend-row,
.factor-row,
.dimension-row,
.group-row,
.sample-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.trend-row,
.factor-row,
.dimension-row,
.group-row,
.sample-row {
  padding: 12px 0;
  border-top: 1px solid rgba(28, 34, 56, 0.08);
}

.sample-row {
  color: inherit;
}

.sample-main,
.sample-metrics {
  display: grid;
  gap: 4px;
}

.sample-metrics {
  justify-items: end;
}

.trend-meta,
.align-end {
  align-items: flex-end;
}

.compact {
  gap: 4px;
}

@media (max-width: 960px) {
  .trajectory-grid {
    grid-template-columns: 1fr;
  }
}
</style>
