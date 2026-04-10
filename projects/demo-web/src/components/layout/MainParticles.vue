<template>
  <div class="main-particles-layer" aria-hidden="true">
    <div :id="containerId" class="main-particles-mount"></div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted } from 'vue'
import { tsParticles, type Container } from '@tsparticles/engine'
import { loadSlim } from '@tsparticles/slim'

import { readMotionBudget } from '@/lib/motionBudget'

const containerId = `main-particles-${Math.random().toString(36).slice(2, 10)}`
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
          value: motionBudget.lite ? 40 : 56,
          density: {
            enable: true,
            width: 1200,
            height: 780,
          },
        },
        color: {
          value: ['#8a59cf', '#7442bf', '#5b2ea3'],
        },
        shape: {
          type: motionBudget.lite ? 'circle' : ['circle', 'star'],
        },
        size: {
          value: motionBudget.lite ? { min: 1.1, max: 2.3 } : { min: 1.2, max: 2.8 },
        },
        opacity: {
          value: motionBudget.lite ? { min: 0.16, max: 0.34 } : { min: 0.2, max: 0.42 },
        },
        move: {
          enable: true,
          direction: 'none',
          random: true,
          straight: false,
          speed: motionBudget.lite ? { min: 0.06, max: 0.18 } : { min: 0.08, max: 0.22 },
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
