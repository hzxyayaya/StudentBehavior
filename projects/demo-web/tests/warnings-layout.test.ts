import { RouterLinkStub, flushPromises, mount } from '@vue/test-utils'
import { QueryClient, VueQueryPlugin } from '@tanstack/vue-query'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import { useAuthStore } from '@/app/auth'
import { createRouter as createAppRouter } from '@/app/router'
import WarningsPage from '@/features/warnings/WarningsPage.vue'

function createPlugins() {
  const router = createAppRouter()
  const vueQueryPlugin: [typeof VueQueryPlugin, { queryClient: QueryClient }] = [VueQueryPlugin, { queryClient: new QueryClient() }]
  return { router, vueQueryPlugin }
}

describe('warnings page layout hooks', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    sessionStorage.clear()
  })

  it('keeps the apply action in a dedicated trailing filter slot with a stable label', async () => {
    const auth = useAuthStore()
    auth.signIn('demo-token', '演示管理员', '2024-2')

    vi.stubGlobal(
      'fetch',
      vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: async () => ({
            code: 200,
            message: 'OK',
            data: {
              items: [
                {
                  student_id: 'pjwrqxbj901',
                  student_name: '示例学生',
                  major_name: '计算机科学与技术',
                  group_segment: '作息失衡风险组',
                  risk_level: '较高风险',
                  academic_risk_level: '一般风险',
                  behavior_risk_level: '较高风险',
                  intervention_priority_level: '高风险',
                  intervention_priority_score: 82.6,
                  adjusted_risk_score: 79.4,
                  risk_probability: 0.82,
                  risk_change_direction: 'rising',
                  top_risk_factors: [{ feature: 'academic_base', feature_cn: '学业基础表现' }],
                  top_protective_factors: [{ feature: 'library_immersion', feature_cn: '图书馆沉浸度' }],
                },
              ],
              page: 1,
              page_size: 5,
              total: 1,
            },
            meta: { request_id: 'req-warnings-layout', term: '2024-2' },
          }),
        }),
      ),
    )

    const { router, vueQueryPlugin } = createPlugins()
    await router.push('/warnings?term=2024-2')
    await router.isReady()

    const wrapper = mount(WarningsPage, {
      global: {
        plugins: [router, vueQueryPlugin],
        stubs: { RouterLink: RouterLinkStub },
      },
    })

    await flushPromises()
    await flushPromises()

    const filters = wrapper.find('.filters')
    const filterChildren = filters.element.children
    const trailingChild = filterChildren.item(filterChildren.length - 1)
    const filterAction = wrapper.find('.filter-action')
    const applyButton = wrapper.find('.filters-apply')

    expect(filterAction.exists()).toBe(true)
    expect(trailingChild).toBe(filterAction.element)
    expect(filterAction.findAll('button')).toHaveLength(1)
    expect(applyButton.exists()).toBe(true)
    expect(applyButton.text()).toBe('应用筛选')

    await wrapper.find('.filter-search').setValue('计算机')
    await applyButton.trigger('click')

    expect(wrapper.find('.filter-action .filters-apply').text()).toBe('应用筛选')
    expect(wrapper.find('.filter-search').element).not.toBe(applyButton.element)
  })

  it('adds data-label metadata to every warning row cell for responsive fallback layouts', async () => {
    const auth = useAuthStore()
    auth.signIn('demo-token', '演示管理员', '2024-2')

    vi.stubGlobal(
      'fetch',
      vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: async () => ({
            code: 200,
            message: 'OK',
            data: {
              items: [
                {
                  student_id: 'pjwrqxbj901',
                  student_name: '示例学生',
                  major_name: '计算机科学与技术',
                  group_segment: '作息失衡风险组',
                  risk_level: '较高风险',
                  academic_risk_level: '一般风险',
                  behavior_risk_level: '较高风险',
                  intervention_priority_level: '高风险',
                  intervention_priority_score: 82.6,
                  adjusted_risk_score: 79.4,
                  risk_probability: 0.82,
                  risk_change_direction: 'rising',
                  top_risk_factors: [{ feature: 'academic_base', feature_cn: '学业基础表现' }],
                  top_protective_factors: [{ feature: 'library_immersion', feature_cn: '图书馆沉浸度' }],
                },
              ],
              page: 1,
              page_size: 5,
              total: 1,
            },
            meta: { request_id: 'req-warnings-layout', term: '2024-2' },
          }),
        }),
      ),
    )

    const { router, vueQueryPlugin } = createPlugins()
    await router.push('/warnings?term=2024-2')
    await router.isReady()

    const wrapper = mount(WarningsPage, {
      global: {
        plugins: [router, vueQueryPlugin],
        stubs: { RouterLink: RouterLinkStub },
      },
    })

    await flushPromises()
    await flushPromises()

    const firstDataRow = wrapper.findAll('.table-row').find((row) => !row.classes().includes('header'))
    expect(firstDataRow).toBeTruthy()

    const labeledCells = firstDataRow!.findAll('.table-cell')
    expect(labeledCells).toHaveLength(7)
    expect(labeledCells.map((cell) => cell.attributes('data-label'))).toEqual([
      '学号',
      '姓名',
      '专业',
      '群体标签',
      '风险等级',
      '风险详情',
      '风险因素',
    ])
    expect(firstDataRow!.find('.table-cell-detail').attributes('data-label')).toBe('风险详情')
    expect(firstDataRow!.find('.table-cell-factors').attributes('data-label')).toBe('风险因素')
    expect(labeledCells.every((cell) => Boolean(cell.text().trim()))).toBe(true)
  })

  it('keeps loading skeleton cells unlabeled for responsive fallback rules', async () => {
    const auth = useAuthStore()
    auth.signIn('demo-token', '演示管理员', '2024-2')

    let resolveFetch: ((value: unknown) => void) | undefined
    vi.stubGlobal(
      'fetch',
      vi.fn(
        () =>
          new Promise((resolve) => {
            resolveFetch = resolve
          }),
      ),
    )

    const { router, vueQueryPlugin } = createPlugins()
    await router.push('/warnings?term=2024-2')
    await router.isReady()

    const wrapper = mount(WarningsPage, {
      global: {
        plugins: [router, vueQueryPlugin],
        stubs: { RouterLink: RouterLinkStub },
      },
    })

    await flushPromises()

    const skeletonCells = wrapper.findAll('.skeleton-row .table-cell')
    expect(skeletonCells.length).toBeGreaterThan(0)
    expect(skeletonCells.every((cell) => cell.attributes('data-label') === undefined)).toBe(true)

    resolveFetch?.({
      ok: true,
      json: async () => ({
        code: 200,
        message: 'OK',
        data: { items: [], page: 1, page_size: 5, total: 0 },
        meta: { request_id: 'req-warnings-layout-loading', term: '2024-2' },
      }),
    })
  })
})
