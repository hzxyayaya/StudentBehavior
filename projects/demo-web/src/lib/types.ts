export type Envelope<T> = {
  code: number
  message: string
  data: T
  meta: { request_id: string; term?: string | null }
}

export type RiskLevel = 'high' | 'medium' | 'low' | '高风险' | '较高风险' | '一般风险' | '低风险'
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

export type WarningFactor = {
  feature: string
  feature_cn?: string
  dimension?: string
  importance?: number
}

export type OverviewData = {
  student_count: number
  risk_distribution: Array<{ risk_level: RiskLevel; count: number }>
  risk_band_distribution: Record<string, number>
  group_distribution: Array<{ group_segment: GroupSegment; count: number }>
  dimension_summary: CalibratedDimensionScore[]
  major_risk_summary: Array<{
    major_name: string
    high_risk_count: number
    elevated_risk_count?: number
    elevated_risk_ratio?: number
    student_count: number
    average_risk_probability?: number
  }>
  trend_summary: Array<{ term: string; high_risk_count: number }>
  risk_trend_summary: Array<{
    term: string
    avg_risk_score: number
    high_risk_count: number
    elevated_risk_count?: number
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
    term_gpa?: number
    failed_course_count?: number
    borderline_course_count?: number
    failed_course_ratio?: number
    academic_risk_score?: number
    academic_risk_level?: RiskLevel
    behavior_risk_score?: number
    behavior_risk_level?: RiskLevel
    intervention_priority_score?: number
    intervention_priority_level?: RiskLevel
    base_risk_score?: number
    risk_adjustment_score?: number
    adjusted_risk_score?: number
    risk_delta?: number
    risk_change_direction?: RiskChangeDirection
    top_risk_factors: WarningFactor[]
    top_protective_factors: WarningFactor[]
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
  term_gpa?: number
  failed_course_count?: number
  borderline_course_count?: number
  failed_course_ratio?: number
  academic_risk_score?: number
  academic_risk_level?: RiskLevel
  behavior_risk_score?: number
  behavior_risk_level?: RiskLevel
  intervention_priority_score?: number
  intervention_priority_level?: RiskLevel
  base_risk_score?: number
  risk_adjustment_score?: number
  adjusted_risk_score?: number
  risk_delta?: number
  risk_change_direction?: RiskChangeDirection
  base_risk_explanation?: string
  behavior_adjustment_explanation?: string
  risk_change_explanation?: string
  dimension_scores: CalibratedDimensionScore[]
  trend: Array<{
    term: string
    risk_level?: RiskLevel
    risk_probability?: number
    adjusted_risk_score?: number
    risk_delta?: number
    risk_change_direction?: RiskChangeDirection
    dimension_scores: CalibratedDimensionScore[]
  }>
}

export type StudentReportData = {
  term?: string
  top_factors: CalibratedFactor[]
  base_risk_explanation?: string
  behavior_adjustment_explanation?: string
  risk_change_explanation?: string
  intervention_advice: string[]
  intervention_advice_items?: Array<{ title?: string; text?: string }>
  intervention_plan?: string | string[]
  report_text: string
  report_source?: string
  prompt_version?: string
  report_generation?: Record<string, unknown>
  risk_level?: RiskLevel
  risk_probability?: number
  base_risk_score?: number
  risk_adjustment_score?: number
  adjusted_risk_score?: number
  risk_delta?: number
  risk_change_direction?: RiskChangeDirection
  trend?: Array<{
    term: string
    risk_level?: RiskLevel
    risk_probability?: number
    base_risk_score?: number
    risk_adjustment_score?: number
    adjusted_risk_score?: number
    risk_delta?: number
    risk_change_direction?: RiskChangeDirection
  }>
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

export type TrajectoryAnalysisData = {
  term: string
  risk_trend_summary: Array<{
    term: string
    avg_risk_score: number
    high_risk_count: number
    elevated_risk_count?: number
    risk_change_direction?: RiskChangeDirection
  }>
  key_factors: Array<{
    feature: string
    feature_cn?: string
    count: number
    importance: number
  }>
  current_dimensions: CalibratedDimensionScore[]
  group_changes: GroupsData['groups']
  student_samples: WarningsData['items']
}

export type DestinationDistribution = Record<string, number>

export type MajorDestinationSummaryRow = {
  major_name: string
  student_count: number
  destination_student_count: number
  top_destination_label?: string
  top_destination_count?: number
  destination_distribution: DestinationDistribution
}

export type GroupDestinationAssociationRow = {
  group_segment: string
  destination_label?: string
  student_count: number
  group_student_count?: number
  share_within_group?: number
}

export type DevelopmentAnalysisData = {
  term: string
  major_comparison: OverviewData['major_risk_summary']
  destination_distribution: DestinationDistribution
  major_destination_summary: MajorDestinationSummaryRow[]
  group_destination_association: GroupDestinationAssociationRow[]
  dimension_highlights: CalibratedDimensionScore[]
  group_direction_segments: Array<
    GroupsData['groups'][number] & {
      direction_label?: string
    }
  >
  direction_chains: Array<{
    group_segment: string
    direction_label?: string
    leading_protective_factor?: string | null
    leading_dimension?: string | null
    avg_risk_score?: number
  }>
  disclaimer: string
}
