<template>
  <div ref="hostRef" class="poly-sphere-host" aria-hidden="true"></div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import {
  AmbientLight,
  BufferGeometry,
  Color,
  Float32BufferAttribute,
  Group,
  IcosahedronGeometry,
  LineBasicMaterial,
  LineSegments,
  LineLoop,
  MathUtils,
  Mesh,
  MeshBasicMaterial,
  Object3D,
  PerspectiveCamera,
  Points,
  PointsMaterial,
  Scene,
  WebGLRenderer,
  WireframeGeometry,
} from 'three'

import { getMotionBudget, type MotionBudget, readMotionBudget } from '@/lib/motionBudget'

const hostRef = ref<HTMLElement | null>(null)

let renderer: WebGLRenderer | null = null
let scene: Scene | null = null
let camera: PerspectiveCamera | null = null
let frameId = 0
let animationRunning = false
let lastRenderTime = 0
let resizeObserver: ResizeObserver | null = null
let intersectionObserver: IntersectionObserver | null = null
let sphereGroup: Group | null = null
let fieldGroup: Group | null = null
let motionBudget: MotionBudget = getMotionBudget()
let hostInViewport = true
let targetRotationX = 0.2
let targetRotationY = -0.35
let targetFieldX = 0
let targetFieldY = 0

function buildRing(radius: number, depth: number, color: string, opacity: number, segmentCount: number) {
  const geometry = new BufferGeometry()
  const positions: number[] = []

  for (let i = 0; i < segmentCount; i += 1) {
    const angle = (i / segmentCount) * Math.PI * 2
    positions.push(Math.cos(angle) * radius, Math.sin(angle) * radius, depth)
  }

  geometry.setAttribute('position', new Float32BufferAttribute(positions, 3))

  return new LineLoop(
    geometry,
    new LineBasicMaterial({
      color,
      transparent: true,
      opacity,
    }),
  )
}

function buildHaloPoints(pointCount: number) {
  const geometry = new BufferGeometry()
  const positions: number[] = []

  for (let i = 0; i < pointCount; i += 1) {
    const theta = Math.random() * Math.PI * 2
    const phi = Math.acos(2 * Math.random() - 1)
    const radius = 1.95 + Math.random() * 0.45
    positions.push(
      radius * Math.sin(phi) * Math.cos(theta),
      radius * Math.cos(phi),
      radius * Math.sin(phi) * Math.sin(theta),
    )
  }

  geometry.setAttribute('position', new Float32BufferAttribute(positions, 3))

  return new Points(
    geometry,
    new PointsMaterial({
      color: '#d8ccff',
      size: 0.045,
      transparent: true,
      opacity: 0.95,
      depthWrite: false,
    }),
  )
}

function buildFieldLines(horizontalCount: number, verticalCount: number) {
  const geometry = new BufferGeometry()
  const positions: number[] = []

  for (let i = 0; i < horizontalCount; i += 1) {
    const progress = horizontalCount === 1 ? 0.5 : i / (horizontalCount - 1)
    const y = -2.5 + progress * 5
    positions.push(-4.9, y, -1.2, 4.9, y + Math.sin(i * 0.55) * 0.08, -1.2)
  }

  for (let i = 0; i < verticalCount; i += 1) {
    const progress = verticalCount === 1 ? 0.5 : i / (verticalCount - 1)
    const x = -3.6 + progress * 7.2
    positions.push(x, -2.8, -1.2, x + Math.cos(i * 0.45) * 0.06, 2.8, -1.2)
  }

  geometry.setAttribute('position', new Float32BufferAttribute(positions, 3))

  return new LineSegments(
    geometry,
    new LineBasicMaterial({
      color: '#c9b3ff',
      transparent: true,
      opacity: 0.12,
    }),
  )
}

function resizeRenderer() {
  const host = hostRef.value
  if (!host || !renderer || !camera) return

  const width = Math.max(host.clientWidth, 1)
  const height = Math.max(host.clientHeight, 1)
  renderer.setSize(width, height, false)
  camera.aspect = width / height
  camera.updateProjectionMatrix()
  if (scene) renderer.render(scene, camera)
}

function handlePointerMove(event: PointerEvent) {
  const host = hostRef.value
  if (!host) return

  const bounds = host.getBoundingClientRect()
  if (bounds.width <= 0 || bounds.height <= 0) return

  const x = (event.clientX - bounds.left) / bounds.width - 0.5
  const y = (event.clientY - bounds.top) / bounds.height - 0.5

  targetRotationY = -0.35 + x * 0.75
  targetRotationX = 0.2 + y * 0.45
  targetFieldX = x * 0.9
  targetFieldY = y * 0.65
}

function handlePointerLeave() {
  targetRotationX = 0.2
  targetRotationY = -0.35
  targetFieldX = 0
  targetFieldY = 0
}

function scheduleNextFrame() {
  if (!animationRunning) return
  frameId = window.requestAnimationFrame(animate)
}

function stopAnimation() {
  animationRunning = false
  lastRenderTime = 0
  if (frameId) {
    window.cancelAnimationFrame(frameId)
    frameId = 0
  }
}

function startAnimation() {
  if (animationRunning) return
  animationRunning = true
  lastRenderTime = 0
  scheduleNextFrame()
}

function syncAnimationState() {
  if (document.visibilityState === 'visible' && hostInViewport) startAnimation()
  else stopAnimation()
}

function handleVisibilityChange() {
  syncAnimationState()
}

function animate(now: number) {
  if (!renderer || !scene || !camera || !sphereGroup || !fieldGroup) return

  if (lastRenderTime && now - lastRenderTime < motionBudget.webglFrameIntervalMs) {
    scheduleNextFrame()
    return
  }

  lastRenderTime = now
  sphereGroup.rotation.x = MathUtils.lerp(sphereGroup.rotation.x, targetRotationX, 0.035)
  sphereGroup.rotation.y = MathUtils.lerp(sphereGroup.rotation.y, targetRotationY, 0.035)
  sphereGroup.rotation.z += motionBudget.lite ? 0.0016 : 0.0021

  fieldGroup.rotation.x = MathUtils.lerp(fieldGroup.rotation.x, -targetFieldY * 0.18, 0.04)
  fieldGroup.rotation.y = MathUtils.lerp(fieldGroup.rotation.y, targetFieldX * 0.18, 0.04)
  fieldGroup.position.x = MathUtils.lerp(fieldGroup.position.x, targetFieldX * 0.18, 0.04)
  fieldGroup.position.y = MathUtils.lerp(fieldGroup.position.y, -targetFieldY * 0.14, 0.04)

  renderer.render(scene, camera)
  scheduleNextFrame()
}

onMounted(() => {
  const host = hostRef.value
  if (!host) return
  if (typeof window.WebGLRenderingContext === 'undefined') return
  motionBudget = readMotionBudget()

  scene = new Scene()
  scene.background = null

  camera = new PerspectiveCamera(34, 1, 0.1, 100)
  camera.position.set(0, 0, 8.4)

  try {
    renderer = new WebGLRenderer({ antialias: !motionBudget.lite, alpha: true, powerPreference: 'low-power' })
  } catch {
    return
  }

  renderer.setPixelRatio(motionBudget.webglPixelRatio)
  renderer.setClearColor(new Color('#000000'), 0)
  host.appendChild(renderer.domElement)

  fieldGroup = new Group()
  sphereGroup = new Group()

  const shell = new Mesh(
    new IcosahedronGeometry(2.05, 1),
    new MeshBasicMaterial({
      color: '#7c4dff',
      transparent: true,
      opacity: 0.08,
      wireframe: false,
    }),
  )

  const wireframe = new LineSegments(
    new WireframeGeometry(new IcosahedronGeometry(2.16, 1)),
    new LineBasicMaterial({
      color: '#d7c3ff',
      transparent: true,
      opacity: 0.9,
    }),
  )

  const innerWireframe = new LineSegments(
    new WireframeGeometry(new IcosahedronGeometry(1.42, 0)),
    new LineBasicMaterial({
      color: '#73ecff',
      transparent: true,
      opacity: 0.42,
    }),
  )

  const haloPoints = buildHaloPoints(motionBudget.lite ? 72 : 96)
  const outerRing = buildRing(2.82, -0.3, '#d6c6ff', 0.42, motionBudget.lite ? 36 : 44)
  outerRing.rotation.x = 1.08
  outerRing.rotation.y = 0.22

  const middleRing = buildRing(2.28, 0.35, '#73ecff', 0.28, motionBudget.lite ? 28 : 36)
  middleRing.rotation.x = 0.52
  middleRing.rotation.y = 0.94

  const rearField = buildFieldLines(motionBudget.lite ? 18 : 22, motionBudget.lite ? 12 : 15)

  sphereGroup.add(shell)
  sphereGroup.add(wireframe)
  sphereGroup.add(innerWireframe)
  sphereGroup.add(haloPoints)
  sphereGroup.add(outerRing)
  sphereGroup.add(middleRing)
  sphereGroup.rotation.x = targetRotationX
  sphereGroup.rotation.y = targetRotationY

  fieldGroup.add(rearField)
  fieldGroup.add(sphereGroup)

  scene.add(fieldGroup)
  scene.add(new AmbientLight('#ffffff', 1.6))

  resizeRenderer()
  resizeObserver = new ResizeObserver(() => resizeRenderer())
  resizeObserver.observe(host)

  if (typeof IntersectionObserver !== 'undefined') {
    intersectionObserver = new IntersectionObserver(
      ([entry]) => {
        hostInViewport = entry?.isIntersecting ?? true
        syncAnimationState()
      },
      { threshold: 0.12 },
    )
    intersectionObserver.observe(host)
  }

  host.addEventListener('pointermove', handlePointerMove)
  host.addEventListener('pointerleave', handlePointerLeave)
  document.addEventListener('visibilitychange', handleVisibilityChange)

  syncAnimationState()
})

onBeforeUnmount(() => {
  const host = hostRef.value
  host?.removeEventListener('pointermove', handlePointerMove)
  host?.removeEventListener('pointerleave', handlePointerLeave)
  document.removeEventListener('visibilitychange', handleVisibilityChange)

  stopAnimation()
  resizeObserver?.disconnect()
  resizeObserver = null
  intersectionObserver?.disconnect()
  intersectionObserver = null

  scene?.traverse((object: Object3D) => {
    const mesh = object as Mesh
    mesh.geometry?.dispose?.()
    const material = mesh.material
    if (Array.isArray(material)) material.forEach((item) => item.dispose())
    else material?.dispose?.()
  })

  renderer?.dispose()
  renderer?.domElement.remove()
  renderer = null
  scene = null
  camera = null
  sphereGroup = null
  fieldGroup = null
})
</script>

<style scoped>
.poly-sphere-host {
  width: 100%;
  height: 100%;
  min-height: 420px;
  margin: 0 auto;
  position: relative;
  overflow: hidden;
  filter: drop-shadow(0 24px 56px rgba(16, 8, 38, 0.34));
}

.poly-sphere-host :deep(canvas) {
  display: block;
  width: 100%;
  height: 100%;
}

@media (max-width: 640px) {
  .poly-sphere-host {
    min-height: 280px;
    height: 320px;
  }
}
</style>
