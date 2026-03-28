<template>
  <AppShell>
    <section class="panel">
      <div class="panel-inner stack">
        <p class="eyebrow">群体分层</p>
        <h2 class="title">四象限画像</h2>
        <p class="muted">用象限和主导因子描述当前学期的群体结构。</p>
      </div>
    </section>

    <LoadingState v-if="query.isLoading.value" label="正在加载四象限..." />
    <ErrorState v-else-if="query.error.value" title="群体分层加载失败" :description="query.error.value.message" @retry="query.refetch()" />
    <section v-else class="quad-grid">
      <article v-for="item in quadrants" :key="item.quadrant_label" class="panel quad-card">
        <div class="panel-inner stack">
          <div class="quad-head">
            <h3>{{ item.quadrant_label }}</h3>
            <span class="tag">{{ item.student_count }} 人</span>
          </div>
          <div class="quad-metric">
            <span class="muted">平均风险概率</span>
            <strong>{{ item.avg_risk_probability.toFixed(2) }}</strong>
          </div>
          <div class="stack">
            <p class="muted">主导因子</p>
            <div v-for="factor in item.top_factors" :key="factor.dimension" class="factor-row">
              <strong>{{ factor.dimension }}</strong>
              <span class="muted">{{ factor.explanation }}</span>
            </div>
          </div>
        </div>
      </article>
    </section>
  </AppShell>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'

import AppShell from '@/components/layout/AppShell.vue'
import LoadingState from '@/components/state/LoadingState.vue'
import ErrorState from '@/components/state/ErrorState.vue'
import { getQuadrants } from '@/lib/api'
import { useTermStore } from '@/app/term'

const termStore = useTermStore()
const query = useQuery({
  queryKey: computed(() => ['quadrants', termStore.term.value]),
  queryFn: () => getQuadrants(termStore.term.value),
})

const quadrants = computed(() => query.data.value?.quadrants ?? [])
</script>

<style scoped>
.quad-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.quad-card {
  min-height: 280px;
}

.quad-head,
.quad-metric {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.factor-row {
  display: grid;
  gap: 6px;
  padding: 12px 0;
  border-top: 1px solid rgba(28, 34, 56, 0.08);
}

@media (max-width: 960px) {
  .quad-grid {
    grid-template-columns: 1fr;
  }
}
</style>
