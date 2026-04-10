<template>
  <div class="student-page">
    <section class="panel header-panel">
      <div class="panel-inner header-inner">
        <RouterLink class="back-btn" :to="backToWarningsTarget">← 返回预警列表</RouterLink>
        <div class="title-wrap">
          <h1>{{ profile?.student_name || studentId }}</h1>
          <p class="muted">{{ profile?.major_name || '学生详情' }}</p>
          <div v-if="availableTerms.length" class="term-switch">
            <button
              v-for="item in availableTerms"
              :key="item"
              type="button"
              class="term-switch-btn"
              :class="{ active: item === term }"
              :disabled="isSwitchingTerm && item === pendingTerm"
              @click="setStudentTerm(item)"
            >
              {{ isSwitchingTerm && item === pendingTerm ? '切换中...' : item }}
            </button>
          </div>
        </div>
        <div class="tag-row" v-if="profile">
          <span class="tag">{{ term }}</span>
          <span class="tag" :class="riskTagClass">{{ riskLabel(profile.intervention_priority_level ?? profile.risk_level) }}</span>
          <span class="tag">{{ profile.group_segment }}</span>
        </div>
      </div>
    </section>

    <section v-if="profile" class="panel academic-panel">
      <div class="panel-inner">
        <div class="academic-strip">
          <div class="academic-chip">
            <span class="academic-chip-label">GPA</span>
            <strong class="academic-chip-value">
              <span>{{ formatAcademicValue(profile.term_gpa, 2) }}</span>
              <small class="academic-chip-unit">/4.5</small>
            </strong>
          </div>
          <div class="academic-chip">
            <span class="academic-chip-label">挂科数</span>
            <strong class="academic-chip-value">
              <span>{{ formatAcademicCount(profile.failed_course_count) }}</span>
              <small class="academic-chip-unit">门</small>
            </strong>
          </div>
          <div class="academic-chip">
            <span class="academic-chip-label">临界数</span>
            <strong class="academic-chip-value">
              <span>{{ formatAcademicCount(profile.borderline_course_count) }}</span>
              <small class="academic-chip-unit">门</small>
            </strong>
          </div>
          <div class="academic-chip">
            <span class="academic-chip-label">挂科占比</span>
            <strong class="academic-chip-value">
              <span>{{ formatAcademicRatio(profile.failed_course_ratio).replace('%', '') }}</span>
              <small v-if="formatAcademicRatio(profile.failed_course_ratio).includes('%')" class="academic-chip-unit">%</small>
            </strong>
          </div>
        </div>
      </div>
    </section>

    <Transition name="overview-stage">
      <LoadingState
        v-if="isInitialLoading"
        key="loading"
        label="正在加载学生详情..."
      />
      <ErrorState
        v-else-if="errorMessage"
        key="error"
        title="学生详情加载失败"
        :description="errorMessage"
        @retry="retry"
      />
      <EmptyState v-else-if="!profile || !report" key="empty" title="暂无学生详情数据" description="请切换学期后重试" />

      <div v-else key="content">
        <section class="profile-main-row stage stage-1">
        <article class="panel summary-panel">
          <div class="panel-inner stack">
            <h3>风险概览</h3>
            <div class="summary-metrics-grid">
              <div class="metric-card">
                <span class="muted">干预优先级</span>
                <strong :class="riskClass">{{ riskLabel(profile.intervention_priority_level ?? profile.risk_level) }}</strong>
              </div>
              <div class="metric-card">
                <span class="muted">学业风险</span>
                <strong>{{ riskLabel(profile.academic_risk_level ?? profile.risk_level) }}</strong>
              </div>
              <div class="metric-card">
                <span class="muted">行为风险</span>
                <strong>{{ riskLabel(profile.behavior_risk_level ?? profile.risk_level) }}</strong>
              </div>
              <div class="metric-card">
                <span class="muted">干预分级分</span>
                <strong>{{ formatRiskScore(profile.intervention_priority_score ?? report.adjusted_risk_score ?? profile.adjusted_risk_score) }}</strong>
              </div>
              <div class="metric-card">
                <span class="muted">风险概率</span>
                <strong>{{ formatRisk(profile.risk_probability) }}</strong>
              </div>
              <div class="metric-card">
                <span class="muted">风险变化</span>
                <strong>{{ formatSignedRisk(report.risk_delta ?? profile.risk_delta) }}</strong>
              </div>
            </div>
          </div>
        </article>

        <article class="panel radar-panel">
          <div class="panel-inner stack">
            <div class="panel-head">
              <h3>八维评分雷达</h3>
              <button class="btn secondary detail-toggle" type="button" @click="showRadarDetails = !showRadarDetails">
                {{ showRadarDetails ? '收起' : '详情' }}
              </button>
            </div>
            <LazyEChart v-if="!showRadarDetails" :option="dimensionRadarOption" height="340px" />
            <div v-else class="radar-detail-grid">
              <article v-for="item in simplifiedDimensionRows" :key="item.dimension" class="radar-detail-item">
                <div class="radar-detail-head">
                  <strong>{{ item.dimension }}</strong>
                  <span class="tag" :class="detailDimensionTagClass(item.level)">{{ detailDimensionLevelText(item.level) }}</span>
                </div>
                <div class="radar-detail-meta">
                  <span>{{ Math.round(item.score * 100) }}分</span>
                  <span class="muted">{{ item.label ?? '待补充' }}</span>
                </div>
              </article>
            </div>
          </div>
        </article>
      </section>

      <section class="profile-third-row stage stage-2">
        <article class="panel">
          <div class="panel-inner stack">
            <h3>学期趋势</h3>
            <LazyEChart :option="trendLineOption" height="300px" />
          </div>
        </article>

        <article class="panel explain-panel">
          <div class="panel-inner stack">
            <h3>风险说明</h3>
            <div class="explain-stack">
              <section class="explain-item">
                <h4>基础风险解释</h4>
                <p class="muted">{{ shortText(report.base_risk_explanation || profile.base_risk_explanation, '暂无基础风险解释') }}</p>
              </section>
              <section class="explain-item">
                <h4>行为调整解释</h4>
                <p class="muted">{{ shortText(report.behavior_adjustment_explanation || profile.behavior_adjustment_explanation, '暂无行为调整解释') }}</p>
              </section>
              <section class="explain-item">
                <h4>风险变化说明</h4>
                <p class="muted">{{ shortText(report.risk_change_explanation || profile.risk_change_explanation, '暂无风险变化说明') }}</p>
              </section>
            </div>
          </div>
        </article>

        <article class="panel">
          <div class="panel-inner stack">
            <h3>关键影响因素</h3>
            <div v-for="item in report.top_factors" :key="item.dimension" class="factor-row">
              <div class="factor-head">
                <strong>{{ item.dimension }}</strong>
                <span v-if="item.label" class="tag">{{ item.label }}</span>
              </div>
              <p class="muted">{{ item.explanation }}</p>
              <div v-if="item.metrics?.length" class="factor-metrics">
                <span v-for="metric in item.metrics?.slice(0, 2) ?? []" :key="metric.metric" class="tag">
                  {{ metric.metric }} {{ formatMetric(metric) }}
                </span>
              </div>
            </div>
          </div>
        </article>
      </section>

      <section class="detail-grid stage stage-3">
        <article class="panel">
          <div class="panel-inner stack">
            <h3>干预建议</h3>
            <ol class="advice-list">
              <li v-for="item in report.intervention_advice" :key="item">{{ item }}</li>
            </ol>
            <div v-if="interventionPlanLines.length" class="summary-box">
              <p class="muted">干预计划</p>
              <p v-for="line in interventionPlanLines" :key="line" class="plan-line">{{ line }}</p>
            </div>
            <div class="summary-box">
              <p class="muted">报告摘要</p>
              <div v-if="reportMetadataItems.length" class="report-source-strip" aria-label="报告来源">
                <span class="report-source-heading">报告来源</span>
                <span v-for="item in reportMetadataItems" :key="`${item.label}:${item.value}`" class="report-source-pill">
                  <span class="report-source-label">{{ item.label }}</span>
                  <strong>{{ item.value }}</strong>
                </span>
              </div>
              <div class="markdown-report" v-html="reportMarkdownHtml"></div>
            </div>
          </div>
        </article>
      </section>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useQuery, useQueryClient } from '@tanstack/vue-query'
import type { EChartsOption } from 'echarts'

import { AVAILABLE_TERMS } from '@/app/term'
import LazyEChart from '@/components/charts/LazyEChart.vue'
import EmptyState from '@/components/state/EmptyState.vue'
import ErrorState from '@/components/state/ErrorState.vue'
import LoadingState from '@/components/state/LoadingState.vue'
import { getStudentProfile, getStudentReport } from '@/lib/api'
import { formatApiErrorMessage, formatRisk } from '@/lib/format'
import { parseWarningQuery, buildWarningQuery } from '@/features/warnings/query'

const route = useRoute()
const router = useRouter()
const queryClient = useQueryClient()

const studentId = computed(() => String(route.params.studentId ?? ''))
const term = computed(() => String(route.query.term ?? '2024-2'))
const warningState = computed(() => parseWarningQuery(route.query))

const profileQuery = useQuery({
  queryKey: computed(() => ['student-profile', studentId.value, term.value]),
  queryFn: () => getStudentProfile(studentId.value, term.value),
  placeholderData: (previousData) => previousData,
  staleTime: 0,
  refetchOnMount: 'always',
})

const reportQuery = useQuery({
  queryKey: computed(() => ['student-report', studentId.value, term.value]),
  queryFn: () => getStudentReport(studentId.value, term.value),
  placeholderData: (previousData) => previousData,
  staleTime: 0,
  refetchOnMount: 'always',
})

const profile = computed(() => profileQuery.data.value)
const report = computed(() => reportQuery.data.value)
const stableAvailableTerms = ref<string[]>([term.value])
const pendingTerm = ref<string | null>(null)
const pendingTermStartedAt = ref(0)

const availableTerms = computed(() => {
  const trendTerms = (profile.value?.trend ?? [])
    .map((item) => item.term)
    .filter((value): value is string => typeof value === 'string' && value.length > 0)
  if (!trendTerms.length && stableAvailableTerms.value.length > 1) return stableAvailableTerms.value
  const merged = Array.from(new Set([term.value, ...trendTerms]))
  const nextTerms = AVAILABLE_TERMS.filter((item) => merged.includes(item))
  return nextTerms.length ? nextTerms : stableAvailableTerms.value
})
const showRadarDetails = ref(false)
const reportMarkdownHtml = computed(() => renderMarkdown(report.value?.report_text || '暂无报告摘要'))
const reportMetadataItems = computed(() => {
  const currentReport = report.value
  if (!currentReport) return []

  const items: Array<{ label: string; value: string }> = []
  if (currentReport.report_source) items.push({ label: '来源', value: currentReport.report_source })
  if (currentReport.prompt_version) items.push({ label: 'Prompt', value: currentReport.prompt_version })

  const generation = asMetadataRecord(currentReport.report_generation)
  if (!generation) return items

  const generationSource = readMetadataValue(generation.source)
  if (generationSource && generationSource !== currentReport.report_source) {
    items.push({ label: '生成方式', value: generationSource })
  }

  const generationModel = readMetadataValue(generation.model)
  if (generationModel) items.push({ label: '模型', value: generationModel })

  const generatedAt = readMetadataValue(generation.generated_at)
  if (generatedAt) items.push({ label: '生成时间', value: formatMetadataTimestamp(generatedAt) })

  const fallbackReason = readMetadataValue(generation.fallback_reason)
  if (fallbackReason) items.push({ label: '回退原因', value: fallbackReason })

  const requestedPromptVersion = readMetadataValue(generation.requested_prompt_version)
  if (requestedPromptVersion && requestedPromptVersion !== currentReport.prompt_version) {
    items.push({ label: '请求 Prompt', value: requestedPromptVersion })
  }

  return items
})
const interventionPlanLines = computed(() => {
  const plan = report.value?.intervention_plan
  if (typeof plan === 'string') {
    return plan
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean)
  }
  if (Array.isArray(plan)) return plan.filter(Boolean)
  return []
})

const errorMessage = computed(() => {
  const firstError = profileQuery.error.value ?? reportQuery.error.value
  return firstError ? formatApiErrorMessage(firstError, '当前学生详情暂不可用，请稍后重试') : ''
})
const isInitialLoading = computed(
  () =>
    (profileQuery.isLoading.value || reportQuery.isLoading.value) &&
    (!profile.value || !report.value),
)
const isSwitchingTerm = computed(
  () =>
    pendingTerm.value !== null &&
    pendingTerm.value === term.value &&
    reportQuery.dataUpdatedAt.value <= pendingTermStartedAt.value,
)

watch(
  availableTerms,
  (nextTerms) => {
    if (nextTerms.length > 1) stableAvailableTerms.value = nextTerms
  },
  { immediate: true },
)

watch(
  () => [term.value, reportQuery.dataUpdatedAt.value] as const,
  ([currentTerm, reportUpdatedAt]) => {
    if (
      pendingTerm.value &&
      pendingTerm.value === currentTerm &&
      reportUpdatedAt > pendingTermStartedAt.value
    ) {
      pendingTerm.value = null
      pendingTermStartedAt.value = 0
    }
  },
  { immediate: true },
)

watch(
  () => [studentId.value, availableTerms.value.join('|')] as const,
  ([currentStudentId, termKey]) => {
    if (!currentStudentId || !termKey) return
    const termsToPrefetch = availableTerms.value.filter((item) => item !== term.value)
    for (const prefetchTerm of termsToPrefetch) {
      void queryClient.prefetchQuery({
        queryKey: ['student-profile', currentStudentId, prefetchTerm],
        queryFn: () => getStudentProfile(currentStudentId, prefetchTerm),
        staleTime: 5 * 60 * 1000,
      })
      void queryClient.prefetchQuery({
        queryKey: ['student-report', currentStudentId, prefetchTerm],
        queryFn: () => getStudentReport(currentStudentId, prefetchTerm),
        staleTime: 5 * 60 * 1000,
      })
    }
  },
  { immediate: true },
)

const trendLineOption = computed<EChartsOption>(() => {
  const rows = profile.value?.trend ?? []
  return {
    color: ['#6750A4'],
    tooltip: { trigger: 'axis' },
    xAxis: {
      type: 'category',
      data: rows.map((item) => item.term),
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
        type: 'line',
        smooth: true,
        symbolSize: 7,
        areaStyle: { color: 'rgba(103, 80, 164, 0.12)' },
        data: rows.map((item) => item.risk_probability ?? null),
      },
    ],
  }
})

const dimensionRadarOption = computed<EChartsOption>(() => {
  const rows = profile.value?.dimension_scores ?? []
  const indicators = rows.slice(0, 8).map((item) => ({ name: item.dimension, max: 1 }))
  const values = rows.slice(0, 8).map((item) => item.score ?? 0)

  return {
    color: ['#3b82f6'],
    tooltip: { trigger: 'item' },
    radar: {
      radius: '66%',
      indicator: indicators,
      splitNumber: 4,
      splitLine: { lineStyle: { color: 'rgba(59, 130, 246, 0.25)' } },
      splitArea: { areaStyle: { color: ['rgba(59,130,246,0.02)', 'rgba(59,130,246,0.05)'] } },
      axisLine: { lineStyle: { color: 'rgba(59, 130, 246, 0.35)' } },
    },
    series: [
      {
        type: 'radar',
        data: [
          {
            value: values,
            name: '八维评分',
            areaStyle: { color: 'rgba(59, 130, 246, 0.22)' },
            lineStyle: { width: 2 },
            symbol: 'circle',
            symbolSize: 6,
          },
        ],
      },
    ],
  }
})

const simplifiedDimensionRows = computed(() => (profile.value?.dimension_scores ?? []).slice(0, 8))

const riskClass = computed(() => {
  const level = profile.value?.intervention_priority_level ?? profile.value?.risk_level
  if (level === 'high' || level === '高风险' || level === '较高风险') return 'risk-high'
  if (level === 'medium' || level === '一般风险') return 'risk-medium'
  return 'risk-low'
})

const riskTagClass = computed(() => {
  const level = profile.value?.intervention_priority_level ?? profile.value?.risk_level
  if (level === 'high' || level === '高风险' || level === '较高风险') return 'tag-high'
  if (level === 'medium' || level === '一般风险') return 'tag-medium'
  return 'tag-low'
})

const backToWarningsTarget = computed(() => {
  if (route.query.source === 'warnings') {
    return { path: '/warnings', query: buildWarningQuery(warningState.value) }
  }
  return { path: '/warnings', query: { term: term.value } }
})

function shortText(text: string | undefined, fallback: string) {
  const value = (text ?? '').trim()
  if (!value) return fallback
  return value
}

function asMetadataRecord(value: unknown) {
  return value && typeof value === 'object' && !Array.isArray(value) ? (value as Record<string, unknown>) : null
}

function readMetadataValue(value: unknown) {
  if (typeof value === 'string' && value.trim()) return value.trim()
  if (typeof value === 'number' && Number.isFinite(value)) return String(value)
  if (typeof value === 'boolean') return value ? 'true' : 'false'
  return ''
}

function formatMetadataTimestamp(value: string) {
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime())) return value
  return `${parsed.getUTCFullYear()}-${String(parsed.getUTCMonth() + 1).padStart(2, '0')}-${String(
    parsed.getUTCDate(),
  ).padStart(2, '0')} ${String(parsed.getUTCHours()).padStart(2, '0')}:${String(parsed.getUTCMinutes()).padStart(2, '0')} UTC`
}

function detailDimensionLevelText(level?: string) {
  if (!level) return '待补充'
  if (level === 'high') return '高'
  if (level === 'medium') return '中'
  return '低'
}

function detailDimensionTagClass(level?: string) {
  if (!level) return 'tag-pending'
  if (level === 'high') return 'tag-high'
  if (level === 'medium') return 'tag-medium'
  return 'tag-low'
}

function formatMetric(metric: { display?: string; value: number | string }) {
  return metric.display || String(metric.value)
}

function riskLabel(level: string) {
  if (level === 'high' || level === '高风险') return '高风险'
  if (level === '较高风险') return '较高风险'
  if (level === 'medium' || level === '一般风险') return '一般风险'
  return '低风险'
}

function riskChangeText(direction?: string) {
  if (direction === 'rising') return '上升'
  if (direction === 'steady') return '持平'
  if (direction === 'falling') return '下降'
  return '未更新'
}

function formatRiskScore(value?: number) {
  if (typeof value !== 'number') return '--'
  return value.toFixed(1)
}

function formatAcademicValue(value?: number, digits = 1) {
  if (typeof value !== 'number') return '--'
  return value.toFixed(digits)
}

function formatAcademicCount(value?: number) {
  if (typeof value !== 'number') return '--'
  return Math.round(value).toString()
}

function formatAcademicRatio(value?: number) {
  if (typeof value !== 'number') return '--'
  return `${(value * 100).toFixed(1)}%`
}

function formatSignedRisk(value?: number) {
  if (typeof value !== 'number') return '--'
  return `${value > 0 ? '+' : ''}${value.toFixed(1)}`
}

function retry() {
  profileQuery.refetch()
  reportQuery.refetch()
}

function setStudentTerm(nextTerm: string) {
  if (nextTerm === term.value) return
  pendingTerm.value = nextTerm
  pendingTermStartedAt.value = Date.now()
  router.replace({
    path: `/students/${studentId.value}`,
    query: {
      ...route.query,
      term: nextTerm,
    },
  })
}

function renderMarkdown(source: string) {
  const normalized = source.replace(/\r\n/g, '\n').trim()
  if (!normalized) return '<p>暂无报告摘要</p>'

  const lines = normalized.split('\n')
  const html: string[] = []
  let listItems: string[] = []
  let paragraphLines: string[] = []

  const flushList = () => {
    if (!listItems.length) return
    html.push(`<ul>${listItems.map((item) => `<li>${renderInlineMarkdown(item)}</li>`).join('')}</ul>`)
    listItems = []
  }

  const flushParagraph = () => {
    if (!paragraphLines.length) return
    html.push(`<p>${paragraphLines.map((line) => renderInlineMarkdown(line)).join('<br>')}</p>`)
    paragraphLines = []
  }

  for (const rawLine of lines) {
    const line = rawLine.trim()

    if (!line) {
      flushList()
      flushParagraph()
      continue
    }

    const heading = line.match(/^(#{1,3})\s*(.+)$/)
    if (heading) {
      flushList()
      flushParagraph()
      const marker = heading[1] ?? '#'
      const headingText = heading[2] ?? line.replace(/^#+\s*/, '')
      html.push(`<h${marker.length}>${renderInlineMarkdown(headingText)}</h${marker.length}>`)
      continue
    }

    const listItem = line.match(/^[-*]\s+(.+)$/)
    if (listItem) {
      flushParagraph()
      listItems.push(listItem[1] ?? line.replace(/^[-*]\s+/, ''))
      continue
    }

    flushList()
    paragraphLines.push(line)
  }

  flushList()
  flushParagraph()

  return html.join('')
}

function renderInlineMarkdown(source: string) {
  let html = escapeHtml(source)
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>')
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>')
  return html
}

function escapeHtml(source: string) {
  return source
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}
</script>

<style scoped>
.student-page {
  min-height: 100vh;
  padding: 18px;
  background: #f4f6fa;
}

.header-panel {
  margin-bottom: 16px;
}

.header-inner {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 14px;
}

.back-btn {
  border: 1px solid #e2e7ee;
  background: #fff;
  border-radius: 10px;
  padding: 10px 12px;
}

.title-wrap h1 {
  margin: 0;
  font-size: 1.6rem;
}

.title-wrap p {
  margin: 4px 0 0;
}

.academic-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.academic-panel {
  margin-bottom: 16px;
}

.academic-chip {
  display: grid;
  align-content: space-between;
  min-height: 78px;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid #dbe4f0;
  background: #f8fbff;
  color: #334155;
  text-align: left;
}

.academic-chip-label {
  color: #64748b;
  font-size: 0.8rem;
  font-weight: 600;
  line-height: 1.2;
}

.academic-chip-value {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  width: 100%;
  color: #1e293b;
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.25;
  text-align: center;
}

.academic-chip-unit {
  color: #64748b;
  font-size: 0.78rem;
  font-weight: 600;
  line-height: 1;
}

.term-switch {
  margin-top: 10px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.term-switch-btn {
  min-height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid #dbe3ee;
  background: #fff;
  color: #556070;
  font-size: 0.84rem;
  font-weight: 600;
  transition: all 180ms cubic-bezier(0.2, 0, 0, 1);
}

.term-switch-btn.active {
  background: #6750a4;
  border-color: #6750a4;
  color: #fff;
}

.tag-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.profile-main-row {
  display: grid;
  grid-template-columns: 2fr 3fr;
  gap: 16px;
}

.summary-metrics-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.metric-card {
  padding: 12px;
  border: 1px solid #edf1f6;
  border-radius: 12px;
  background: #fafbfd;
  display: grid;
  gap: 6px;
  opacity: 0;
  animation: slideFromTop 460ms cubic-bezier(0.2, 0, 0, 1) both;
}

.metric-card strong {
  font-size: 1.2rem;
}

.summary-metrics-grid .metric-card:nth-child(odd) {
  animation-name: slideFromLeft;
}

.summary-metrics-grid .metric-card:nth-child(even) {
  animation-name: slideFromRight;
}

.summary-metrics-grid .metric-card:nth-child(1) {
  animation-delay: 220ms;
}

.summary-metrics-grid .metric-card:nth-child(2) {
  animation-delay: 280ms;
}

.summary-metrics-grid .metric-card:nth-child(3) {
  animation-delay: 340ms;
}

.summary-metrics-grid .metric-card:nth-child(4) {
  animation-delay: 400ms;
}

.summary-metrics-grid .metric-card:nth-child(5) {
  animation-delay: 460ms;
}

.summary-metrics-grid .metric-card:nth-child(6) {
  animation-delay: 520ms;
}

.radar-panel :deep(canvas) {
  border-radius: 12px;
}

.detail-toggle {
  min-height: 34px;
  padding: 0 14px;
}

.radar-detail-grid {
  margin-top: -2px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.radar-detail-item {
  border: 1px solid #edf1f6;
  border-radius: 10px;
  background: #fafbfd;
  padding: 8px 10px;
  display: grid;
  gap: 6px;
  opacity: 0;
  animation: slideFromBottom 420ms cubic-bezier(0.2, 0, 0, 1) both;
}

.radar-detail-item:nth-child(odd) {
  animation-delay: 220ms;
}

.radar-detail-item:nth-child(even) {
  animation-delay: 300ms;
}

.radar-detail-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.radar-detail-meta {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  font-size: 0.86rem;
}

.profile-second-row {
  margin-top: 16px;
}

.profile-third-row {
  margin-top: 16px;
  display: grid;
  grid-template-columns: 3fr 4fr 3fr;
  gap: 16px;
}

.detail-grid {
  margin-top: 16px;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.dimension-metrics,
.factor-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.explain-stack {
  display: grid;
  gap: 10px;
}

.explain-item {
  border: 1px solid #edf1f6;
  border-radius: 12px;
  background: #fafbfd;
  padding: 10px 12px;
  opacity: 0;
  animation: slideFromLeft 480ms cubic-bezier(0.2, 0, 0, 1) both;
}

.explain-item:nth-child(1) {
  animation-delay: 240ms;
}

.explain-item:nth-child(2) {
  animation-delay: 320ms;
}

.explain-item:nth-child(3) {
  animation-delay: 400ms;
}

.explain-item h4 {
  margin: 0 0 6px;
  font-size: 0.98rem;
}

.explain-item p {
  margin: 0;
}

.tag-high {
  color: #fff;
  border-color: #ef4444;
  background: #ef4444;
}

.tag-medium {
  color: #fff;
  border-color: #f59e0b;
  background: #f59e0b;
}

.tag-low {
  color: #fff;
  border-color: #22b573;
  background: #22b573;
}

.tag-pending {
  color: #667085;
  border-color: #d0d5dd;
  background: #f2f4f7;
}

.risk-high {
  color: #ef4444;
}

.risk-medium {
  color: #f59e0b;
}

.risk-low {
  color: #22b573;
}

h3 {
  margin: 0 0 10px;
}

.factor-row {
  border-top: 1px solid #edf1f6;
  padding: 10px 0;
  opacity: 0;
  animation: slideFromRight 500ms cubic-bezier(0.2, 0, 0, 1) both;
}

.factor-row:nth-child(2) {
  animation-delay: 250ms;
}

.factor-row:nth-child(3) {
  animation-delay: 330ms;
}

.factor-row:nth-child(4) {
  animation-delay: 410ms;
}

.factor-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.factor-row:first-of-type {
  border-top: 0;
}

.factor-row p {
  margin: 6px 0 0;
}

.advice-list {
  margin: 0;
  padding-left: 18px;
}

.summary-box {
  margin-top: 10px;
  border-radius: 10px;
  border: 1px solid #edf1f6;
  background: #fafbfd;
  padding: 10px 12px;
  opacity: 0;
  animation: slideFromBottom 520ms cubic-bezier(0.2, 0, 0, 1) 280ms both;
}

.summary-box p {
  margin: 0 0 6px;
}

.report-source-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 0 0 10px;
}

.report-source-heading {
  display: inline-flex;
  align-items: center;
  color: #475569;
  font-size: 0.82rem;
  font-weight: 600;
}

.report-source-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  min-height: 30px;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid #d9e2ec;
  background: #f1f5f9;
  color: #334155;
  font-size: 0.82rem;
  line-height: 1.2;
}

.report-source-label {
  color: #64748b;
}

.markdown-report {
  color: #2a3447;
  line-height: 1.75;
  font-family: inherit;
  font-size: 1rem;
}

.markdown-report :deep(h1),
.markdown-report :deep(h2),
.markdown-report :deep(h3),
.markdown-report :deep(p),
.markdown-report :deep(ul) {
  margin: 0 0 8px;
}

.markdown-report :deep(h1),
.markdown-report :deep(h2),
.markdown-report :deep(h3) {
  color: #192235;
  font-size: 1rem;
}

.markdown-report :deep(ul) {
  padding-left: 18px;
}

.markdown-report :deep(code) {
  padding: 1px 6px;
  border-radius: 6px;
  background: rgba(81, 101, 133, 0.12);
  color: #2f4669;
  font-size: 0.92em;
}

.plan-line {
  margin: 0;
  white-space: pre-wrap;
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
  animation-delay: 80ms;
}

.stage-2 {
  animation-name: slideFromLeft;
  animation-delay: 200ms;
}

.stage-3 {
  animation-name: slideFromRight;
  animation-delay: 320ms;
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
    transform: translateY(-18px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideFromLeft {
  from {
    opacity: 0;
    transform: translateX(-22px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideFromRight {
  from {
    opacity: 0;
    transform: translateX(22px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideFromBottom {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 980px) {
  .header-inner {
    grid-template-columns: 1fr;
    align-items: start;
  }

  .profile-main-row,
  .profile-third-row {
    grid-template-columns: 1fr;
  }

  .summary-metrics-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .academic-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .radar-detail-grid {
    grid-template-columns: 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  .overview-stage-enter-active,
  .overview-stage-leave-active,
  .stage,
  .stage-1,
  .stage-2,
  .stage-3,
  .metric-card,
  .radar-detail-item,
  .explain-item,
  .factor-row,
  .summary-box {
    transition: none !important;
    animation: none !important;
    transform: none !important;
    opacity: 1 !important;
  }
}
</style>
