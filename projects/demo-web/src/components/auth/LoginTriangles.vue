<template>
  <div class="login-triangles-layer" aria-hidden="true">
    <div :id="containerId" class="login-triangles-mount"></div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted } from 'vue'
import { tsParticles, type Container } from '@tsparticles/engine'
import { loadSlim } from '@tsparticles/slim'

const containerId = `login-triangles-${Math.random().toString(36).slice(2, 10)}`
let container: Container | undefined

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
          value: 112,
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
          value: { min: 0.12, max: 0.28 },
          animation: {
            enable: true,
            speed: 0.4,
            sync: false,
          },
        },
        rotate: {
          value: { min: 0, max: 360 },
          direction: 'random',
          animation: {
            enable: true,
            speed: 3,
            sync: false,
          },
        },
        move: {
          enable: true,
          direction: 'top-right',
          random: true,
          straight: false,
          speed: { min: 0.08, max: 0.22 },
          outModes: {
            default: 'out',
          },
        },
        links: {
          enable: true,
          distance: 212,
          color: '#f1e7ff',
          opacity: 0.2,
          width: 1.35,
          triangles: {
            enable: true,
            opacity: 0.11,
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
