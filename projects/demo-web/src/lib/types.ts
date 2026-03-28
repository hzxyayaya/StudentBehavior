export type Envelope<T> = {
  code: number
  message: string
  data: T
  meta: { request_id: string; term?: string | null }
}

export type RiskLevel = 'high' | 'medium' | 'low'
export type QuadrantLabel = '自律共鸣型' | '被动守纪型' | '脱节离散型' | '情绪驱动型'

export type OverviewData = {
  student_count: number
  risk_distribution: Array<{ risk_level: RiskLevel; count: number }>
  quadrant_distribution: Array<{ quadrant_label: QuadrantLabel; count: number }>
  major_risk_summary: Array<{ major_name: string; high_risk_count: number; student_count: number }>
  trend_summary: Array<{ term: string; high_risk_count: number }>
}

export type QuadrantsData = {
  quadrants: Array<{
    quadrant_label: QuadrantLabel
    student_count: number
    avg_risk_probability: number
    top_factors: Array<{ dimension: string; explanation: string }>
  }>
}

export type WarningsData = {
  items: Array<{
    student_id: string
    student_name: string
    major_name: string
    quadrant_label: QuadrantLabel
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
  quadrant_label: QuadrantLabel
  risk_level: RiskLevel
  risk_probability: number
  dimension_scores: Array<{ dimension: string; score: number }>
  trend: Array<{ term: string; risk_probability: number }>
}

export type StudentReportData = {
  top_factors: Array<{ dimension: string; explanation: string; direction: 'up' | 'down'; impact: number }>
  intervention_advice: string[]
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
  user_id: string
  display_name: string
  role: string
  session_token: string
}
