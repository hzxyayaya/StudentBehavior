import { createRouter as createVueRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from './auth'
const LoginPage = () => import('@/features/auth/LoginPage.vue')
const DevelopmentPage = () => import('@/features/development/DevelopmentPage.vue')
const OverviewPage = () => import('@/features/overview/OverviewPage.vue')
const GroupsPage = () => import('@/features/quadrants/QuadrantsPage.vue')
const StudentPage = () => import('@/features/students/StudentPage.vue')
const TrajectoryPage = () => import('@/features/trajectory/TrajectoryPage.vue')
const WarningsPage = () => import('@/features/warnings/WarningsPage.vue')

export function createRouter() {
  const router = createVueRouter({
    history: createWebHistory(),
    routes: [
      { path: '/', redirect: '/overview' },
      { path: '/login', component: LoginPage },
      { path: '/overview', component: OverviewPage, meta: { requiresAuth: true } },
      { path: '/warnings', component: WarningsPage, meta: { requiresAuth: true } },
      { path: '/trajectory', component: TrajectoryPage, meta: { requiresAuth: true } },
      { path: '/profiles', component: GroupsPage, meta: { requiresAuth: true } },
      { path: '/development', component: DevelopmentPage, meta: { requiresAuth: true } },
      { path: '/students/:studentId', component: StudentPage, meta: { requiresAuth: true } },
      { path: '/risk-overview', redirect: '/overview' },
      { path: '/risk', redirect: '/warnings' },
      { path: '/groups', redirect: '/profiles' },
      { path: '/quadrants', redirect: '/profiles' },
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
