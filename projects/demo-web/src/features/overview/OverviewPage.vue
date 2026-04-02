<template>
  <AppShell>
    <section class="panel tab-panel">
      <div class="panel-inner">
        <p class="term-note">学期</p>
        <div class="term-tabs">
          <button
            v-for="item in AVAILABLE_TERMS"
            :key="item"
            type="button"
            class="term-tab"
            :class="{ active: item === term }"
            @click="setTerm(item)"
          >
            {{ item }}
          </button>
        </div>
      </div>
    </section>

    <LoadingState v-if="overviewQuery.isLoading.value || summaryQuery.isLoading.value" label="正在加载总览..." />
    <ErrorState v-else-if="errorMessage" title="总览加载失败" :description="errorMessage" @retry="retry" />
    <EmptyState
      v-else-if="!overview || !summary"
      title="当前学期暂无可展示数据"
      description="请切换学期后重试"
    />
    <template v-else>
      <section class="grid-3">
        <article class="card-kpi panel">
          <div class="muted">高风险</div>
          <div class="kpi-value risk-high">{{ riskCount('high') }}</div>
        </article>
        <article class="card-kpi panel">
          <div class="muted">中风险</div>
          <div class="kpi-value risk-medium">{{ riskCount('medium') }}</div>
        </article>
        <article class="card-kpi panel">
          <div class="muted">低风险</div>
          <div class="kpi-value risk-low">{{ riskCount('low') }}</div>
        </article>
      </section>

      <section class="panel segment-panel">
        <div class="panel-inner">
          <div class="segment-head">
            <h3>风险占比</h3>
            <span class="muted">总人数：{{ totalRiskPopulation }}</span>
          </div>
          <div class="segment-track">
            <div class="segment high" :style="{ width: `${riskPercent.high}%` }"></div>
            <div class="segment medium" :style="{ width: `${riskPercent.medium}%` }"></div>
            <div class="segment low" :style="{ width: `${riskPercent.low}%` }"></div>
          </div>
          <div class="segment-legend">
            <span class="legend-item"><i class="dot high"></i>高风险 {{ riskPercent.high.toFixed(1) }}%</span>
            <span class="legend-item"><i class="dot medium"></i>中风险 {{ riskPercent.medium.toFixed(1) }}%</span>
            <span class="legend-item"><i class="dot low"></i>低风险 {{ riskPercent.low.toFixed(1) }}%</span>
          </div>
        </div>
      </section>

      <section class="overview-risk-grid">
        <article class="panel">
          <div class="panel-inner stack">
            <div class="section-head">
              <h3>学业风险四档分布</h3>
              <span class="muted">按学业风险等级统计</span>
            </div>
            <div class="risk-band-grid">
              <div v-for="item in riskBandRows" :key="item.label" class="risk-band-row">
                <span class="muted">{{ item.label }}</span>
                <strong>{{ item.count }}</strong>
              </div>
            </div>
          </div>
        </article>
        <article class="panel">
          <div class="panel-inner stack">
            <div class="section-head">
              <h3>风险趋势摘要</h3>
              <span class="muted">近学期均值变化</span>
            </div>
            <div class="risk-trend-list">
              <div v-for="row in riskTrendRows" :key="row.term" class="risk-trend-row">
                <strong>{{ row.term }}</strong>
                <span class="muted">均值 {{ row.avg_risk_score.toFixed(1) }}</span>
                <span class="muted">高风险 {{ row.high_risk_count }}</span>
                <span class="tag">{{ riskChangeText(row.risk_change_direction) }}</span>
              </div>
            </div>
          </div>
        </article>
        <article class="panel">
          <div class="panel-inner stack">
            <div class="section-head">
              <h3>风险因素 Top</h3>
              <span class="muted">当前学期触发因子</span>
            </div>
            <div class="risk-factor-list">
              <div v-for="factor in riskFactorRows" :key="factor.feature" class="risk-factor-row">
                <strong>{{ factor.feature_cn || factor.feature }}</strong>
                <span class="muted">涉及 {{ factor.count }} 人</span>
                <span class="muted">重要度 {{ factor.importance.toFixed(2) }}</span>
              </div>
            </div>
          </div>
        </article>
      </section>

      <section class="overview-top-grid">
        <article class="panel">
          <div class="panel-inner chart-panel">
            <div class="section-head">
              <h3>八维总体画像</h3>
              <span class="muted">当前学期全体学生平均得分</span>
            </div>
            <EChart :option="dimensionBarOption" height="280px" />
          </div>
        </article>
        <article class="panel">
          <div class="panel-inner stack">
            <div class="section-head">
              <h3>模型摘要说明</h3>
              <span class="muted">当前总览口径</span>
            </div>
            <div class="summary-list">
              <div class="summary-row">
                <span class="muted">聚类口径</span>
                <strong>{{ summary.cluster_method }}</strong>
              </div>
              <div class="summary-row">
                <span class="muted">风险模型</span>
                <strong>{{ summary.risk_model }}</strong>
              </div>
              <div class="summary-row">
                <span class="muted">目标标签</span>
                <strong>{{ summary.target_label }}</strong>
              </div>
              <div class="summary-row">
                <span class="muted">AUC</span>
                <strong>{{ summary.auc.toFixed(4) }}</strong>
              </div>
              <div class="summary-row">
                <span class="muted">更新时间</span>
                <strong>{{ summary.updated_at }}</strong>
              </div>
            </div>
          </div>
        </article>
      </section>

      <section class="panel dimension-detail-panel">
        <div class="panel-inner stack">
          <div class="section-head">
            <h3>八维结果明细</h3>
            <span class="muted">标签、指标与解释一并展示</span>
          </div>
          <div class="dimension-detail-grid">
            <article v-for="item in dimensionRows" :key="item.dimension" class="dimension-detail-card">
              <div class="dimension-detail-head">
                <div class="dimension-detail-copy">
                  <strong>{{ item.dimension }}</strong>
                  <p class="muted">{{ item.explanation ?? '当前维度尚未提供完整校准结果' }}</p>
                </div>
                <div class="dimension-detail-score">
                  <span class="tag" :class="dimensionTagClass(item.level)">
                    {{ dimensionLevelText(item.level) }}
                  </span>
                  <strong>{{ Math.round(item.score * 100) }}分</strong>
                </div>
              </div>
              <div class="dimension-label">{{ item.label ?? '待补充' }}</div>
              <div v-if="item.metrics?.length" class="dimension-metrics">
                <span v-for="metric in item.metrics?.slice(0, 3) ?? []" :key="metric.metric" class="tag">
                  {{ metric.metric }} {{ formatMetric(metric) }}
                </span>
              </div>
              <div v-else class="muted">暂无指标</div>
            </article>
          </div>
        </div>
      </section>

      <section class="overview-grid">
        <article class="panel major-panel">
          <div class="panel-inner major-content">
            <h3>专业高风险摘要</h3>
            <div class="major-body">
              <EChart :option="majorPieOption" height="260px" @chart-click="handleMajorPieClick" />
              <div ref="majorListEl" class="major-list">
                <RouterLink
                  v-for="row in majorRows"
                  :key="row.major_name"
                  class="major-row"
                  :data-major="row.major_name"
                  :class="{ active: row.major_name === activeMajor }"
                  :to="buildMajorWarningLink(row.major_name)"
                  @click="handleMajorRowClick(row.major_name)"
                >
                  <span>{{ row.major_name }}</span>
                  <strong>{{ row.high_risk_count }} 人</strong>
                </RouterLink>
              </div>
            </div>
          </div>
        </article>

        <div class="right-stack">
          <article class="panel">
            <div class="panel-inner chart-panel">
              <h3>学期趋势</h3>
              <EChart :option="trendLineOption" height="250px" />
            </div>
          </article>
          <article class="panel">
            <div class="panel-inner chart-panel">
              <h3>重点群体分布</h3>
              <EChart :option="groupBarOption" height="250px" />
            </div>
          </article>
        </div>
      </section>
    </template>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import type { EChartsOption } from 'echarts'
import { RouterLink } from 'vue-router'

import { AVAILABLE_TERMS, useTermStore } from '@/app/term'
import AppShell from '@/components/layout/AppShell.vue'
import EChart from '@/components/charts/EChart.vue'
import EmptyState from '@/components/state/EmptyState.vue'
import ErrorState from '@/components/state/ErrorState.vue'
import LoadingState from '@/components/state/LoadingState.vue'
import { getModelSummary, getOverview } from '@/lib/api'
import { formatApiErrorMessage } from '@/lib/format'
import type { RiskLevel } from '@/lib/types'

const termStore = useTermStore()
const activeMajor = ref('')
const majorListEl = ref<HTMLElement | null>(null)

const overviewQuery = useQuery({
  queryKey: computed(() => ['overview', termStore.term.value]),
  queryFn: () => getOverview(termStore.term.value),
})

const summaryQuery = useQuery({
  queryKey: computed(() => ['model-summary', termStore.term.value]),
  queryFn: () => getModelSummary(termStore.term.value),
})

const overview = computed(() => overviewQuery.data.value)
const summary = computed(() => summaryQuery.data.value)
const term = computed(() => termStore.term.value)
const majorRows = computed(() => overview.value?.major_risk_summary ?? [])
const dimensionRows = computed(() => overview.value?.dimension_summary ?? [])
const riskBandRows = computed(() => {
  const distribution = overview.value?.risk_band_distribution ?? {}
  return [
    { label: '高风险', count: distribution['高风险'] ?? 0 },
    { label: '较高风险', count: distribution['较高风险'] ?? 0 },
    { label: '一般风险', count: distribution['一般风险'] ?? 0 },
    { label: '低风险', count: distribution['低风险'] ?? 0 },
  ]
})
const riskTrendRows = computed(() => overview.value?.risk_trend_summary ?? [])
const riskFactorRows = computed(() => (overview.value?.risk_factor_summary ?? []).slice(0, 5))
const totalHighRisk = computed(() => majorRows.value.reduce((sum, item) => sum + item.high_risk_count, 0))
const totalRiskPopulation = computed(() => {
  const data = overview.value?.risk_distribution ?? []
  return data.reduce((sum, item) => sum + item.count, 0)
})
const riskPercent = computed(() => {
  const total = totalRiskPopulation.value || 1
  return {
    high: (riskCount('high') / total) * 100,
    medium: (riskCount('medium') / total) * 100,
    low: (riskCount('low') / total) * 100,
  }
})

const errorMessage = computed(() => {
  const firstError = overviewQuery.error.value ?? summaryQuery.error.value
  return firstError ? formatApiErrorMessage(firstError, '当前总览数据暂不可用，请稍后重试') : ''
})

const majorPieOption = computed<EChartsOption>(() => {
  const rows = majorRows.value
  return {
    color: ['#ff4b00', '#f97316', '#3b82f6', '#22b573', '#ef4444', '#f59e0b', '#8b5cf6'],
    tooltip: {
      trigger: 'item',
      formatter: (params: any) =>
        `${params?.name ?? ''}<br/>高风险人数：${params?.value ?? 0} 人<br/>占比：${params?.percent ?? 0}%`,
    },
    title: {
      text: `${totalHighRisk.value}`,
      subtext: '高风险总人数',
      left: 'center',
      top: 'center',
      textStyle: {
        color: '#ff4b00',
        fontSize: 28,
        fontWeight: 700,
      },
      subtextStyle: {
        color: '#7f8896',
        fontSize: 13,
      },
      itemGap: 6,
    },
    series: [
      {
        name: '专业高风险',
        type: 'pie',
        selectedMode: 'single',
        selectedOffset: 14,
        radius: ['35%', '68%'],
        center: ['50%', '50%'],
        itemStyle: { borderColor: '#fff', borderWidth: 2 },
        label: { show: false },
        emphasis: {
          scale: true,
          scaleSize: 10,
          itemStyle: {
            shadowBlur: 24,
            shadowColor: 'rgba(255, 75, 0, 0.35)',
          },
        },
        data: rows.map((item) => ({
          name: item.major_name,
          value: item.high_risk_count,
          selected: activeMajor.value ? item.major_name === activeMajor.value : false,
          itemStyle: {
            opacity: !activeMajor.value || item.major_name === activeMajor.value ? 1 : 0.4,
          },
        })),
      },
    ],
  }
})

const trendLineOption = computed<EChartsOption>(() => {
  const rows = overview.value?.trend_summary ?? []
  return {
    color: ['#ff4b00'],
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: rows.map((item) => item.term),
      axisLine: { lineStyle: { color: '#d9dee6' } },
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#eef1f5' } },
    },
    series: [
      {
        type: 'line',
        smooth: true,
        symbolSize: 8,
        lineStyle: { width: 3 },
        areaStyle: { color: 'rgba(255, 75, 0, 0.14)' },
        data: rows.map((item) => item.high_risk_count),
      },
    ],
  }
})

const groupBarOption = computed<EChartsOption>(() => {
  const rows = overview.value?.group_distribution ?? []
  return {
    color: ['#3b82f6', '#ff4b00', '#22b573', '#f59e0b'],
    grid: { left: 92, right: 20, top: 16, bottom: 18, containLabel: true },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: '#eef1f5' } },
      axisLine: { lineStyle: { color: '#d9dee6' } },
    },
    yAxis: {
      type: 'category',
      data: rows.map((item) => item.group_segment),
      axisLine: { lineStyle: { color: '#d9dee6' } },
      axisTick: { show: false },
      axisLabel: { interval: 0, margin: 10 },
    },
    series: [
      {
        type: 'bar',
        barWidth: 24,
        barCategoryGap: '10%',
        data: rows.map((item) => item.count),
      },
    ],
  }
})

const dimensionBarOption = computed<EChartsOption>(() => {
  const rows = dimensionRows.value
  return {
    color: ['#ff4b00'],
    grid: { left: 56, right: 18, top: 12, bottom: 60 },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: {
      type: 'category',
      data: rows.map((item) => item.dimension),
      axisLabel: { interval: 0, rotate: 24 },
      axisLine: { lineStyle: { color: '#d9dee6' } },
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 1,
      splitLine: { lineStyle: { color: '#eef1f5' } },
    },
    series: [
      {
        type: 'bar',
        barWidth: 26,
        data: rows.map((item) => item.score),
      },
    ],
  }
})

function dimensionLevelText(level?: RiskLevel) {
  if (!level) return '待补充'
  if (level === 'high') return '高'
  if (level === 'medium') return '中'
  return '低'
}

function dimensionTagClass(level?: RiskLevel) {
  if (!level) return 'pending'
  if (level === 'high') return 'hot'
  if (level === 'medium') return 'warn'
  return 'cool'
}

function formatMetric(metric: { display?: string; value: number | string }) {
  return metric.display || String(metric.value)
}

function riskChangeText(direction?: string) {
  if (direction === 'rising') return '上升'
  if (direction === 'falling') return '下降'
  return '持平'
}

function riskCount(level: RiskLevel) {
  return overview.value?.risk_distribution.find((item) => item.risk_level === level)?.count ?? 0
}

function setTerm(nextTerm: string) {
  termStore.setTerm(nextTerm)
  activeMajor.value = ''
}

function handleMajorPieClick(params: unknown) {
  const name = (params as { name?: string } | undefined)?.name
  if (!name) return
  scrollMajorRow(name)
}

function handleMajorRowClick(name: string) {
  scrollMajorRow(name)
}

function buildMajorWarningLink(majorName: string) {
  return {
    path: '/warnings',
    query: {
      term: termStore.term.value,
      risk_level: 'high',
      major_name: majorName,
    },
  }
}

function scrollMajorRow(name: string) {
  activeMajor.value = name
  const listEl = majorListEl.value
  if (!listEl) return
  const target = listEl.querySelector<HTMLElement>(`[data-major="${CSS.escape(name)}"]`)
  if (!target) return
  target.scrollIntoView({ behavior: 'smooth', block: 'center' })
}

function retry() {
  overviewQuery.refetch()
  summaryQuery.refetch()
}
</script>

<style scoped>
.tab-panel {
  margin-bottom: 14px;
}

.term-note {
  margin: 0 0 10px;
  color: #7f8896;
  font-size: 0.9rem;
}

.term-tabs {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.term-tab {
  border: 1px solid #e3e8ef;
  background: #fff;
  color: #4e5868;
  border-radius: 999px;
  padding: 8px 14px;
}

.term-tab.active {
  background: #ff4b00;
  border-color: #ff4b00;
  color: #fff;
}

.risk-high {
  color: var(--danger);
}

.risk-medium {
  color: var(--warning);
}

.risk-low {
  color: var(--success);
}

.tag.pending {
  color: #667085;
  border-color: #d0d5dd;
  background: #f2f4f7;
}

.segment-panel {
  margin-top: 12px;
}

.overview-risk-grid {
  margin-top: 14px;
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.risk-band-grid,
.risk-trend-list,
.risk-factor-list {
  display: grid;
  gap: 10px;
}

.risk-band-row,
.risk-trend-row,
.risk-factor-row {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  align-items: center;
  padding: 8px 0;
  border-top: 1px solid rgba(28, 34, 56, 0.08);
}

.risk-band-row:first-child,
.risk-trend-row:first-child,
.risk-factor-row:first-child {
  border-top: 0;
  padding-top: 0;
}

.overview-top-grid {
  margin-top: 14px;
  display: grid;
  gap: 16px;
  grid-template-columns: minmax(0, 1.4fr) minmax(320px, 0.8fr);
}

.dimension-detail-panel {
  margin-top: 16px;
}

.dimension-detail-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.dimension-detail-card {
  border: 1px solid rgba(28, 34, 56, 0.08);
  border-radius: 14px;
  background: #fafbfd;
  padding: 14px 16px;
  display: grid;
  gap: 10px;
}

.dimension-detail-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.dimension-detail-copy {
  display: grid;
  gap: 6px;
}

.dimension-detail-copy p {
  margin: 0;
}

.dimension-detail-score {
  display: grid;
  gap: 6px;
  justify-items: end;
  white-space: nowrap;
}

.dimension-label {
  font-weight: 700;
}

.dimension-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.section-head h3 {
  margin: 0;
}

.summary-list {
  display: grid;
  gap: 10px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: start;
  padding: 10px 0;
  border-top: 1px solid rgba(28, 34, 56, 0.08);
}

.summary-row:first-child {
  border-top: 0;
  padding-top: 0;
}

.segment-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.segment-head h3 {
  margin: 0;
}

.segment-track {
  height: 16px;
  border-radius: 999px;
  overflow: hidden;
  border: 1px solid #eceff4;
  background: #f7f9fc;
  display: flex;
}

.segment {
  height: 100%;
  min-width: 0;
}

.segment.high {
  background: #ef4444;
}

.segment.medium {
  background: #f59e0b;
}

.segment.low {
  background: #22b573;
}

.segment-legend {
  margin-top: 10px;
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
}

.legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #5f6977;
  font-size: 0.9rem;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.dot.high {
  background: #ef4444;
}

.dot.medium {
  background: #f59e0b;
}

.dot.low {
  background: #22b573;
}

.overview-grid {
  margin-top: 14px;
  display: grid;
  gap: 16px;
  grid-template-columns: minmax(400px, 1.1fr) minmax(0, 1fr);
}

.major-panel {
  min-height: 560px;
  max-height: 560px;
}

.major-content {
  display: grid;
  gap: 14px;
  height: 100%;
}

.major-content h3,
.chart-panel h3 {
  margin: 0;
}

.major-body {
  display: grid;
  grid-template-columns: 48% 52%;
  gap: 14px;
  align-items: stretch;
  min-height: 0;
  height: 100%;
}

.major-list {
  border: 1px solid #eceff4;
  border-radius: 12px;
  max-height: 470px;
  overflow: auto;
  padding: 8px;
}

.major-row {
  width: 100%;
  border: 1px solid transparent;
  background: #fff;
  border-radius: 10px;
  padding: 10px 12px;
  text-align: left;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.major-row:hover {
  background: #fff5f1;
}

.major-row.active {
  border-color: #ffb294;
  background: #fff1eb;
}

.right-stack {
  display: grid;
  gap: 16px;
}

.chart-panel {
  display: grid;
  gap: 8px;
}

@media (max-width: 1200px) {
  .dimension-detail-grid,
  .overview-risk-grid,
  .overview-top-grid,
  .overview-grid {
    grid-template-columns: 1fr;
  }

  .major-panel {
    min-height: 520px;
    max-height: none;
  }
}

@media (max-width: 880px) {
  .major-body {
    grid-template-columns: 1fr;
  }

  .major-list {
    max-height: 240px;
  }
}
</style>
