<template>
  <div class="login-wrap">
    <div class="login-hero panel">
      <div class="panel-inner stack">
        <p class="eyebrow">演示入口</p>
        <h1 class="title">学生行为分析中台</h1>
        <p class="muted">用当前真实联调值进入总览、群体分层、风险预警和个体画像。</p>
        <div class="login-actions">
          <button class="btn" type="button" :disabled="loading" @click="handleLogin">
            {{ loading ? '进入中...' : '进入演示' }}
          </button>
          <RouterLink class="btn secondary" to="/overview">跳过登录</RouterLink>
        </div>
      </div>
    </div>

    <div class="login-panel panel">
      <div class="panel-inner stack">
        <label>
          <span class="muted">默认账号</span>
          <input v-model="username" class="field" />
        </label>
        <label>
          <span class="muted">默认密码</span>
          <input v-model="password" class="field" type="password" />
        </label>
        <label>
          <span class="muted">角色</span>
          <input v-model="role" class="field" />
        </label>
        <label>
          <span class="muted">默认学期</span>
          <select v-model="term" class="select">
            <option value="2024-2">2024-2</option>
            <option value="2024-1">2024-1</option>
            <option value="2023-2">2023-2</option>
          </select>
        </label>
        <p v-if="error" class="error">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'

import { useAuthStore } from '@/app/auth'
import { useTermStore } from '@/app/term'
import { loginDemo } from '@/lib/api'

const router = useRouter()
const auth = useAuthStore()
const termStore = useTermStore()

const username = ref('demo_admin')
const password = ref('demo_only')
const role = ref('manager')
const term = ref(termStore.term.value)
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    const data = await loginDemo()
    auth.signIn(data.session_token, data.display_name, term.value)
    termStore.setTerm(term.value)
    await router.push('/overview')
  } catch (err) {
    error.value = err instanceof Error ? err.message : '登录失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-wrap {
  min-height: 100vh;
  display: grid;
  gap: 20px;
  grid-template-columns: 1.2fr 0.8fr;
  padding: 20px;
}

.login-hero {
  display: grid;
  align-items: end;
  min-height: 70vh;
  background:
    linear-gradient(135deg, rgba(23, 58, 114, 0.95), rgba(11, 90, 109, 0.94)),
    radial-gradient(circle at top right, rgba(255, 255, 255, 0.16), transparent 28%);
  color: white;
}

.login-hero .muted {
  color: rgba(255, 255, 255, 0.78);
}

.login-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.login-panel {
  min-height: 70vh;
  align-self: end;
}

.error {
  color: var(--hot);
  margin: 0;
}

@media (max-width: 960px) {
  .login-wrap {
    grid-template-columns: 1fr;
  }
}
</style>
