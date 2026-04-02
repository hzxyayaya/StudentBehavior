import { RouterLinkStub, flushPromises, mount } from '@vue/test-utils'
import { QueryClient, VueQueryPlugin } from '@tanstack/vue-query'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { createRouter as createAppRouter } from '@/app/router'
import { useAuthStore } from '@/app/auth'
import OverviewPage from '@/features/overview/OverviewPage.vue'
import GroupsPage from '@/features/quadrants/QuadrantsPage.vue'
import StudentPage from '@/features/students/StudentPage.vue'
import WarningsPage from '@/features/warnings/WarningsPage.vue'

function createPlugins() {
  const router = createAppRouter()
  const vueQueryPlugin: [typeof VueQueryPlugin, { queryClient: QueryClient }] = [VueQueryPlugin, { queryClient: new QueryClient() }]
  return { router, vueQueryPlugin }
}

describe('demo flow links', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    sessionStorage.clear()
  })

  it('links major risk summary to high-risk warnings for the same major', async () => {
    const auth = useAuthStore()
    auth.signIn('demo-token', '演示管理员', '2024-2')

    vi.stubGlobal(
      'fetch',
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input)

        if (url.includes('/analytics/overview')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({
              code: 200,
              message: 'OK',
              data: {
                student_count: 179,
                risk_distribution: [
                  { risk_level: 'high', count: 12 },
                  { risk_level: 'medium', count: 34 },
                  { risk_level: 'low', count: 133 },
                ],
                risk_band_distribution: { 高风险: 12, 较高风险: 24, 一般风险: 40, 低风险: 103 },
                group_distribution: [
                  { group_segment: '学习投入稳定组', count: 45 },
                  { group_segment: '综合发展优势组', count: 51 },
                  { group_segment: '作息失衡风险组', count: 39 },
                  { group_segment: '课堂参与薄弱组', count: 44 },
                ],
                major_risk_summary: [
                  { major_name: '计算机科学与技术', high_risk_count: 5, student_count: 18 },
                ],
                trend_summary: [
                  { term: '2024-1', high_risk_count: 10 },
                  { term: '2024-2', high_risk_count: 12 },
                ],
                risk_trend_summary: [
                  { term: '2024-1', avg_risk_score: 48.2, high_risk_count: 10, risk_change_direction: 'rising' },
                  { term: '2024-2', avg_risk_score: 51.7, high_risk_count: 12, risk_change_direction: 'rising' },
                ],
                risk_factor_summary: [
                  { feature: 'academic_base', feature_cn: '学业基础表现', count: 52, importance: 0.82 },
                  { feature: 'class_engagement', feature_cn: '课堂学习投入', count: 43, importance: 0.64 },
                ],
                dimension_summary: [
                  {
                    dimension: '学业基础表现',
                    score: 82,
                    level: 'high',
                    label: '学业基础稳健',
                    explanation: '学期 GPA 保持稳定。',
                    metrics: [{ metric: '学期GPA', value: 3.1, display: '3.1' }],
                  },
                  {
                    dimension: '课堂学习投入',
                    score: 74,
                    level: 'medium',
                    label: '课堂投入一般',
                    explanation: '出勤较稳但课堂参与仍有提升空间。',
                    metrics: [{ metric: '全勤率', value: 0.87, display: '87%' }],
                  },
                ],
              },
              meta: { request_id: 'req-overview', term: '2024-2' },
            }),
          })
        }

        return Promise.resolve({
          ok: true,
          json: async () => ({
            code: 200,
            message: 'OK',
            data: {
              cluster_method: 'stub-group-rules',
              risk_model: 'stub-risk-rules',
              target_label: '综合测评低等级风险',
              auc: 0.81,
              updated_at: '2026-03-28T12:00:00+08:00',
            },
            meta: { request_id: 'req-summary', term: '2024-2' },
          }),
        })
      }),
    )

    const { router, vueQueryPlugin } = createPlugins()
    await router.push('/overview')
    await router.isReady()

    const wrapper = mount(OverviewPage, {
      global: {
        plugins: [router, vueQueryPlugin],
        stubs: { RouterLink: RouterLinkStub, EChart: { template: '<div class="echart-stub" />' } },
      },
    })

    await flushPromises()
    await flushPromises()

    const links = wrapper.findAllComponents(RouterLinkStub)
    const majorLink = links.find((link) => link.text().includes('计算机科学与技术'))

    expect(majorLink).toBeTruthy()
    expect(majorLink!.props('to')).toEqual({
      path: '/warnings',
      query: {
        term: '2024-2',
        risk_level: 'high',
        major_name: '计算机科学与技术',
      },
    })
    const overviewCards = wrapper.findAll('.dimension-detail-card')
    const [firstOverviewCard, secondOverviewCard] = overviewCards
    if (!firstOverviewCard || !secondOverviewCard) {
      throw new Error('missing overview dimension cards')
    }

    expect(overviewCards).toHaveLength(2)
    expect(firstOverviewCard.text()).toContain('学业基础表现')
    expect(firstOverviewCard.text()).toContain('高')
    expect(firstOverviewCard.text()).toContain('82分')
    expect(firstOverviewCard.text()).toContain('学业基础稳健')
    expect(firstOverviewCard.text()).toContain('学期GPA')
    expect(firstOverviewCard.text()).toContain('3.1')
    expect(firstOverviewCard.text()).toContain('学期 GPA 保持稳定。')
    expect(secondOverviewCard.text()).toContain('课堂学习投入')
    expect(secondOverviewCard.text()).toContain('中')
    expect(secondOverviewCard.text()).toContain('74分')
    expect(secondOverviewCard.text()).toContain('课堂投入一般')
    expect(secondOverviewCard.text()).toContain('出勤较稳但课堂参与仍有提升空间。')
    expect(wrapper.text()).toContain('学业风险四档分布')
    expect(wrapper.text()).toContain('较高风险')
    expect(wrapper.text()).toContain('24')
    expect(wrapper.text()).toContain('风险趋势摘要')
    expect(wrapper.text()).toContain('2024-1')
    expect(wrapper.text()).toContain('风险因素 Top')
    expect(wrapper.text()).toContain('学业基础表现')
  })

  it('keeps warning filters in the back link on student page', async () => {
    const auth = useAuthStore()
    auth.signIn('demo-token', '演示管理员', '2024-2')

    vi.stubGlobal(
      'fetch',
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input)

        if (url.includes('/profile')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({
              code: 200,
              message: 'OK',
              data: {
                student_id: 'pjwrqxbj901',
                student_name: '示例学生',
                major_name: '计算机科学与技术',
                group_segment: '作息失衡风险组',
                risk_level: '较高风险',
                risk_probability: 0.82,
                base_risk_score: 76,
                risk_adjustment_score: 6,
                adjusted_risk_score: 82,
                risk_delta: 2,
                risk_change_direction: 'rising',
                base_risk_explanation: '基础风险主要来自核心课程成绩下滑。',
                behavior_adjustment_explanation: '行为表现使风险上调 6 分，重点集中在出勤与课堂参与。',
                risk_change_explanation: '较上学期继续上升，需要立即跟进。',
                dimension_scores: [
                  {
                    dimension: '课堂学习投入',
                    score: 0.26,
                    level: 'low',
                    label: '课堂投入不足',
                    explanation: '迟到与缺勤较多。',
                    metrics: [{ metric: '迟到次数', value: 6, display: '6 次' }],
                  },
                ],
                trend: [{ term: '2024-2', risk_probability: 0.82 }],
              },
              meta: { request_id: 'req-profile', term: '2024-2' },
            }),
          })
        }

        return Promise.resolve({
          ok: true,
          json: async () => ({
            code: 200,
            message: 'OK',
              data: {
                top_factors: [
                  {
                    dimension: '课堂学习投入',
                  explanation: '课堂参与下降',
                  direction: 'up',
                  impact: 0.21,
                  label: '课堂投入不足',
                  metrics: [{ metric: '迟到次数', value: 6, display: '6 次' }],
                  },
                ],
                base_risk_explanation: '基础风险主要来自核心课程成绩下滑。',
                behavior_adjustment_explanation: '行为表现使风险上调 6 分，重点集中在出勤与课堂参与。',
                risk_change_explanation: '较上学期继续上升，需要立即跟进。',
                intervention_advice: ['安排阶段性学习跟踪'],
                intervention_plan: '较高风险干预计划：\n1. 每周复盘课堂参与。\n2. 联动辅导员跟进作业完成。',
                report_text: '当前学生处于较高风险。',
                risk_level: '较高风险',
                risk_delta: 2,
                risk_change_direction: 'rising',
              },
              meta: { request_id: 'req-report', term: '2024-2' },
            }),
          })
      }),
    )

    const { router, vueQueryPlugin } = createPlugins()
    await router.push(
      '/students/pjwrqxbj901?term=2024-2&source=warnings&page=2&risk_level=high&group_segment=' +
        encodeURIComponent('作息失衡风险组') +
        '&major_name=' +
        encodeURIComponent('计算机科学与技术') +
        '&risk_change_direction=rising',
    )
    await router.isReady()

    const wrapper = mount(StudentPage, {
      global: {
        plugins: [router, vueQueryPlugin],
        stubs: { RouterLink: RouterLinkStub, EChart: { template: '<div class="echart-stub" />' } },
      },
    })

    await flushPromises()
    await flushPromises()

    const backLink = wrapper.findAllComponents(RouterLinkStub).find((link) => link.text().includes('返回预警列表'))
    const dimensionCards = wrapper.findAll('.dimension-card')
    const [firstDimensionCard] = dimensionCards
    if (!firstDimensionCard) {
      throw new Error('missing student dimension card')
    }

    expect(backLink).toBeTruthy()
    expect(backLink!.props('to')).toEqual({
      path: '/warnings',
      query: {
        term: '2024-2',
        page: '2',
        risk_level: 'high',
        group_segment: '作息失衡风险组',
        major_name: '计算机科学与技术',
        risk_change_direction: 'rising',
      },
    })
    expect(dimensionCards).toHaveLength(1)
    expect(firstDimensionCard.text()).toContain('课堂学习投入')
    expect(firstDimensionCard.text()).toContain('低')
    expect(firstDimensionCard.text()).toContain('课堂投入不足')
    expect(firstDimensionCard.text()).toContain('26分')
    expect(firstDimensionCard.text()).toContain('迟到次数')
    expect(firstDimensionCard.text()).toContain('6 次')
    expect(firstDimensionCard.text()).toContain('迟到与缺勤较多。')
    expect(wrapper.text()).toContain('课堂参与下降')
    expect(wrapper.text()).toContain('基础风险主要来自核心课程成绩下滑。')
    expect(wrapper.text()).toContain('行为表现使风险上调 6 分')
    expect(wrapper.text()).toContain('较高风险干预计划')
  })

  it('fetches all coarse high-risk pages and computes exact 高风险 pagination client-side', async () => {
    const auth = useAuthStore()
    auth.signIn('demo-token', '演示管理员', '2024-2')

    const highRiskRisingItems = Array.from({ length: 11 }, (_, index) => ({
      student_id: `high-${index + 1}`,
      student_name: `高风险学生${index + 1}`,
      major_name: '计算机科学与技术',
      group_segment: '作息失衡风险组',
      risk_level: '高风险',
      risk_probability: 0.95 - index * 0.01,
      base_risk_score: 86,
      risk_adjustment_score: 4,
      adjusted_risk_score: 90 - index * 0.2,
      risk_delta: 3,
      risk_change_direction: 'rising',
      top_risk_factors: [
        { feature: 'academic_base', feature_cn: '学业基础表现', dimension: '学业基础表现', importance: 0.9 },
      ],
      top_protective_factors: [
        { feature: 'library_immersion', feature_cn: '图书馆沉浸度', dimension: '图书馆沉浸度', importance: 0.2 },
      ],
    }))
    const elevatedRiskRisingItems = Array.from({ length: 10 }, (_, index) => ({
      ...highRiskRisingItems[0],
      student_id: `elevated-${index + 1}`,
      student_name: `较高风险学生${index + 1}`,
      risk_level: '较高风险',
      adjusted_risk_score: 72 - index * 0.2,
      risk_change_direction: 'rising',
    }))

    const backendItems = [...highRiskRisingItems, ...elevatedRiskRisingItems]
    const page1Items = backendItems.slice(0, 20)
    const page2Items = backendItems.slice(20)

    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input)

      if (url.includes('/warnings?') && url.includes('risk_level=high') && url.includes('risk_change_direction=rising')) {
        const page = Number(new URL(url, 'http://localhost').searchParams.get('page') ?? '1')
        return Promise.resolve({
          ok: true,
          json: async () => ({
            code: 200,
            message: 'OK',
            data: {
              items: page === 1 ? page1Items : page2Items,
              page,
              page_size: 20,
              total: backendItems.length,
            },
            meta: { request_id: 'req-warnings', term: '2024-2' },
          }),
        })
      }

      return Promise.resolve({
        ok: true,
        json: async () => ({
          code: 200,
          message: 'OK',
          data: {
            cluster_method: 'stub-group-rules',
            risk_model: 'stub-risk-rules',
            target_label: '综合测评低等级风险',
            auc: 0.81,
            updated_at: '2026-03-28T12:00:00+08:00',
          },
          meta: { request_id: 'req-summary', term: '2024-2' },
        }),
      })
    })

    vi.stubGlobal('fetch', fetchMock)

    const { router, vueQueryPlugin } = createPlugins()
    await router.push('/warnings?term=2024-2&risk_level=%E9%AB%98%E9%A3%8E%E9%99%A9&risk_change_direction=rising')
    await router.isReady()

    const wrapper = mount(WarningsPage, {
      global: {
        plugins: [router, vueQueryPlugin],
        stubs: { RouterLink: RouterLinkStub },
      },
    })

    await flushPromises()
    await flushPromises()

    const warningCalls = fetchMock.mock.calls
      .map(([requestUrl]) => String(requestUrl))
      .filter((requestUrl) => requestUrl.includes('/warnings?'))
    expect(warningCalls).toEqual([
      expect.stringContaining('/warnings?term=2024-2&page=1&page_size=20&risk_level=high&risk_change_direction=rising'),
      expect.stringContaining('/warnings?term=2024-2&page=2&page_size=20&risk_level=high&risk_change_direction=rising'),
    ])

    const text = wrapper.text()
    expect(text).toContain('共 11 条')
    expect(text).toContain('第 1 / 1 页')
    expect(text).toContain('风险分')
    expect(text).toContain('90.0')
    expect(text).toContain('+3.0')
    expect(text).toContain('学业基础表现')
    expect(text).toContain('图书馆沉浸度')
    expect(text).toContain('上升')
    expect(text).toContain('高风险学生1')
    expect(text).not.toContain('较高风险学生1')
  })

  it('renders calibrated labels, explanations, and metrics on the group page', async () => {
    const auth = useAuthStore()
    auth.signIn('demo-token', '演示管理员', '2024-2')

    vi.stubGlobal(
      'fetch',
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input)

        if (url.includes('/analytics/groups')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({
              code: 200,
              message: 'OK',
              data: {
                groups: [
                  {
                    group_segment: '作息失衡风险组',
                    student_count: 39,
                    avg_risk_probability: 0.62,
                    avg_risk_score: 57.4,
                    avg_risk_level: '较高风险',
                    risk_change_summary: { rising: 18, steady: 14, falling: 7 },
                    avg_dimension_scores: [
                      {
                        dimension: '网络作息自律指数',
                        score: 0.43,
                        level: 'low',
                        label: '网络使用偏强',
                        explanation: '月均上网时长较高，且与群体均值差距明显。',
                        metrics: [
                          { metric: '月均上网时长', value: 66, display: '66 小时' },
                          { metric: '相对学校平均值偏差', value: 0.18, display: '偏高 18%' },
                        ],
                      },
                    ],
                    top_factors: [
                      {
                        dimension: '网络作息自律指数',
                        importance: 0.75,
                        count: 39,
                        label: '网络使用偏强',
                        explanation: '覆盖 39 人，重要度 0.75',
                        metrics: [{ metric: '月均上网时长', value: 66, display: '66 小时' }],
                      },
                    ],
                    risk_amplifiers: [
                      {
                        feature: 'academic_base',
                        feature_cn: '学业基础表现',
                        count: 27,
                        importance: 0.79,
                      },
                    ],
                    protective_factors: [
                      {
                        feature: 'library_immersion',
                        feature_cn: '图书馆沉浸度',
                        count: 13,
                        importance: 0.52,
                      },
                    ],
                  },
                ],
              },
              meta: { request_id: 'req-groups', term: '2024-2' },
            }),
          })
        }

        return Promise.resolve({
          ok: true,
          json: async () => ({
            code: 200,
            message: 'OK',
            data: {
              cluster_method: 'stub-group-rules',
              risk_model: 'stub-risk-rules',
              target_label: '综合测评低等级风险',
              auc: 0.81,
              updated_at: '2026-03-28T12:00:00+08:00',
            },
            meta: { request_id: 'req-summary', term: '2024-2' },
          }),
        })
      }),
    )

    const { router, vueQueryPlugin } = createPlugins()
    await router.push('/groups')
    await router.isReady()

    const wrapper = mount(GroupsPage, {
      global: {
        plugins: [router, vueQueryPlugin],
        stubs: { RouterLink: RouterLinkStub, EChart: { template: '<div class="echart-stub" />' } },
      },
    })

    await flushPromises()
    await flushPromises()

    const groupCards = wrapper.findAll('.group-card')
    const [firstGroupCard] = groupCards
    if (!firstGroupCard) {
      throw new Error('missing group card')
    }

    expect(groupCards).toHaveLength(1)
    expect(firstGroupCard.text()).toContain('作息失衡风险组')
    expect(firstGroupCard.text()).toContain('39 人')
    expect(firstGroupCard.text()).toContain('0.62')
    expect(firstGroupCard.text()).toContain('57.4')
    expect(firstGroupCard.text()).toContain('较高风险')
    const dimensionRows = firstGroupCard.findAll('.dimension-row')
    const [firstDimensionRow] = dimensionRows
    if (!firstDimensionRow) {
      throw new Error('missing group dimension row')
    }
    expect(dimensionRows).toHaveLength(1)
    expect(firstDimensionRow.text()).toContain('网络作息自律指数')
    expect(firstDimensionRow.text()).toContain('低')
    expect(firstDimensionRow.text()).toContain('网络使用偏强')
    expect(firstDimensionRow.text()).toContain('43分')
    expect(firstDimensionRow.text()).toContain('月均上网时长')
    expect(firstDimensionRow.text()).toContain('66 小时')
    expect(firstDimensionRow.text()).toContain('相对学校平均值偏差')
    expect(firstDimensionRow.text()).toContain('偏高 18%')
    expect(firstGroupCard.text()).toContain('覆盖 39 人，重要度 0.75')
    expect(firstGroupCard.text()).toContain('风险放大因素')
    expect(firstGroupCard.text()).toContain('学业基础表现')
    expect(firstGroupCard.text()).toContain('保护性因素')
    expect(firstGroupCard.text()).toContain('图书馆沉浸度')
  })

  it('shows incomplete calibrated fields explicitly when the backend leaves them unavailable', async () => {
    const auth = useAuthStore()
    auth.signIn('demo-token', '演示管理员', '2024-2')

    vi.stubGlobal(
      'fetch',
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input)

        if (url.includes('/profile')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({
              code: 200,
              message: 'OK',
              data: {
                student_id: 'pjwrqxbj901',
                student_name: '示例学生',
                major_name: '计算机科学与技术',
                group_segment: '待校准组',
                risk_level: 'medium',
                risk_probability: 0.52,
                dimension_scores: [
                  {
                    dimension: '课堂学习投入',
                    score: 0.48,
                  },
                ],
                trend: [{ term: '2024-2', dimension_scores: [{ dimension: '课堂学习投入', score: 0.48 }] }],
              },
              meta: { request_id: 'req-profile', term: '2024-2' },
            }),
          })
        }

        return Promise.resolve({
          ok: true,
          json: async () => ({
            code: 200,
            message: 'OK',
            data: {
              top_factors: [
                {
                  dimension: '课堂学习投入',
                  explanation: '课堂参与下降',
                  direction: 'up',
                  impact: 0.21,
                },
              ],
              intervention_advice: ['安排阶段性学习跟踪'],
              report_text: '当前学生处于较高风险。',
            },
            meta: { request_id: 'req-report', term: '2024-2' },
          }),
        })
      }),
    )

    const { router, vueQueryPlugin } = createPlugins()
    await router.push('/students/pjwrqxbj901?term=2024-2')
    await router.isReady()

    const wrapper = mount(StudentPage, {
      global: {
        plugins: [router, vueQueryPlugin],
        stubs: { RouterLink: RouterLinkStub, EChart: { template: '<div class="echart-stub" />' } },
      },
    })

    await flushPromises()
    await flushPromises()

    const dimensionCards = wrapper.findAll('.dimension-card')
    const [firstIncompleteCard] = dimensionCards
    if (!firstIncompleteCard) {
      throw new Error('missing incomplete dimension card')
    }

    expect(dimensionCards).toHaveLength(1)
    expect(firstIncompleteCard.text()).toContain('课堂学习投入')
    expect(firstIncompleteCard.text()).toContain('待补充')
    expect(firstIncompleteCard.text()).toContain('48分')
    expect(firstIncompleteCard.text()).toContain('暂无指标')
    expect(firstIncompleteCard.text()).toContain('当前维度尚未提供完整校准结果')
    expect(wrapper.text()).not.toContain('低')
  })
})
