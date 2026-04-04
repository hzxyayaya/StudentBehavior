<template>
  <AppShell>
    <section class="panel">
      <div class="panel-inner stack">
        <p class="eyebrow">发展方向与去向关联分析</p>
        <h2 class="title">专业差异与群体方向视角</h2>
        <p class="muted">当前页面基于专业、群体与八维特征做发展方向关联分析。去向真值暂未接入，因此这里展示的是方向关联视角，不是毕业去向标签真值。</p>
      </div>
    </section>

    <LoadingState v-if="developmentQuery.isLoading.value" label="正在加载发展方向分析..." />
    <ErrorState v-else-if="hasError" title="发展方向分析加载失败" :description="errorMessage" @retry="retry" />
    <EmptyState
      v-else-if="majorRows.length === 0 && groups.length === 0 && dimensionRows.length === 0"
      title="当前学期暂无发展方向分析结果"
      description="请切换到有真实专业和群体对比数据的学期后重试。"
    />
    <template v-else>
      <section class="development-grid">
        <article class="panel">
          <div class="panel-inner stack">
            <h3>专业/学院群体对比</h3>
            <div v-if="majorRows.length === 0" class="muted">暂无专业对比数据</div>
            <div v-for="row in majorRows" :key="row.major_name" class="major-row">
              <div>
                <strong>{{ row.major_name }}</strong>
                <div class="muted">{{ row.student_count }} 人</div>
              </div>
              <strong>高风险 {{ row.high_risk_count }}</strong>
            </div>
          </div>
        </article>

        <article class="panel">
          <div class="panel-inner stack">
            <h3>群体发展方向视角</h3>
            <div v-if="groups.length === 0" class="muted">暂无群体方向数据</div>
            <div v-for="group in groups" :key="group.group_segment" class="group-row">
              <div>
                <strong>{{ group.group_segment }}</strong>
                <div class="muted">{{ group.student_count }} 人</div>
              </div>
              <div class="stack compact align-end">
                <strong>{{ summarizeGroupDirection(group) }}</strong>
                <span class="tag cool">方向标签</span>
                <span class="muted">{{ summarizeGroupSignal(group) }}</span>
              </div>
            </div>
          </div>
        </article>
      </section>

      <section class="development-grid">
        <article class="panel">
          <div class="panel-inner stack">
            <h3>当前学期优势维度</h3>
            <div v-if="dimensionRows.length === 0" class="muted">暂无维度摘要</div>
            <div v-for="item in dimensionRows" :key="item.dimension" class="dimension-row">
              <div>
                <strong>{{ item.dimension }}</strong>
                <div class="muted">{{ item.label ?? '待补充' }}</div>
              </div>
              <strong>{{ displayDimensionScore(item) }}</strong>
            </div>
          </div>
        </article>

        <article class="panel">
          <div class="panel-inner stack">
            <h3>方向解释链路</h3>
            <div v-if="directionChains.length === 0" class="muted">暂无方向解释链路</div>
            <div v-for="chain in directionChains" :key="`${chain.group_segment}-chain`" class="chain-card">
              <strong>{{ chain.group_segment }}</strong>
              <p class="muted">
                方向标签由{{ chain.leading_protective_factor ?? '保护性因素待补充' }}、{{ chain.leading_dimension ?? '维度支撑待补充' }}与平均风险分
                {{ typeof chain.avg_risk_score === 'number' ? chain.avg_risk_score.toFixed(1) : '待补充' }}共同支撑。
              </p>
            </div>
          </div>
        </article>

        <article class="panel">
          <div class="panel-inner stack">
            <h3>当前口径说明</h3>
            <div class="note-card">
              <strong>{{ disclaimer }}</strong>
              <p class="muted">当前系统使用专业对比、群体标签、保护性因素与八维表现来呈现“发展方向关联分析”。后续如果接入升学/就业/出国等真值表，可以在此页升级成真实去向关联分析。</p>
            </div>
          </div>
        </article>
      </section>
    </template>
  </AppShell>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'

import { useTermStore } from '@/app/term'
import AppShell from '@/components/layout/AppShell.vue'
import EmptyState from '@/components/state/EmptyState.vue'
import ErrorState from '@/components/state/ErrorState.vue'
import LoadingState from '@/components/state/LoadingState.vue'
import { getDevelopmentAnalysis } from '@/lib/api'
import { formatApiErrorMessage } from '@/lib/format'
import type { DevelopmentAnalysisData } from '@/lib/types'

const termStore = useTermStore()

const developmentQuery = useQuery({
  queryKey: computed(() => ['development-analysis', termStore.term.value]),
  queryFn: () => getDevelopmentAnalysis(termStore.term.value),
})

const majorRows = computed(() => (developmentQuery.data.value?.major_comparison ?? []).slice(0, 6))
const dimensionRows = computed(() => (developmentQuery.data.value?.dimension_highlights ?? []).slice(0, 4))
const groups = computed(() => (developmentQuery.data.value?.group_direction_segments ?? []).slice(0, 4))
const directionChains = computed(() => (developmentQuery.data.value?.direction_chains ?? []).slice(0, 4))
const disclaimer = computed(() => developmentQuery.data.value?.disclaimer ?? '去向真值暂未接入')
const hasError = computed(() => Boolean(developmentQuery.error.value))
const errorMessage = computed(() =>
  formatApiErrorMessage(developmentQuery.error.value, '当前发展方向分析数据暂不可用，请稍后重试'),
)

function retry() {
  developmentQuery.refetch()
}

function displayDimensionScore(item: { average_score?: number; score?: number }) {
  const value = typeof item.average_score === 'number' ? item.average_score : item.score
  if (typeof value !== 'number') return '待补充'
  return value <= 1 ? `${Math.round(value * 100)}分` : `${Math.round(value)}分`
}

function summarizeGroupDirection(group: DevelopmentAnalysisData['group_direction_segments'][number]) {
  return group.direction_label ?? '方向特征待补充'
}

function summarizeGroupSignal(group: DevelopmentAnalysisData['group_direction_segments'][number]) {
  return `平均风险分 ${group.avg_risk_score.toFixed(1)}`
}
</script>

<style scoped>
.development-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.major-row,
.group-row,
.dimension-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 0;
  border-top: 1px solid rgba(28, 34, 56, 0.08);
}

.chain-card {
  border-top: 1px solid rgba(28, 34, 56, 0.08);
  padding-top: 12px;
}

.compact {
  gap: 4px;
}

.align-end {
  align-items: flex-end;
}

.note-card {
  border-radius: 18px;
  border: 1px solid rgba(28, 34, 56, 0.08);
  padding: 16px;
  background: #fff8f2;
}

@media (max-width: 960px) {
  .development-grid {
    grid-template-columns: 1fr;
  }
}
</style>
