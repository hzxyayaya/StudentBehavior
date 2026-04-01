<template>
  <div class="login-page">
    <div class="login-card">
      <section class="login-left">
        <div class="logo-row">
          <span class="logo-dot"></span>
          <strong>学生行为检测系统</strong>
        </div>
        <h1>欢迎登录</h1>
        <p>使用演示账号进入系统</p>

        <div class="form-stack">
          <label class="field-wrap">
            <span>账号</span>
            <input v-model="username" class="field" placeholder="demo_admin" />
          </label>
          <label class="field-wrap">
            <span>密码</span>
            <input v-model="password" type="password" class="field" placeholder="demo_only" />
          </label>
          <label class="field-wrap">
            <span>学期</span>
            <select v-model="term" class="select">
              <option value="2024-2">2024-2</option>
              <option value="2024-1">2024-1</option>
              <option value="2023-2">2023-2</option>
            </select>
          </label>

          <button class="btn" :disabled="loading" type="button" @click="handleLogin">
            {{ loading ? '登录中...' : '登录' }}
          </button>
          <button class="btn secondary" :disabled="loading" type="button" @click="handleSkipLogin">
            跳过登录
          </button>
          <p v-if="error" class="error-text">{{ error }}</p>
        </div>
      </section>

      <section class="login-right">
        <img class="cover-image" :src="illustrationUrl" alt="student behavior vector" />
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/app/auth'
import { useTermStore } from '@/app/term'
import { loginDemo } from '@/lib/api'
import illustrationUrl from '@/assets/login-illustration.svg'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const termStore = useTermStore()

const username = ref('demo_admin')
const password = ref('demo_only')
const term = ref(termStore.term.value)
const loading = ref(false)
const error = ref('')

const redirectTarget = computed(() => {
  const redirect = route.query.redirect
  return typeof redirect === 'string' && redirect.startsWith('/') ? redirect : '/overview'
})

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    const data = await loginDemo()
    auth.signIn(data.session_token, '系统管理员', term.value)
    termStore.setTerm(term.value)
    await router.push(redirectTarget.value)
  } catch (err) {
    error.value = formatLoginError(err)
  } finally {
    loading.value = false
  }
}

async function handleSkipLogin() {
  error.value = ''
  auth.signIn('local-demo-token', '系统管理员', term.value)
  termStore.setTerm(term.value)
  await router.push(redirectTarget.value)
}

function formatLoginError(err: unknown) {
  if (!(err instanceof Error)) return '登录失败，请稍后重试'
  if (err.message.includes('Failed to fetch') || err.message.includes('NetworkError')) {
    return '未连接到 demo-api，请先启动后端'
  }
  return err.message || '登录失败，请稍后重试'
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 20px;
  background: linear-gradient(180deg, #eef2f6 0%, #e8edf3 100%);
}

.login-card {
  width: min(1240px, 100%);
  min-height: 700px;
  border-radius: 28px;
  overflow: hidden;
  border: 1px solid #dfe5ec;
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.1);
  display: grid;
  grid-template-columns: minmax(340px, 430px) minmax(0, 1fr);
  background: #fff;
}

.login-left {
  padding: 36px 30px;
  border-right: 1px solid #e8edf2;
  display: grid;
  align-content: start;
  gap: 16px;
}

.logo-row {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.logo-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ff4b00;
}

h1 {
  margin: 8px 0 0;
  font-size: 2rem;
}

p {
  margin: 0;
  color: #7a8492;
}

.form-stack {
  margin-top: 10px;
  display: grid;
  gap: 12px;
}

.field-wrap {
  display: grid;
  gap: 6px;
}

.field-wrap span {
  color: #6f7987;
  font-size: 0.9rem;
  font-weight: 600;
}

.error-text {
  color: #ef4444;
  border: 1px solid #f9caca;
  background: #fff0f0;
  border-radius: 10px;
  padding: 10px 12px;
}

.login-right {
  position: relative;
  background: radial-gradient(circle at 20% 30%, #fff5ef 0%, #fff 46%, #f8fafc 100%);
  display: grid;
  place-items: center;
  padding: 24px;
}

.cover-image {
  width: min(92%, 840px);
  max-height: 92%;
  object-fit: contain;
}

@media (max-width: 980px) {
  .login-card {
    grid-template-columns: 1fr;
  }

  .login-left {
    border-right: 0;
    border-bottom: 1px solid #e8edf2;
  }

  .login-right {
    min-height: 320px;
  }
}
</style>
