import { beforeEach, describe, expect, it, vi } from 'vitest'

import { getOverview, loginDemo } from '@/lib/api'

describe('api client', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('parses demo login envelope', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          code: 200,
          message: 'OK',
          data: {
            user_id: 'demo_admin',
            display_name: '演示管理员',
            role: 'manager',
            session_token: 'demo-token',
          },
          meta: { request_id: 'demo-request', term: '2024-2' },
        }),
      }),
    )

    const data = await loginDemo()
    expect(data.session_token).toBe('demo-token')
  })

  it('throws for non-200 envelopes', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          code: 404,
          message: 'term not found',
          data: {},
          meta: { request_id: 'demo-request', term: '2099-1' },
        }),
      }),
    )

    await expect(getOverview('2099-1')).rejects.toThrow('term not found')
  })
})
