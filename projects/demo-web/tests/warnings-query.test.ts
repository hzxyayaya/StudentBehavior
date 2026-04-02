import { describe, expect, it } from 'vitest'

import {
  buildWarningQuery,
  getWarningLevelFilterPlan,
  matchesSelectedWarningLevel,
  parseWarningQuery,
} from '@/features/warnings/query'

describe('warnings query helpers', () => {
  it('parses valid warning query state', () => {
    const state = parseWarningQuery({
      term: '2023-2',
      page: '3',
      risk_level: '较高风险',
      group_segment: '作息失衡风险组',
      major_name: '计算机科学与技术',
      risk_change_direction: 'rising',
    })

    expect(state).toEqual({
      term: '2023-2',
      page: 3,
      riskLevel: '较高风险',
      groupSegment: '作息失衡风险组',
      majorName: '计算机科学与技术',
      riskChangeDirection: 'rising',
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
        riskChangeDirection: 'falling',
      }),
    ).toEqual({
      term: '2024-2',
      group_segment: '学习投入稳定组',
      risk_change_direction: 'falling',
    })
  })

  it.each([
    ['高风险', { apiRiskLevel: 'high', exactRiskLevel: '高风险', needsClientExactFiltering: true }],
    ['较高风险', { apiRiskLevel: 'high', exactRiskLevel: '较高风险', needsClientExactFiltering: true }],
    ['一般风险', { apiRiskLevel: 'medium', exactRiskLevel: '一般风险', needsClientExactFiltering: false }],
    ['低风险', { apiRiskLevel: 'low', exactRiskLevel: '低风险', needsClientExactFiltering: false }],
    ['', { apiRiskLevel: null, exactRiskLevel: '', needsClientExactFiltering: false }],
  ])('builds an exact filter plan for %s', (riskLevel, expectedPlan) => {
    expect(getWarningLevelFilterPlan(riskLevel)).toEqual(expectedPlan)
  })

  it.each([
    ['高风险', '高风险', true],
    ['高风险', '较高风险', false],
    ['较高风险', '较高风险', true],
    ['较高风险', '高风险', false],
    ['一般风险', '一般风险', true],
    ['一般风险', 'medium', true],
    ['一般风险', '低风险', false],
    ['低风险', '低风险', true],
    ['低风险', 'low', true],
    ['低风险', '一般风险', false],
    ['', '高风险', true],
  ])('matches exact warning level selection %s against %s', (selectedLevel, itemLevel, expected) => {
    expect(matchesSelectedWarningLevel(selectedLevel, itemLevel)).toBe(expected)
  })
})
