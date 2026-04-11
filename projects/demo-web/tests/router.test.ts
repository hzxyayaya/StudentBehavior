import { mount, flushPromises } from '@vue/test-utils'
import { beforeEach, describe, expect, it } from 'vitest'

import { createRouter as createAppRouter } from '@/app/router'
import { useAuthStore } from '@/app/auth'
import LoginPage from '@/features/auth/LoginPage.vue'

describe('router', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('registers page routes as lazy-loaded components', () => {
    const router = createAppRouter()
    const pagePaths = ['/login', '/overview', '/warnings', '/trajectory', '/profiles', '/development', '/students/:studentId']

    for (const path of pagePaths) {
      const route = router.getRoutes().find((candidate) => candidate.path === path)
      expect(route?.components?.default).toEqual(expect.any(Function))
    }
  })

  it('redirects root to overview', async () => {
    const auth = useAuthStore()
    auth.signIn('demo-token', '演示管理员', '2024-2')
    const router = createAppRouter()
    await router.push('/')
    await flushPromises()
    await router.isReady()
    expect(router.currentRoute.value.path).toBe('/overview')
  })

  it('keeps overview route accessible', async () => {
    const auth = useAuthStore()
    auth.signIn('demo-token', '演示管理员', '2024-2')
    const router = createAppRouter()
    await router.push('/overview')
    await router.isReady()
    expect(router.currentRoute.value.path).toBe('/overview')
  })

  it('sends unauthenticated users to login', async () => {
    const auth = useAuthStore()
    auth.signOut()
    const router = createAppRouter()
    await router.push('/warnings')
    await router.isReady()
    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('renders the login entry point', () => {
    const wrapper = mount(LoginPage, {
      global: { plugins: [createAppRouter()] },
    })
    expect(wrapper.text()).toContain('欢迎登录')
  })

  it('allows authenticated users to continue to the requested protected route', async () => {
    const auth = useAuthStore()
    auth.signOut()
    const router = createAppRouter()
    await router.push('/login?redirect=%2Fwarnings')
    await router.isReady()

    auth.signIn('local-demo-token', '演示管理员', '2024-2')
    const redirectTarget = String(router.currentRoute.value.query.redirect ?? '/overview')
    await router.push(redirectTarget)

    expect(sessionStorage.getItem('demo-token')).toBe('local-demo-token')
    expect(router.currentRoute.value.path).toBe('/warnings')
  })
})
