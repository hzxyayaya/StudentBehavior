<template>
  <div :id="containerId" class="risk-card-particles" aria-hidden="true"></div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted } from 'vue'
import { tsParticles, type Container } from '@tsparticles/engine'
import { loadSlim } from '@tsparticles/slim'

const props = defineProps<{
  variant: 'low' | 'medium' | 'higher' | 'high'
}>()

const containerId = `risk-card-particles-${Math.random().toString(36).slice(2, 10)}`
let container: Container | undefined

const paletteMap: Record<'low' | 'medium' | 'higher' | 'high', string[]> = {
  low: ['#166534', '#15803d', '#22c55e'],
  medium: ['#1e40af', '#2563eb', '#60a5fa'],
  higher: ['#9a3412', '#c2410c', '#fb923c'],
  high: ['#9f1239', '#be123c', '#fb7185'],
}

onMounted(async () => {
  await loadSlim(tsParticles)

  container = await tsParticles.load({
    id: containerId,
    options: {
      fullScreen: { enable: false },
      detectRetina: true,
      fpsLimit: 60,
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
          value: 12,
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
          value: { min: 2.4, max: 5.8 },
          animation: {
            enable: true,
            speed: 0.4,
            sync: false,
          },
        },
        opacity: {
          value: { min: 0.08, max: 0.24 },
          animation: {
            enable: true,
            speed: 0.28,
            sync: false,
          },
        },
        move: {
          enable: true,
          direction: 'none',
          random: true,
          straight: false,
          speed: { min: 0.05, max: 0.16 },
          outModes: {
            default: 'bounce',
          },
        },
        links: {
          enable: false,
        },
        rotate: {
          value: { min: 0, max: 360 },
          direction: 'random',
          animation: {
            enable: true,
            speed: 6,
            sync: false,
          },
        },
      },
      pauseOnBlur: true,
      pauseOnOutsideViewport: true,
    },
  })
})

onBeforeUnmount(() => {
  container?.destroy()
})
</script>
