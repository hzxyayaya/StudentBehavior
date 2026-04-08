<template>
  <div v-if="!isReady" class="chart-placeholder" :style="{ height }" aria-hidden="true"></div>
  <Suspense v-else>
    <AsyncEChart :option="option" :height="height" @chart-click="emit('chart-click', $event)" />
    <template #fallback>
      <div class="chart-placeholder" :style="{ height }" aria-hidden="true"></div>
    </template>
  </Suspense>
</template>

<script setup lang="ts">
import { defineAsyncComponent, onMounted, ref } from 'vue'
import type { EChartsOption } from 'echarts'

withDefaults(
  defineProps<{
    option: EChartsOption
    height?: string
  }>(),
  {
    height: '320px',
  },
)

const emit = defineEmits<{
  (event: 'chart-click', params: unknown): void
}>()

const isReady = ref(false)
const AsyncEChart = defineAsyncComponent(() => import('./EChart.vue'))

onMounted(() => {
  isReady.value = true
})
</script>

<style scoped>
.chart-placeholder {
  width: 100%;
  min-height: 180px;
  border-radius: 16px;
  background:
    linear-gradient(135deg, rgba(103, 80, 164, 0.06), rgba(79, 124, 255, 0.05)),
    linear-gradient(180deg, rgba(255, 255, 255, 0.82), rgba(247, 249, 252, 0.9));
  border: 1px solid rgba(103, 80, 164, 0.08);
}
</style>
