<template>
  <div class="login-triangles-layer" aria-hidden="true">
    <div :id="containerId" class="login-triangles-mount"></div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted } from 'vue'
import { tsParticles, type Container } from '@tsparticles/engine'
import { loadSlim } from '@tsparticles/slim'

import { readMotionBudget } from '@/lib/motionBudget'

const containerId = `login-triangles-${Math.random().toString(36).slice(2, 10)}`
let container: Container | undefined

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
          value: motionBudget.lite ? 60 : 78,
          density: {
            enable: true,
            width: 1440,
            height: 900,
          },
        },
        color: {
          value: ['#efe7ff', '#d8c5ff', '#b798ff'],
        },
        shape: {
          type: 'polygon',
          options: {
            polygon: {
              sides: 3,
            },
          },
        },
        size: {
          value: { min: 12, max: 30 },
        },
        opacity: {
          value: motionBudget.lite ? { min: 0.08, max: 0.18 } : { min: 0.1, max: 0.22 },
        },
        move: {
          enable: true,
          direction: 'top-right',
          random: true,
          straight: false,
          speed: motionBudget.lite ? { min: 0.05, max: 0.14 } : { min: 0.06, max: 0.18 },
          outModes: {
            default: 'out',
          },
        },
        links: {
          enable: true,
          distance: motionBudget.lite ? 176 : 194,
          color: '#f1e7ff',
          opacity: motionBudget.lite ? 0.14 : 0.18,
          width: motionBudget.lite ? 0.95 : 1.1,
          triangles: {
            enable: true,
            opacity: motionBudget.lite ? 0.06 : 0.08,
            color: '#f4edff',
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

<style scoped>
.login-triangles-layer {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
  opacity: 1;
  filter: saturate(1.12) brightness(1.08);
}

.login-triangles-mount,
.login-triangles-layer > div[id^='login-triangles-'] {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.login-triangles-layer :deep(canvas) {
  display: block;
  width: 100%;
  height: 100%;
}
</style>
