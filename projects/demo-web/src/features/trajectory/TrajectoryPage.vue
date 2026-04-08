<template>
    <section class="panel">
      <div class="panel-inner stack">
        <div class="page-title-row">
          <span class="title-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M5 17.25h14M6.5 14.75 10 11.25l3 2.5 4.5-6M10 11.25V7.5" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" />
            </svg>
          </span>
          <div>
            <p class="eyebrow">轨迹分析</p>
            <h2 class="title">学期轨迹与关键因子</h2>
          </div>
        </div>
      </div>
    </section>

    <Transition name="overview-stage" mode="out-in">
      <LoadingState
        v-if="isInitialLoading"
        key="loading"
        class="section-gap"
        label="正在加载轨迹分析..."
      />
      <ErrorState
        v-else-if="hasError"
        key="error"
        class="section-gap"
        title="轨迹分析加载失败"
        :description="errorMessage"
        @retry="retry"
      />
      <EmptyState
        v-else-if="trajectoryRows.length === 0 && factorRows.length === 0 && dimensionRows.length === 0 && groups.length === 0"
        key="empty"
        class="section-gap"
        title="当前学期暂无轨迹分析数据"
        description="请切换到有数据的学期后重试。"
      />

      <section v-else key="content" class="trajectory-stack">
        <section class="trend-section">
          <article class="panel trend-panel">
            <div class="panel-inner stack">
              <div class="section-head">
                <h3>学期趋势图</h3>
                <span class="tag">{{ trajectoryRows.length }} 个学期</span>
              </div>
              <LazyEChart :option="trajectoryChartOption" height="320px" />
            </div>
          </article>
        </section>

        <section class="ranking-strip">
          <article class="panel mini-panel">
            <div class="panel-inner stack compact-stack">
              <div class="section-head">
                <h3>关键行为因子排行</h3>
                <span class="tag">{{ factorRankingRows.length }} 项</span>
              </div>
              <div v-if="factorRankingRows.length === 0" class="empty-copy muted">暂无关键因子</div>
              <div v-else class="ranking-list">
                <div v-for="(item, index) in factorRankingRows" :key="item.feature" class="ranking-row">
                  <span class="ranking-index">{{ index + 1 }}</span>
                  <div class="ranking-copy">
                    <strong>{{ item.feature_cn ?? item.feature }}</strong>
                    <small class="muted">{{ item.count }} 人</small>
                  </div>
                  <strong class="ranking-value">{{ item.importance.toFixed(2) }}</strong>
                </div>
              </div>
            </div>
          </article>

          <article class="panel mini-panel">
            <div class="panel-inner stack compact-stack">
              <div class="section-head">
                <h3>当前学期关键维度排行</h3>
                <span class="tag">{{ dimensionRankingRows.length }} 项</span>
              </div>
              <div v-if="dimensionRankingRows.length === 0" class="empty-copy muted">暂无维度排行</div>
              <div v-else class="ranking-list">
                <div v-for="(item, index) in dimensionRankingRows" :key="item.dimension" class="ranking-row">
                  <span class="ranking-index">{{ index + 1 }}</span>
                  <div class="ranking-copy">
                    <strong>{{ item.dimension }}</strong>
                    <small class="muted">{{ item.label ?? '待补充' }}</small>
                  </div>
                  <strong class="ranking-value">{{ displayDimensionScore(item) }}</strong>
                </div>
              </div>
            </div>
          </article>

          <article class="panel mini-panel">
            <div class="panel-inner stack compact-stack">
              <div class="section-head">
                <h3>重点群体变化排行</h3>
                <span class="tag">{{ groupRankingRows.length }} 组</span>
              </div>
              <div v-if="groupRankingRows.length === 0" class="empty-copy muted">暂无群体变化</div>
              <div v-else class="ranking-list">
                <div v-for="(item, index) in groupRankingRows" :key="item.group_segment" class="ranking-row group-ranking-row">
                  <span class="ranking-index">{{ index + 1 }}</span>
                  <div class="ranking-copy">
                    <strong>{{ item.group_segment }}</strong>
                    <small class="muted">{{ formatChangeSummary(item.risk_change_summary) }}</small>
                  </div>
                  <strong class="ranking-value">{{ dominantRiskChange(item.risk_change_summary) }}</strong>
                </div>
              </div>
            </div>
          </article>
        </section>

        <section class="panel sample-panel">
          <div class="panel-inner stack">
            <div class="section-head">
              <div class="section-title-meta">
                <h3>重点学生样本轨迹</h3>
                <span class="tag">{{ term }}</span>
              </div>
              <span class="tag">共 {{ sampleRows.length }} 条</span>
            </div>

            <div class="sample-table">
              <div class="sample-row header">
                <span>学生</span>
                <span>专业 / 群体</span>
                <span>风险</span>
                <span>关键因子</span>
              </div>

              <RouterLink
                v-for="item in pagedSampleRows"
                :key="item.student_id"
                class="sample-row"
                :to="{
                  path: `/students/${item.student_id}`,
                  query: { term, source: 'warnings', risk_level: item.intervention_priority_level ?? item.risk_level },
                }"
              >
                <span>{{ item.student_name }} / {{ item.student_id }}</span>
                <span>{{ item.major_name }} / {{ item.group_segment }}</span>
                <span>{{ formatWarningLevel(item.intervention_priority_level ?? item.risk_level) }} · {{ formatRisk(item.risk_probability) }}</span>
                <span>{{ sampleFactorText(item) }}</span>
              </RouterLink>
            </div>

            <div v-if="samplePageCount > 1" class="pagination-bar">
              <button class="btn secondary" type="button" :disabled="samplePage <= 1" @click="samplePage -= 1">上一页</button>
              <div class="page-numbers">
                <button
                  v-for="item in visiblePageItems"
                  :key="String(item)"
                  class="page-num"
                  :class="{ active: item === samplePage, ellipsis: item === '...' }"
                  :disabled="item === '...'"
                  @click="typeof item === 'number' ? (samplePage = item) : undefined"
                >
                  {{ item }}
                </button>
              </div>
              <button class="btn secondary" type="button" :disabled="samplePage >= samplePageCount" @click="samplePage += 1">下一页</button>
            </div>
          </div>
        </section>
      </section>
    </Transition>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { RouterLink } from 'vue-router'
import type { EChartsOption } from 'echarts'

import { AVAILABLE_TERMS, useTermStore } from '@/app/term'
import LazyEChart from '@/components/charts/LazyEChart.vue'
import EmptyState from '@/components/state/EmptyState.vue'
import ErrorState from '@/components/state/ErrorState.vue'
import LoadingState from '@/components/state/LoadingState.vue'
import { getOverview, getTrajectoryAnalysis } from '@/lib/api'
import { formatApiErrorMessage, formatRisk, formatRiskLevel } from '@/lib/format'
import type { WarningsData } from '@/lib/types'

const termStore = useTermStore()

const trajectoryQuery = useQuery({
  queryKey: computed(() => ['trajectory-analysis', termStore.term.value]),
  queryFn: () => getTrajectoryAnalysis(termStore.term.value),
  placeholderData: (previousData) => previousData,
  staleTime: 0,
  refetchOnMount: 'always',
})
const overviewTrendQuery = useQuery({
  queryKey: ['trajectory-overview-trend'],
  queryFn: async () =>
    Promise.all(
      AVAILABLE_TERMS.map(async (item) => {
        const overview = await getOverview(item)
        return { term: item, overview }
      }),
    ),
  placeholderData: (previousData) => previousData,
  staleTime: 5 * 60 * 1000,
})

const term = computed(() => termStore.term.value)
const trajectoryRows = computed(() => trajectoryQuery.data.value?.risk_trend_summary ?? [])
const factorRows = computed(() => trajectoryQuery.data.value?.key_factors ?? [])
const dimensionRows = computed(() => trajectoryQuery.data.value?.current_dimensions ?? [])
const groups = computed(() => trajectoryQuery.data.value?.group_changes ?? [])
const sampleRows = computed(() => trajectoryQuery.data.value?.student_samples ?? [])
const factorRankingRows = computed(() => [...factorRows.value].sort((a, b) => b.importance - a.importance).slice(0, 5))
const dimensionRankingRows = computed(() => {
  const rows = [...dimensionRows.value]
  rows.sort((a, b) => dimensionNumericScore(b) - dimensionNumericScore(a))
  return rows.slice(0, 6)
})
const groupRankingRows = computed(() => {
  const rows = [...groups.value]
  rows.sort((a, b) => groupTrendScore(b.risk_change_summary) - groupTrendScore(a.risk_change_summary))
  return rows.slice(0, 5)
})
const elevatedRiskCounts = computed(() => {
  const rows = overviewTrendQuery.data.value ?? []
  return Object.fromEntries(
    rows.map(({ term: itemTerm, overview }) => [
      itemTerm,
      overview.risk_distribution.find((item) => item.risk_level === 'high')?.count ?? 0,
    ]),
  ) as Record<string, number>
})
const isInitialLoading = computed(
  () =>
    trajectoryQuery.isLoading.value &&
    trajectoryRows.value.length === 0 &&
    factorRows.value.length === 0 &&
    dimensionRows.value.length === 0 &&
    groups.value.length === 0,
)
const trajectoryChartOption = computed<EChartsOption>(() => ({
  color: ['#6d4fd2', '#4f7cff'],
  tooltip: { trigger: 'axis' },
  legend: {
    bottom: 0,
    textStyle: { color: '#667085' },
  },
  grid: { left: 52, right: 52, top: 46, bottom: 46, containLabel: true },
  xAxis: {
    type: 'category',
    data: [...trajectoryRows.value].reverse().map((item) => item.term),
    axisLine: { lineStyle: { color: '#d9dee6' } },
    axisTick: { show: false },
    axisLabel: { color: '#667085', margin: 10 },
  },
  yAxis: [
    {
      type: 'value',
      name: '平均风险分',
      nameLocation: 'end',
      nameGap: 16,
      nameTextStyle: { color: '#667085', fontSize: 12, align: 'left' },
      axisLine: { show: false },
      axisLabel: { color: '#667085' },
      splitLine: { lineStyle: { color: '#eef2f7' } },
    },
    {
      type: 'value',
      name: '较高及以上人数',
      nameLocation: 'end',
      nameGap: 16,
      nameTextStyle: { color: '#667085', fontSize: 12, align: 'right' },
      axisLine: { show: false },
      axisLabel: { color: '#667085' },
      splitLine: { show: false },
    },
  ],
  series: [
    {
      name: '平均风险分',
      type: 'line',
      smooth: true,
      yAxisIndex: 0,
      symbolSize: 8,
      areaStyle: { color: 'rgba(109, 79, 210, 0.14)' },
      lineStyle: { width: 3 },
      data: [...trajectoryRows.value].reverse().map((item) => item.avg_risk_score),
    },
    {
      name: '较高及以上人数',
      type: 'bar',
      yAxisIndex: 1,
      barMaxWidth: 26,
      itemStyle: {
        borderRadius: [8, 8, 0, 0],
        color: '#4f7cff',
      },
      data: [...trajectoryRows.value].reverse().map(
        (item) => elevatedRiskCounts.value[item.term] ?? item.elevated_risk_count ?? item.high_risk_count,
      ),
    },
  ],
}))

const samplePage = ref(1)
const samplePageSize = 5
const samplePageCount = computed(() => Math.max(1, Math.ceil(sampleRows.value.length / samplePageSize)))
const pagedSampleRows = computed(() => {
  const start = (samplePage.value - 1) * samplePageSize
  return sampleRows.value.slice(start, start + samplePageSize)
})

watch(
  () => termStore.term.value,
  () => {
    samplePage.value = 1
  },
)

watch(samplePageCount, (next) => {
  if (samplePage.value > next) samplePage.value = next
})

const visiblePageItems = computed<Array<number | '...'>>(() => {
  const totalPages = samplePageCount.value
  const current = samplePage.value
  if (totalPages <= 7) return Array.from({ length: totalPages }, (_, index) => index + 1)
  if (current <= 4) return [1, 2, 3, 4, 5, '...', totalPages]
  if (current >= totalPages - 3) return [1, '...', totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages]
  return [1, '...', current - 1, current, current + 1, '...', totalPages]
})

const hasError = computed(() => Boolean(trajectoryQuery.error.value))
const errorMessage = computed(() =>
  formatApiErrorMessage(trajectoryQuery.error.value, '当前轨迹分析数据暂不可用，请稍后重试'),
)

function retry() {
  trajectoryQuery.refetch()
}

function displayDimensionScore(item: { average_score?: number; score?: number }) {
  const value = typeof item.average_score === 'number' ? item.average_score : item.score
  if (typeof value !== 'number') return '待补充'
  return value <= 1 ? `${Math.round(value * 100)}分` : `${Math.round(value)}分`
}

function dimensionNumericScore(item: { average_score?: number; score?: number }) {
  const value = typeof item.average_score === 'number' ? item.average_score : item.score
  if (typeof value !== 'number') return 0
  return value <= 1 ? value * 100 : value
}

function dominantRiskChange(summary?: Partial<Record<'rising' | 'steady' | 'falling', number>>) {
  if (!summary) return '--'
  const entries = Object.entries(summary)
  if (entries.length === 0) return '--'
  const top = entries.sort((a, b) => (b[1] ?? 0) - (a[1] ?? 0))[0]
  if (!top) return '--'
  return `${riskChangeText(top[0] as 'rising' | 'steady' | 'falling')} ${top[1] ?? 0}`
}

function groupTrendScore(summary?: Partial<Record<'rising' | 'steady' | 'falling', number>>) {
  if (!summary) return 0
  return (summary.rising ?? 0) * 3 + (summary.steady ?? 0) - (summary.falling ?? 0)
}

function formatChangeSummary(summary?: Partial<Record<'rising' | 'steady' | 'falling', number>>) {
  if (!summary) return '--'
  const up = summary.rising ?? 0
  const steady = summary.steady ?? 0
  const down = summary.falling ?? 0
  return `▲${up} ▬${steady} ▼${down}`
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
  return parts.join(' / ') || '暂无'
}
</script>

<style scoped>
.page-title-row {
  display: flex;
  align-items: center;
  gap: 14px;
}

.title-icon {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(109, 79, 210, 0.1);
  color: #5d3fc0;
  border: 1px solid rgba(109, 79, 210, 0.14);
}

.title-icon svg {
  width: 22px;
  height: 22px;
}

.section-gap {
  margin-top: 12px;
}

.trajectory-stack {
  display: grid;
  gap: 12px;
  margin-top: 12px;
}

.trend-panel {
  min-height: 392px;
}

.trend-section {
  display: grid;
}

.ranking-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.mini-panel h3 {
  margin: 0;
  font-size: 1rem;
}

.compact-stack {
  gap: 6px;
}

.ranking-list {
  display: grid;
  gap: 8px;
}

.ranking-row {
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr) auto;
  gap: 10px;
  align-items: center;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(28, 34, 56, 0.08);
  background: rgba(255, 255, 255, 0.82);
}

.ranking-index {
  width: 28px;
  height: 28px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(109, 79, 210, 0.12);
  color: #5d3fc0;
  font-size: 0.84rem;
  font-weight: 700;
}

.ranking-copy {
  display: grid;
  gap: 2px;
  min-width: 0;
}

.ranking-copy strong,
.ranking-value {
  color: #1f2937;
}

.ranking-value {
  white-space: nowrap;
  text-align: right;
}

.group-ranking-row .ranking-value {
  color: #4b5563;
  font-size: 0.86rem;
}

.empty-copy {
  padding: 8px 0;
}

.mini-row {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  padding: 6px 0;
  border-top: 1px solid rgba(28, 34, 56, 0.08);
  font-size: 0.88rem;
}

.kpi-line {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  font-size: 0.92rem;
  align-items: center;
}

.kpi-line strong {
  text-align: right;
}

.sample-panel {
  margin-top: 0;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.section-title-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.sample-table {
  display: grid;
  gap: 8px;
}

.sample-row {
  display: grid;
  grid-template-columns: 1.1fr 1.2fr 0.9fr 1.2fr;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid rgba(28, 34, 56, 0.08);
  background: rgba(255, 255, 255, 0.84);
}

.sample-row.header {
  border: 0;
  background: transparent;
  color: var(--muted);
  padding-bottom: 0;
}

.pagination-bar {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
}

.page-numbers {
  display: flex;
  align-items: center;
  gap: 6px;
}

.page-num {
  min-width: 34px;
  height: 34px;
  border-radius: 999px;
  border: 1px solid rgba(103, 80, 164, 0.28);
  background: #fff;
  color: #4b3f68;
  font-weight: 600;
}

.page-num.active {
  background: #6750a4;
  border-color: #6750a4;
  color: #fff;
}

.page-num.ellipsis {
  border-color: transparent;
  background: transparent;
  color: #8c86a1;
}

@media (max-width: 1200px) {
  .ranking-strip {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 960px) {
  .ranking-strip,
  .sample-row {
    grid-template-columns: 1fr;
  }
}

.overview-stage-enter-active,
.overview-stage-leave-active {
  transition: opacity 220ms cubic-bezier(0.2, 0, 0, 1);
}

.overview-stage-enter-from {
  opacity: 0;
}

.overview-stage-leave-to {
  opacity: 0;
}
</style>
