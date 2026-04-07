<template>
  <div class="main-particles-layer" aria-hidden="true">
    <div :id="containerId" class="main-particles-mount"></div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted } from 'vue'
import { tsParticles, type Container } from '@tsparticles/engine'
import { loadSlim } from '@tsparticles/slim'

const containerId = `main-particles-${Math.random().toString(36).slice(2, 10)}`
let container: Container | undefined
let refreshTimer: ReturnType<typeof setTimeout> | undefined

function syncParticleLayout() {
  if (!container) return

  void nextTick(() => {
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        void container?.refresh()
      })
    })
  })
}

function handleWindowLayoutChange() {
  syncParticleLayout()
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
          value: 88,
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
          type: ['circle', 'star'],
        },
        size: {
          value: { min: 1.2, max: 3.2 },
          animation: {
            enable: true,
            speed: 0.55,
            sync: false,
          },
        },
        opacity: {
          value: { min: 0.28, max: 0.64 },
          animation: {
            enable: true,
            speed: 0.52,
            sync: false,
          },
        },
        move: {
          enable: true,
          direction: 'none',
          random: true,
          straight: false,
          speed: { min: 0.12, max: 0.34 },
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
  window.removeEventListener('resize', handleWindowLayoutChange)
  window.removeEventListener('load', handleWindowLayoutChange)
  container?.destroy()
})
</script>
