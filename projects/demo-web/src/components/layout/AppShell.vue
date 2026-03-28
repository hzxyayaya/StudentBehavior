<template>
  <div class="shell-page">
    <div class="shell-frame">
      <aside class="side panel">
        <div class="panel-inner">
          <p class="eyebrow">Student Behavior Demo</p>
          <h1 class="shell-title">行为分析中台</h1>
          <p class="muted">学业风险、群体分层、个体画像一体展示。</p>
          <nav class="nav">
            <RouterLink class="nav-link" to="/overview">总览</RouterLink>
            <RouterLink class="nav-link" to="/quadrants">群体分层</RouterLink>
            <RouterLink class="nav-link" to="/warnings">风险预警</RouterLink>
          </nav>
        </div>
      </aside>

      <main class="main">
        <header class="topbar panel">
          <div class="panel-inner topbar-inner">
            <div>
              <p class="eyebrow">V1 Demo</p>
              <div class="top-title">学生行为分析与预警</div>
            </div>
            <div class="top-meta">
              <span class="tag cool">{{ term }}</span>
              <span class="tag">{{ displayName }}</span>
            </div>
          </div>
        </header>
        <section class="content">
          <slot />
        </section>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
import { useAuthStore } from '@/app/auth'
import { useTermStore } from '@/app/term'

const { displayName } = useAuthStore()
const { term } = useTermStore()
</script>

<style scoped>
.shell-frame {
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr);
  gap: 20px;
  padding: 20px;
}

.side {
  position: sticky;
  top: 20px;
  align-self: start;
  background:
    linear-gradient(180deg, rgba(23, 58, 114, 0.96), rgba(14, 26, 52, 0.94)),
    radial-gradient(circle at top right, rgba(255, 255, 255, 0.16), transparent 28%);
  color: white;
}

.shell-title {
  margin: 10px 0 6px;
  font-size: 2rem;
  line-height: 1.1;
}

.nav {
  display: grid;
  gap: 10px;
  margin-top: 24px;
}

.nav-link {
  display: block;
  padding: 12px 14px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
}

.nav-link.router-link-active {
  background: rgba(255, 255, 255, 0.18);
}

.main {
  min-width: 0;
  display: grid;
  gap: 20px;
}

.topbar {
  background:
    linear-gradient(135deg, rgba(255, 255, 255, 0.88), rgba(240, 244, 250, 0.9)),
    radial-gradient(circle at top right, rgba(23, 58, 114, 0.08), transparent 30%);
}

.topbar-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.top-title {
  font-size: 1.15rem;
  font-weight: 700;
}

.top-meta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.content {
  display: grid;
  gap: 20px;
  padding-bottom: 20px;
}

@media (max-width: 1080px) {
  .shell-frame {
    grid-template-columns: 1fr;
  }

  .side {
    position: static;
  }
}
</style>
