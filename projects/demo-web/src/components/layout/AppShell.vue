<template>
  <div class="shell-page">
    <aside class="side-nav">
      <div class="brand">学生行为检测系统</div>
      <nav class="nav">
        <RouterLink class="nav-link" to="/risk">学业风险动态感知与预警</RouterLink>
        <RouterLink class="nav-link" to="/trajectory">学业轨迹演化与关键行为分析</RouterLink>
        <RouterLink class="nav-link" to="/profiles">学生个体画像与群体分层分析</RouterLink>
        <RouterLink class="nav-link" to="/development">发展方向与去向关联分析</RouterLink>
      </nav>
    </aside>
    <main class="main">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<style scoped>
.shell-page {
  min-height: 100vh;
  background: var(--main-bg);
}

.side-nav {
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  width: 220px;
  background: var(--nav-bg);
  border-right: 1px solid var(--line);
  padding: 18px 14px;
}

.brand {
  font-size: 0.98rem;
  font-weight: 700;
  padding: 8px 10px 14px;
  color: #303847;
}

.nav {
  display: grid;
  gap: 6px;
}

.nav-link {
  border-radius: 10px;
  padding: 10px 12px;
  color: #515a69;
  font-weight: 600;
}

.nav-link.router-link-active {
  background: #ff4b00;
  color: #fff;
}

.main {
  margin-left: 220px;
  background: var(--main-bg);
  min-height: 100vh;
  padding: 18px;
  width: calc(100% - 220px);
}

@media (max-width: 900px) {
  .side-nav {
    position: sticky;
    left: auto;
    top: 0;
    bottom: auto;
    width: 100%;
    height: auto;
    border-right: 0;
    border-bottom: 1px solid var(--line);
    z-index: 20;
  }

  .main {
    margin-left: 0;
    padding: 14px;
    width: 100%;
  }
}
</style>
