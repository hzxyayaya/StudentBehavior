import { describe, expect, it } from 'vitest'

import { buildWarningQuery, parseWarningQuery } from '@/features/warnings/query'

describe('warnings query helpers', () => {
  it('parses valid warning query state', () => {
    const state = parseWarningQuery({
      term: '2023-2',
      page: '3',
      risk_level: 'high',
      group_segment: '作息失衡风险组',
      major_name: '计算机科学与技术',
    })

    expect(state).toEqual({
      term: '2023-2',
      page: 3,
      riskLevel: 'high',
      groupSegment: '作息失衡风险组',
      majorName: '计算机科学与技术',
    })
  })

  it('falls back to default term and page when query is invalid', () => {
    const state = parseWarningQuery({
      term: '2099-1',
      page: '0',
    })

    expect(state.term).toBe('2024-2')
    expect(state.page).toBe(1)
  })

  it('builds compact route query for warning filters', () => {
    expect(
      buildWarningQuery({
        term: '2024-2',
        page: 1,
        riskLevel: '',
        groupSegment: '学习投入稳定组',
        majorName: '',
      }),
    ).toEqual({
      term: '2024-2',
      group_segment: '学习投入稳定组',
    })
  })
})
