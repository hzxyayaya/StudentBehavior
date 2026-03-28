<template>
  <AppShell>
    <div class="stack">
      <section class="panel">
        <div class="panel-inner grid-2 hero">
          <div class="stack">
            <p class="eyebrow">总览</p>
            <h2 class="title">风险态势与学期趋势</h2>
            <p class="muted">当前页展示群体风险分布、四象限概览和模型摘要。</p>
            <div class="term-switcher">
              <button
                v-for="item in terms"
                :key="item"
                class="tag"
                :class="{ hot: item === term }"
                type="button"
                @click="setTerm(item)"
              >
                {{ item }}
              </button>
            </div>
          </div>
          <div class="kpi-rail">
            <div class="card-kpi">
              <span class="muted">总学生数</span>
              <div class="kpi-value">{{ overview?.student_count ?? '—' }}</div>
            </div>
            <div class="card-kpi">
              <span class="muted">模型方法</span>
              <div class="kpi-value">{{ summary?.risk_model ?? 'stub' }}</div>
            </div>
          </div>
        </div>
      </section>

      <LoadingState v-if="overviewQuery.isLoading.value || summaryQuery.isLoading.value" label="正在加载总览..." />
      <ErrorState v-else-if="errorMessage" title="总览加载失败" :description="errorMessage" @retry="retry" />
      <template v-else-if="overview && summary">
        <section class="grid-3">
          <div class="card-kpi panel">
            <div class="muted">高风险</div>
            <div class="kpi-value">{{ riskCount('high') }}</div>
          </div>
          <div class="card-kpi panel">
            <div class="muted">中风险</div>
            <div class="kpi-value">{{ riskCount('medium') }}</div>
          </div>
          <div class="card-kpi panel">
            <div class="muted">低风险</div>
            <div class="kpi-value">{{ riskCount('low') }}</div>
          </div>
        </section>

        <section class="grid-2">
          <div class="panel">
            <div class="panel-inner stack">
              <h3>风险分布</h3>
              <div v-for="item in overview.risk_distribution" :key="item.risk_level" class="bar-row">
                <span>{{ labelOfRisk(item.risk_level) }}</span>
                <div class="bar-track">
                  <div class="bar-fill" :style="{ width: `${Math.max((item.count / maxRiskCount) * 100, 8)}%` }" />
                </div>
                <strong>{{ item.count }}</strong>
              </div>
            </div>
          </div>

          <div class="panel">
            <div class="panel-inner stack">
              <h3>四象限分布</h3>
              <div v-for="item in overview.quadrant_distribution" :key="item.quadrant_label" class="bar-row">
                <span>{{ item.quadrant_label }}</span>
                <div class="bar-track">
                  <div class="bar-fill cool" :style="{ width: `${Math.max((item.count / maxQuadrantCount) * 100, 8)}%` }" />
                </div>
                <strong>{{ item.count }}</strong>
              </div>
            </div>
          </div>
        </section>

        <section class="grid-2">
          <div class="panel">
            <div class="panel-inner stack">
              <h3>专业高风险摘要</h3>
              <div v-for="row in overview.major_risk_summary" :key="row.major_name" class="summary-row">
                <div>
                  <strong>{{ row.major_name }}</strong>
                  <p class="muted">{{ row.student_count }} 人</p>
                </div>
                <strong class="hot">{{ row.high_risk_count }}</strong>
              </div>
            </div>
          </div>

          <div class="panel">
            <div class="panel-inner stack">
              <h3>学期趋势</h3>
              <div v-for="item in overview.trend_summary" :key="item.term" class="summary-row">
                <span>{{ item.term }}</span>
                <strong>{{ item.high_risk_count }}</strong>
              </div>
              <div class="panel-inner mini-summary">
                <div>
                  <p class="muted">摘要方法</p>
                  <strong>{{ summary.cluster_method }}</strong>
                </div>
                <div>
                  <p class="muted">更新时间</p>
                  <strong>{{ summary.updated_at }}</strong>
                </div>
              </div>
            </div>
          </div>
        </section>
      </template>
    </div>
  </AppShell>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'

import AppShell from '@/components/layout/AppShell.vue'
import LoadingState from '@/components/state/LoadingState.vue'
import ErrorState from '@/components/state/ErrorState.vue'
import { getModelSummary, getOverview } from '@/lib/api'
import { useTermStore } from '@/app/term'
import type { RiskLevel } from '@/lib/types'

const termStore = useTermStore()
const terms = ['2024-2', '2024-1', '2023-2']

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
const errorMessage = computed(() => overviewQuery.error.value?.message || summaryQuery.error.value?.message || '')
const maxRiskCount = computed(() => Math.max(...(overview.value?.risk_distribution.map((item) => item.count) ?? [1])))
const maxQuadrantCount = computed(() => Math.max(...(overview.value?.quadrant_distribution.map((item) => item.count) ?? [1])))
const term = computed(() => termStore.term.value)

function riskCount(level: RiskLevel) {
  return overview.value?.risk_distribution.find((item) => item.risk_level === level)?.count ?? 0
}

function labelOfRisk(level: RiskLevel) {
  return { high: '高风险', medium: '中风险', low: '低风险' }[level]
}

function setTerm(nextTerm: string) {
  termStore.setTerm(nextTerm)
  overviewQuery.refetch()
  summaryQuery.refetch()
}

function retry() {
  overviewQuery.refetch()
  summaryQuery.refetch()
}
</script>

<style scoped>
.hero {
  align-items: center;
}

.kpi-rail {
  display: grid;
  gap: 12px;
}

.bar-row,
.summary-row {
  display: grid;
  gap: 12px;
  align-items: center;
  grid-template-columns: 120px minmax(0, 1fr) auto;
}

.bar-track {
  height: 12px;
  border-radius: 999px;
  background: rgba(28, 34, 56, 0.08);
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(135deg, var(--hot), var(--warn));
}

.bar-fill.cool {
  background: linear-gradient(135deg, var(--cool), var(--brand));
}

.mini-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
  padding: 18px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.72);
}

@media (max-width: 960px) {
  .bar-row,
  .summary-row {
    grid-template-columns: 1fr;
  }

  .mini-summary {
    grid-template-columns: 1fr;
  }
}
</style>
