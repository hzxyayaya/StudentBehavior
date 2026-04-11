<template>
  <Transition name="overview-stage" mode="out-in">
    <LoadingState
      v-if="overviewQuery.isLoading.value || summaryQuery.isLoading.value"
      key="loading"
      label="正在加载总览..."
    />
    <ErrorState v-else-if="errorMessage" key="error" title="总览加载失败" :description="errorMessage" @retry="retry" />
    <EmptyState
      v-else-if="!overview || !summary"
      key="empty"
      title="当前学期暂无可展示数据"
      description="请切换学期后重试"
    />

    <div v-else key="content" class="overview-content">
      <section class="risk-overview-layer stage stage-1">
        <article class="panel">
          <div class="panel-inner stack">
            <div class="section-head">
              <div class="section-title-with-icon">
                <span class="section-icon danger" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none">
                    <path
                      d="M12 4.75 19 17.25H5L12 4.75Z"
                      stroke="currentColor"
                      stroke-width="1.8"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                    <path
                      d="M12 9v4.5M12 15.75h.01"
                      stroke="currentColor"
                      stroke-width="1.8"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </span>
                <h3>干预优先级分级概览</h3>
              </div>
              <span class="muted">共 {{ totalRiskPopulation }} 人</span>
            </div>

            <div class="risk-kpi-grid">
              <div
                v-for="item in riskBandCards"
                :key="item.key"
                class="card-kpi risk-kpi-card"
                :class="riskCardClass(item.key)"
              >
                <RiskCardParticles :variant="item.key as 'low' | 'medium' | 'higher' | 'high'" />
                <div class="risk-card-main">
                  <div class="risk-card-copy">
                    <div class="muted">{{ item.label }}</div>
                    <div class="kpi-value">{{ item.count }}</div>
                  </div>

                  <div class="risk-card-icon" aria-hidden="true">
                    <svg v-if="item.key === 'low'" viewBox="0 0 24 24" fill="none">
                      <path
                        d="M12 4.75 18 7v4.8c0 3.42-2.22 6.42-6 7.45-3.78-1.03-6-4.03-6-7.45V7l6-2.25Z"
                        stroke="currentColor"
                        stroke-width="1.8"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                      <path
                        d="m9.2 11.95 1.85 1.85 3.75-4.1"
                        stroke="currentColor"
                        stroke-width="1.8"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                    </svg>
                    <svg v-else-if="item.key === 'medium'" viewBox="0 0 24 24" fill="none">
                      <path
                        d="M12 4.75 19 17.25H5L12 4.75Z"
                        stroke="currentColor"
                        stroke-width="1.8"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                      <path
                        d="M12 9v4.5M12 15.75h.01"
                        stroke="currentColor"
                        stroke-width="1.8"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                    </svg>
                    <svg v-else-if="item.key === 'higher'" viewBox="0 0 24 24" fill="none">
                      <path
                        d="M12 4.75 19 17.25H5L12 4.75Z"
                        stroke="currentColor"
                        stroke-width="1.8"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                      <path
                        d="M12 9v4.5M12 15.75h.01"
                        stroke="currentColor"
                        stroke-width="1.8"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="none">
                      <path
                        d="M12 5.25a4 4 0 0 0-4 4v1.9c0 .55-.17 1.08-.48 1.53l-1.22 1.82a.9.9 0 0 0 .74 1.4h9.92a.9.9 0 0 0 .74-1.4l-1.22-1.82a2.7 2.7 0 0 1-.48-1.53v-1.9a4 4 0 0 0-4-4Z"
                        stroke="currentColor"
                        stroke-width="1.8"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                      <path d="M10 18.25a2 2 0 0 0 4 0" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </article>
      </section>

      <section class="middle-layout stage stage-2">
        <article class="panel portrait-panel">
          <div class="panel-inner chart-panel">
            <div class="section-head">
              <div class="section-title-with-icon">
                <span class="section-icon brand" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none">
                    <path
                      d="M12 5.75 17.75 9v6L12 18.25 6.25 15V9L12 5.75Z"
                      stroke="currentColor"
                      stroke-width="1.8"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                    <path
                      d="M12 5.75V12m0 0 5.75-3M12 12l-5.75-3"
                      stroke="currentColor"
                      stroke-width="1.8"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                </span>
                <h3>八维整体画像</h3>
              </div>
              <div class="portrait-head-actions">
                <span class="muted">当前学期全体学生平均得分</span>
                <div class="portrait-tabs" role="tablist" aria-label="八维画像视图切换">
                  <button
                    v-for="tab in portraitTabs"
                    :key="tab.key"
                    class="portrait-tab"
                    :class="{ active: activePortraitTab === tab.key }"
                    type="button"
                    role="tab"
                    :aria-selected="activePortraitTab === tab.key"
                    @click="activePortraitTab = tab.key"
                  >
                    {{ tab.label }}
                  </button>
                </div>
              </div>
            </div>

            <div class="portrait-stage">
              <div v-if="activePortraitTab === 'bar'" class="portrait-chart-wrap">
                <LazyEChart :option="dimensionBarOption" height="100%" />
              </div>
              <div v-else-if="activePortraitTab === 'radar'" class="portrait-chart-wrap">
                <LazyEChart :option="dimensionRadarOption" height="100%" />
              </div>
              <div v-else class="dimension-summary-grid">
                <article v-for="item in dimensionRows" :key="`summary-${item.dimension}`" class="dimension-summary-card">
                  <div class="dimension-summary-head">
                    <strong>{{ item.dimension }}</strong>
                    <span class="tag" :class="dimensionTagClass(item.level)">
                      {{ dimensionLevelText(item.level) }}
                    </span>
                  </div>
                  <div class="dimension-summary-score">{{ Math.round(item.score * 100) }}分</div>
                  <div class="dimension-summary-label">{{ item.label ?? '待补充说明' }}</div>
                </article>
              </div>
            </div>
          </div>
        </article>

        <div class="right-column">
          <article class="panel right-card right-group-card">
            <div class="panel-inner right-group-inner">
              <div class="right-group-top">
                <section class="right-subcard">
                  <div class="subcard-title">
                    <span class="section-icon amber" aria-hidden="true">
                      <svg viewBox="0 0 24 24" fill="none">
                        <path
                          d="M5 17.25h14M6.5 14.75 10 11.25l3 2.5 4.5-6"
                          stroke="currentColor"
                          stroke-width="1.8"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        />
                      </svg>
                    </span>
                    <h3>趋势</h3>
                  </div>
                  <div v-for="row in riskTrendRows" :key="row.term" class="simple-row">
                    <span>{{ row.term }}</span>
                    <strong>
                      {{ row.avg_risk_score.toFixed(1) }} 分 · {{ row.high_risk_count }} 人
                      <span class="trend-indicator" :class="trendClass(row.risk_change_direction)">
                        {{ trendSymbol(row.risk_change_direction) }}
                      </span>
                    </strong>
                  </div>
                </section>
              </div>

              <section class="right-subcard right-subcard-bottom">
                <div class="subcard-title">
                  <span class="section-icon brand" aria-hidden="true">
                    <svg viewBox="0 0 24 24" fill="none">
                      <path
                        d="M6.5 16.5 10 13l2.5 2.5 5-6"
                        stroke="currentColor"
                        stroke-width="1.8"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                      <path d="M5 18.25h14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
                    </svg>
                  </span>
                  <h3>当前学期 Top 影响因素</h3>
                </div>
                <div v-for="factor in riskFactorRows" :key="factor.feature" class="simple-row">
                  <span>{{ factor.feature_cn || factor.feature }}</span>
                  <strong>{{ factor.count }} 人 · 权重 {{ factor.importance.toFixed(2) }}</strong>
                </div>
              </section>
            </div>
          </article>
        </div>
      </section>

      <section class="panel dimension-detail-panel stage stage-3">
        <div class="panel-inner">
          <details class="dimension-details">
            <summary>八维结果明细</summary>
            <div class="dimension-detail-grid">
              <article v-for="item in dimensionRows" :key="item.dimension" class="dimension-detail-card">
                <div class="dimension-detail-head">
                  <div class="dimension-detail-copy">
                    <strong>{{ item.dimension }}</strong>
                    <p class="muted">{{ item.explanation ?? '当前维度暂无完整说明' }}</p>
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
          </details>
        </div>
      </section>

      <section class="panel dimension-detail-panel stage stage-4">
        <div class="panel-inner">
          <details class="dimension-details">
            <summary>模型信息</summary>
            <div class="summary-list">
              <div v-for="row in summaryRows" :key="row.key" class="summary-row">
                <span class="muted">{{ row.label }}</span>
                <strong>{{ row.value }}</strong>
              </div>
            </div>
          </details>
        </div>
      </section>
    </div>
  </Transition>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import type { EChartsOption } from 'echarts'

import { useTermStore } from '@/app/term'
import LazyEChart from '@/components/charts/LazyEChart.vue'
import RiskCardParticles from '@/components/layout/RiskCardParticles.vue'
import EmptyState from '@/components/state/EmptyState.vue'
import ErrorState from '@/components/state/ErrorState.vue'
import LoadingState from '@/components/state/LoadingState.vue'
import { getModelSummary, getOverview } from '@/lib/api'
import { formatApiErrorMessage } from '@/lib/format'
import type { ModelSummaryData, RiskLevel } from '@/lib/types'

const OVERVIEW_DIMENSIONS = [
  { dimension: '学业基础表现', dimension_code: 'academic_base' },
  { dimension: '课堂学习投入', dimension_code: 'class_engagement' },
  { dimension: '在线学习积极性', dimension_code: 'online_activeness' },
  { dimension: '图书馆沉浸度', dimension_code: 'library_immersion' },
  { dimension: '网络作息自律指数', dimension_code: 'network_habits' },
  { dimension: '早晚生活作息规律', dimension_code: 'daily_routine_boundary' },
  { dimension: '体质及运动状况', dimension_code: 'physical_resilience' },
  { dimension: '综合荣誉与异动预警', dimension_code: 'appraisal_status_alert' },
] as const

const termStore = useTermStore()

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
const dimensionRows = computed(() => {
  const rows = overview.value?.dimension_summary ?? []
  const rowMap = new Map(
    rows.map((item) => [item.dimension_code ?? item.dimension, item] as const),
  )
  return OVERVIEW_DIMENSIONS.map((base) => {
    const matched = rowMap.get(base.dimension_code) ?? rowMap.get(base.dimension)
    if (matched) return matched
    return {
      dimension: base.dimension,
      dimension_code: base.dimension_code,
      score: 0,
      level: 'low' as const,
      label: '当前学期无有效数据',
      explanation: `${base.dimension}当前学期无有效源表指标，暂不做该维度判定。`,
      metrics: [],
    }
  })
})
const activePortraitTab = ref<'bar' | 'radar' | 'detail'>('bar')
const portraitTabs = [
  { key: 'bar', label: '柱状图' },
  { key: 'radar', label: '雷达图' },
  { key: 'detail', label: '详细数据' },
] as const

const riskBandRows = computed(() => {
  const distribution = overview.value?.risk_band_distribution ?? {}
  const rawValues = Object.values(distribution).filter((value): value is number => typeof value === 'number')
  const fallbackHigh = overview.value?.risk_distribution.find((item) => item.risk_level === 'high')?.count ?? 0
  const fallbackMedium = overview.value?.risk_distribution.find((item) => item.risk_level === 'medium')?.count ?? 0
  const fallbackLow = overview.value?.risk_distribution.find((item) => item.risk_level === 'low')?.count ?? 0
  const high = rawValues[0] ?? fallbackHigh
  const higher = rawValues[1] ?? 0
  const medium = rawValues[2] ?? fallbackMedium
  const low = rawValues[3] ?? fallbackLow
  return [
    { key: 'high', label: '高优先', count: high },
    { key: 'higher', label: '较高优先', count: higher },
    { key: 'medium', label: '一般优先', count: medium },
    { key: 'low', label: '低优先', count: low },
  ]
})

const riskBandCards = computed(() => {
  const rows = riskBandRows.value
  return [
    { key: 'low', label: '低优先', count: rows.find((item) => item.key === 'low')?.count ?? 0 },
    { key: 'medium', label: '一般优先', count: rows.find((item) => item.key === 'medium')?.count ?? 0 },
    { key: 'higher', label: '较高优先', count: rows.find((item) => item.key === 'higher')?.count ?? 0 },
    { key: 'high', label: '高优先', count: rows.find((item) => item.key === 'high')?.count ?? 0 },
  ]
})

const riskTrendRows = computed(() => (overview.value?.risk_trend_summary ?? []).slice(0, 3))
const riskFactorRows = computed(() => (overview.value?.risk_factor_summary ?? []).slice(0, 3))
const totalRiskPopulation = computed(() => riskBandRows.value.reduce((sum, item) => sum + item.count, 0))
const summaryRows = computed(() => {
  const currentSummary = summary.value
  if (!currentSummary) return []

  const summaryRecord = asSummaryRecord(currentSummary)
  const rows = [
    { key: 'risk_model', label: '风险模型', value: currentSummary.risk_model },
    { key: 'cluster_method', label: '聚类口径', value: currentSummary.cluster_method },
    { key: 'target_label', label: '目标标签', value: currentSummary.target_label },
    { key: 'auc', label: 'AUC', value: currentSummary.auc.toFixed(4) },
  ]

  appendSummaryRow(rows, 'source', '模型来源', formatSummaryText(summaryRecord.source))
  appendSummaryRow(rows, 'accuracy', 'Accuracy', formatSummaryMetric(summaryRecord.accuracy))
  appendSummaryRow(rows, 'precision', 'Precision', formatSummaryMetric(summaryRecord.precision))
  appendSummaryRow(rows, 'recall', 'Recall', formatSummaryMetric(summaryRecord.recall))
  appendSummaryRow(rows, 'f1', 'F1', formatSummaryMetric(summaryRecord.f1))
  appendSummaryRow(rows, 'sample_count', '总样本数', formatSummaryCount(summaryRecord.sample_count))
  appendSummaryRow(rows, 'positive_sample_count', '正样本数', formatSummaryCount(summaryRecord.positive_sample_count))
  appendSummaryRow(rows, 'negative_sample_count', '负样本数', formatSummaryCount(summaryRecord.negative_sample_count))
  appendSummaryRow(rows, 'train_sample_count', '训练样本数', formatSummaryCount(summaryRecord.train_sample_count))
  appendSummaryRow(rows, 'valid_sample_count', '验证样本数', formatSummaryCount(summaryRecord.valid_sample_count))
  appendSummaryRow(rows, 'test_sample_count', '测试样本数', formatSummaryCount(summaryRecord.test_sample_count))
  appendSummaryRow(rows, 'updated_at', '更新时间', currentSummary.updated_at)

  return rows
})

const errorMessage = computed(() => {
  const firstError = overviewQuery.error.value ?? summaryQuery.error.value
  return firstError ? formatApiErrorMessage(firstError, '当前总览数据暂不可用，请稍后重试') : ''
})

const dimensionBarOption = computed<EChartsOption>(() => {
  const rows = dimensionRows.value
  return {
    color: ['#6750A4'],
    grid: { left: 56, right: 18, top: 12, bottom: 70 },
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
    series: [{ type: 'bar', barWidth: 24, data: rows.map((item) => item.score) }],
  }
})

const dimensionRadarOption = computed<EChartsOption>(() => {
  const rows = dimensionRows.value
  return {
    color: ['#6750A4'],
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(31, 23, 46, 0.92)',
      borderWidth: 0,
      textStyle: { color: '#fff' },
    },
    radar: {
      radius: '68%',
      center: ['50%', '54%'],
      splitNumber: 4,
      axisName: {
        color: '#514a61',
        fontSize: 12,
      },
      splitArea: {
        areaStyle: {
          color: ['rgba(103, 80, 164, 0.02)', 'rgba(103, 80, 164, 0.04)'],
        },
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(103, 80, 164, 0.14)',
        },
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(103, 80, 164, 0.14)',
        },
      },
      indicator: rows.map((item) => ({
        name: item.dimension,
        max: 1,
      })),
    },
    series: [
      {
        type: 'radar',
        symbol: 'circle',
        symbolSize: 7,
        data: [
          {
            value: rows.map((item) => Number(item.score.toFixed(3))),
            areaStyle: {
              color: 'rgba(103, 80, 164, 0.18)',
            },
            lineStyle: {
              color: '#6750A4',
              width: 2.4,
            },
            itemStyle: {
              color: '#ffffff',
              borderColor: '#6750A4',
              borderWidth: 2,
            },
          },
        ],
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

function trendSymbol(direction?: string) {
  if (direction === 'falling') return '↓'
  if (direction === 'rising') return '↑'
  return '→'
}

function trendClass(direction?: string) {
  if (direction === 'falling') return 'trend-down'
  if (direction === 'rising') return 'trend-up'
  return 'trend-steady'
}

function riskCardClass(key: string) {
  if (key === 'low') return 'risk-card-low'
  if (key === 'medium') return 'risk-card-medium'
  if (key === 'higher') return 'risk-card-higher'
  return 'risk-card-high'
}

function asSummaryRecord(value: ModelSummaryData): Record<string, unknown> {
  return value as ModelSummaryData & Record<string, unknown>
}

function appendSummaryRow(
  rows: Array<{ key: string; label: string; value: string }>,
  key: string,
  label: string,
  value?: string,
) {
  if (!value) return
  rows.push({ key, label, value })
}

function formatSummaryText(value: unknown) {
  return typeof value === 'string' && value ? value : undefined
}

function formatSummaryMetric(value: unknown) {
  return typeof value === 'number' && Number.isFinite(value) ? value.toFixed(4) : undefined
}

function formatSummaryCount(value: unknown) {
  return typeof value === 'number' && Number.isFinite(value) ? String(value) : undefined
}

function retry() {
  overviewQuery.refetch()
  summaryQuery.refetch()
}
</script>

<style scoped>
.section-title-with-icon,
.subcard-title {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.section-icon {
  width: 34px;
  height: 34px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid transparent;
  flex: 0 0 auto;
}

.section-icon svg {
  width: 18px;
  height: 18px;
}

.section-icon.brand {
  background: rgba(109, 79, 210, 0.1);
  color: #5d3fc0;
  border-color: rgba(109, 79, 210, 0.14);
}

.section-icon.danger {
  background: rgba(226, 67, 91, 0.1);
  color: #c7324b;
  border-color: rgba(226, 67, 91, 0.14);
}

.section-icon.mint {
  background: rgba(15, 118, 110, 0.1);
  color: #0f766e;
  border-color: rgba(15, 118, 110, 0.14);
}

.section-icon.amber {
  background: rgba(217, 122, 21, 0.12);
  color: #bf690d;
  border-color: rgba(217, 122, 21, 0.14);
}

.overview-content {
  display: grid;
}

.risk-overview-layer {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
  align-items: stretch;
}

.middle-layout {
  margin-top: 16px;
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: 16px;
  align-items: stretch;
}

.right-column {
  display: grid;
  gap: 8px;
}

.right-group-inner {
  display: grid;
  gap: 14px;
}

.right-group-top {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}

.right-subcard {
  min-height: 100%;
  padding: 16px 16px 14px;
  border-radius: 16px;
  border: 1px solid rgba(28, 34, 56, 0.08);
  background: rgba(250, 251, 253, 0.82);
}

.right-subcard h3 {
  margin: 0 0 10px;
}

.right-card {
  box-shadow: none;
  transition: transform 240ms cubic-bezier(0.2, 0, 0, 1), box-shadow 240ms cubic-bezier(0.2, 0, 0, 1);
}

.right-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(29, 25, 43, 0.12);
}

.stage {
  opacity: 0;
  animation-duration: 560ms;
  animation-timing-function: cubic-bezier(0.2, 0, 0, 1);
  animation-fill-mode: both;
  will-change: transform, opacity;
}

.stage-1 {
  animation-name: slideFromTop;
  animation-delay: 70ms;
}

.stage-2 {
  animation-name: slideFromLeft;
  animation-delay: 190ms;
}

.stage-3 {
  animation-name: slideFromRight;
  animation-delay: 320ms;
}

.stage-4 {
  animation-name: slideFromBottom;
  animation-delay: 440ms;
}

.right-group-card {
  opacity: 0;
  animation: slideFromRight 560ms cubic-bezier(0.2, 0, 0, 1) 460ms both;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.section-head h3,
.chart-panel h3 {
  margin: 0;
}

.risk-kpi-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.risk-kpi-card {
  position: relative;
  overflow: hidden;
  min-height: 96px;
  isolation: isolate;
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid rgba(207, 213, 224, 0.72);
  border-right-width: 6px;
  border-radius: 0;
  box-shadow: 0 8px 24px rgba(149, 157, 165, 0.1);
  transition: transform 240ms cubic-bezier(0.2, 0, 0, 1), box-shadow 240ms cubic-bezier(0.2, 0, 0, 1);
}

.risk-kpi-card > :not(.risk-card-particles) {
  position: relative;
  z-index: 1;
}

.risk-card-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  min-height: 100%;
}

.risk-card-copy {
  display: grid;
  gap: 6px;
}

.risk-card-icon {
  width: 54px;
  height: 54px;
  border-radius: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.5);
  flex: 0 0 auto;
}

.risk-card-icon svg {
  width: 28px;
  height: 28px;
}

.risk-kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 28px rgba(149, 157, 165, 0.14);
}

.risk-kpi-card:active {
  transform: scale(0.98);
}

.risk-card-particles {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  contain: paint;
}

.risk-card-particles :deep(canvas) {
  display: block;
  width: 100%;
  height: 100%;
}

.risk-card-low {
  color: #166534;
}

.risk-card-medium {
  color: #1e40af;
}

.risk-card-higher {
  color: #9a3412;
}

.risk-card-high {
  color: #9f1239;
}

.risk-kpi-card .muted {
  color: #5f6779;
  opacity: 1;
}

.risk-kpi-card .kpi-value {
  color: currentColor;
}

.risk-card-low {
  border-right-color: #166534;
}

.risk-card-medium {
  border-right-color: #1e40af;
}

.risk-card-higher {
  border-right-color: #9a3412;
}

.risk-card-high {
  border-right-color: #9f1239;
}

.portrait-panel .panel-inner {
  height: 100%;
  display: grid;
  grid-template-rows: auto 1fr;
}

.portrait-head-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}

.portrait-tabs {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.portrait-tab {
  min-height: 34px;
  padding: 0 14px;
  border-radius: 999px;
  border: 1px solid rgba(103, 80, 164, 0.14);
  background: rgba(247, 243, 252, 0.82);
  color: #5b5270;
  font-size: 0.82rem;
  font-weight: 600;
  transition: all 200ms cubic-bezier(0.2, 0, 0, 1);
}

.portrait-tab:hover {
  border-color: rgba(103, 80, 164, 0.28);
  background: rgba(239, 232, 249, 0.9);
}

.portrait-tab.active {
  background: #6750a4;
  border-color: #6750a4;
  color: #fff;
  box-shadow: 0 8px 18px rgba(103, 80, 164, 0.2);
}

.portrait-chart-wrap {
  min-height: 100%;
  height: 100%;
}

.portrait-stage {
  height: 340px;
  min-height: 340px;
}

.dimension-summary-grid {
  height: 100%;
  overflow: auto;
  padding-right: 4px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  align-content: start;
}

.dimension-summary-card {
  min-height: 108px;
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid rgba(28, 34, 56, 0.08);
  background: rgba(250, 251, 253, 0.88);
  display: grid;
  gap: 8px;
}

.dimension-summary-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: start;
}

.dimension-summary-score {
  font-size: 1.35rem;
  font-weight: 700;
  color: #241a37;
}

.dimension-summary-label {
  color: #6b637a;
  font-size: 0.82rem;
  line-height: 1.45;
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
  transition: background-color 180ms cubic-bezier(0.2, 0, 0, 1);
}

.summary-row:hover {
  background: rgba(103, 80, 164, 0.06);
}

.summary-row:first-child {
  border-top: 0;
  padding-top: 0;
}

.simple-row {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  padding: 4px 0;
  border-top: 1px solid rgba(28, 34, 56, 0.08);
  font-size: 0.88rem;
  transition: transform 180ms cubic-bezier(0.2, 0, 0, 1), background-color 180ms cubic-bezier(0.2, 0, 0, 1);
}

.simple-row:hover {
  transform: translateX(2px);
  background: rgba(103, 80, 164, 0.06);
}

.trend-indicator {
  margin-left: 6px;
  font-weight: 700;
}

.trend-up {
  color: #2e7d32;
}

.trend-down {
  color: #c62828;
}

.trend-steady {
  color: #ef6c00;
}

.simple-row:first-of-type {
  border-top: 0;
}

.dimension-detail-panel {
  margin-top: 16px;
}

.dimension-details > summary {
  cursor: pointer;
  list-style: none;
  font-weight: 700;
  padding: 6px 0 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.dimension-details > summary::-webkit-details-marker {
  display: none;
}

.dimension-details > summary::after {
  content: '▸';
  color: #6750a4;
  font-size: 0.92rem;
  transition: transform 220ms cubic-bezier(0.2, 0, 0, 1), color 220ms cubic-bezier(0.2, 0, 0, 1);
}

.dimension-details[open] > summary::after {
  content: '▾';
  transform: translateY(1px);
}

.dimension-details > summary:hover::after {
  color: #513b90;
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
  transition: transform 220ms cubic-bezier(0.2, 0, 0, 1), box-shadow 220ms cubic-bezier(0.2, 0, 0, 1);
}

.dimension-detail-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(29, 25, 43, 0.12);
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

.tag.pending {
  color: #667085;
  border-color: #d0d5dd;
  background: #f2f4f7;
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

@keyframes slideFromTop {
  from {
    opacity: 0;
    transform: translateY(-22px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideFromLeft {
  from {
    opacity: 0;
    transform: translateX(-28px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideFromRight {
  from {
    opacity: 0;
    transform: translateX(28px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideFromBottom {
  from {
    opacity: 0;
    transform: translateY(24px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 960px) {
  .risk-overview-layer,
  .middle-layout,
  .right-group-top,
  .dimension-detail-grid,
  .dimension-summary-grid {
    grid-template-columns: 1fr;
  }

  .risk-kpi-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .portrait-head-actions {
    width: 100%;
    justify-content: flex-start;
  }
}

@media (prefers-reduced-motion: reduce) {
  .overview-stage-enter-active,
  .overview-stage-leave-active,
  .stage,
  .stage-1,
  .stage-2,
  .stage-3,
  .stage-4,
  .right-group-card,
  .right-card,
  .risk-kpi-card,
  .summary-row,
  .simple-row,
  .dimension-details > summary::after,
  .dimension-detail-card {
    transition: none !important;
    animation: none !important;
    transform: none !important;
  }
}
</style>

