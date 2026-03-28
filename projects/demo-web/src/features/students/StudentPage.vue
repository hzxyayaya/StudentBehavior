<template>
  <AppShell>
    <section class="panel">
      <div class="panel-inner stack">
        <p class="eyebrow">学生个体</p>
        <h2 class="title">{{ studentId }}</h2>
        <p class="muted">当前学期 {{ term }} 的画像、因子和建议。</p>
      </div>
    </section>

    <LoadingState v-if="profileQuery.isLoading.value || reportQuery.isLoading.value" label="正在加载学生画像..." />
    <ErrorState v-else-if="errorMessage" title="学生画像加载失败" :description="errorMessage" @retry="retry" />
    <template v-else-if="profile && report">
      <section class="grid-3">
        <div class="card-kpi panel">
          <div class="muted">风险等级</div>
          <div class="kpi-value">{{ profile.risk_level }}</div>
        </div>
        <div class="card-kpi panel">
          <div class="muted">风险概率</div>
          <div class="kpi-value">{{ profile.risk_probability.toFixed(2) }}</div>
        </div>
        <div class="card-kpi panel">
          <div class="muted">象限</div>
          <div class="kpi-value">{{ profile.quadrant_label }}</div>
        </div>
      </section>

      <section class="grid-2">
        <div class="panel">
          <div class="panel-inner stack">
            <h3>维度评分</h3>
            <div v-for="item in profile.dimension_scores" :key="item.dimension" class="score-row">
              <span>{{ item.dimension }}</span>
              <div class="score-track">
                <div class="score-fill" :style="{ width: `${Math.max(item.score * 100, 10)}%` }" />
              </div>
              <strong>{{ item.score.toFixed(2) }}</strong>
            </div>
          </div>
        </div>

        <div class="panel">
          <div class="panel-inner stack">
            <h3>学期趋势</h3>
            <div v-for="item in profile.trend" :key="item.term" class="score-row">
              <span>{{ item.term }}</span>
              <div class="score-track">
                <div class="score-fill cool" :style="{ width: `${Math.max(item.risk_probability * 100, 10)}%` }" />
              </div>
              <strong>{{ item.risk_probability.toFixed(2) }}</strong>
            </div>
          </div>
        </div>
      </section>

      <section class="grid-2">
        <div class="panel">
          <div class="panel-inner stack">
            <h3>关键影响因子</h3>
            <div v-for="item in report.top_factors" :key="item.dimension" class="factor-card">
              <strong>{{ item.dimension }}</strong>
              <p class="muted">{{ item.explanation }}</p>
              <span class="tag">{{ item.direction }} / {{ item.impact.toFixed(2) }}</span>
            </div>
          </div>
        </div>
        <div class="panel">
          <div class="panel-inner stack">
            <h3>干预建议</h3>
            <ol class="advice-list">
              <li v-for="item in report.intervention_advice" :key="item">{{ item }}</li>
            </ol>
            <div class="panel-inner summary-box">
              <p class="muted">报告摘要</p>
              <strong>{{ report.report_text }}</strong>
            </div>
          </div>
        </div>
      </section>
    </template>
  </AppShell>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useQuery } from '@tanstack/vue-query'

import AppShell from '@/components/layout/AppShell.vue'
import LoadingState from '@/components/state/LoadingState.vue'
import ErrorState from '@/components/state/ErrorState.vue'
import { getStudentProfile, getStudentReport } from '@/lib/api'
import { useTermStore } from '@/app/term'

const route = useRoute()
const termStore = useTermStore()
const studentId = computed(() => String(route.params.studentId ?? ''))
const term = computed(() => String(route.query.term ?? termStore.term.value))

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
const errorMessage = computed(() => profileQuery.error.value?.message || reportQuery.error.value?.message || '')

function retry() {
  profileQuery.refetch()
  reportQuery.refetch()
}
</script>

<style scoped>
.score-row {
  display: grid;
  gap: 10px;
  grid-template-columns: 150px minmax(0, 1fr) auto;
  align-items: center;
}

.score-track {
  height: 12px;
  border-radius: 999px;
  background: rgba(28, 34, 56, 0.08);
  overflow: hidden;
}

.score-fill {
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(135deg, var(--warn), var(--hot));
}

.score-fill.cool {
  background: linear-gradient(135deg, var(--cool), var(--brand));
}

.factor-card {
  padding: 14px 0;
  border-top: 1px solid rgba(28, 34, 56, 0.08);
}

.advice-list {
  margin: 0;
  padding-left: 20px;
}

.summary-box {
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.74);
}

@media (max-width: 960px) {
  .score-row {
    grid-template-columns: 1fr;
  }
}
</style>
