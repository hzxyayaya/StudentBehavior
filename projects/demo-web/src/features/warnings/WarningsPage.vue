<template>
  <AppShell>
    <section class="panel">
      <div class="panel-inner stack">
        <p class="eyebrow">风险预警</p>
        <h2 class="title">预警列表</h2>
        <p class="muted">按真实联调学期筛选中高风险学生，并支持继续下钻到学生个体页。</p>
        <div class="filters">
          <select :value="term" class="select" @change="handleTermChange">
            <option v-for="item in AVAILABLE_TERMS" :key="item" :value="item">{{ item }}</option>
          </select>
          <select v-model="draftFilters.riskLevel" class="select">
            <option value="">全部风险等级</option>
            <option value="high">高风险</option>
            <option value="medium">中风险</option>
            <option value="low">低风险</option>
          </select>
          <select v-model="draftFilters.groupSegment" class="select">
            <option value="">全部群体标签</option>
            <option v-for="item in groupOptions" :key="item" :value="item">{{ item }}</option>
          </select>
          <input v-model="draftFilters.majorName" class="field" placeholder="按专业名称筛选" />
          <button class="btn" type="button" @click="applyFilters">应用筛选</button>
        </div>
      </div>
    </section>

    <LoadingState v-if="query.isLoading.value" label="正在加载预警..." />
    <ErrorState v-else-if="query.error.value" title="预警加载失败" :description="errorMessage" @retry="query.refetch()" />
    <EmptyState
      v-else-if="items.length === 0"
      title="当前筛选下没有预警学生"
      description="可以切换学期、放宽风险等级或清空专业筛选后重试。"
    />
    <section v-else class="panel">
      <div class="panel-inner stack">
        <div class="table-meta">
          <span class="tag cool">{{ term }}</span>
          <span class="tag">{{ paginationText }}</span>
          <button class="btn secondary" type="button" :disabled="page <= 1" @click="page -= 1">上一页</button>
          <button class="btn secondary" type="button" :disabled="page >= pageCount" @click="page += 1">下一页</button>
        </div>
        <div class="table">
          <div class="table-row header">
            <span>学号</span>
            <span>姓名</span>
            <span>专业</span>
            <span>群体标签</span>
            <span>风险等级</span>
            <span>风险概率</span>
          </div>
          <RouterLink
            v-for="item in items"
            :key="`${item.student_id}-${item.major_name}`"
            class="table-row"
            :to="buildStudentLink(item.student_id)"
          >
            <span>{{ item.student_id }}</span>
            <span>{{ item.student_name }}</span>
            <span>{{ item.major_name }}</span>
            <span>{{ item.group_segment }}</span>
            <span>{{ formatRiskLevel(item.risk_level) }}</span>
            <span>{{ formatRisk(item.risk_probability) }}</span>
          </RouterLink>
        </div>
      </div>
    </section>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { AVAILABLE_TERMS, useTermStore } from '@/app/term'
import AppShell from '@/components/layout/AppShell.vue'
import EmptyState from '@/components/state/EmptyState.vue'
import ErrorState from '@/components/state/ErrorState.vue'
import LoadingState from '@/components/state/LoadingState.vue'
import { getWarnings } from '@/lib/api'
import { formatApiErrorMessage, formatRisk, formatRiskLevel } from '@/lib/format'
import { buildWarningContextQuery, buildWarningQuery, parseWarningQuery } from './query'

const groupOptions = ['学习投入稳定组', '综合发展优势组', '作息失衡风险组', '课堂参与薄弱组']

const route = useRoute()
const router = useRouter()
const termStore = useTermStore()
const initialState = parseWarningQuery(route.query)

termStore.setTerm(initialState.term)

const page = ref(initialState.page)
const pageSize = ref(20)
const draftFilters = reactive({
  riskLevel: initialState.riskLevel,
  groupSegment: initialState.groupSegment,
  majorName: initialState.majorName,
})
const appliedFilters = reactive({
  riskLevel: initialState.riskLevel,
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
    appliedFilters.groupSegment,
    appliedFilters.majorName,
  ]),
  queryFn: () =>
    getWarnings({
      term: termStore.term.value,
      page: page.value,
      page_size: pageSize.value,
      risk_level: appliedFilters.riskLevel || null,
      group_segment: appliedFilters.groupSegment || null,
      major_name: appliedFilters.majorName || null,
    }),
})

watch(
  () => termStore.term.value,
  () => {
    page.value = 1
  },
)

watch(
  () => [termStore.term.value, page.value, appliedFilters.riskLevel, appliedFilters.groupSegment, appliedFilters.majorName],
  () => {
    router.replace({
      path: '/warnings',
      query: buildWarningQuery({
        term: termStore.term.value,
        page: page.value,
        riskLevel: appliedFilters.riskLevel,
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
const paginationText = computed(() => `第 ${page.value} / ${pageCount.value} 页，共 ${total.value} 条`)
const errorMessage = computed(() => formatApiErrorMessage(query.error.value, '当前预警数据暂不可用，请稍后重试'))

function applyFilters() {
  page.value = 1
  appliedFilters.riskLevel = draftFilters.riskLevel
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
      groupSegment: appliedFilters.groupSegment,
      majorName: appliedFilters.majorName,
    }),
  }
}
</script>

<style scoped>
.filters {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(5, minmax(0, 1fr));
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

.table-row {
  display: grid;
  gap: 12px;
  grid-template-columns: 1.1fr 1fr 1.2fr 1fr 0.8fr 0.7fr;
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


@media (max-width: 960px) {
  .filters,
  .table-row {
    grid-template-columns: 1fr;
  }
}
</style>
