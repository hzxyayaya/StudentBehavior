import type { RiskLevel } from './types'

type ErrorWithStatus = Error & {
  status?: number
}

export function formatRisk(value: number) {
  return value.toFixed(2)
}

export function formatRiskLevel(level: RiskLevel) {
  return {
    high: '高风险',
    medium: '中风险',
    low: '低风险',
    高风险: '高风险',
    较高风险: '较高风险',
    一般风险: '一般风险',
    低风险: '低风险',
  }[level]
}

export function formatApiErrorMessage(error: unknown, fallback = '当前数据暂不可用，请稍后重试') {
  if (!(error instanceof Error)) return fallback

  const { status } = error as ErrorWithStatus
  const rawMessage = error.message.toLowerCase()

  if (status === 404) {
    if (rawMessage.includes('student')) return '当前学生在所选学期不存在，请更换后重试'
    return '当前学期暂无可用数据，请切换学期后重试'
  }
  if (status === 500) {
    return '后端产物缺失或暂不可用，请先检查 demo-api 依赖数据'
  }
  return fallback
}
