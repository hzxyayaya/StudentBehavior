<template>
    <section class="panel">
      <div class="panel-inner stack">
        <div class="page-title-row">
          <span class="title-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M8 11a2.25 2.25 0 1 0 0-4.5A2.25 2.25 0 0 0 8 11Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
              <path d="M15.75 11a2.25 2.25 0 1 0 0-4.5 2.25 2.25 0 0 0 0 4.5Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
              <path d="M4.75 17.25a4.25 4.25 0 0 1 6.75-3.35M12.5 13.9a4.25 4.25 0 0 1 6.75 3.35" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </span>
          <div>
            <p class="eyebrow">群体画像</p>
            <h2 class="title">群体画像与模式分层</h2>
            <p class="muted">按重点群体查看风险概况、八维得分、风险放大与保护因素。</p>
          </div>
        </div>
      </div>
    </section>

    <Transition name="overview-stage" mode="out-in">
      <LoadingState v-if="query.isLoading.value" key="loading" class="section-gap" label="正在加载群体分层..." />
      <ErrorState
        v-else-if="query.error.value"
        key="error"
        class="section-gap"
        title="群体分层加载失败"
        :description="errorMessage"
        @retry="query.refetch()"
      />
      <EmptyState
        v-else-if="groups.length === 0"
        key="empty"
        class="section-gap"
        title="当前学期暂无群体分层结果"
        description="请切换到有数据的学期后重试。"
      />

      <section v-else key="content" class="group-grid section-gap">
        <article v-for="item in groups" :key="item.group_segment" class="panel group-card">
          <div class="panel-inner group-body">
            <div class="group-overview">
              <div class="group-head">
                <h3>{{ item.group_segment }}</h3>
                <span class="tag">{{ item.student_count }} 人</span>
              </div>

              <div class="metric-strip">
                <div class="group-metric">
                  <span class="muted">平均风险概率</span>
                  <strong>{{ formatRisk(item.avg_risk_probability) }}</strong>
                </div>
                <div class="group-metric">
                  <span class="muted">平均风险分</span>
                  <strong>{{ formatRiskScore(item.avg_risk_score) }}</strong>
                </div>
                <div class="group-metric">
                  <span class="muted">平均风险等级</span>
                  <strong>{{ item.avg_risk_level ?? '待补充' }}</strong>
                </div>
              </div>
            </div>

            <div class="content-row">
              <div class="section-block">
                <p class="muted">群体平均八维得分</p>
                <div class="dimension-grid">
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
                    <div class="dimension-track">
                      <div class="dimension-fill" :style="{ width: `${dimension.score * 100}%` }"></div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="factors-column">
                <div class="section-block factor-panel">
                  <div class="factor-tabs" role="tablist" aria-label="群体因素切换">
                    <button
                      type="button"
                      class="factor-tab"
                      :class="{ active: currentFactorTab(item.group_segment) === 'risk' }"
                      @click="setFactorTab(item.group_segment, 'risk')"
                    >
                      风险放大因素
                    </button>
                    <button
                      type="button"
                      class="factor-tab"
                      :class="{ active: currentFactorTab(item.group_segment) === 'protect' }"
                      @click="setFactorTab(item.group_segment, 'protect')"
                    >
                      保护性因素
                    </button>
                    <button
                      type="button"
                      class="factor-tab"
                      :class="{ active: currentFactorTab(item.group_segment) === 'top' }"
                      @click="setFactorTab(item.group_segment, 'top')"
                    >
                      主导因素
                    </button>
                  </div>

                  <div class="factor-tab-panel">
                    <template v-if="currentFactorTab(item.group_segment) === 'risk'">
                      <div v-if="item.risk_amplifiers.length === 0" class="muted">暂无放大因素</div>
                      <div v-else class="factor-inline-list">
                        <div
                          v-for="factor in sortedWeightFactors(item.risk_amplifiers)"
                          :key="`${factor.feature}-amp`"
                          class="factor-chip"
                          :style="factorChipStyle('risk', factor.importance, sortedWeightFactors(item.risk_amplifiers))"
                        >
                          <strong>{{ factor.feature_cn ?? factor.feature }}</strong>
                          <span class="muted">{{ factor.count }} 人 · {{ factor.importance.toFixed(2) }}</span>
                        </div>
                      </div>
                    </template>

                    <template v-else-if="currentFactorTab(item.group_segment) === 'protect'">
                      <div v-if="item.protective_factors.length === 0" class="muted">暂无保护性因素</div>
                      <div v-else class="factor-inline-list">
                        <div
                          v-for="factor in sortedWeightFactors(item.protective_factors)"
                          :key="`${factor.feature}-pro`"
                          class="factor-chip"
                          :style="factorChipStyle('protect', factor.importance, sortedWeightFactors(item.protective_factors))"
                        >
                          <strong>{{ factor.feature_cn ?? factor.feature }}</strong>
                          <span class="muted">{{ factor.count }} 人 · {{ factor.importance.toFixed(2) }}</span>
                        </div>
                      </div>
                    </template>

                    <template v-else>
                      <div v-if="item.top_factors.length === 0" class="muted">暂无主导因素</div>
                      <div v-else class="factor-stack">
                        <div
                          v-for="factor in sortedTopFactors(item.top_factors)"
                          :key="factor.dimension"
                          class="factor-row"
                          :style="topFactorRowStyle(factor.importance ?? factor.impact, sortedTopFactors(item.top_factors))"
                        >
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
                    </template>
                  </div>
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
    </Transition>
</template>

<script setup lang="ts">
import { computed, reactive } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { RouterLink } from 'vue-router'

import { useTermStore } from '@/app/term'
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
const activeFactorTab = reactive<Record<string, 'risk' | 'protect' | 'top'>>({})

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

function formatRiskScore(score: number) {
  return score.toFixed(1)
}

function setFactorTab(groupSegment: string, tab: 'risk' | 'protect' | 'top') {
  activeFactorTab[groupSegment] = tab
}

function currentFactorTab(groupSegment: string) {
  return activeFactorTab[groupSegment] ?? 'risk'
}

function sortedWeightFactors<T extends { importance: number }>(factors: T[]) {
  return [...factors].sort((a, b) => b.importance - a.importance)
}

function sortedTopFactors<T extends { importance?: number; impact?: number }>(factors: T[]) {
  return [...factors].sort((a, b) => (b.importance ?? b.impact ?? 0) - (a.importance ?? a.impact ?? 0))
}

function factorChipStyle(
  kind: 'risk' | 'protect',
  importance: number | undefined,
  factors: Array<{ importance: number }>,
) {
  const alpha = rankedFactorAlpha(importance, factors.map((item) => item.importance))
  if (kind === 'risk') {
    return {
      background: `rgba(239, 68, 68, ${alpha})`,
      borderColor: `rgba(185, 28, 28, ${Math.min(alpha + 0.16, 0.98)})`,
      color: '#fff',
    }
  }
  return {
    background: `rgba(34, 197, 94, ${alpha})`,
    borderColor: `rgba(21, 128, 61, ${Math.min(alpha + 0.14, 0.94)})`,
    color: '#fff',
  }
}

function topFactorRowStyle(weight: number | undefined, factors: Array<{ importance?: number; impact?: number }>) {
  const alpha = rankedFactorAlpha(
    weight,
    factors.map((item) => item.importance ?? item.impact ?? 0),
  )
  return {
    background: `rgba(79, 124, 255, ${alpha})`,
    borderTopColor: 'transparent',
    borderLeft: `3px solid rgba(79, 124, 255, ${Math.min(alpha + 0.18, 0.95)})`,
    paddingLeft: '12px',
    borderRadius: '10px',
    color: '#fff',
  }
}

function rankedFactorAlpha(weight: number | undefined, weights: number[]) {
  const normalizedWeights = weights
    .filter((item) => Number.isFinite(item))
    .map((item) => Number(item))
    .sort((a, b) => b - a)

  const value = Number.isFinite(weight) ? Number(weight) : 0
  if (normalizedWeights.length <= 1) return 0.78

  const rank = Math.max(0, normalizedWeights.findIndex((item) => item === value))
  const ratio = 1 - rank / (normalizedWeights.length - 1)
  return 0.28 + ratio * 0.62
}
</script>

<style scoped>
.page-title-row {
  display: flex;
  align-items: flex-start;
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
  flex: 0 0 auto;
}

.title-icon svg {
  width: 22px;
  height: 22px;
}

.section-gap {
  margin-top: 12px;
}

.group-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: minmax(0, 1fr);
}

.group-card {
  min-height: 280px;
}

.group-body {
  display: grid;
  gap: 12px;
}

.group-overview {
  display: grid;
  gap: 10px;
}

.group-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.metric-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.group-metric {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  padding: 10px 12px;
  border: 1px solid rgba(28, 34, 56, 0.08);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.75);
}

.section-block {
  display: grid;
  gap: 8px;
}

.content-row {
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: 12px;
}

.factors-column {
  display: grid;
  gap: 10px;
  align-content: start;
}

.factor-panel {
  min-height: 440px;
}

.factor-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.factor-tab {
  min-height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid rgba(28, 34, 56, 0.1);
  background: rgba(255, 255, 255, 0.78);
  color: #667085;
  font-size: 0.82rem;
  font-weight: 600;
  transition: all 180ms cubic-bezier(0.2, 0, 0, 1);
}

.factor-tab.active {
  color: #3b3f4b;
  border-color: rgba(93, 63, 192, 0.24);
  background: rgba(109, 79, 210, 0.1);
}

.factor-tab-panel {
  min-height: 372px;
  max-height: 372px;
  overflow: auto;
  padding-right: 4px;
}

.dimension-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.dimension-row {
  display: grid;
  gap: 6px;
  padding: 10px 12px;
  border: 1px solid rgba(28, 34, 56, 0.08);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.72);
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
  background: linear-gradient(90deg, #6d4fd2 0%, #4f7cff 100%);
}

.factor-inline-list,
.factor-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.factor-stack {
  display: grid;
  gap: 0;
}

.factor-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid rgba(28, 34, 56, 0.1);
  white-space: nowrap;
}

.factor-chip .muted,
.factor-row .muted,
.factor-row .tag {
  color: rgba(255, 255, 255, 0.88);
}

.factor-row {
  display: grid;
  gap: 6px;
  padding: 12px 0;
  border-top: 1px solid rgba(28, 34, 56, 0.08);
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

@media (max-width: 1280px) {
  .metric-strip {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 960px) {
  .content-row,
  .dimension-grid {
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
