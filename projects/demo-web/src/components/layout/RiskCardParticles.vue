<template>
  <div ref="hostRef" :id="containerId" class="risk-card-particles" aria-hidden="true"></div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { tsParticles, type Container } from '@tsparticles/engine'
import { loadSlim } from '@tsparticles/slim'

import { readMotionBudget } from '@/lib/motionBudget'

const props = defineProps<{
  variant: 'low' | 'medium' | 'higher' | 'high'
}>()

const containerId = `risk-card-particles-${Math.random().toString(36).slice(2, 10)}`
const hostRef = ref<HTMLElement | null>(null)
let container: Container | undefined
let inViewport = true
let viewportObserver: IntersectionObserver | null = null

const paletteMap: Record<'low' | 'medium' | 'higher' | 'high', string[]> = {
  low: ['#166534', '#15803d', '#22c55e'],
  medium: ['#1e40af', '#2563eb', '#60a5fa'],
  higher: ['#9a3412', '#c2410c', '#fb923c'],
  high: ['#9f1239', '#be123c', '#fb7185'],
}

function syncPlayback() {
  if (!container) return

  if (document.visibilityState === 'visible' && inViewport) container.play()
  else container.pause()
}

function handleVisibilityChange() {
  syncPlayback()
}

onMounted(async () => {
  const motionBudget = readMotionBudget()

  await loadSlim(tsParticles)

  container = await tsParticles.load({
    id: containerId,
    options: {
      fullScreen: { enable: false },
      detectRetina: motionBudget.particleDetectRetina,
      fpsLimit: motionBudget.lite ? 24 : 30,
      background: {
        color: 'transparent',
      },
      interactivity: {
        events: {
          onClick: { enable: false, mode: [] },
          onHover: { enable: false, mode: [] },
          resize: { enable: true },
        },
      },
      particles: {
        number: {
          value: motionBudget.lite ? 5 : 8,
          density: {
            enable: true,
            width: 260,
            height: 120,
          },
        },
        color: {
          value: paletteMap[props.variant],
        },
        shape: {
          type: ['square', 'polygon'],
          options: {
            polygon: {
              sides: 6,
            },
          },
        },
        size: {
          value: motionBudget.lite ? { min: 1.8, max: 4 } : { min: 2, max: 4.6 },
        },
        opacity: {
          value: motionBudget.lite ? { min: 0.06, max: 0.14 } : { min: 0.07, max: 0.18 },
        },
        move: {
          enable: true,
          direction: 'none',
          random: true,
          straight: false,
          speed: motionBudget.lite ? { min: 0.03, max: 0.07 } : { min: 0.04, max: 0.1 },
          outModes: {
            default: 'bounce',
          },
        },
        links: {
          enable: false,
        },
      },
      pauseOnBlur: true,
      pauseOnOutsideViewport: true,
    },
  })

  if (typeof IntersectionObserver !== 'undefined') {
    viewportObserver = new IntersectionObserver(
      ([entry]) => {
        inViewport = entry?.isIntersecting ?? true
        syncPlayback()
      },
      { threshold: 0.18 },
    )

    if (hostRef.value) viewportObserver.observe(hostRef.value)
  }
  document.addEventListener('visibilitychange', handleVisibilityChange)
  syncPlayback()
})

onBeforeUnmount(() => {
  document.removeEventListener('visibilitychange', handleVisibilityChange)
  viewportObserver?.disconnect()
  viewportObserver = null
  container?.destroy()
})
</script>
