<template>
    <section class="panel filter-panel">
      <div class="panel-inner stack">
        <div class="page-title-row">
          <span class="title-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M12 4.75 19 17.25H5L12 4.75Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
              <path d="M12 9v4.5M12 15.75h.01" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
            </svg>
          </span>
          <div>
            <p class="eyebrow">风险预警</p>
            <h2 class="title">预警学生筛查</h2>
          </div>
        </div>
        <div class="filters">
          <label class="custom-select-wrap" aria-label="学期选择">
            <select class="custom-select" :value="term" @change="handleTermChange">
              <option v-for="item in AVAILABLE_TERMS" :key="item" :value="item">{{ item }}</option>
            </select>
            <span class="custom-select-arrow">▾</span>
          </label>
          <label class="custom-select-wrap" aria-label="风险等级筛选">
            <select v-model="draftFilters.riskLevel" class="custom-select">
              <option value="">全部风险等级</option>
              <option value="高风险">高风险</option>
              <option value="较高风险">较高风险</option>
              <option value="一般风险">一般风险</option>
              <option value="低风险">低风险</option>
            </select>
            <span class="custom-select-arrow">▾</span>
          </label>
          <label class="custom-select-wrap" aria-label="变化方向筛选">
            <select v-model="draftFilters.riskChangeDirection" class="custom-select">
              <option value="">全部变化方向</option>
              <option value="rising">上升</option>
              <option value="steady">持平</option>
              <option value="falling">下降</option>
            </select>
            <span class="custom-select-arrow">▾</span>
          </label>
          <label class="custom-select-wrap" aria-label="群体筛选">
            <select v-model="draftFilters.groupSegment" class="custom-select">
              <option value="">全部群体标签</option>
              <option v-for="item in groupOptions" :key="item" :value="item">{{ item }}</option>
            </select>
            <span class="custom-select-arrow">▾</span>
          </label>
          <input v-model="draftFilters.majorName" class="search-input" placeholder="按专业名称筛选" />
          <button class="btn" type="button" @click="applyFilters">应用筛选</button>
        </div>
      </div>
    </section>

    <ErrorState v-if="query.error.value && !query.isLoading.value" title="预警加载失败" :description="errorMessage" @retry="query.refetch()" />
    <EmptyState
      v-else-if="!query.isLoading.value && items.length === 0"
      title="当前筛选下没有预警学生"
      description="可切换学期或放宽筛选条件后重试。"
    />

    <section v-else class="panel">
      <div class="panel-inner stack table-shell">
        <div class="table-meta">
          <span class="tag cool">{{ term }}</span>
          <span class="tag">{{ query.isLoading.value ? '加载中...' : `共 ${total} 条` }}</span>
        </div>

        <div class="table">
          <div class="table-row header">
            <span>学号</span>
            <span>姓名</span>
            <span>专业</span>
            <span>群体标签</span>
            <span>风险等级</span>
            <span>风险详情</span>
            <span>风险因素</span>
          </div>

          <template v-if="query.isLoading.value">
            <div v-for="index in 5" :key="`skeleton-${index}`" class="table-row skeleton-row">
              <span class="skeleton-block"></span>
              <span class="skeleton-block"></span>
              <span class="skeleton-block"></span>
              <span class="skeleton-block"></span>
              <span class="skeleton-block"></span>
              <span class="skeleton-block"></span>
              <span class="skeleton-block"></span>
            </div>
          </template>

          <RouterLink
            v-else
            v-for="item in items"
            :key="`${item.student_id}-${item.major_name}`"
            class="table-row"
            :to="buildStudentLink(item.student_id)"
          >
            <span>{{ item.student_id }}</span>
            <span>{{ item.student_name }}</span>
            <span>{{ item.major_name }}</span>
            <span>{{ item.group_segment }}</span>
            <span>
              <strong :class="warningLevelClass(item.intervention_priority_level ?? item.risk_level)">
                {{ formatWarningLevel(item.intervention_priority_level ?? item.risk_level) }}
              </strong>
              <small class="risk-direction">{{ riskChangeText(item.risk_change_direction) }}</small>
            </span>
            <span class="stack compact">
              <strong>干预 {{ formatWarningLevel(item.intervention_priority_level ?? item.risk_level) }}</strong>
              <small>学业 {{ formatWarningLevel(item.academic_risk_level ?? item.risk_level) }}</small>
              <small>行为 {{ formatWarningLevel(item.behavior_risk_level ?? item.risk_level) }}</small>
            </span>
            <span class="factor-cell">
              <small>优先分 {{ formatScore(item.intervention_priority_score ?? item.adjusted_risk_score ?? item.risk_probability * 100) }}</small>
              <small>风险 {{ factorText(item.top_risk_factors) }}</small>
              <small>保护 {{ factorText(item.top_protective_factors) }}</small>
            </span>
          </RouterLink>
        </div>

        <div v-if="!query.isLoading.value" class="pagination-bar">
          <button class="btn secondary" type="button" :disabled="page <= 1" @click="page -= 1">上一页</button>
          <div class="page-numbers">
            <button
              v-for="item in visiblePageItems"
              :key="String(item)"
              class="page-num"
              :class="{ active: item === page, ellipsis: item === '...' }"
              :disabled="item === '...'"
              @click="typeof item === 'number' ? (page = item) : undefined"
            >
              {{ item }}
            </button>
          </div>
          <button class="btn secondary" type="button" :disabled="page >= pageCount" @click="page += 1">下一页</button>
        </div>
      </div>
    </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { AVAILABLE_TERMS, useTermStore } from '@/app/term'
import EmptyState from '@/components/state/EmptyState.vue'
import ErrorState from '@/components/state/ErrorState.vue'
import { getWarnings } from '@/lib/api'
import { formatApiErrorMessage, formatRisk } from '@/lib/format'
import type { RiskChangeDirection, RiskLevel, WarningFactor } from '@/lib/types'
import {
  buildWarningContextQuery,
  buildWarningQuery,
  formatWarningLevelLabel,
  getWarningLevelFilterPlan,
  parseWarningQuery,
} from './query'

const groupOptions = ['学习投入稳定组', '综合发展优势组', '作息失衡风险组', '课堂参与薄弱组']
const route = useRoute()
const router = useRouter()
const termStore = useTermStore()
const initialState = parseWarningQuery(route.query)

termStore.setTerm(initialState.term)

const page = ref(initialState.page)
const pageSize = ref(5)
const draftFilters = reactive({
  riskLevel: initialState.riskLevel,
  riskChangeDirection: initialState.riskChangeDirection,
  groupSegment: initialState.groupSegment,
  majorName: initialState.majorName,
})
const appliedFilters = reactive({
  riskLevel: initialState.riskLevel,
  riskChangeDirection: initialState.riskChangeDirection,
  groupSegment: initialState.groupSegment,
  majorName: initialState.majorName,
})

const query = useQuery({
  queryKey: computed(() => [
    'warnings',
    termStore.term.value,
    page.value,
    pageSize.value,
    appliedFilters.riskLevel,
    appliedFilters.riskChangeDirection,
    appliedFilters.groupSegment,
    appliedFilters.majorName,
  ]),
  queryFn: async () => {
    const levelPlan = getWarningLevelFilterPlan(appliedFilters.riskLevel)
    return getWarnings({
      term: termStore.term.value,
      page: page.value,
      page_size: pageSize.value,
      risk_level: levelPlan.apiRiskLevel,
      risk_change_direction: appliedFilters.riskChangeDirection || null,
      group_segment: appliedFilters.groupSegment || null,
      major_name: appliedFilters.majorName || null,
    })
  },
})

watch(
  () => termStore.term.value,
  () => {
    page.value = 1
  },
)

watch(
  () => query.data.value?.page,
  (nextPage) => {
    if (typeof nextPage === 'number' && nextPage > 0 && nextPage !== page.value) {
      page.value = nextPage
    }
  },
)

watch(
  () => [
    termStore.term.value,
    page.value,
    appliedFilters.riskLevel,
    appliedFilters.riskChangeDirection,
    appliedFilters.groupSegment,
    appliedFilters.majorName,
  ],
  () => {
    router.replace({
      path: '/warnings',
      query: buildWarningQuery({
        term: termStore.term.value,
        page: page.value,
        riskLevel: appliedFilters.riskLevel,
        riskChangeDirection: appliedFilters.riskChangeDirection,
        groupSegment: appliedFilters.groupSegment,
        majorName: appliedFilters.majorName,
      }),
    })
  },
)

const term = computed(() => termStore.term.value)
const items = computed(() => query.data.value?.items ?? [])
const total = computed(() => query.data.value?.total ?? 0)
const pageCount = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))
const errorMessage = computed(() => formatApiErrorMessage(query.error.value, '当前预警数据暂不可用，请稍后重试'))
const visiblePageItems = computed<Array<number | '...'>>(() => {
  const totalPages = pageCount.value
  const current = page.value
  if (totalPages <= 7) return Array.from({ length: totalPages }, (_, index) => index + 1)
  if (current <= 4) return [1, 2, 3, 4, 5, '...', totalPages]
  if (current >= totalPages - 3) return [1, '...', totalPages - 4, totalPages - 3, totalPages - 2, totalPages - 1, totalPages]
  return [1, '...', current - 1, current, current + 1, '...', totalPages]
})

function applyFilters() {
  page.value = 1
  appliedFilters.riskLevel = draftFilters.riskLevel
  appliedFilters.riskChangeDirection = draftFilters.riskChangeDirection
  appliedFilters.groupSegment = draftFilters.groupSegment
  appliedFilters.majorName = draftFilters.majorName.trim()
}

function setTerm(nextTerm: string) {
  termStore.setTerm(nextTerm)
}

function handleTermChange(event: Event) {
  setTerm((event.target as HTMLSelectElement).value)
}

function buildStudentLink(studentId: string) {
  return {
    path: `/students/${studentId}`,
    query: buildWarningContextQuery({
      term: termStore.term.value,
      page: page.value,
      riskLevel: appliedFilters.riskLevel,
      riskChangeDirection: appliedFilters.riskChangeDirection,
      groupSegment: appliedFilters.groupSegment,
      majorName: appliedFilters.majorName,
    }),
  }
}

function formatWarningLevel(level: RiskLevel) {
  return formatWarningLevelLabel(level)
}

function warningLevelClass(level: RiskLevel) {
  if (level === 'high' || level === '高风险') return 'is-high'
  if (level === '较高风险') return 'is-elevated'
  if (level === 'medium' || level === '一般风险') return 'is-medium'
  return 'is-low'
}

function riskChangeText(direction?: RiskChangeDirection) {
  if (direction === 'rising') return '上升'
  if (direction === 'steady') return '持平'
  if (direction === 'falling') return '下降'
  return '未更新'
}

function formatScore(value: number) {
  return value.toFixed(1)
}

function factorText(factors: WarningFactor[]) {
  const labels = factors.map((item) => item.feature_cn || item.dimension || item.feature).filter(Boolean)
  return labels.length > 0 ? labels.slice(0, 3).join('、') : '暂无'
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
  background: rgba(226, 67, 91, 0.1);
  color: #c7324b;
  border: 1px solid rgba(226, 67, 91, 0.14);
  flex: 0 0 auto;
}

.title-icon svg {
  width: 22px;
  height: 22px;
}

.filters {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(6, minmax(0, 1fr));
}

.filter-panel {
  margin-bottom: 10px;
}

.custom-select-wrap {
  position: relative;
  display: block;
}

.custom-select {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  width: 100%;
  min-height: 48px;
  padding: 10px 38px 10px 12px;
  border-radius: 14px;
  border: 1px solid rgba(103, 80, 164, 0.28);
  background: linear-gradient(135deg, rgba(103, 80, 164, 0.08), rgba(255, 255, 255, 0.92));
  color: #382a5f;
  font-weight: 600;
  cursor: pointer;
  transition: all 220ms cubic-bezier(0.2, 0, 0, 1);
}

.custom-select:hover {
  border-color: rgba(103, 80, 164, 0.48);
  box-shadow: 0 8px 18px rgba(103, 80, 164, 0.16);
}

.custom-select:focus {
  outline: none;
  border-color: #6750a4;
  box-shadow: 0 0 0 3px rgba(103, 80, 164, 0.2);
}

.custom-select-arrow {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #6750a4;
  pointer-events: none;
  font-size: 0.95rem;
}

.search-input {
  width: 100%;
  min-height: 48px;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid rgba(103, 80, 164, 0.28);
  background: linear-gradient(135deg, rgba(103, 80, 164, 0.08), rgba(255, 255, 255, 0.92));
  color: #382a5f;
  font-weight: 500;
  transition: all 220ms cubic-bezier(0.2, 0, 0, 1);
}

.search-input::placeholder {
  color: rgba(56, 42, 95, 0.6);
}

.search-input:hover {
  border-color: rgba(103, 80, 164, 0.48);
  box-shadow: 0 8px 18px rgba(103, 80, 164, 0.14);
}

.search-input:focus {
  outline: none;
  border-color: #6750a4;
  box-shadow: 0 0 0 3px rgba(103, 80, 164, 0.2);
}

.table-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.table {
  display: grid;
  gap: 10px;
}

.table-shell {
  min-height: 520px;
}

.table-row {
  display: grid;
  gap: 12px;
  grid-template-columns: 1fr 0.9fr 1.1fr 1fr 0.9fr 1.1fr 1.4fr;
  padding: 14px 16px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(28, 34, 56, 0.08);
}

.table-row.header {
  background: transparent;
  border: 0;
  color: var(--muted);
  padding-bottom: 0;
}

.skeleton-row {
  pointer-events: none;
}

.skeleton-block {
  display: block;
  width: 100%;
  height: 14px;
  border-radius: 8px;
  background: linear-gradient(90deg, rgba(228, 223, 238, 0.6), rgba(244, 240, 250, 0.9), rgba(228, 223, 238, 0.6));
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite linear;
}

.compact {
  gap: 4px;
}

.is-high {
  color: #dc2626;
}

.is-elevated {
  color: #ea580c;
}

.is-medium {
  color: #ca8a04;
}

.is-low {
  color: #16a34a;
}

.risk-direction {
  display: block;
  margin-top: 4px;
  color: var(--muted);
}

.factor-cell {
  display: grid;
  gap: 4px;
}

.pagination-bar {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  margin-top: 8px;
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
  transition: all 200ms cubic-bezier(0.2, 0, 0, 1);
}

.page-num:hover:not(:disabled) {
  border-color: rgba(103, 80, 164, 0.5);
  transform: translateY(-1px);
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
  cursor: default;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

@media (max-width: 960px) {
  .filters,
  .table-row {
    grid-template-columns: 1fr;
  }
}
</style>
