import { describe, expect, it } from 'vitest'

import { getMotionBudget } from '@/lib/motionBudget'

describe('getMotionBudget', () => {
  it('keeps a lighter but full desktop animation budget by default', () => {
    expect(
      getMotionBudget({
        devicePixelRatio: 1,
        hardwareConcurrency: 8,
        reducedMotion: false,
        saveData: false,
        viewportWidth: 1440,
      }),
    ).toEqual({
      lite: false,
      particleDetectRetina: true,
      particleFpsLimit: 42,
      webglPixelRatio: 1,
      webglFrameIntervalMs: 32,
    })
  })

  it('drops to the lite budget on constrained devices', () => {
    expect(
      getMotionBudget({
        devicePixelRatio: 2,
        hardwareConcurrency: 4,
        reducedMotion: false,
        saveData: false,
        viewportWidth: 1024,
      }),
    ).toEqual({
      lite: true,
      particleDetectRetina: false,
      particleFpsLimit: 32,
      webglPixelRatio: 1.25,
      webglFrameIntervalMs: 48,
    })
  })

  it('treats reduced-motion and save-data requests as a lite budget', () => {
    expect(getMotionBudget({ reducedMotion: true })).toMatchObject({
      lite: true,
      particleFpsLimit: 32,
      webglFrameIntervalMs: 48,
    })

    expect(getMotionBudget({ saveData: true })).toMatchObject({
      lite: true,
      particleDetectRetina: false,
    })
  })
})
