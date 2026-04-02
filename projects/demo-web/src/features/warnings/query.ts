import type { LocationQuery, LocationQueryRaw } from 'vue-router'
import type { RiskLevel } from '@/lib/types'

import { AVAILABLE_TERMS, DEFAULT_TERM } from '@/app/term'

export type WarningFilterState = {
  term: string
  page: number
  riskLevel: string
  groupSegment: string
  majorName: string
  riskChangeDirection: string
}

function readSingle(queryValue: LocationQuery[string] | undefined) {
  return typeof queryValue === 'string' ? queryValue : ''
}

function parsePage(value: string) {
  const parsed = Number.parseInt(value, 10)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 1
}

export function formatWarningLevelLabel(level: string | RiskLevel) {
  return (
    {
      high: '高风险',
      medium: '一般风险',
      low: '低风险',
      高风险: '高风险',
      较高风险: '较高风险',
      一般风险: '一般风险',
      低风险: '低风险',
    }[level] ?? '低风险'
  )
}

export function getWarningLevelFilterPlan(level: string) {
  if (level === '高风险' || level === '较高风险') {
    return {
      apiRiskLevel: 'high',
      exactRiskLevel: level,
      needsClientExactFiltering: true,
    } as const
  }
  if (level === '一般风险') {
    return {
      apiRiskLevel: 'medium',
      exactRiskLevel: level,
      needsClientExactFiltering: false,
    } as const
  }
  if (level === '低风险') {
    return {
      apiRiskLevel: 'low',
      exactRiskLevel: level,
      needsClientExactFiltering: false,
    } as const
  }
  if (level === 'high' || level === 'medium' || level === 'low') {
    return {
      apiRiskLevel: level,
      exactRiskLevel: '',
      needsClientExactFiltering: false,
    } as const
  }
  return {
    apiRiskLevel: null,
    exactRiskLevel: '',
    needsClientExactFiltering: false,
  } as const
}

export function matchesSelectedWarningLevel(selectedLevel: string, itemLevel: string | RiskLevel) {
  if (!selectedLevel) return true

  const normalizedItemLevel = formatWarningLevelLabel(itemLevel)
  if (selectedLevel === 'high') {
    return normalizedItemLevel === '高风险' || normalizedItemLevel === '较高风险'
  }
  if (selectedLevel === 'medium') {
    return normalizedItemLevel === '一般风险'
  }
  if (selectedLevel === 'low') {
    return normalizedItemLevel === '低风险'
  }
  return normalizedItemLevel === selectedLevel
}

export function parseWarningQuery(query: LocationQuery): WarningFilterState {
  const term = readSingle(query.term)

  return {
    term: AVAILABLE_TERMS.includes(term as (typeof AVAILABLE_TERMS)[number]) ? term : DEFAULT_TERM,
    page: parsePage(readSingle(query.page)),
    riskLevel: readSingle(query.risk_level),
    groupSegment: readSingle(query.group_segment),
    majorName: readSingle(query.major_name),
    riskChangeDirection: readSingle(query.risk_change_direction),
  }
}

export function buildWarningQuery(state: WarningFilterState): LocationQueryRaw {
  const query: LocationQueryRaw = {
    term: state.term,
  }

  if (state.page > 1) {
    query.page = String(state.page)
  }
  if (state.riskLevel) {
    query.risk_level = state.riskLevel
  }
  if (state.groupSegment) {
    query.group_segment = state.groupSegment
  }
  if (state.majorName) {
    query.major_name = state.majorName
  }
  if (state.riskChangeDirection) {
    query.risk_change_direction = state.riskChangeDirection
  }

  return query
}

export function buildWarningContextQuery(state: WarningFilterState): LocationQueryRaw {
  return {
    ...buildWarningQuery(state),
    source: 'warnings',
  }
}
