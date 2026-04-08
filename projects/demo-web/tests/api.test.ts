import { beforeEach, describe, expect, it, vi } from 'vitest'

import { getDevelopmentAnalysis, getGroups, getOverview, loginDemo, getStudentProfile, getStudentReport } from '@/lib/api'

describe('api client', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('parses demo login envelope', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          code: 200,
          message: 'OK',
          data: {
            session_token: 'demo-token',
          },
          meta: { request_id: 'demo-request', term: '2024-2' },
        }),
      }),
    )

    const data = await loginDemo()
    expect(data).toEqual({ session_token: 'demo-token' })
  })

  it('throws for non-200 envelopes', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          code: 404,
          message: 'term not found',
          data: {},
          meta: { request_id: 'demo-request', term: '2099-1' },
        }),
      }),
    )

    await expect(getOverview('2099-1')).rejects.toThrow('term not found')
  })

  it('throws a readable error for empty responses', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: false,
        status: 502,
        text: async () => '',
      }),
    )

    await expect(loginDemo()).rejects.toThrow('demo-api returned an empty response')
  })

  it('normalizes overview and related payloads from the current demo-api shape', async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input)

      if (url.includes('/analytics/overview')) {
        return Promise.resolve({
          ok: true,
          text: async () =>
            JSON.stringify({
              code: 200,
              message: 'OK',
              data: {
                student_count: 179,
                risk_distribution: { high: 0, medium: 0, low: 179 },
                risk_band_distribution: { 高风险: 12, 较高风险: 21, 一般风险: 34, 低风险: 112 },
                group_distribution: { 作息失衡风险组: 179 },
                dimension_summary: [
                  {
                    dimension: '学业基础表现',
                    average_score: 82,
                    level: 'high',
                    label: '学业基础稳健',
                    explanation: '学期 GPA 保持稳定。',
                    metrics: [{ metric: '学期GPA', value: 3.2, display: '3.2' }],
                  },
                  {
                    dimension: '课堂学习投入',
                    average_score: 74,
                    level: 'medium',
                    label: '课堂投入一般',
                    explanation: '出勤较稳但课堂参与仍有提升空间。',
                    metrics: [
                      { metric: '全勤率', value: 0.91, display: '91%' },
                      { metric: '迟到次数', value: 3, display: '3 次' },
                    ],
                  },
                ],
                major_risk_summary: [{ major_name: '应用化学', student_count: 7, high_risk_count: 0 }],
                trend_summary: {
                  terms: [
                    {
                      term_key: '2024-2',
                      risk_distribution: { high: 0, medium: 0, low: 81 },
                    },
                  ],
                },
                risk_trend_summary: [
                  {
                    term: '2024-1',
                    avg_risk_score: 49.8,
                    high_risk_count: 10,
                    elevated_risk_count: 10,
                    risk_change_direction: 'rising',
                  },
                  {
                    term: '2024-2',
                    avg_risk_score: 52.1,
                    high_risk_count: 12,
                    elevated_risk_count: 12,
                    risk_change_direction: 'rising',
                  },
                ],
                risk_factor_summary: [
                  { feature: 'academic_base', feature_cn: '学业基础表现', count: 52, importance: 0.82 },
                  { feature: 'class_engagement', feature_cn: '课堂学习投入', count: 41, importance: 0.66 },
                ],
              },
              meta: { request_id: 'demo-request', term: '2024-2' },
            }),
        })
      }

      if (url.includes('/analytics/groups')) {
        return Promise.resolve({
          ok: true,
          text: async () =>
            JSON.stringify({
              code: 200,
              message: 'OK',
              data: {
                groups: [
                  {
                    group_segment: '作息失衡风险组',
                    student_count: 81,
                    avg_risk_probability: 0.38,
                    avg_risk_score: 57.4,
                    avg_risk_level: '较高风险',
                    risk_change_summary: { rising: 31, steady: 40, falling: 10 },
                    avg_dimension_scores: [
                      {
                        dimension: '学业基础表现',
                        average_score: 80,
                        level: 'high',
                        label: '学业基础稳健',
                        explanation: '学期 GPA 保持稳定。',
                        metrics: [{ metric: '学期GPA', value: 3.1, display: '3.1' }],
                      },
                      {
                        dimension: '课堂学习投入',
                        average_score: 68,
                        level: 'medium',
                        label: '课堂投入一般',
                        explanation: '出勤较稳但课堂参与仍有提升空间。',
                        metrics: [{ metric: '全勤率', value: 0.87, display: '87%' }],
                      },
                    ],
                    top_factors: [
                      {
                        dimension: '网络作息自律指数',
                        importance: 0.75,
                        count: 81,
                        label: '网络使用偏强',
                        explanation: '覆盖 81 人，重要度 0.75',
                        metrics: [{ metric: '月均上网时长', value: 66, display: '66 小时' }],
                      },
                    ],
                    risk_amplifiers: [
                      {
                        feature: 'academic_base',
                        feature_cn: '学业基础表现',
                        count: 51,
                        importance: 0.79,
                      },
                    ],
                    protective_factors: [
                      {
                        feature: 'library_immersion',
                        feature_cn: '图书馆沉浸度',
                        count: 29,
                        importance: 0.52,
                      },
                    ],
                  },
                ],
              },
              meta: { request_id: 'demo-request', term: '2024-2' },
            }),
        })
      }

      if (url.includes('/profile')) {
        return Promise.resolve({
          ok: true,
          text: async () =>
            JSON.stringify({
              code: 200,
              message: 'OK',
              data: {
                student_id: 'pjwrqxbj901',
                student_name: '示例学生',
                major_name: '应用化学',
                group_segment: '作息失衡风险组',
                risk_level: 'low',
                risk_probability: 0.38,
                dimension_scores: [
                  {
                    dimension: '学业基础表现',
                    score: 82,
                    level: 'high',
                    label: '学业基础稳健',
                    explanation: '学期 GPA 保持稳定。',
                    metrics: [{ metric: '学期GPA', value: 3.2, display: '3.2' }],
                  },
                  {
                    dimension: '课堂学习投入',
                    score: 20,
                    level: 'low',
                    label: '课堂投入不足',
                    explanation: '迟到与缺勤较多。',
                    metrics: [{ metric: '迟到次数', value: 6, display: '6 次' }],
                  },
                ],
                trend: [
                  {
                    term: '2024-2',
                    dimension_scores: [
                      {
                        dimension: '学业基础表现',
                        score: 82,
                        level: 'high',
                        label: '学业基础稳健',
                        explanation: '学期 GPA 保持稳定。',
                        metrics: [{ metric: '学期GPA', value: 3.2, display: '3.2' }],
                      },
                      {
                        dimension: '课堂学习投入',
                        score: 20,
                        level: 'low',
                        label: '课堂投入不足',
                        explanation: '迟到与缺勤较多。',
                        metrics: [{ metric: '迟到次数', value: 6, display: '6 次' }],
                      },
                    ],
                  },
                ],
              },
              meta: { request_id: 'demo-request', term: '2024-2' },
            }),
        })
      }

      return Promise.resolve({
        ok: true,
        text: async () =>
          JSON.stringify({
            code: 200,
            message: 'OK',
            data: {
              top_factors: [{ feature_cn: '课堂学习投入', effect: 'positive', importance: 0.75 }],
              intervention_advice: ['保持当前节奏'],
              report_text: '报告摘要',
            },
            meta: { request_id: 'demo-request', term: '2024-2' },
          }),
      })
    })

    vi.stubGlobal('fetch', fetchMock)

    await expect(getOverview('2024-2')).resolves.toEqual({
      student_count: 179,
      risk_distribution: [
        { risk_level: 'high', count: 0 },
        { risk_level: 'medium', count: 0 },
        { risk_level: 'low', count: 179 },
      ],
      risk_band_distribution: { 高风险: 12, 较高风险: 21, 一般风险: 34, 低风险: 112 },
      group_distribution: [{ group_segment: '作息失衡风险组', count: 179 }],
      dimension_summary: [
        {
          dimension: '学业基础表现',
          score: 0.82,
          level: 'high',
          label: '学业基础稳健',
          explanation: '学期 GPA 保持稳定。',
          metrics: [{ metric: '学期GPA', value: 3.2, display: '3.2' }],
        },
        {
          dimension: '课堂学习投入',
          score: 0.74,
          level: 'medium',
          label: '课堂投入一般',
          explanation: '出勤较稳但课堂参与仍有提升空间。',
          metrics: [
            { metric: '全勤率', value: 0.91, display: '91%' },
            { metric: '迟到次数', value: 3, display: '3 次' },
          ],
        },
      ],
      major_risk_summary: [{ major_name: '应用化学', high_risk_count: 0, student_count: 7 }],
      trend_summary: [{ term: '2024-2', high_risk_count: 0 }],
      risk_trend_summary: [
        { term: '2024-1', avg_risk_score: 49.8, high_risk_count: 10, elevated_risk_count: 10, risk_change_direction: 'rising' },
        { term: '2024-2', avg_risk_score: 52.1, high_risk_count: 12, elevated_risk_count: 12, risk_change_direction: 'rising' },
      ],
      risk_factor_summary: [
        { feature: 'academic_base', feature_cn: '学业基础表现', count: 52, importance: 0.82 },
        { feature: 'class_engagement', feature_cn: '课堂学习投入', count: 41, importance: 0.66 },
      ],
    })

    await expect(getGroups('2024-2')).resolves.toEqual({
      groups: [
        {
          group_segment: '作息失衡风险组',
          student_count: 81,
          avg_risk_probability: 0.38,
          avg_risk_score: 57.4,
          avg_risk_level: '较高风险',
          risk_change_summary: { rising: 31, steady: 40, falling: 10 },
          avg_dimension_scores: [
            {
              dimension: '学业基础表现',
              score: 0.8,
              level: 'high',
              label: '学业基础稳健',
              explanation: '学期 GPA 保持稳定。',
              metrics: [{ metric: '学期GPA', value: 3.1, display: '3.1' }],
            },
            {
              dimension: '课堂学习投入',
              score: 0.68,
              level: 'medium',
              label: '课堂投入一般',
              explanation: '出勤较稳但课堂参与仍有提升空间。',
              metrics: [{ metric: '全勤率', value: 0.87, display: '87%' }],
            },
          ],
          top_factors: [
            {
              dimension: '网络作息自律指数',
              explanation: '覆盖 81 人，重要度 0.75',
              direction: 'up',
              impact: 0.75,
              importance: 0.75,
              count: 81,
              label: '网络使用偏强',
              metrics: [{ metric: '月均上网时长', value: 66, display: '66 小时' }],
            },
          ],
          risk_amplifiers: [
            {
              feature: 'academic_base',
              feature_cn: '学业基础表现',
              count: 51,
              importance: 0.79,
            },
          ],
          protective_factors: [
            {
              feature: 'library_immersion',
              feature_cn: '图书馆沉浸度',
              count: 29,
              importance: 0.52,
            },
          ],
        },
      ],
    })

    await expect(getStudentProfile('pjwrqxbj901', '2024-2')).resolves.toEqual({
      student_id: 'pjwrqxbj901',
      student_name: '示例学生',
      major_name: '应用化学',
      group_segment: '作息失衡风险组',
      risk_level: 'low',
      risk_probability: 0.38,
      dimension_scores: [
        {
          dimension: '学业基础表现',
          score: 0.82,
          level: 'high',
          label: '学业基础稳健',
          explanation: '学期 GPA 保持稳定。',
          metrics: [{ metric: '学期GPA', value: 3.2, display: '3.2' }],
        },
        {
          dimension: '课堂学习投入',
          score: 0.2,
          level: 'low',
          label: '课堂投入不足',
          explanation: '迟到与缺勤较多。',
          metrics: [{ metric: '迟到次数', value: 6, display: '6 次' }],
        },
      ],
      trend: [
        {
          term: '2024-2',
          dimension_scores: [
            {
              dimension: '学业基础表现',
              score: 0.82,
              level: 'high',
              label: '学业基础稳健',
              explanation: '学期 GPA 保持稳定。',
              metrics: [{ metric: '学期GPA', value: 3.2, display: '3.2' }],
            },
            {
              dimension: '课堂学习投入',
              score: 0.2,
              level: 'low',
              label: '课堂投入不足',
              explanation: '迟到与缺勤较多。',
              metrics: [{ metric: '迟到次数', value: 6, display: '6 次' }],
            },
          ],
        },
      ],
    })

    await expect(getStudentReport('pjwrqxbj901', '2024-2')).resolves.toMatchObject({
      top_factors: [
        {
          dimension: '课堂学习投入',
          explanation: '课堂学习投入 是当前重点关注维度，重要度 0.75',
          direction: 'up',
          impact: 0.75,
          importance: 0.75,
          effect: 'positive',
          feature_cn: '课堂学习投入',
        },
      ],
      intervention_advice: ['保持当前节奏'],
      report_text: '报告摘要',
    })
  })

  it('preserves calibrated metrics and explanations in the normalized API payloads', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input)

        if (url.includes('/overview')) {
          return Promise.resolve({
            ok: true,
            text: async () =>
              JSON.stringify({
                code: 200,
                message: 'OK',
                data: {
                  student_count: 10,
                  risk_distribution: { high: 1, medium: 2, low: 7 },
                  group_distribution: { 学习投入稳定组: 6 },
                  dimension_summary: [
                    {
                      dimension: '学业基础表现',
                      score: 82,
                      level: 'high',
                      label: '学业基础稳健',
                      explanation: 'GPA 保持稳定。',
                      metrics: [{ metric: '学期GPA', value: 3.3, display: '3.3' }],
                    },
                  ],
                  major_risk_summary: [{ major_name: '软件工程', student_count: 3, high_risk_count: 1 }],
                  trend_summary: { terms: [{ term_key: '2024-2', risk_distribution: { high: 1, medium: 2, low: 7 } }] },
                },
                meta: { request_id: 'demo-request', term: '2024-2' },
              }),
          })
        }

        return Promise.resolve({
          ok: true,
          text: async () =>
            JSON.stringify({
              code: 200,
              message: 'OK',
              data: {
                student_id: 'demo',
                student_name: '示例',
                major_name: '软件工程',
                group_segment: '学习投入稳定组',
                risk_level: 'medium',
                risk_probability: 0.41,
                dimension_scores: [
                  {
                    dimension: '学业基础表现',
                    score: 82,
                    level: 'high',
                    label: '学业基础稳健',
                    explanation: 'GPA 保持稳定。',
                    metrics: [{ metric: '学期GPA', value: 3.3, display: '3.3' }],
                  },
                ],
                trend: [
                  {
                    term: '2024-2',
                    dimension_scores: [
                      {
                        dimension: '学业基础表现',
                        score: 82,
                        level: 'high',
                        label: '学业基础稳健',
                        explanation: 'GPA 保持稳定。',
                        metrics: [{ metric: '学期GPA', value: 3.3, display: '3.3' }],
                      },
                    ],
                  },
                ],
              },
              meta: { request_id: 'demo-request', term: '2024-2' },
            }),
        })
      }),
    )

    const overview = await getOverview('2024-2')
    const profile = await getStudentProfile('demo', '2024-2')

    const overviewDimension = overview.dimension_summary[0]
    const profileDimension = profile.dimension_scores[0]
    if (!overviewDimension || !profileDimension) {
      throw new Error('missing calibrated dimension payload')
    }

    expect(overviewDimension).toMatchObject({
      dimension: '学业基础表现',
      score: 0.82,
      level: 'high',
      label: '学业基础稳健',
      explanation: 'GPA 保持稳定。',
    })
    expect(overviewDimension.metrics).toEqual([
      { metric: '学期GPA', value: 3.3, display: '3.3' },
    ])
    expect(profileDimension).toMatchObject({
      dimension: '学业基础表现',
      score: 0.82,
      level: 'high',
      label: '学业基础稳健',
      explanation: 'GPA 保持稳定。',
    })
    expect(profileDimension.metrics).toEqual([
      { metric: '学期GPA', value: 3.3, display: '3.3' },
    ])
  })

  it('keeps missing calibrated fields unavailable and avoids fabricating trend probabilities', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input)

        if (url.includes('/overview')) {
          return Promise.resolve({
            ok: true,
            text: async () =>
              JSON.stringify({
                code: 200,
                message: 'OK',
                data: {
                  student_count: 3,
                  risk_distribution: { high: 1, medium: 1, low: 1 },
                  group_distribution: { 待校准组: 3 },
                  dimension_summary: [
                    {
                      dimension: '学业基础表现',
                      score: 48,
                    },
                  ],
                  major_risk_summary: [],
                  trend_summary: { terms: [{ term_key: '2024-2', risk_distribution: { high: 1, medium: 1, low: 1 } }] },
                },
                meta: { request_id: 'demo-request', term: '2024-2' },
              }),
          })
        }

        return Promise.resolve({
          ok: true,
          text: async () =>
            JSON.stringify({
              code: 200,
              message: 'OK',
              data: {
                student_id: 'demo',
                student_name: '示例',
                major_name: '软件工程',
                group_segment: '待校准组',
                risk_level: 'medium',
                risk_probability: 0.41,
                dimension_scores: [
                  {
                    dimension: '学业基础表现',
                    score: 48,
                  },
                ],
                trend: [
                  {
                    term: '2024-2',
                    dimension_scores: [
                      {
                        dimension: '学业基础表现',
                        score: 48,
                      },
                    ],
                  },
                ],
              },
              meta: { request_id: 'demo-request', term: '2024-2' },
            }),
        })
      }),
    )

    const overview = await getOverview('2024-2')
    const profile = await getStudentProfile('demo', '2024-2')

    expect(overview.dimension_summary).toEqual([
      {
        dimension: '学业基础表现',
        score: 0.48,
      },
    ])
    expect(overview.dimension_summary[0]).not.toHaveProperty('level')
    expect(overview.dimension_summary[0]).not.toHaveProperty('label')
    expect(overview.dimension_summary[0]).not.toHaveProperty('metrics')
    expect(overview.dimension_summary[0]).not.toHaveProperty('explanation')

    expect(profile.dimension_scores).toEqual([
      {
        dimension: '学业基础表现',
        score: 0.48,
      },
    ])
    expect(profile.dimension_scores[0]).not.toHaveProperty('level')
    expect(profile.dimension_scores[0]).not.toHaveProperty('label')
    expect(profile.dimension_scores[0]).not.toHaveProperty('metrics')
    expect(profile.dimension_scores[0]).not.toHaveProperty('explanation')
    expect(profile.trend).toEqual([
      {
        term: '2024-2',
        dimension_scores: [
          {
            dimension: '学业基础表现',
            score: 0.48,
          },
        ],
      },
    ])
    expect(profile.trend[0]).not.toHaveProperty('risk_probability')
  })

  it('preserves explicit zero avg_risk_score instead of falling back to probability-based score', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input)

        if (url.includes('/analytics/groups')) {
          return Promise.resolve({
            ok: true,
            text: async () =>
              JSON.stringify({
                code: 200,
                message: 'OK',
                data: {
                  groups: [
                    {
                      group_segment: '稳态组',
                      student_count: 12,
                      avg_risk_probability: 0.61,
                      avg_risk_score: 0,
                      avg_dimension_scores: [],
                      top_factors: [],
                      risk_amplifiers: [],
                      protective_factors: [],
                    },
                  ],
                },
                meta: { request_id: 'demo-request', term: '2024-2' },
              }),
          })
        }

        return Promise.resolve({
          ok: true,
          text: async () =>
            JSON.stringify({
              code: 200,
              message: 'OK',
              data: {},
              meta: { request_id: 'demo-request', term: '2024-2' },
            }),
        })
      }),
    )

    const groups = await getGroups('2024-2')
    expect(groups.groups[0]?.avg_risk_probability).toBe(0.61)
    expect(groups.groups[0]?.avg_risk_score).toBe(0)
  })

  it('omits optional major comparison fields when backend leaves them out', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input)

        if (url.includes('/analytics/overview')) {
          return Promise.resolve({
            ok: true,
            text: async () =>
              JSON.stringify({
                code: 200,
                message: 'OK',
                data: {
                  student_count: 1,
                  risk_distribution: { high: 0, medium: 0, low: 1 },
                  risk_band_distribution: { 高风险: 0, 较高风险: 0, 一般风险: 0, 低风险: 1 },
                  group_distribution: {},
                  dimension_summary: [],
                  major_risk_summary: [{ major_name: '应用化学', high_risk_count: 0, student_count: 7 }],
                  trend_summary: { terms: [] },
                  risk_trend_summary: [],
                  risk_factor_summary: [],
                },
                meta: { request_id: 'demo-request', term: '2024-2' },
              }),
          })
        }

        return Promise.resolve({
          ok: true,
          text: async () =>
            JSON.stringify({
              code: 200,
              message: 'OK',
              data: {
                term: '2024-2',
                major_comparison: [{ major_name: '应用化学', high_risk_count: 0, student_count: 7 }],
                dimension_highlights: [],
                group_direction_segments: [],
                direction_chains: [],
                disclaimer: '去向真值暂未接入',
              },
              meta: { request_id: 'demo-request', term: '2024-2' },
            }),
        })
      }),
    )

    const overview = await getOverview('2024-2')
    const development = await getDevelopmentAnalysis('2024-2')

    expect(overview.major_risk_summary[0]).not.toHaveProperty('elevated_risk_count')
    expect(overview.major_risk_summary[0]).not.toHaveProperty('elevated_risk_ratio')
    expect(overview.major_risk_summary[0]).not.toHaveProperty('average_risk_probability')

    expect(development.major_comparison[0]).not.toHaveProperty('elevated_risk_count')
    expect(development.major_comparison[0]).not.toHaveProperty('elevated_risk_ratio')
    expect(development.major_comparison[0]).not.toHaveProperty('average_risk_probability')
  })
})
