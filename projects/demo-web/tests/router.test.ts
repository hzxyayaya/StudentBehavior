import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it } from 'vitest'

import { createRouter as createAppRouter } from '@/app/router'
import { useAuthStore } from '@/app/auth'
import LoginPage from '@/features/auth/LoginPage.vue'

describe('router', () => {
  beforeEach(() => {
    sessionStorage.clear()
  })

  it('redirects root to overview', async () => {
    const auth = useAuthStore()
    auth.signIn('demo-token', '演示管理员', '2024-2')
    const router = createAppRouter()
    await router.push('/')
    await router.isReady()
    expect(router.currentRoute.value.path).toBe('/risk')
  })

  it('keeps legacy overview route as an alias to risk task', async () => {
    const auth = useAuthStore()
    auth.signIn('demo-token', '演示管理员', '2024-2')
    const router = createAppRouter()
    await router.push('/overview')
    await router.isReady()
    expect(router.currentRoute.value.path).toBe('/risk')
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

  it('allows skipping login into the protected demo shell', async () => {
    const auth = useAuthStore()
    auth.signOut()
    const router = createAppRouter()
    await router.push('/login?redirect=%2Fwarnings')
    await router.isReady()

    const wrapper = mount(LoginPage, {
      global: { plugins: [router] },
    })

    await wrapper.get('button.secondary').trigger('click')
    await flushPromises()

    expect(sessionStorage.getItem('demo-token')).toBe('local-demo-token')
    expect(router.currentRoute.value.path).toBe('/risk')
  })
})
