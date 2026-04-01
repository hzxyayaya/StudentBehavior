import { createRouter as createVueRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from './auth'
import LoginPage from '@/features/auth/LoginPage.vue'
import OverviewPage from '@/features/overview/OverviewPage.vue'
import GroupsPage from '@/features/quadrants/QuadrantsPage.vue'
import StudentPage from '@/features/students/StudentPage.vue'
import WarningsPage from '@/features/warnings/WarningsPage.vue'

export function createRouter() {
  const router = createVueRouter({
    history: createWebHistory(),
    routes: [
      { path: '/', redirect: '/overview' },
      { path: '/login', component: LoginPage },
      { path: '/overview', component: OverviewPage, meta: { requiresAuth: true } },
      { path: '/groups', component: GroupsPage, meta: { requiresAuth: true } },
      { path: '/quadrants', redirect: '/groups' },
      { path: '/warnings', component: WarningsPage, meta: { requiresAuth: true } },
      { path: '/students/:studentId', component: StudentPage, meta: { requiresAuth: true } },
      { path: '/:pathMatch(.*)*', redirect: '/overview' },
    ],
  })

  router.beforeEach((to) => {
    const auth = useAuthStore()
    if (to.path === '/login') return true
    if (to.meta.requiresAuth && !auth.isAuthenticated.value) return { path: '/login', query: { redirect: to.fullPath } }
    return true
  })

  return router
}
