<template>
  <div class="student-page">
    <section class="panel header-panel">
      <div class="panel-inner header-inner">
        <RouterLink class="back-btn" :to="backToWarningsTarget">← 返回预警列表</RouterLink>
        <div class="title-wrap">
          <h1>{{ profile?.student_name || studentId }}</h1>
          <p class="muted">{{ profile?.major_name || '学生详情' }}</p>
        </div>
        <div class="tag-row" v-if="profile">
          <span class="tag">{{ term }}</span>
          <span class="tag" :class="riskTagClass">{{ riskLabel(profile.risk_level) }}</span>
          <span class="tag">{{ profile.group_segment }}</span>
        </div>
      </div>
    </section>

    <LoadingState v-if="profileQuery.isLoading.value || reportQuery.isLoading.value" label="正在加载学生详情..." />
    <ErrorState v-else-if="errorMessage" title="学生详情加载失败" :description="errorMessage" @retry="retry" />
    <EmptyState v-else-if="!profile || !report" title="暂无学生详情数据" description="请切换学期后重试" />
    <template v-else>
      <section class="grid-3">
        <article class="card-kpi panel">
          <div class="muted">风险等级</div>
          <div class="kpi-value" :class="riskClass">{{ riskLabel(profile.risk_level) }}</div>
        </article>
        <article class="card-kpi panel">
          <div class="muted">风险概率</div>
          <div class="kpi-value">{{ formatRisk(profile.risk_probability) }}</div>
        </article>
        <article class="card-kpi panel">
          <div class="muted">所属群体标签</div>
          <div class="kpi-value">{{ profile.group_segment }}</div>
        </article>
      </section>

      <section class="grid-2 detail-grid">
        <article class="panel">
          <div class="panel-inner">
            <h3>学期趋势</h3>
            <EChart :option="trendLineOption" height="300px" />
          </div>
        </article>

        <article class="panel">
          <div class="panel-inner">
            <h3>维度评分</h3>
            <EChart :option="dimensionBarOption" height="300px" />
          </div>
        </article>
      </section>

      <section class="panel">
        <div class="panel-inner stack">
          <div class="panel-head">
            <h3>八维画像明细</h3>
            <span class="muted">按学生当前学期结果展示</span>
          </div>
          <div class="dimension-card-grid">
            <article v-for="item in profile.dimension_scores" :key="item.dimension" class="dimension-card">
              <div class="dimension-card-head">
                <div class="dimension-card-title">
                  <strong>{{ item.dimension }}</strong>
                  <span class="muted">{{ item.label ?? '待补充' }}</span>
                </div>
                <div class="dimension-card-score">
                  <span class="tag" :class="dimensionTagClass(item.level)">
                    {{ dimensionLevelText(item.level) }}
                  </span>
                  <span class="muted">{{ Math.round(item.score * 100) }}分</span>
                </div>
              </div>
              <p class="muted dimension-explanation">
                {{ item.explanation ?? '当前维度尚未提供完整校准结果' }}
              </p>
              <div class="dimension-track">
                <div class="dimension-fill" :style="{ width: `${item.score * 100}%` }"></div>
              </div>
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

      <section class="grid-2">
        <article class="panel">
          <div class="panel-inner stack">
            <h3>关键影响因子</h3>
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
        <article class="panel">
          <div class="panel-inner stack">
            <h3>干预建议</h3>
            <ol class="advice-list">
              <li v-for="item in report.intervention_advice" :key="item">{{ item }}</li>
            </ol>
            <div class="summary-box">
              <p class="muted">报告摘要</p>
              <strong>{{ report.report_text }}</strong>
            </div>
          </div>
        </article>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useQuery } from '@tanstack/vue-query'
import type { EChartsOption } from 'echarts'

import EChart from '@/components/charts/EChart.vue'
import EmptyState from '@/components/state/EmptyState.vue'
import ErrorState from '@/components/state/ErrorState.vue'
import LoadingState from '@/components/state/LoadingState.vue'
import { getStudentProfile, getStudentReport } from '@/lib/api'
import { formatApiErrorMessage, formatRisk } from '@/lib/format'
import { parseWarningQuery, buildWarningQuery } from '@/features/warnings/query'

const route = useRoute()

const studentId = computed(() => String(route.params.studentId ?? ''))
const term = computed(() => String(route.query.term ?? '2024-2'))
const warningState = computed(() => parseWarningQuery(route.query))

const profileQuery = useQuery({
  queryKey: computed(() => ['student-profile', studentId.value, term.value]),
  queryFn: () => getStudentProfile(studentId.value, term.value),
})

const reportQuery = useQuery({
  queryKey: computed(() => ['student-report', studentId.value, term.value]),
  queryFn: () => getStudentReport(studentId.value, term.value),
})

const profile = computed(() => profileQuery.data.value)
const report = computed(() => reportQuery.data.value)

const errorMessage = computed(() => {
  const firstError = profileQuery.error.value ?? reportQuery.error.value
  return firstError ? formatApiErrorMessage(firstError, '当前学生详情暂不可用，请稍后重试') : ''
})

const trendLineOption = computed<EChartsOption>(() => {
  const rows = profile.value?.trend ?? []
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
      min: 0,
      max: 1,
      splitLine: { lineStyle: { color: '#eef1f5' } },
    },
    series: [
      {
        type: 'line',
        smooth: true,
        symbolSize: 8,
        areaStyle: { color: 'rgba(255, 75, 0, 0.12)' },
        data: rows.map((item) => item.risk_probability ?? null),
      },
    ],
  }
})

const dimensionBarOption = computed<EChartsOption>(() => {
  const rows = profile.value?.dimension_scores ?? []
  return {
    color: ['#3b82f6'],
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    xAxis: {
      type: 'category',
      data: rows.map((item) => item.dimension),
      axisLabel: { interval: 0, rotate: 18 },
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

const riskClass = computed(() => {
  const level = profile.value?.risk_level
  if (level === 'high') return 'risk-high'
  if (level === 'medium') return 'risk-medium'
  return 'risk-low'
})

const riskTagClass = computed(() => {
  const level = profile.value?.risk_level
  if (level === 'high') return 'tag-high'
  if (level === 'medium') return 'tag-medium'
  return 'tag-low'
})

function dimensionLevelText(level?: string) {
  if (!level) return '待补充'
  if (level === 'high') return '高'
  if (level === 'medium') return '中'
  return '低'
}

function dimensionTagClass(level?: string) {
  if (!level) return 'pending'
  if (level === 'high') return 'tag-high'
  if (level === 'medium') return 'tag-medium'
  return 'tag-low'
}

function formatMetric(metric: { display?: string; value: number | string }) {
  return metric.display || String(metric.value)
}
const backToWarningsTarget = computed(() => {
  if (route.query.source === 'warnings') {
    return { path: '/warnings', query: buildWarningQuery(warningState.value) }
  }
  return { path: '/warnings', query: { term: term.value } }
})

function riskLabel(level: string) {
  if (level === 'high') return '高风险'
  if (level === 'medium') return '中风险'
  return '低风险'
}

function retry() {
  profileQuery.refetch()
  reportQuery.refetch()
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

.tag-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
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

.tag.pending {
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

.detail-grid {
  margin-top: 16px;
  margin-bottom: 16px;
}

h3 {
  margin: 0 0 10px;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.dimension-card-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.dimension-card {
  border: 1px solid #edf1f6;
  border-radius: 12px;
  background: #fafbfd;
  padding: 12px 14px;
  display: grid;
  gap: 8px;
}

.dimension-card-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.dimension-card-title {
  display: grid;
  gap: 4px;
}

.dimension-card-score {
  display: grid;
  gap: 6px;
  justify-items: end;
  white-space: nowrap;
}

.dimension-explanation {
  margin: 0;
}

.dimension-track {
  height: 10px;
  border-radius: 999px;
  background: #e9eef5;
  overflow: hidden;
}

.dimension-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
}

.dimension-metrics,
.factor-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.factor-row {
  border-top: 1px solid #edf1f6;
  padding: 10px 0;
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
}

.summary-box p {
  margin: 0 0 6px;
}

@media (max-width: 980px) {
  .header-inner {
    grid-template-columns: 1fr;
    align-items: start;
  }

  .dimension-card-grid {
    grid-template-columns: 1fr;
  }
}
</style>
