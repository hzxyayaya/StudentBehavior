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

const hostRef = ref<HTMLElement | null>(null)

let renderer: WebGLRenderer | null = null
let scene: Scene | null = null
let camera: PerspectiveCamera | null = null
let frameId = 0
let resizeObserver: ResizeObserver | null = null
let sphereGroup: Group | null = null
let fieldGroup: Group | null = null
let targetRotationX = 0.2
let targetRotationY = -0.35
let targetFieldX = 0
let targetFieldY = 0

function buildRing(radius: number, depth: number, color: string, opacity: number) {
  const geometry = new BufferGeometry()
  const positions: number[] = []

  for (let i = 0; i < 64; i += 1) {
    const angle = (i / 64) * Math.PI * 2
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

function buildHaloPoints() {
  const geometry = new BufferGeometry()
  const positions: number[] = []

  for (let i = 0; i < 140; i += 1) {
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

function buildFieldLines() {
  const geometry = new BufferGeometry()
  const positions: number[] = []

  for (let i = 0; i < 28; i += 1) {
    const y = -2.5 + i * 0.18
    positions.push(-4.9, y, -1.2, 4.9, y + Math.sin(i * 0.55) * 0.08, -1.2)
  }

  for (let i = 0; i < 20; i += 1) {
    const x = -3.6 + i * 0.36
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
}

function handlePointerMove(event: PointerEvent) {
  const x = event.clientX / window.innerWidth - 0.5
  const y = event.clientY / window.innerHeight - 0.5

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

function animate() {
  if (!renderer || !scene || !camera || !sphereGroup || !fieldGroup) return

  sphereGroup.rotation.x = MathUtils.lerp(sphereGroup.rotation.x, targetRotationX, 0.035)
  sphereGroup.rotation.y = MathUtils.lerp(sphereGroup.rotation.y, targetRotationY, 0.035)
  sphereGroup.rotation.z += 0.0028

  fieldGroup.rotation.x = MathUtils.lerp(fieldGroup.rotation.x, -targetFieldY * 0.18, 0.04)
  fieldGroup.rotation.y = MathUtils.lerp(fieldGroup.rotation.y, targetFieldX * 0.18, 0.04)
  fieldGroup.position.x = MathUtils.lerp(fieldGroup.position.x, targetFieldX * 0.18, 0.04)
  fieldGroup.position.y = MathUtils.lerp(fieldGroup.position.y, -targetFieldY * 0.14, 0.04)

  renderer.render(scene, camera)
  frameId = window.requestAnimationFrame(animate)
}

onMounted(() => {
  const host = hostRef.value
  if (!host) return

  scene = new Scene()
  scene.background = null

  camera = new PerspectiveCamera(34, 1, 0.1, 100)
  camera.position.set(0, 0, 8.4)

  renderer = new WebGLRenderer({ antialias: true, alpha: true })
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
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

  const haloPoints = buildHaloPoints()
  const outerRing = buildRing(2.82, -0.3, '#d6c6ff', 0.42)
  outerRing.rotation.x = 1.08
  outerRing.rotation.y = 0.22

  const middleRing = buildRing(2.28, 0.35, '#73ecff', 0.28)
  middleRing.rotation.x = 0.52
  middleRing.rotation.y = 0.94

  const rearField = buildFieldLines()

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

  window.addEventListener('pointermove', handlePointerMove)
  window.addEventListener('pointerleave', handlePointerLeave)

  animate()
})

onBeforeUnmount(() => {
  window.removeEventListener('pointermove', handlePointerMove)
  window.removeEventListener('pointerleave', handlePointerLeave)

  if (frameId) window.cancelAnimationFrame(frameId)
  resizeObserver?.disconnect()
  resizeObserver = null

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
