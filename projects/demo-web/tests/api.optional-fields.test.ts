import { beforeEach, describe, expect, it, vi } from 'vitest'

import { getDevelopmentAnalysis, getOverview } from '@/lib/api'

function okResponse(data: unknown) {
  return {
    ok: true,
    text: async () =>
      JSON.stringify({
        code: 200,
        message: 'OK',
        data,
        meta: { request_id: 'demo-request', term: '2024-2' },
      }),
  }
}

describe('api client optional field normalization', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('omits absent optional major risk fields in overview responses', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input)
        if (!url.includes('/analytics/overview')) {
          throw new Error(`Unexpected fetch url: ${url}`)
        }

        return Promise.resolve(
          okResponse({
            student_count: 179,
            risk_distribution: { high: 0, medium: 0, low: 179 },
            risk_band_distribution: { 高风险: 12, 较高风险: 21, 一般风险: 34, 低风险: 112 },
            group_distribution: { 作息失衡风险组: 179 },
            dimension_summary: [],
            major_risk_summary: [{ major_name: '应用化学', high_risk_count: 0, student_count: 7 }],
            trend_summary: { terms: [] },
            risk_trend_summary: [],
            risk_factor_summary: [],
          }),
        )
      }),
    )

    const data = await getOverview('2024-2')
    const row = data.major_risk_summary[0]

    expect(row).toStrictEqual({
      major_name: '应用化学',
      high_risk_count: 0,
      student_count: 7,
    })
    expect(row).not.toHaveProperty('elevated_risk_count')
    expect(row).not.toHaveProperty('elevated_risk_ratio')
    expect(row).not.toHaveProperty('average_risk_probability')
  })

  it('omits absent optional major comparison fields in development analysis responses', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input)
        if (!url.includes('/analytics/development')) {
          throw new Error(`Unexpected fetch url: ${url}`)
        }

        return Promise.resolve(
          okResponse({
            term: '2024-2',
            major_comparison: [{ major_name: '应用化学', high_risk_count: 1, student_count: 9 }],
            dimension_highlights: [],
            group_direction_segments: [],
            direction_chains: [],
            disclaimer: '仅供演示',
          }),
        )
      }),
    )

    const data = await getDevelopmentAnalysis('2024-2')
    const row = data.major_comparison[0]

    expect(row).toStrictEqual({
      major_name: '应用化学',
      high_risk_count: 1,
      student_count: 9,
    })
    expect(row).not.toHaveProperty('elevated_risk_count')
    expect(row).not.toHaveProperty('elevated_risk_ratio')
    expect(row).not.toHaveProperty('average_risk_probability')
  })
})
