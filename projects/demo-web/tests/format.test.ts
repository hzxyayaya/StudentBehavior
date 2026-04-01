import { describe, expect, it } from 'vitest'

import { formatApiErrorMessage, formatRisk, formatRiskLevel } from '@/lib/format'

describe('format helpers', () => {
  it('formats risk values with two decimals', () => {
    expect(formatRisk(0.1234)).toBe('0.12')
  })

  it('formats risk level labels in Chinese', () => {
    expect(formatRiskLevel('high')).toBe('高风险')
    expect(formatRiskLevel('medium')).toBe('中风险')
    expect(formatRiskLevel('low')).toBe('低风险')
  })

  it('maps 404 term errors to localized copy', () => {
    const error = Object.assign(new Error('term not found'), { status: 404 })
    expect(formatApiErrorMessage(error)).toContain('当前学期暂无可用数据')
  })

  it('maps 404 student errors to localized copy', () => {
    const error = Object.assign(new Error('student not found'), { status: 404 })
    expect(formatApiErrorMessage(error)).toContain('当前学生在所选学期不存在')
  })

  it('maps 500 artifact errors to localized copy', () => {
    const error = Object.assign(new Error('overview artifact unavailable'), { status: 500 })
    expect(formatApiErrorMessage(error)).toContain('后端产物缺失或暂不可用')
  })
})
