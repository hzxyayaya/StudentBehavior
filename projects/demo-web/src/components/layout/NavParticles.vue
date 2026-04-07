<template>
  <div class="nav-particles-layer" aria-hidden="true">
    <div :id="containerId" class="nav-particles-mount"></div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted } from 'vue'
import { tsParticles, type Container } from '@tsparticles/engine'
import { loadSlim } from '@tsparticles/slim'

const containerId = `nav-particles-${Math.random().toString(36).slice(2, 10)}`
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
          value: 42,
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
          distance: 108,
          color: '#f1ddff',
          opacity: 0.42,
          width: 1.35,
          triangles: {
            enable: true,
            opacity: 0.16,
            color: '#e8d2ff',
          },
        },
        move: {
          enable: true,
          direction: 'none',
          random: true,
          straight: false,
          speed: 1.2,
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
  window.removeEventListener('resize', handleWindowLayoutChange)
  window.removeEventListener('load', handleWindowLayoutChange)
  container?.destroy()
})
</script>
