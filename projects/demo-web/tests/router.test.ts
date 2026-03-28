import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import { createRouter as createAppRouter } from '@/app/router'
import { useAuthStore } from '@/app/auth'
import LoginPage from '@/features/auth/LoginPage.vue'

describe('router', () => {
  it('redirects root to overview', async () => {
    const auth = useAuthStore()
    auth.signIn('demo-token', '演示管理员', '2024-2')
    const router = createAppRouter()
    await router.push('/')
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
    expect(wrapper.text()).toContain('演示入口')
  })
})
