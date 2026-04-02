export type Envelope<T> = {
  code: number
  message: string
  data: T
  meta: { request_id: string; term?: string | null }
}

export type RiskLevel = 'high' | 'medium' | 'low'
export type GroupSegment = string
export type RiskChangeDirection = 'rising' | 'steady' | 'falling'

export type DimensionMetric = {
  metric: string
  value: number | string
  display?: string
  label?: string
  threshold_strategy?: string
  deferred_status?: string
  caveat?: string
}

export type CalibratedDimensionScore = {
  dimension: string
  score: number
  level?: RiskLevel
  label?: string
  metrics?: DimensionMetric[]
  explanation?: string
  average_score?: number
  dimension_code?: string
  feature?: string
  feature_cn?: string
  provenance?: {
    has_caveated_metrics?: boolean
    has_deferred_metrics?: boolean
    threshold_strategies?: string[]
  }
}

export type CalibratedFactor = {
  dimension: string
  explanation: string
  direction?: 'up' | 'down'
  impact?: number
  importance?: number
  count?: number
  label?: string
  metrics?: DimensionMetric[]
  feature?: string
  feature_cn?: string
  effect?: string
  dimension_code?: string
}

export type OverviewData = {
  student_count: number
  risk_distribution: Array<{ risk_level: RiskLevel; count: number }>
  risk_band_distribution: Record<string, number>
  group_distribution: Array<{ group_segment: GroupSegment; count: number }>
  dimension_summary: CalibratedDimensionScore[]
  major_risk_summary: Array<{ major_name: string; high_risk_count: number; student_count: number }>
  trend_summary: Array<{ term: string; high_risk_count: number }>
  risk_trend_summary: Array<{
    term: string
    avg_risk_score: number
    high_risk_count: number
    risk_change_direction?: RiskChangeDirection
  }>
  risk_factor_summary: Array<{
    feature: string
    feature_cn?: string
    count: number
    importance: number
  }>
}

export type GroupsData = {
  groups: Array<{
    group_segment: GroupSegment
    student_count: number
    avg_risk_probability: number
    avg_risk_score: number
    avg_risk_level?: string
    risk_change_summary?: Partial<Record<RiskChangeDirection, number>>
    avg_dimension_scores: CalibratedDimensionScore[]
    top_factors: CalibratedFactor[]
    risk_amplifiers: Array<{ feature: string; feature_cn?: string; count: number; importance: number }>
    protective_factors: Array<{ feature: string; feature_cn?: string; count: number; importance: number }>
  }>
}

export type WarningsData = {
  items: Array<{
    student_id: string
    student_name: string
    major_name: string
    group_segment: GroupSegment
    risk_level: RiskLevel
    risk_probability: number
  }>
  page: number
  page_size: number
  total: number
}

export type StudentProfileData = {
  student_id: string
  student_name: string
  major_name: string
  group_segment: GroupSegment
  risk_level: RiskLevel
  risk_probability: number
  dimension_scores: CalibratedDimensionScore[]
  trend: Array<{ term: string; risk_probability?: number; dimension_scores: CalibratedDimensionScore[] }>
}

export type StudentReportData = {
  top_factors: CalibratedFactor[]
  intervention_advice: string[]
  intervention_advice_items?: Array<{ title?: string; text?: string }>
  report_text: string
}

export type ModelSummaryData = {
  cluster_method: string
  risk_model: string
  target_label: string
  auc: number
  updated_at: string
}

export type DemoLoginData = {
  session_token: string
}
