<template>
  <div ref="el" class="chart" :style="{ height }"></div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { BarChart, LineChart, RadarChart } from 'echarts/charts'
import { AxisPointerComponent, GridComponent, LegendComponent, RadarComponent, TooltipComponent } from 'echarts/components'
import { init, use } from 'echarts/core'
import type { EChartsType } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import type { EChartsOption } from 'echarts'

use([BarChart, LineChart, RadarChart, AxisPointerComponent, GridComponent, LegendComponent, RadarComponent, TooltipComponent, CanvasRenderer])

const props = defineProps<{
  option: EChartsOption
  height?: string
}>()

const emit = defineEmits<{
  (event: 'chart-click', params: unknown): void
}>()

const el = ref<HTMLDivElement | null>(null)
let chart: EChartsType | null = null

function render() {
  if (!chart) return
  chart.setOption(props.option, true)
}

function resize() {
  chart?.resize()
}

onMounted(() => {
  if (!el.value) return
  chart = init(el.value)
  chart.on('click', (params) => emit('chart-click', params))
  render()
  window.addEventListener('resize', resize)
})

watch(
  () => props.option,
  () => render(),
  { deep: true },
)

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  chart?.dispose()
  chart = null
})
</script>

<style scoped>
.chart {
  width: 100%;
  min-height: 180px;
}
</style>
