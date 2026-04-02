import type {
  CalibratedDimensionScore,
  CalibratedFactor,
  DimensionMetric,
  DemoLoginData,
  Envelope,
  GroupsData,
  ModelSummaryData,
  OverviewData,
  RiskChangeDirection,
  RiskLevel,
  StudentProfileData,
  StudentReportData,
  WarningFactor,
  WarningsData,
} from './types'

const API_BASE = import.meta.env.VITE_API_BASE_URL || '/api'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
  })
  const payload = await parseEnvelope<T>(response)
  if (!response.ok || payload.code !== 200) {
    const error = new Error(payload.message || 'request failed')
    ;(error as Error & { status?: number }).status = response.status
    throw error
  }
  return payload.data
}

async function parseEnvelope<T>(response: Response): Promise<Envelope<T>> {
  if (typeof response.text !== 'function') {
    if (typeof response.json === 'function') {
      return (await response.json()) as Envelope<T>
    }
    throw createParseError('demo-api returned an unreadable response', response.status)
  }
  const raw = await response.text()
  if (!raw.trim()) {
    throw createParseError('demo-api returned an empty response', response.status)
  }
  try {
    return JSON.parse(raw) as Envelope<T>
  } catch {
    throw createParseError('demo-api returned invalid JSON', response.status)
  }
}

function createParseError(message: string, status?: number) {
  const error = new Error(message)
  if (status !== undefined) (error as Error & { status?: number }).status = status
  return error
}

export function loginDemo() {
  return request<DemoLoginData>('/auth/demo-login', {
    method: 'POST',
    body: JSON.stringify({ username: 'demo_admin', password: 'demo_only', role: 'manager' }),
  })
}

export function getOverview(term: string) {
  return request<unknown>(`/analytics/overview?term=${encodeURIComponent(term)}`).then(normalizeOverviewData)
}

export function getGroups(term: string) {
  return request<unknown>(`/analytics/groups?term=${encodeURIComponent(term)}`).then(normalizeGroupsData)
}

export function getWarnings(params: {
  term: string
  page: number
  page_size: number
  risk_level?: string | null
  group_segment?: string | null
  major_name?: string | null
  risk_change_direction?: string | null
}) {
  const search = new URLSearchParams({
    term: params.term,
    page: String(params.page),
    page_size: String(params.page_size),
  })
  if (params.risk_level) search.set('risk_level', params.risk_level)
  if (params.group_segment) search.set('group_segment', params.group_segment)
  if (params.major_name) search.set('major_name', params.major_name)
  if (params.risk_change_direction) search.set('risk_change_direction', params.risk_change_direction)
  return request<unknown>(`/warnings?${search.toString()}`).then(normalizeWarningsData)
}

export function getStudentProfile(studentId: string, term: string) {
  return request<unknown>(`/students/${encodeURIComponent(studentId)}/profile?term=${encodeURIComponent(term)}`).then(
    normalizeStudentProfileData,
  )
}

export function getStudentReport(studentId: string, term: string) {
  return request<unknown>(`/students/${encodeURIComponent(studentId)}/report?term=${encodeURIComponent(term)}`).then(
    normalizeStudentReportData,
  )
}

export function getModelSummary(term: string) {
  return request<ModelSummaryData>(`/models/summary?term=${encodeURIComponent(term)}`)
}

function normalizeOverviewData(raw: unknown): OverviewData {
  const data = asRecord(raw)

  return {
    student_count: asNumber(data.student_count),
    risk_distribution: normalizeRiskDistribution(data.risk_distribution),
    risk_band_distribution: normalizeRiskBandDistribution(data.risk_band_distribution),
    group_distribution: normalizeGroupDistribution(data.group_distribution),
    dimension_summary: normalizeCalibratedDimensions(data.dimension_summary),
    major_risk_summary: asArray(data.major_risk_summary).map((item) => {
      const row = asRecord(item)
      return {
        major_name: asString(row.major_name),
        high_risk_count: asNumber(row.high_risk_count),
        student_count: asNumber(row.student_count),
      }
    }),
    trend_summary: normalizeTrendSummary(data.trend_summary),
    risk_trend_summary: normalizeRiskTrendSummary(data.risk_trend_summary),
    risk_factor_summary: normalizeRiskFactorSummary(data.risk_factor_summary),
  }
}

function normalizeGroupsData(raw: unknown): GroupsData {
  const data = asRecord(raw)
  return {
    groups: asArray(data.groups).map((item) => {
      const row = asRecord(item)
      const group: GroupsData['groups'][number] = {
        group_segment: asString(row.group_segment),
        student_count: asNumber(row.student_count),
        avg_risk_probability: asNumber(row.avg_risk_probability),
        avg_risk_score: asOptionalNumber(row.avg_risk_score) ?? asNumber(row.avg_risk_probability) * 100,
        avg_dimension_scores: normalizeCalibratedDimensions(row.avg_dimension_scores),
        top_factors: asArray(row.top_factors).map(normalizeCalibratedFactor),
        risk_amplifiers: normalizeRiskFactorSummary(row.risk_amplifiers ?? row.top_factors),
        protective_factors: normalizeRiskFactorSummary(row.protective_factors),
      }
      const avgRiskLevel = asOptionalString(row.avg_risk_level)
      if (avgRiskLevel !== undefined) group.avg_risk_level = avgRiskLevel
      const riskChangeSummary = normalizeRiskChangeSummary(row.risk_change_summary)
      if (riskChangeSummary !== undefined) group.risk_change_summary = riskChangeSummary
      return group
    }),
  }
}

function normalizeWarningsData(raw: unknown): WarningsData {
  const data = asRecord(raw)
  return {
    items: asArray(data.items).map((item) => {
      const row = asRecord(item)
      const warning: WarningsData['items'][number] = {
        student_id: asString(row.student_id),
        student_name: asString(row.student_name),
        major_name: asString(row.major_name),
        group_segment: asString(row.group_segment),
        risk_level: asRiskLevel(row.risk_level),
        risk_probability: asNumber(row.risk_probability),
        top_risk_factors: normalizeWarningFactors(row.top_risk_factors),
        top_protective_factors: normalizeWarningFactors(row.top_protective_factors),
      }
      const baseRiskScore = asOptionalNumber(row.base_risk_score)
      if (baseRiskScore !== undefined) warning.base_risk_score = baseRiskScore
      const riskAdjustmentScore = asOptionalNumber(row.risk_adjustment_score)
      if (riskAdjustmentScore !== undefined) warning.risk_adjustment_score = riskAdjustmentScore
      const adjustedRiskScore = asOptionalNumber(row.adjusted_risk_score)
      if (adjustedRiskScore !== undefined) warning.adjusted_risk_score = adjustedRiskScore
      const riskDelta = asOptionalNumber(row.risk_delta)
      if (riskDelta !== undefined) warning.risk_delta = riskDelta
      const riskChangeDirection = asOptionalRiskChangeDirection(row.risk_change_direction)
      if (riskChangeDirection !== undefined) warning.risk_change_direction = riskChangeDirection
      return warning
    }),
    page: asNumber(data.page),
    page_size: asNumber(data.page_size),
    total: asNumber(data.total),
  }
}

function normalizeStudentProfileData(raw: unknown): StudentProfileData {
  const data = asRecord(raw)
  const currentRisk = asNumber(data.risk_probability)
  const profile: StudentProfileData = {
    student_id: asString(data.student_id),
    student_name: asString(data.student_name),
    major_name: asString(data.major_name),
    group_segment: asString(data.group_segment),
    risk_level: asRiskLevel(data.risk_level),
    risk_probability: currentRisk,
    dimension_scores: normalizeCalibratedDimensions(data.dimension_scores),
    trend: asArray(data.trend).map((item) => {
      const row = asRecord(item)
      const trendScores = normalizeCalibratedDimensions(row.dimension_scores)
      const trendRow: StudentProfileData['trend'][number] = {
        term: asString(row.term),
        dimension_scores: trendScores,
      }
      const riskProbability = asOptionalNumber(row.risk_probability)
      if (riskProbability !== undefined) trendRow.risk_probability = riskProbability
      const riskLevel = asOptionalRiskLevel(row.risk_level)
      if (riskLevel !== undefined) trendRow.risk_level = riskLevel
      const adjustedRiskScore = asOptionalNumber(row.adjusted_risk_score)
      if (adjustedRiskScore !== undefined) trendRow.adjusted_risk_score = adjustedRiskScore
      const riskDelta = asOptionalNumber(row.risk_delta)
      if (riskDelta !== undefined) trendRow.risk_delta = riskDelta
      const riskChangeDirection = asOptionalRiskChangeDirection(row.risk_change_direction)
      if (riskChangeDirection !== undefined) trendRow.risk_change_direction = riskChangeDirection
      return trendRow
    }),
  }
  const baseRiskScore = asOptionalNumber(data.base_risk_score)
  if (baseRiskScore !== undefined) profile.base_risk_score = baseRiskScore
  const riskAdjustmentScore = asOptionalNumber(data.risk_adjustment_score)
  if (riskAdjustmentScore !== undefined) profile.risk_adjustment_score = riskAdjustmentScore
  const adjustedRiskScore = asOptionalNumber(data.adjusted_risk_score)
  if (adjustedRiskScore !== undefined) profile.adjusted_risk_score = adjustedRiskScore
  const riskDelta = asOptionalNumber(data.risk_delta)
  if (riskDelta !== undefined) profile.risk_delta = riskDelta
  const riskChangeDirection = asOptionalRiskChangeDirection(data.risk_change_direction)
  if (riskChangeDirection !== undefined) profile.risk_change_direction = riskChangeDirection
  const baseRiskExplanation = asOptionalString(data.base_risk_explanation)
  if (baseRiskExplanation !== undefined) profile.base_risk_explanation = baseRiskExplanation
  const behaviorAdjustmentExplanation = asOptionalString(data.behavior_adjustment_explanation)
  if (behaviorAdjustmentExplanation !== undefined) profile.behavior_adjustment_explanation = behaviorAdjustmentExplanation
  const riskChangeExplanation = asOptionalString(data.risk_change_explanation)
  if (riskChangeExplanation !== undefined) profile.risk_change_explanation = riskChangeExplanation
  return profile
}

function normalizeStudentReportData(raw: unknown): StudentReportData {
  const data = asRecord(raw)
  const report: StudentReportData = {
    top_factors: asArray(data.top_factors).map(normalizeCalibratedFactor),
    intervention_advice: asArray(data.intervention_advice).map((item) => asString(item)),
    report_text: asString(data.report_text),
  }
  const baseRiskExplanation = asOptionalString(data.base_risk_explanation)
  if (baseRiskExplanation !== undefined) report.base_risk_explanation = baseRiskExplanation
  const behaviorAdjustmentExplanation = asOptionalString(data.behavior_adjustment_explanation)
  if (behaviorAdjustmentExplanation !== undefined) report.behavior_adjustment_explanation = behaviorAdjustmentExplanation
  const riskChangeExplanation = asOptionalString(data.risk_change_explanation)
  if (riskChangeExplanation !== undefined) report.risk_change_explanation = riskChangeExplanation
  const interventionPlan = normalizeInterventionPlan(data.intervention_plan)
  if (interventionPlan !== undefined) report.intervention_plan = interventionPlan
  const riskLevel = asOptionalRiskLevel(data.risk_level)
  if (riskLevel !== undefined) report.risk_level = riskLevel
  const riskProbability = asOptionalNumber(data.risk_probability)
  if (riskProbability !== undefined) report.risk_probability = riskProbability
  const baseRiskScore = asOptionalNumber(data.base_risk_score)
  if (baseRiskScore !== undefined) report.base_risk_score = baseRiskScore
  const riskAdjustmentScore = asOptionalNumber(data.risk_adjustment_score)
  if (riskAdjustmentScore !== undefined) report.risk_adjustment_score = riskAdjustmentScore
  const adjustedRiskScore = asOptionalNumber(data.adjusted_risk_score)
  if (adjustedRiskScore !== undefined) report.adjusted_risk_score = adjustedRiskScore
  const riskDelta = asOptionalNumber(data.risk_delta)
  if (riskDelta !== undefined) report.risk_delta = riskDelta
  const riskChangeDirection = asOptionalRiskChangeDirection(data.risk_change_direction)
  if (riskChangeDirection !== undefined) report.risk_change_direction = riskChangeDirection
  const interventionAdviceItems = asArray(data.intervention_advice_items)
  if (interventionAdviceItems.length > 0) {
    report.intervention_advice_items = interventionAdviceItems.map((item) => {
      const row = asRecord(item)
      const adviceItem: { title?: string; text?: string } = {}
      const title = asOptionalString(row.title)
      if (title !== undefined) adviceItem.title = title
      const text = asOptionalString(row.text)
      if (text !== undefined) adviceItem.text = text
      return adviceItem
    })
  }
  const trend = asArray(data.trend)
  if (trend.length > 0) {
    report.trend = trend.map((item) => {
      const row = asRecord(item)
      const trendRow: NonNullable<StudentReportData['trend']>[number] = {
        term: asString(row.term),
      }
      const trendRiskLevel = asOptionalRiskLevel(row.risk_level)
      if (trendRiskLevel !== undefined) trendRow.risk_level = trendRiskLevel
      const trendRiskProbability = asOptionalNumber(row.risk_probability)
      if (trendRiskProbability !== undefined) trendRow.risk_probability = trendRiskProbability
      const trendBaseRiskScore = asOptionalNumber(row.base_risk_score)
      if (trendBaseRiskScore !== undefined) trendRow.base_risk_score = trendBaseRiskScore
      const trendRiskAdjustmentScore = asOptionalNumber(row.risk_adjustment_score)
      if (trendRiskAdjustmentScore !== undefined) trendRow.risk_adjustment_score = trendRiskAdjustmentScore
      const trendAdjustedRiskScore = asOptionalNumber(row.adjusted_risk_score)
      if (trendAdjustedRiskScore !== undefined) trendRow.adjusted_risk_score = trendAdjustedRiskScore
      const trendRiskDelta = asOptionalNumber(row.risk_delta)
      if (trendRiskDelta !== undefined) trendRow.risk_delta = trendRiskDelta
      const trendRiskChangeDirection = asOptionalRiskChangeDirection(row.risk_change_direction)
      if (trendRiskChangeDirection !== undefined) trendRow.risk_change_direction = trendRiskChangeDirection
      return trendRow
    })
  }
  return report
}

function normalizeWarningFactors(raw: unknown): WarningFactor[] {
  return asArray(raw).map((item) => {
    const row = asRecord(item)
    const factor: WarningFactor = {
      feature: asString(row.feature || row.dimension),
    }
    const featureCn = asOptionalString(row.feature_cn)
    if (featureCn !== undefined) factor.feature_cn = featureCn
    const dimension = asOptionalString(row.dimension)
    if (dimension !== undefined) factor.dimension = dimension
    const importance = asOptionalNumber(row.importance)
    if (importance !== undefined) factor.importance = importance
    return factor
  })
}

function normalizeInterventionPlan(raw: unknown): StudentReportData['intervention_plan'] | undefined {
  if (typeof raw === 'string' && raw) return raw
  if (Array.isArray(raw)) return raw.map((item) => asString(item)).filter(Boolean)
  return undefined
}

function normalizeCalibratedDimensions(raw: unknown): CalibratedDimensionScore[] {
  return asArray(raw).map((item) => {
    const row = asRecord(item)
    const level = asOptionalRiskLevel(row.level ?? row.risk_level)
    const score = normalizeScore(asNumber(row.score ?? row.average_score))
    const dimensionScore: CalibratedDimensionScore = {
      dimension: asString(row.dimension || row.feature_cn || row.feature),
      score,
    }
    if (level !== undefined) dimensionScore.level = level
    const label = asOptionalString(row.label)
    if (label !== undefined) dimensionScore.label = label
    const metrics = normalizeDimensionMetrics(row.metrics)
    if (metrics.length > 0) dimensionScore.metrics = metrics
    const explanation = asOptionalString(row.explanation)
    if (explanation !== undefined) dimensionScore.explanation = explanation
    const dimensionCode = asOptionalString(row.dimension_code)
    if (dimensionCode !== undefined) dimensionScore.dimension_code = dimensionCode
    const feature = asOptionalString(row.feature)
    if (feature !== undefined) dimensionScore.feature = feature
    const featureCn = asOptionalString(row.feature_cn)
    if (featureCn !== undefined) dimensionScore.feature_cn = featureCn
    const provenance = normalizeProvenance(row.provenance)
    if (provenance !== undefined) dimensionScore.provenance = provenance
    return dimensionScore
  })
}

function normalizeRiskDistribution(raw: unknown) {
  const rows = asArray(raw)
  if (rows.length > 0) {
    return rows.map((item) => {
      const row = asRecord(item)
      return {
        risk_level: asRiskLevel(row.risk_level),
        count: asNumber(row.count),
      }
    })
  }
  const record = asRecord(raw)
  const localizedHigh = asNumber(record['高风险']) + asNumber(record['较高风险'])
  const localizedMedium = asNumber(record['一般风险'])
  const localizedLow = asNumber(record['低风险'])
  if (localizedHigh || localizedMedium || localizedLow) {
    return [
      { risk_level: 'high' as const, count: localizedHigh },
      { risk_level: 'medium' as const, count: localizedMedium },
      { risk_level: 'low' as const, count: localizedLow },
    ]
  }
  return (['high', 'medium', 'low'] as const).map((riskLevel) => ({
    risk_level: riskLevel,
    count: asNumber(record[riskLevel]),
  }))
}

function normalizeRiskBandDistribution(raw: unknown) {
  const record = asRecord(raw)
  return {
    高风险: asNumber(record['高风险']),
    较高风险: asNumber(record['较高风险']),
    一般风险: asNumber(record['一般风险']),
    低风险: asNumber(record['低风险']),
  }
}

function normalizeGroupDistribution(raw: unknown) {
  const rows = asArray(raw)
  if (rows.length > 0) {
    return rows.map((item) => {
      const row = asRecord(item)
      return {
        group_segment: asString(row.group_segment),
        count: asNumber(row.count),
      }
    })
  }
  const record = asRecord(raw)
  return Object.entries(record).map(([groupSegment, count]) => ({
    group_segment: groupSegment,
    count: asNumber(count),
  }))
}

function normalizeTrendSummary(raw: unknown) {
  const trendSummary = asRecord(raw)
  const trendTerms = asArray(trendSummary.terms)
  return trendTerms.map((item) => {
    const row = asRecord(item)
    const rowRiskDistribution = asRecord(row.risk_distribution)
    const highRiskCount =
      asNumber(rowRiskDistribution.high) +
      asNumber(rowRiskDistribution['高风险']) +
      asNumber(rowRiskDistribution['较高风险'])
    return {
      term: asString(row.term_key || row.term),
      high_risk_count: highRiskCount,
    }
  })
}

function normalizeRiskTrendSummary(raw: unknown) {
  const record = asRecord(raw)
  const rows = asArray(record.terms).length > 0 ? asArray(record.terms) : asArray(raw)
  return rows.map((item) => {
    const row = asRecord(item)
    const riskDistribution = asRecord(row.risk_distribution)
    const highRiskCount =
      asNumber(row.high_risk_count) +
      asNumber(riskDistribution.high) +
      asNumber(riskDistribution['高风险']) +
      asNumber(riskDistribution['较高风险'])
    const avgRiskScore =
      asOptionalNumber(row.avg_risk_score) ??
      ((asOptionalNumber(row.average_risk_probability) ?? asOptionalNumber(row.avg_risk_probability) ?? 0) * 100)
    const summary: OverviewData['risk_trend_summary'][number] = {
      term: asString(row.term || row.term_key),
      avg_risk_score: avgRiskScore,
      high_risk_count: highRiskCount,
    }
    const riskChangeDirection = asOptionalRiskChangeDirection(row.risk_change_direction)
    if (riskChangeDirection !== undefined) summary.risk_change_direction = riskChangeDirection
    return summary
  })
}

function normalizeRiskFactorSummary(raw: unknown) {
  return asArray(raw).map((item) => {
    const row = asRecord(item)
    const feature = asString(row.feature || row.dimension)
    const featureCn = asOptionalString(row.feature_cn || row.dimension)
    const summary: OverviewData['risk_factor_summary'][number] = {
      feature,
      count: asNumber(row.count),
      importance: asNumber(row.importance ?? row.impact ?? row.average_score),
    }
    if (featureCn !== undefined) summary.feature_cn = featureCn
    return summary
  })
}

function normalizeRiskChangeSummary(raw: unknown) {
  const row = asRecord(raw)
  if (Object.keys(row).length === 0) return undefined
  return {
    rising: asOptionalNumber(row.rising) ?? 0,
    steady: asOptionalNumber(row.steady) ?? 0,
    falling: asOptionalNumber(row.falling) ?? 0,
  }
}

function normalizeDimensionMetrics(raw: unknown) {
  return asArray(raw).map((item) => {
    const row = asRecord(item)
    const metric: DimensionMetric = {
      metric: asString(row.metric || row.name || row.key || row.label),
      value: asMetricValue(row.value ?? row.score ?? row.amount),
    }
    const display = asOptionalString(row.display)
    if (display !== undefined) metric.display = display
    const label = asOptionalString(row.label)
    if (label !== undefined) metric.label = label
    const thresholdStrategy = asOptionalString(row.threshold_strategy)
    if (thresholdStrategy !== undefined) metric.threshold_strategy = thresholdStrategy
    const deferredStatus = asOptionalString(row.deferred_status)
    if (deferredStatus !== undefined) metric.deferred_status = deferredStatus
    const caveat = asOptionalString(row.caveat)
    if (caveat !== undefined) metric.caveat = caveat
    return metric
  })
}

function normalizeCalibratedFactor(raw: unknown): CalibratedFactor {
  const row = asRecord(raw)
  const dimension = asString(row.dimension || row.feature_cn || row.feature)
  const count = asOptionalNumber(row.count)
  const importance = asOptionalNumber(row.importance)
  const impact = asOptionalNumber(row.impact)
  const effect = asOptionalString(row.effect)
  const direction = effect === 'negative' || effect === 'down' ? 'down' : 'up'
  const factor: CalibratedFactor = {
    dimension,
    explanation:
      asOptionalString(row.explanation) ||
      (count !== undefined || importance !== undefined
        ? `${dimension} 是当前重点关注维度，${buildFactorExplanation(count, importance)}`
        : `${dimension} 是当前重点关注维度`),
    direction,
    impact: impact ?? importance ?? 0,
  }
  const metrics = normalizeDimensionMetrics(row.metrics)
  if (metrics.length > 0) factor.metrics = metrics
  if (importance !== undefined) factor.importance = importance
  if (count !== undefined) factor.count = count
  const label = asOptionalString(row.label)
  if (label !== undefined) factor.label = label
  const feature = asOptionalString(row.feature)
  if (feature !== undefined) factor.feature = feature
  const featureCn = asOptionalString(row.feature_cn)
  if (featureCn !== undefined) factor.feature_cn = featureCn
  if (effect !== undefined) factor.effect = effect
  const dimensionCode = asOptionalString(row.dimension_code)
  if (dimensionCode !== undefined) factor.dimension_code = dimensionCode
  return factor
}

function normalizeProvenance(raw: unknown) {
  const record = asRecord(raw)
  const keys = Object.keys(record)
  if (keys.length === 0) return undefined
  const provenance: NonNullable<CalibratedDimensionScore['provenance']> = {}
  const hasCaveatedMetrics = asOptionalBoolean(record.has_caveated_metrics)
  if (hasCaveatedMetrics !== undefined) provenance.has_caveated_metrics = hasCaveatedMetrics
  const hasDeferredMetrics = asOptionalBoolean(record.has_deferred_metrics)
  if (hasDeferredMetrics !== undefined) provenance.has_deferred_metrics = hasDeferredMetrics
  const thresholdStrategies = asArray(record.threshold_strategies).map((item) => asString(item)).filter(Boolean)
  if (thresholdStrategies.length > 0) provenance.threshold_strategies = thresholdStrategies
  return provenance
}

function normalizeScore(score: number) {
  if (score > 1) return Number((score / 100).toFixed(4))
  return score
}

function buildFactorExplanation(count?: number, importance?: number) {
  if (count !== undefined && importance !== undefined) return `覆盖 ${count} 人，重要度 ${importance.toFixed(2)}`
  if (count !== undefined) return `覆盖 ${count} 人`
  if (importance !== undefined) return `重要度 ${importance.toFixed(2)}`
  return '当前群体的主要影响因子'
}

function asArray(value: unknown) {
  return Array.isArray(value) ? value : []
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' && !Array.isArray(value) ? (value as Record<string, unknown>) : {}
}

function asString(value: unknown) {
  return typeof value === 'string' ? value : ''
}

function asNumber(value: unknown) {
  return typeof value === 'number' && Number.isFinite(value) ? value : 0
}

function asOptionalNumber(value: unknown) {
  return typeof value === 'number' && Number.isFinite(value) ? value : undefined
}

function asOptionalString(value: unknown) {
  return typeof value === 'string' && value ? value : undefined
}

function asOptionalBoolean(value: unknown) {
  return typeof value === 'boolean' ? value : undefined
}

function asMetricValue(value: unknown): number | string {
  if (typeof value === 'number' && Number.isFinite(value)) return value
  if (typeof value === 'string' && value) return value
  return 0
}

function asRiskLevel(value: unknown): RiskLevel {
  return asOptionalRiskLevel(value) ?? 'low'
}

function asOptionalRiskLevel(value: unknown): RiskLevel | undefined {
  return value === 'high' ||
    value === 'medium' ||
    value === 'low' ||
    value === '高风险' ||
    value === '较高风险' ||
    value === '一般风险' ||
    value === '低风险'
    ? value
    : undefined
}

function asOptionalRiskChangeDirection(value: unknown): RiskChangeDirection | undefined {
  return value === 'rising' || value === 'steady' || value === 'falling' ? value : undefined
}
