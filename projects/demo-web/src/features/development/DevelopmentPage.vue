<template>
  <section class="panel">
    <div class="panel-inner stack">
      <p class="eyebrow">发展方向与去向关联分析</p>
      <h2 class="title">专业差异与群体方向视角</h2>
      <p class="muted">{{ introductionText }}</p>
    </div>
  </section>

  <LoadingState v-if="developmentQuery.isLoading.value" label="正在加载发展方向分析..." />
  <ErrorState
    v-else-if="hasError"
    title="发展方向分析加载失败"
    :description="errorMessage"
    @retry="retry"
  />
  <EmptyState
    v-else-if="!hasRenderableContent"
    title="当前学期暂无发展方向分析结果"
    description="请切换到有真实专业和群体对比数据的学期后重试。"
  />
  <template v-else>
    <section class="development-grid">
      <article class="panel">
        <div class="panel-inner stack">
          <h3>毕业去向分布</h3>
          <div v-if="destinationDistributionRows.length === 0" class="muted">
            当前学期暂无真实毕业去向分布，将继续展示专业与群体方向分析。
          </div>
          <div v-for="item in destinationDistributionRows" :key="item.label" class="destination-row">
            <div>
              <strong>{{ item.label }}</strong>
              <div class="muted">{{ item.count }} 人</div>
            </div>
            <div class="stack compact align-end">
              <strong>{{ formatDestinationRatio(item.count, matchedDestinationTotal) }}</strong>
              <span class="muted">占已匹配去向学生</span>
            </div>
          </div>
        </div>
      </article>

      <article class="panel">
        <div class="panel-inner stack">
          <h3>专业去向对比</h3>
          <div v-if="majorDestinationRows.length === 0 && majorRows.length === 0" class="muted">
            暂无专业去向或专业对比数据
          </div>
          <template v-if="majorDestinationRows.length > 0">
            <div v-for="row in majorDestinationRows" :key="row.major_name" class="major-row">
              <div>
                <strong>{{ row.major_name }}</strong>
                <div class="muted">{{ row.student_count }} 人 · 去向学生 {{ row.destination_student_count }} 人</div>
              </div>
              <div class="stack compact align-end">
                <strong>主去向 {{ row.top_destination_label ?? '待补充' }}</strong>
                <span class="muted">{{ summarizeDestinationDistribution(row.destination_distribution) }}</span>
                <span v-if="summarizeMajorRiskContext(row.major_name)" class="muted">
                  {{ summarizeMajorRiskContext(row.major_name) }}
                </span>
              </div>
            </div>
          </template>
          <template v-else>
            <div v-for="row in majorRows" :key="row.major_name" class="major-row">
              <div>
                <strong>{{ row.major_name }}</strong>
                <div class="muted">{{ row.student_count }} 人</div>
              </div>
              <div class="stack compact align-end">
                <strong>较高风险以上 {{ row.elevated_risk_count ?? row.high_risk_count }}</strong>
                <span class="muted">
                  占比
                  {{
                    formatMajorRiskRatio(
                      row.elevated_risk_ratio,
                      row.elevated_risk_count ?? row.high_risk_count,
                      row.student_count,
                    )
                  }}
                </span>
              </div>
            </div>
          </template>
        </div>
      </article>
    </section>

    <section class="development-grid">
      <article class="panel">
        <div class="panel-inner stack">
          <h3>群体去向关联</h3>
          <div v-if="destinationAssociations.length === 0 && groups.length === 0" class="muted">暂无群体方向数据</div>
          <template v-if="destinationAssociations.length > 0">
            <div v-for="association in destinationAssociations" :key="association.group_segment" class="group-row">
              <div>
                <strong>{{ association.group_segment }}</strong>
                <div class="muted">
                  {{ association.student_count }} 人
                  <span v-if="typeof association.group_student_count === 'number'">
                    · 群体总数 {{ association.group_student_count }} 人
                  </span>
                </div>
              </div>
              <div class="stack compact align-end">
                <strong>{{ association.destination_label ?? '待补充' }}</strong>
                <span class="muted">组内占比 {{ formatRatio(association.share_within_group) }}</span>
                <span v-if="summarizeLegacyGroupContext(association.group_segment)" class="muted">
                  {{ summarizeLegacyGroupContext(association.group_segment) }}
                </span>
              </div>
            </div>
          </template>
          <template v-else>
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
          </template>
        </div>
      </article>

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
              方向标签由 {{ chain.leading_protective_factor ?? '保护性因素待补充' }}、
              {{ chain.leading_dimension ?? '维度支撑待补充' }} 与平均风险分
              {{ typeof chain.avg_risk_score === 'number' ? chain.avg_risk_score.toFixed(1) : '待补充' }}
              共同支撑。
            </p>
          </div>
        </div>
      </article>

      <article class="panel">
        <div class="panel-inner stack">
          <h3>当前口径说明</h3>
          <div class="note-card">
            <strong>{{ disclaimer }}</strong>
            <p class="muted">{{ disclaimerDetail }}</p>
          </div>
        </div>
      </article>
    </section>
  </template>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'

import { useTermStore } from '@/app/term'
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
const destinationDistributionRows = computed(() =>
  Object.entries(developmentQuery.data.value?.destination_distribution ?? {})
    .map(([label, count]) => ({ label, count }))
    .sort((left, right) => right.count - left.count)
    .slice(0, 6),
)
const majorDestinationRows = computed(() => (developmentQuery.data.value?.major_destination_summary ?? []).slice(0, 6))
const destinationAssociations = computed(() => (developmentQuery.data.value?.group_destination_association ?? []).slice(0, 6))
const dimensionRows = computed(() => (developmentQuery.data.value?.dimension_highlights ?? []).slice(0, 4))
const groups = computed(() => (developmentQuery.data.value?.group_direction_segments ?? []).slice(0, 4))
const directionChains = computed(() => (developmentQuery.data.value?.direction_chains ?? []).slice(0, 4))
const disclaimer = computed(() => developmentQuery.data.value?.disclaimer ?? '去向真值暂未接入')
const matchedDestinationTotal = computed(() =>
  destinationDistributionRows.value.reduce((total, item) => total + item.count, 0),
)
const hasRealDestinationData = computed(
  () =>
    destinationDistributionRows.value.length > 0 ||
    majorDestinationRows.value.length > 0 ||
    destinationAssociations.value.length > 0,
)
const hasRenderableContent = computed(
  () =>
    hasRealDestinationData.value ||
    majorRows.value.length > 0 ||
    groups.value.length > 0 ||
    dimensionRows.value.length > 0 ||
    directionChains.value.length > 0,
)
const introductionText = computed(() =>
  hasRealDestinationData.value
    ? '当前页面优先展示真实毕业去向分布、专业去向差异与群体去向关联；若所选学期暂无真值数据，则自动回退到方向关联视角。'
    : '当前页面基于专业、群体与八维特征进行发展方向关联分析。由于暂未接入毕业去向真值，这里展示的是方向关联视角，不是最终去向结论。',
)
const disclaimerDetail = computed(() =>
  hasRealDestinationData.value
    ? '当前系统已优先使用真实毕业去向数据进行分析，同时保留专业风险、群体标签与八维表现作为解释补充；若未命中真实去向数据，则仍回退到方向关联视角。'
    : '当前系统使用专业对比、群体标签、保护性因素与八维表现来呈现“发展方向关联分析”。后续如果接入升学、就业、出国等真值表，可以在此页升级成真实去向关联分析。',
)
const hasError = computed(() => Boolean(developmentQuery.error.value))
const errorMessage = computed(() =>
  formatApiErrorMessage(developmentQuery.error.value, '当前发展方向分析数据暂不可用，请稍后重试'),
)
const legacyMajorByName = computed(() => new Map(majorRows.value.map((row) => [row.major_name, row])))
const legacyGroupByName = computed(() => new Map(groups.value.map((group) => [group.group_segment, group])))

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

function summarizeDestinationDistribution(distribution: DevelopmentAnalysisData['destination_distribution']) {
  const summary = Object.entries(distribution)
    .sort((left, right) => right[1] - left[1])
    .map(([label, count]) => `${label} ${count}`)
  return summary.length > 0 ? summary.join(' · ') : '暂无去向分布'
}

function summarizeMajorRiskContext(majorName: string) {
  const row = legacyMajorByName.value.get(majorName)
  if (!row) return ''
  return `较高风险占比 ${formatMajorRiskRatio(
    row.elevated_risk_ratio,
    row.elevated_risk_count ?? row.high_risk_count,
    row.student_count,
  )}`
}

function summarizeLegacyGroupContext(groupSegment: string) {
  const group = legacyGroupByName.value.get(groupSegment)
  if (!group) return ''
  return `${summarizeGroupDirection(group)} · ${summarizeGroupSignal(group)}`
}

function formatMajorRiskRatio(ratio?: number, count?: number, total?: number) {
  if (typeof ratio === 'number') return `${(ratio * 100).toFixed(1)}%`
  if (typeof count === 'number' && typeof total === 'number' && total > 0) {
    return `${((count / total) * 100).toFixed(1)}%`
  }
  return '--'
}

function formatDestinationRatio(count: number, total: number) {
  if (total <= 0) return '--'
  return `${((count / total) * 100).toFixed(1)}%`
}

function formatRatio(value?: number) {
  if (typeof value !== 'number') return '--'
  return `${(value * 100).toFixed(1)}%`
}
</script>

<style scoped>
.development-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.destination-row,
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
