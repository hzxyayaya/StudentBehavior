<template>
  <AppShell>
    <section class="panel">
      <div class="panel-inner stack">
        <p class="eyebrow">风险预警</p>
        <h2 class="title">预警列表</h2>
        <div class="filters">
          <select v-model="filters.riskLevel" class="select">
            <option value="">全部风险等级</option>
            <option value="high">high</option>
            <option value="medium">medium</option>
            <option value="low">low</option>
          </select>
          <select v-model="filters.quadrantLabel" class="select">
            <option value="">全部象限</option>
            <option value="自律共鸣型">自律共鸣型</option>
            <option value="被动守纪型">被动守纪型</option>
            <option value="脱节离散型">脱节离散型</option>
            <option value="情绪驱动型">情绪驱动型</option>
          </select>
          <input v-model="filters.majorName" class="field" placeholder="专业名称" />
          <button class="btn" type="button" @click="refresh">筛选</button>
        </div>
      </div>
    </section>

    <LoadingState v-if="query.isLoading.value" label="正在加载预警..." />
    <ErrorState v-else-if="query.error.value" title="预警加载失败" :description="query.error.value.message" @retry="query.refetch()" />
    <section v-else class="panel">
      <div class="panel-inner stack">
        <div class="table-meta">
          <span class="tag">{{ paginationText }}</span>
          <button class="btn secondary" type="button" :disabled="page <= 1" @click="page -= 1">上一页</button>
          <button class="btn secondary" type="button" :disabled="page * pageSize >= total" @click="page += 1">下一页</button>
        </div>
        <div class="table">
          <div class="table-row header">
            <span>学号</span>
            <span>姓名</span>
            <span>专业</span>
            <span>象限</span>
            <span>风险</span>
            <span>概率</span>
          </div>
          <RouterLink
            v-for="item in items"
            :key="`${item.student_id}-${item.major_name}`"
            class="table-row"
            :to="`/students/${item.student_id}?term=${term}`"
          >
            <span>{{ item.student_id }}</span>
            <span>{{ item.student_name }}</span>
            <span>{{ item.major_name }}</span>
            <span>{{ item.quadrant_label }}</span>
            <span>{{ item.risk_level }}</span>
            <span>{{ item.risk_probability.toFixed(2) }}</span>
          </RouterLink>
        </div>
      </div>
    </section>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { RouterLink } from 'vue-router'

import AppShell from '@/components/layout/AppShell.vue'
import LoadingState from '@/components/state/LoadingState.vue'
import ErrorState from '@/components/state/ErrorState.vue'
import { getWarnings } from '@/lib/api'
import { useTermStore } from '@/app/term'

const termStore = useTermStore()
const term = termStore.term
const page = ref(1)
const pageSize = ref(20)
const filters = reactive({ riskLevel: '', quadrantLabel: '', majorName: '' })

const query = useQuery({
  queryKey: computed(() => ['warnings', term.value, page.value, pageSize.value, filters.riskLevel, filters.quadrantLabel, filters.majorName]),
  queryFn: () =>
    getWarnings({
      term: term.value,
      page: page.value,
      page_size: pageSize.value,
      risk_level: filters.riskLevel || null,
      quadrant_label: filters.quadrantLabel || null,
      major_name: filters.majorName || null,
    }),
})

watch(term, () => {
  page.value = 1
  query.refetch()
})

const items = computed(() => query.data.value?.items ?? [])
const total = computed(() => query.data.value?.total ?? 0)
const paginationText = computed(() => `${page.value} / ${Math.max(1, Math.ceil(total.value / pageSize.value))} 页，${total.value} 条`)

function refresh() {
  page.value = 1
  query.refetch()
}
</script>

<style scoped>
.filters {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
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
  grid-template-columns: 1.1fr 1fr 1.2fr 1fr 0.7fr 0.7fr;
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
