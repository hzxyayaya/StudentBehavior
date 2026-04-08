<template>
  <div class="nav-particles-layer" aria-hidden="true">
    <div :id="containerId" class="nav-particles-mount"></div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted } from 'vue'
import { tsParticles, type Container } from '@tsparticles/engine'
import { loadSlim } from '@tsparticles/slim'

import { readMotionBudget } from '@/lib/motionBudget'

const containerId = `nav-particles-${Math.random().toString(36).slice(2, 10)}`
let container: Container | undefined
let refreshTimer: ReturnType<typeof setTimeout> | undefined
let refreshFrameId = 0

function syncParticleLayout() {
  if (!container) return

  void nextTick(() => {
    if (refreshFrameId) window.cancelAnimationFrame(refreshFrameId)

    refreshFrameId = window.requestAnimationFrame(() => {
      refreshFrameId = 0
      void container?.refresh()
    })
  })
}

function handleWindowLayoutChange() {
  if (refreshTimer) clearTimeout(refreshTimer)
  refreshTimer = setTimeout(() => {
    refreshTimer = undefined
    syncParticleLayout()
  }, 96)
}

onMounted(async () => {
  const motionBudget = readMotionBudget()

  await loadSlim(tsParticles)

  container = await tsParticles.load({
    id: containerId,
    options: {
      fullScreen: { enable: false },
      detectRetina: motionBudget.particleDetectRetina,
      fpsLimit: motionBudget.particleFpsLimit,
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
          value: motionBudget.lite ? 22 : 30,
          density: {
            enable: true,
            width: 320,
            height: 900,
          },
        },
        color: {
          value: ['#f8f1ff', '#ead8ff', '#cfb0ff'],
        },
        shape: {
          type: 'circle',
        },
        size: {
          value: { min: 1.8, max: 3.6 },
        },
        opacity: {
          value: { min: 0.42, max: 0.78 },
        },
        links: {
          enable: true,
          distance: motionBudget.lite ? 88 : 98,
          color: '#f1ddff',
          opacity: motionBudget.lite ? 0.24 : 0.32,
          width: motionBudget.lite ? 0.9 : 1.1,
          triangles: {
            enable: true,
            opacity: motionBudget.lite ? 0.08 : 0.12,
            color: '#e8d2ff',
          },
        },
        move: {
          enable: true,
          direction: 'none',
          random: true,
          straight: false,
          speed: motionBudget.lite ? 0.7 : 0.9,
          outModes: {
            default: 'bounce',
          },
        },
      },
      pauseOnBlur: true,
      pauseOnOutsideViewport: true,
    },
  })

  syncParticleLayout()
  refreshTimer = setTimeout(() => {
    syncParticleLayout()
  }, 180)

  window.addEventListener('resize', handleWindowLayoutChange)
  window.addEventListener('load', handleWindowLayoutChange)
})

onBeforeUnmount(() => {
  if (refreshTimer) clearTimeout(refreshTimer)
  if (refreshFrameId) window.cancelAnimationFrame(refreshFrameId)
  window.removeEventListener('resize', handleWindowLayoutChange)
  window.removeEventListener('load', handleWindowLayoutChange)
  container?.destroy()
})
</script>
