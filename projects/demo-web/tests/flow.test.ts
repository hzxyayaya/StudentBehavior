import { RouterLinkStub, flushPromises, mount } from '@vue/test-utils'
import { QueryClient, VueQueryPlugin } from '@tanstack/vue-query'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { createRouter as createAppRouter } from '@/app/router'
import { useAuthStore } from '@/app/auth'
import OverviewPage from '@/features/overview/OverviewPage.vue'
import DevelopmentPage from '@/features/development/DevelopmentPage.vue'
import GroupsPage from '@/features/quadrants/QuadrantsPage.vue'
import StudentPage from '@/features/students/StudentPage.vue'
import TrajectoryPage from '@/features/trajectory/TrajectoryPage.vue'
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

  it('renders overview summary cards from the current overview payload', async () => {
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
        stubs: {
          RouterLink: RouterLinkStub,
          EChart: { template: '<div class="echart-stub" />' },
          LazyEChart: { template: '<div class="echart-stub" />' },
        },
      },
    })

    await flushPromises()
    await flushPromises()

    const overviewCards = wrapper.findAll('.dimension-detail-card')
    const summaryRows = wrapper.findAll('.summary-row')
    const [firstOverviewCard, secondOverviewCard] = overviewCards
    if (!firstOverviewCard || !secondOverviewCard) {
      throw new Error('missing overview dimension cards')
    }

    expect(overviewCards).toHaveLength(8)
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
    expect(wrapper.text()).toContain('在线学习积极性')
    expect(wrapper.text()).toContain('当前学期无有效数据')
    expect(wrapper.text()).toContain('干预优先级分级概览')
    expect(wrapper.text()).toContain('较高优先')
    expect(wrapper.text()).toContain('趋势')
    expect(wrapper.text()).toContain('2024-1')
    expect(wrapper.text()).toContain('当前学期 Top 影响因素')
    expect(wrapper.text()).toContain('学业基础表现')
    expect(summaryRows).toHaveLength(5)
    expect(wrapper.text()).toContain('风险模型')
    expect(wrapper.text()).toContain('stub-risk-rules')
    expect(wrapper.text()).not.toContain('模型来源')
    expect(wrapper.text()).not.toContain('Accuracy')
  })

  it('renders trained model summary extras when the backend includes them', async () => {
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
                student_count: 12,
                risk_distribution: [
                  { risk_level: 'high', count: 2 },
                  { risk_level: 'medium', count: 3 },
                  { risk_level: 'low', count: 7 },
                ],
                risk_band_distribution: { 高风险: 2, 较高风险: 1, 一般风险: 3, 低风险: 6 },
                group_distribution: [{ group_segment: '学习投入稳定组', count: 12 }],
                major_risk_summary: [],
                trend_summary: [{ term: '2024-2', high_risk_count: 2 }],
                risk_trend_summary: [{ term: '2024-2', avg_risk_score: 49.5, high_risk_count: 2, risk_change_direction: 'steady' }],
                risk_factor_summary: [{ feature: 'academic_base', feature_cn: '学业基础表现', count: 6, importance: 0.74 }],
                dimension_summary: [
                  {
                    dimension: '学业基础表现',
                    score: 82,
                    level: 'high',
                    label: '学业基础稳健',
                    explanation: '学期 GPA 保持稳定。',
                    metrics: [{ metric: '学期GPA', value: 3.2, display: '3.2' }],
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
              cluster_method: 'stub-eight-dimension-group-rules',
              risk_model: 'trained-academic-risk-model',
              target_label: '综合测评低等级风险',
              auc: 0.9342,
              updated_at: '2026-04-09T09:00:00Z',
              source: 'trained',
              accuracy: 0.88,
              precision: 0.81,
              recall: 0.79,
              f1: 0.8,
              sample_count: 200,
              positive_sample_count: 64,
              negative_sample_count: 136,
              train_sample_count: 120,
              valid_sample_count: 30,
              test_sample_count: 50,
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
        stubs: {
          RouterLink: RouterLinkStub,
          EChart: { template: '<div class="echart-stub" />' },
          LazyEChart: { template: '<div class="echart-stub" />' },
        },
      },
    })

    await flushPromises()
    await flushPromises()

    const summaryRows = wrapper.findAll('.summary-row')

    expect(summaryRows).toHaveLength(16)
    expect(wrapper.text()).toContain('模型来源')
    expect(wrapper.text()).toContain('trained')
    expect(wrapper.text()).toContain('Accuracy')
    expect(wrapper.text()).toContain('0.8800')
    expect(wrapper.text()).toContain('Precision')
    expect(wrapper.text()).toContain('0.8100')
    expect(wrapper.text()).toContain('Recall')
    expect(wrapper.text()).toContain('0.7900')
    expect(wrapper.text()).toContain('F1')
    expect(wrapper.text()).toContain('0.8000')
    expect(wrapper.text()).toContain('总样本数')
    expect(wrapper.text()).toContain('200')
    expect(wrapper.text()).toContain('正样本数')
    expect(wrapper.text()).toContain('64')
    expect(wrapper.text()).toContain('负样本数')
    expect(wrapper.text()).toContain('136')
    expect(wrapper.text()).toContain('训练样本数')
    expect(wrapper.text()).toContain('120')
    expect(wrapper.text()).toContain('验证样本数')
    expect(wrapper.text()).toContain('30')
    expect(wrapper.text()).toContain('测试样本数')
    expect(wrapper.text()).toContain('50')
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
        stubs: {
          RouterLink: RouterLinkStub,
          EChart: { template: '<div class="echart-stub" />' },
          LazyEChart: { template: '<div class="echart-stub" />' },
        },
      },
    })

    await flushPromises()
    await flushPromises()

    const backLink = wrapper.findAllComponents(RouterLinkStub).find((link) => link.text().includes('返回预警列表'))
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
    await wrapper.find('.detail-toggle').trigger('click')
    await flushPromises()

    const radarDetailItems = wrapper.findAll('.radar-detail-item')
    expect(radarDetailItems).toHaveLength(1)
    expect(radarDetailItems[0]?.text()).toContain('课堂学习投入')
    expect(radarDetailItems[0]?.text()).toContain('低')
    expect(radarDetailItems[0]?.text()).toContain('课堂投入不足')
    expect(radarDetailItems[0]?.text()).toContain('26分')
    expect(wrapper.text()).toContain('课堂参与下降')
    expect(wrapper.text()).toContain('基础风险主要来自核心课程成绩下滑。')
    expect(wrapper.text()).toContain('行为表现使风险上调 6 分')
    expect(wrapper.text()).toContain('较高风险干预计划')
  })

  it('shows report source metadata on the student page only when the report includes it', async () => {
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
                },
              ],
              intervention_advice: ['安排阶段性学习跟踪'],
              report_text: '当前学生处于较高风险。',
              report_source: 'llm_stub',
              prompt_version: 'prompt-v3',
              report_generation: {
                model: 'stub-llm',
                generated_at: '2026-04-09T09:00:00Z',
              },
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
        stubs: {
          RouterLink: RouterLinkStub,
          EChart: { template: '<div class="echart-stub" />' },
          LazyEChart: { template: '<div class="echart-stub" />' },
        },
      },
    })

    await flushPromises()
    await flushPromises()

    expect(wrapper.text()).toContain('报告来源')
    expect(wrapper.text()).toContain('llm_stub')
    expect(wrapper.text()).toContain('prompt-v3')
    expect(wrapper.text()).toContain('stub-llm')
    expect(wrapper.text()).toContain('2026-04-09')
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
        stubs: {
          RouterLink: RouterLinkStub,
          EChart: { template: '<div class="echart-stub" />' },
          LazyEChart: { template: '<div class="echart-stub" />' },
        },
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
    expect(firstGroupCard.text()).toContain('风险放大因素')
    expect(firstGroupCard.text()).toContain('学业基础表现')
    expect(firstGroupCard.text()).toContain('保护性因素')
    await firstGroupCard.findAll('button').find((button) => button.text().includes('保护性因素'))?.trigger('click')
    await flushPromises()
    expect(firstGroupCard.text()).toContain('图书馆沉浸度')
    await firstGroupCard.findAll('button').find((button) => button.text().includes('主导因素'))?.trigger('click')
    await flushPromises()

    expect(firstGroupCard.text()).toContain('覆盖 39 人，重要度 0.75')
    expect(firstGroupCard.text()).toContain('月均上网时长')
    expect(firstGroupCard.text()).toContain('66 小时')
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
        stubs: {
          RouterLink: RouterLinkStub,
          EChart: { template: '<div class="echart-stub" />' },
          LazyEChart: { template: '<div class="echart-stub" />' },
        },
      },
    })

    await flushPromises()
    await flushPromises()

    await wrapper.find('.detail-toggle').trigger('click')
    await flushPromises()

    const radarDetailItems = wrapper.findAll('.radar-detail-item')
    const [firstIncompleteCard] = radarDetailItems
    if (!firstIncompleteCard) {
      throw new Error('missing incomplete radar detail item')
    }

    expect(radarDetailItems).toHaveLength(1)
    expect(firstIncompleteCard.text()).toContain('课堂学习投入')
    expect(firstIncompleteCard.text()).toContain('待补充')
    expect(firstIncompleteCard.text()).toContain('48分')
    expect(wrapper.text()).not.toContain('报告来源')
    expect(wrapper.text()).not.toContain('低')
  })
})

describe('task pages', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    sessionStorage.clear()
  })

  it('renders trajectory analysis from task endpoint data', async () => {
    const auth = useAuthStore()
    auth.signIn('demo-token', '演示管理员', '2024-2')

    vi.stubGlobal(
      'fetch',
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input)

        if (url.includes('/analytics/trajectory')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({
              code: 200,
              message: 'OK',
              data: {
                term: '2024-2',
                risk_trend_summary: [
                  { term: '2023-2', avg_risk_score: 46.2, high_risk_count: 9, risk_change_direction: 'steady' },
                  { term: '2024-1', avg_risk_score: 49.5, high_risk_count: 11, risk_change_direction: 'rising' },
                  { term: '2024-2', avg_risk_score: 53.1, high_risk_count: 18, risk_change_direction: 'rising' },
                ],
                key_factors: [
                  { feature: 'academic_base', feature_cn: '学业基础表现', count: 52, importance: 0.82 },
                  { feature: 'class_engagement', feature_cn: '课堂学习投入', count: 41, importance: 0.66 },
                ],
                current_dimensions: [
                  { dimension: '学业基础表现', average_score: 0.7, level: 'high', label: '学业基础稳健' },
                  { dimension: '课堂学习投入', average_score: 0.28, level: 'medium', label: '课堂投入一般' },
                ],
                group_changes: [
                  {
                    group_segment: '作息失衡风险组',
                    student_count: 39,
                    avg_risk_probability: 0.71,
                    avg_risk_score: 62.3,
                    risk_change_summary: { rising: 18, steady: 12, falling: 9 },
                    avg_dimension_scores: [],
                    top_factors: [
                      { dimension: '网络作息自律指数', explanation: '夜间活动偏高', importance: 0.81 },
                    ],
                    risk_amplifiers: [{ feature: 'network_habits', feature_cn: '网络作息自律指数', count: 20, importance: 0.81 }],
                    protective_factors: [],
                  },
                ],
                student_samples: [
                  {
                    student_id: 'pjwrqxbj901',
                    student_name: '示例学生',
                    major_name: '计算机科学与技术',
                    group_segment: '作息失衡风险组',
                    risk_level: '较高风险',
                    risk_probability: 0.82,
                    adjusted_risk_score: 82,
                    risk_delta: 2,
                    risk_change_direction: 'rising',
                    top_risk_factors: [
                      { feature: 'network_habits', feature_cn: '网络作息自律指数', importance: 0.81 },
                      { feature: 'class_engagement', feature_cn: '课堂学习投入', importance: 0.66 },
                    ],
                    top_protective_factors: [
                      { feature: 'academic_base', feature_cn: '学业基础表现', importance: 0.42 },
                    ],
                  },
                ],
              },
              meta: { request_id: 'req-trajectory', term: '2024-2' },
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
    await router.push('/trajectory')
    await router.isReady()

    const wrapper = mount(TrajectoryPage, {
      global: {
        plugins: [router, vueQueryPlugin],
        stubs: {
          RouterLink: RouterLinkStub,
          EChart: { template: '<div class="echart-stub" />' },
          LazyEChart: { template: '<div class="echart-stub" />' },
        },
      },
    })

    await flushPromises()
    await flushPromises()

    expect(wrapper.text()).toContain('学期轨迹与关键因子')
    expect(wrapper.text()).toContain('2024-2')
    expect(wrapper.text()).toContain('学业基础表现')
    expect(wrapper.text()).toContain('作息失衡风险组')
    expect(wrapper.text()).toContain('网络作息自律指数')
    expect(wrapper.text()).toContain('重点学生样本轨迹')
    expect(wrapper.text()).toContain('示例学生')
    expect(wrapper.text()).toContain('0.82')
    expect(wrapper.text()).toContain('课堂学习投入')
  })

  it('renders development analysis with task endpoint data', async () => {
    const auth = useAuthStore()
    auth.signIn('demo-token', '演示管理员', '2024-2')

    vi.stubGlobal(
      'fetch',
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input)

        if (url.includes('/analytics/development')) {
          return Promise.resolve({
            ok: true,
            json: async () => ({
              code: 200,
              message: 'OK',
              data: {
                term: '2024-2',
                major_comparison: [
                  { major_name: '计算机科学与技术', high_risk_count: 5, student_count: 18 },
                  { major_name: '软件工程', high_risk_count: 3, student_count: 21 },
                ],
                destination_distribution: { 升学: 18, 企业就业: 9 },
                major_destination_summary: [
                  {
                    major_name: '计算机科学与技术',
                    student_count: 18,
                    destination_student_count: 7,
                    top_destination_label: '升学',
                    top_destination_count: 4,
                    destination_distribution: { 升学: 4, 企业就业: 3 },
                  },
                ],
                group_destination_association: [
                  {
                    group_segment: '综合发展优势组',
                    destination_label: '升学',
                    student_count: 15,
                    group_student_count: 51,
                    share_within_group: 0.2941,
                  },
                ],
                dimension_highlights: [
                  { dimension: '学业基础表现', average_score: 0.7, level: 'high', label: '学业基础稳健' },
                  { dimension: '图书馆沉浸度', average_score: 0.41, level: 'medium', label: '图书馆投入一般' },
                ],
                group_direction_segments: [
                  {
                    group_segment: '综合发展优势组',
                    student_count: 51,
                    avg_risk_probability: 0.32,
                    avg_risk_score: 41.2,
                    direction_label: '偏向 图书馆沉浸度',
                    avg_dimension_scores: [
                      { dimension: '学业基础表现', average_score: 0.78, label: '学业基础稳健' },
                    ],
                    top_factors: [
                      { dimension: '图书馆沉浸度', explanation: '图书馆行为更稳定', importance: 0.67 },
                    ],
                    risk_amplifiers: [],
                    protective_factors: [
                      { feature: 'library_immersion', feature_cn: '图书馆沉浸度', count: 22, importance: 0.67 },
                    ],
                  },
                ],
                direction_chains: [
                  {
                    group_segment: '综合发展优势组',
                    direction_label: '偏向 图书馆沉浸度',
                    leading_protective_factor: '图书馆沉浸度',
                    leading_dimension: '学业基础表现',
                    avg_risk_score: 41.2,
                  },
                ],
                disclaimer: '去向分析已接入真实毕业去向数据；无匹配数据时相关字段返回空结果',
              },
              meta: { request_id: 'req-development', term: '2024-2' },
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
    await router.push('/development')
    await router.isReady()

    const wrapper = mount(DevelopmentPage, {
      global: {
        plugins: [router, vueQueryPlugin],
        stubs: {
          RouterLink: RouterLinkStub,
          EChart: { template: '<div class="echart-stub" />' },
          LazyEChart: { template: '<div class="echart-stub" />' },
        },
      },
    })

    await flushPromises()
    await flushPromises()

    expect(wrapper.text()).toContain('发展方向与去向关联分析')
    expect(wrapper.text()).toContain('毕业去向分布')
    expect(wrapper.text()).toContain('升学')
    expect(wrapper.text()).toContain('18 人')
    expect(wrapper.text()).toContain('企业就业')
    expect(wrapper.text()).toContain('9 人')
    expect(wrapper.text()).toContain('专业去向对比')
    expect(wrapper.text()).toContain('计算机科学与技术')
    expect(wrapper.text()).toContain('去向学生 7 人')
    expect(wrapper.text()).toContain('主去向 升学')
    expect(wrapper.text()).toContain('升学 4')
    expect(wrapper.text()).toContain('企业就业 3')
    expect(wrapper.text()).toContain('群体去向关联')
    expect(wrapper.text()).toContain('综合发展优势组')
    expect(wrapper.text()).toContain('去向覆盖 15 人')
    expect(wrapper.text()).toContain('升学 15 人')
    expect(wrapper.text()).toContain('图书馆沉浸度')
    expect(wrapper.text()).toContain('方向解释链路')
    expect(wrapper.text()).toContain('学业基础表现')
    expect(wrapper.text()).toContain('平均风险分 41.2')
    expect(wrapper.text()).toContain('去向分析已接入真实毕业去向数据')
  })
})
