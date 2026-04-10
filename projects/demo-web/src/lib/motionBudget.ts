export type MotionBudgetInput = {
  devicePixelRatio?: number
  hardwareConcurrency?: number
  reducedMotion?: boolean
  saveData?: boolean
  viewportWidth?: number
}

export type MotionBudget = {
  lite: boolean
  particleDetectRetina: boolean
  particleFpsLimit: number
  webglPixelRatio: number
  webglFrameIntervalMs: number
}

type NavigatorWithConnection = Navigator & {
  connection?: {
    saveData?: boolean
  }
}

export function getMotionBudget({
  devicePixelRatio = 1,
  hardwareConcurrency = 8,
  reducedMotion = false,
  saveData = false,
  viewportWidth = 1440,
}: MotionBudgetInput = {}): MotionBudget {
  const lite =
    reducedMotion ||
    saveData ||
    hardwareConcurrency <= 4 ||
    devicePixelRatio > 1.5 ||
    viewportWidth < 1200

  return {
    lite,
    particleDetectRetina: !lite && devicePixelRatio <= 1.5,
    particleFpsLimit: lite ? 32 : 42,
    webglPixelRatio: Math.min(devicePixelRatio, lite ? 1.25 : 1.5),
    webglFrameIntervalMs: lite ? 48 : 32,
  }
}

export function readMotionBudget(): MotionBudget {
  if (typeof window === 'undefined') {
    return getMotionBudget()
  }

  const reducedMotion = window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ?? false
  const connection = (navigator as NavigatorWithConnection).connection

  return getMotionBudget({
    devicePixelRatio: window.devicePixelRatio || 1,
    hardwareConcurrency: navigator.hardwareConcurrency || 8,
    reducedMotion,
    saveData: Boolean(connection?.saveData),
    viewportWidth: window.innerWidth || 1440,
  })
}
