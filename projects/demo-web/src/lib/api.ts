import type {
  DemoLoginData,
  Envelope,
  ModelSummaryData,
  OverviewData,
  QuadrantsData,
  StudentProfileData,
  StudentReportData,
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
  const payload = (await response.json()) as Envelope<T>
  if (!response.ok || payload.code !== 200) {
    const error = new Error(payload.message || 'request failed')
    ;(error as Error & { status?: number }).status = response.status
    throw error
  }
  return payload.data
}

export function loginDemo() {
  return request<DemoLoginData>('/auth/demo-login', {
    method: 'POST',
    body: JSON.stringify({ username: 'demo_admin', password: 'demo_only', role: 'manager' }),
  })
}

export function getOverview(term: string) {
  return request<OverviewData>(`/analytics/overview?term=${encodeURIComponent(term)}`)
}

export function getQuadrants(term: string) {
  return request<QuadrantsData>(`/analytics/quadrants?term=${encodeURIComponent(term)}`)
}

export function getWarnings(params: {
  term: string
  page: number
  page_size: number
  risk_level?: string | null
  quadrant_label?: string | null
  major_name?: string | null
}) {
  const search = new URLSearchParams({
    term: params.term,
    page: String(params.page),
    page_size: String(params.page_size),
  })
  if (params.risk_level) search.set('risk_level', params.risk_level)
  if (params.quadrant_label) search.set('quadrant_label', params.quadrant_label)
  if (params.major_name) search.set('major_name', params.major_name)
  return request<WarningsData>(`/warnings?${search.toString()}`)
}

export function getStudentProfile(studentId: string, term: string) {
  return request<StudentProfileData>(`/students/${encodeURIComponent(studentId)}/profile?term=${encodeURIComponent(term)}`)
}

export function getStudentReport(studentId: string, term: string) {
  return request<StudentReportData>(`/students/${encodeURIComponent(studentId)}/report?term=${encodeURIComponent(term)}`)
}

export function getModelSummary(term: string) {
  return request<ModelSummaryData>(`/models/summary?term=${encodeURIComponent(term)}`)
}
