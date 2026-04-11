<template>
  <div class="shell-page" :class="{ collapsed: sidebarCollapsed }">
    <aside class="side-nav" :class="{ collapsed: sidebarCollapsed }">
      <NavParticles />

      <div class="brand-banner">
        <div class="brand-topline">
          <div class="brand-copy" :class="{ hidden: sidebarCollapsed }">
            <p class="brand-eyebrow">Student Behavior</p>
            <h1 class="brand-title">监控系统</h1>
          </div>

          <button
            class="sidebar-collapse-toggle"
            type="button"
            :aria-expanded="!sidebarCollapsed"
            :aria-label="sidebarCollapsed ? '展开导航栏' : '折叠导航栏'"
            @click="toggleSidebar"
          >
            <svg viewBox="0 0 24 24" fill="none">
              <path
                :d="sidebarCollapsed ? 'M9 6.75 14.25 12 9 17.25' : 'M15 6.75 9.75 12 15 17.25'"
                stroke="currentColor"
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1.8"
              />
            </svg>
          </button>
        </div>

      </div>

      <div class="side-top">
        <nav class="nav-cluster" aria-label="系统导航">
          <RouterLink v-for="item in navItems" :key="item.to" class="nav-link" :to="item.to">
            <span class="nav-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none">
                <path
                  v-for="segment in item.icon"
                  :key="segment"
                  :d="segment"
                  stroke="currentColor"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="1.8"
                />
              </svg>
            </span>
            <span v-if="!sidebarCollapsed" class="nav-copy">
              <span class="nav-title">{{ item.label }}</span>
              <small class="nav-desc">{{ item.desc }}</small>
            </span>
          </RouterLink>
        </nav>
      </div>

      <div v-if="!sidebarCollapsed" ref="userMenuRef" class="user-tile-card" :class="{ open: userMenuOpen }">
        <div class="user-tile-head">
          <div class="user-tile-copy">
            <p class="user-tile-label">当前用户</p>
            <h3 class="user-tile-name">{{ auth.displayName.value }}</h3>
          </div>
          <button
            class="user-menu-toggle"
            type="button"
            :aria-expanded="userMenuOpen"
            aria-label="打开用户操作"
            @click="toggleUserMenu"
          >
            <span class="user-menu-dots" aria-hidden="true">
              <span></span>
              <span></span>
              <span></span>
            </span>
          </button>
        </div>

        <div v-if="userMenuOpen" class="user-menu-popover" role="menu" aria-label="用户操作菜单">
          <button class="user-tool-item" type="button" role="menuitem" @click="goLogin">切换账号</button>
          <button class="user-tool-item danger" type="button" role="menuitem" @click="logout">退出登录</button>
        </div>
      </div>
    </aside>

    <main class="main-content">
      <MainParticles />
      <div class="main-shell">
        <section class="content-stage">
          <slot />
        </section>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/app/auth'
import { useTermStore } from '@/app/term'
import MainParticles from '@/components/layout/MainParticles.vue'
import NavParticles from '@/components/layout/NavParticles.vue'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
useTermStore()

const sidebarCollapsed = ref(false)
const userMenuOpen = ref(false)
const userMenuRef = ref<HTMLElement | null>(null)

const navItems = [
  {
    to: '/overview',
    label: '总览分析',
    desc: '风险分布与关键指标',
    icon: [
      'M5.75 5.75h4.5v4.5h-4.5z',
      'M13.75 5.75h4.5v4.5h-4.5z',
      'M5.75 13.75h4.5v4.5h-4.5z',
      'M13.75 13.75h4.5v4.5h-4.5z',
    ],
  },
  {
    to: '/warnings',
    label: '风险预警',
    desc: '预警学生筛查列表',
    icon: [
      'M12 4.75 19 17.25H5L12 4.75Z',
      'M12 9v4.5',
      'M12 15.75h.01',
    ],
  },
  {
    to: '/trajectory',
    label: '轨迹分析',
    desc: '学期变化与关键因子',
    icon: [
      'M5 17.25h14',
      'M6.5 14.75 10 11.25l3 2.5 4.5-6',
      'M10 11.25V7.5',
    ],
  },
  {
    to: '/profiles',
    label: '群体画像',
    desc: '分层群体与行为模式',
    icon: [
      'M8 11a2.25 2.25 0 1 0 0-4.5A2.25 2.25 0 0 0 8 11Z',
      'M15.75 11a2.25 2.25 0 1 0 0-4.5 2.25 2.25 0 0 0 0 4.5Z',
      'M4.75 17.25a4.25 4.25 0 0 1 6.75-3.35',
      'M12.5 13.9a4.25 4.25 0 0 1 6.75 3.35',
    ],
  },
  {
    to: '/development',
    label: '发展分析',
    desc: '专业对比与方向关联',
    icon: [
      'M12 5.25a6.75 6.75 0 1 0 6.75 6.75A6.75 6.75 0 0 0 12 5.25Z',
      'M12 8.25v4.25l2.75 1.75',
      'M12 3.75v1.5',
    ],
  },
]

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
  userMenuOpen.value = false
}

function logout() {
  userMenuOpen.value = false
  auth.signOut()
  router.push('/login')
}

function goLogin() {
  userMenuOpen.value = false
  router.push('/login')
}

function toggleUserMenu() {
  userMenuOpen.value = !userMenuOpen.value
}

function handleDocumentClick(event: MouseEvent) {
  if (!userMenuOpen.value) return
  if (userMenuRef.value?.contains(event.target as Node)) return
  userMenuOpen.value = false
}

watch(
  () => route.fullPath,
  () => {
    userMenuOpen.value = false
  },
)

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
})
</script>
