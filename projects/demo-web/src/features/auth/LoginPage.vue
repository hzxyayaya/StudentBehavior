<template>
  <div class="login-page">
    <Suspense v-if="showAmbientVisuals">
      <LoginTriangles />
      <template #fallback>
        <div class="login-triangles-fallback" aria-hidden="true"></div>
      </template>
    </Suspense>
    <div class="ambient ambient-a"></div>
    <div class="ambient ambient-b"></div>
    <div class="ambient ambient-c"></div>

    <div class="login-card">
      <section class="login-left">
        <div class="brand-block">
          <div class="logo-row">
            <span class="logo-dot"></span>
            <strong>学生行为检测系统</strong>
          </div>
        </div>

        <div class="intro-block">
          <h1>欢迎登录</h1>
          <p>进入学生行为分析平台</p>
        </div>

        <div class="form-stack">
          <label class="field-wrap">
            <span>账号</span>
            <div class="field-shell">
              <span class="field-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" focusable="false">
                  <path
                    d="M12 12a4 4 0 1 0-4-4 4 4 0 0 0 4 4Zm0 2c-4.418 0-8 2.015-8 4.5A1.5 1.5 0 0 0 5.5 20h13a1.5 1.5 0 0 0 1.5-1.5C20 16.015 16.418 14 12 14Z"
                  />
                </svg>
              </span>
              <input v-model="username" class="field" placeholder="demo_admin" />
            </div>
          </label>

          <label class="field-wrap">
            <span>密码</span>
            <div class="field-shell">
              <span class="field-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" focusable="false">
                  <path
                    d="M17 9h-1V7a4 4 0 1 0-8 0v2H7a2 2 0 0 0-2 2v7a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-7a2 2 0 0 0-2-2Zm-6 5.73V16a1 1 0 0 0 2 0v-1.27a2 2 0 1 0-2 0ZM10 9V7a2 2 0 1 1 4 0v2Z"
                  />
                </svg>
              </span>
              <input v-model="password" type="password" class="field" placeholder="demo_only" />
            </div>
          </label>

          <label class="field-wrap">
            <span>学期</span>
            <div class="field-shell select-shell">
              <select v-model="term" class="select">
                <option value="2024-2">2024-2</option>
                <option value="2024-1">2024-1</option>
                <option value="2023-2">2023-2</option>
              </select>
              <span class="select-caret" aria-hidden="true">
                <svg viewBox="0 0 24 24" focusable="false">
                  <path d="m7 10 5 5 5-5" />
                </svg>
              </span>
            </div>
          </label>

          <button class="btn" :disabled="loading" type="button" @click="handleLogin">
            <span>{{ loading ? '登录中...' : '登录系统' }}</span>
          </button>

          <button class="skip-link" :disabled="loading" type="button" @click="handleSkipLogin">
            跳过登录，直接进入演示
          </button>

          <p v-if="error" class="error-text">{{ error }}</p>
        </div>
      </section>

      <section class="login-right" aria-hidden="true">
        <div class="visual-panel">
          <div class="visual-fog visual-fog-a"></div>
          <div class="visual-fog visual-fog-b"></div>
          <div class="visual-grid"></div>
          <div class="visual-copy">
            <p class="visual-kicker">Behavior Intelligence</p>
            <h2 class="visual-title">学期风险画像与行为趋势洞察</h2>
            <p class="visual-text">用更轻的交互方式，查看学生群体状态、风险波动与关键行为信号。</p>
          </div>
          <div class="sphere-stage">
            <div v-if="!showAmbientVisuals" class="sphere-placeholder" aria-hidden="true"></div>
            <Suspense v-else>
              <LoginPolySphere />
              <template #fallback>
                <div class="sphere-placeholder" aria-hidden="true"></div>
              </template>
            </Suspense>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, defineAsyncComponent, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '@/app/auth'
import { useTermStore } from '@/app/term'
import { loginDemo } from '@/lib/api'

const LoginPolySphere = defineAsyncComponent(() => import('@/components/auth/LoginPolySphere.vue'))
const LoginTriangles = defineAsyncComponent(() => import('@/components/auth/LoginTriangles.vue'))

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const termStore = useTermStore()

const username = ref('demo_admin')
const password = ref('demo_only')
const term = ref(termStore.term.value)
const loading = ref(false)
const error = ref('')
const showAmbientVisuals = ref(false)
const shouldLoadAmbientVisuals = import.meta.env.MODE !== 'test'
const previousBodyOverflow = document.body.style.overflow
const previousHtmlOverflow = document.documentElement.style.overflow

const redirectTarget = computed(() => {
  const redirect = route.query.redirect
  return typeof redirect === 'string' && redirect.startsWith('/') ? redirect : '/overview'
})

onMounted(() => {
  document.body.style.overflow = 'hidden'
  document.documentElement.style.overflow = 'hidden'
  showAmbientVisuals.value = shouldLoadAmbientVisuals
})

onBeforeUnmount(() => {
  document.body.style.overflow = previousBodyOverflow
  document.documentElement.style.overflow = previousHtmlOverflow
})

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    const data = await loginDemo()
    auth.signIn(data.session_token, username.value, term.value)
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
  auth.signIn('local-demo-token', username.value, term.value)
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
  --page-bg: linear-gradient(145deg, #f8f5ff 0%, #f4f7ff 42%, #eef4ff 100%);
  --card-border: rgba(139, 92, 246, 0.14);
  --card-shadow: 0 28px 80px rgba(76, 29, 149, 0.16);
  --panel-bg: rgba(255, 255, 255, 0.78);
  --panel-border: rgba(139, 92, 246, 0.16);
  --text-strong: #2e1065;
  --text-body: #5b4b82;
  --text-soft: #7c6aa7;
  --field-bg: rgba(245, 243, 255, 0.92);
  --field-border: rgba(167, 139, 250, 0.3);
  --field-focus: rgba(99, 102, 241, 0.95);
  --field-glow: 0 0 0 4px rgba(99, 102, 241, 0.14);
  --button-bg: linear-gradient(135deg, #4f46e5 0%, #6366f1 52%, #7c3aed 100%);
  --button-shadow: 0 16px 30px rgba(99, 102, 241, 0.28);
  --cyan-glow: #67e8f9;
  position: fixed;
  inset: 0;
  z-index: 100;
  isolation: isolate;
  min-height: 100dvh;
  height: 100dvh;
  display: grid;
  place-items: center;
  overflow: hidden;
  padding: 20px 32px;
  background: var(--page-bg);
}

.ambient {
  position: absolute;
  border-radius: 999px;
  filter: blur(42px);
  opacity: 0.36;
  pointer-events: none;
}

.login-triangles-fallback {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.ambient-a {
  width: 380px;
  height: 380px;
  top: -90px;
  left: -120px;
  background: radial-gradient(circle, rgba(124, 58, 237, 0.26) 0%, rgba(124, 58, 237, 0) 70%);
}

.ambient-b {
  width: 420px;
  height: 420px;
  right: -100px;
  bottom: -140px;
  background: radial-gradient(circle, rgba(79, 70, 229, 0.24) 0%, rgba(79, 70, 229, 0) 72%);
}

.ambient-c {
  width: 320px;
  height: 320px;
  left: 38%;
  top: 8%;
  background: radial-gradient(circle, rgba(103, 232, 249, 0.18) 0%, rgba(103, 232, 249, 0) 68%);
}

.login-card {
  width: min(1120px, 100%);
  min-height: 660px;
  max-height: calc(100dvh - 40px);
  display: grid;
  grid-template-columns: minmax(400px, 470px) minmax(0, 1fr);
  position: relative;
  overflow: hidden;
  border: 1px solid var(--card-border);
  border-radius: 34px;
  box-shadow: var(--card-shadow);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9), rgba(248, 245, 255, 0.78));
  backdrop-filter: blur(18px);
}

.login-left,
.login-right {
  position: relative;
  z-index: 1;
}

.login-left {
  display: grid;
  align-content: start;
  gap: 22px;
  padding: 32px 36px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.34), rgba(247, 244, 255, 0.48)),
    radial-gradient(circle at top left, rgba(103, 232, 249, 0.08), transparent 34%);
  border-right: 1px solid rgba(139, 92, 246, 0.07);
  backdrop-filter: blur(8px);
}

.brand-block,
.intro-block {
  display: grid;
  gap: 8px;
}

.logo-row {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  color: var(--text-strong);
  font-size: 1.05rem;
}

.logo-dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  background: linear-gradient(135deg, #67e8f9, #8b5cf6);
  box-shadow: 0 0 18px rgba(103, 232, 249, 0.5);
}

h1 {
  margin: 0;
  color: var(--text-strong);
  font-size: clamp(2rem, 3vw, 2.6rem);
  line-height: 1.1;
}

.intro-block p {
  margin: 0;
  color: var(--text-body);
  line-height: 1.6;
  font-size: 0.98rem;
}

.form-stack {
  display: grid;
  gap: 14px;
}

.field-wrap {
  display: grid;
  gap: 9px;
}

.field-wrap span {
  color: var(--text-body);
  font-size: 0.92rem;
  font-weight: 700;
}

.field-shell {
  position: relative;
  display: flex;
  align-items: center;
  min-height: 58px;
  border-radius: 18px;
  border: 1px solid var(--field-border);
  background: var(--field-bg);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.55);
  transition:
    border-color 180ms ease,
    box-shadow 180ms ease,
    transform 180ms ease,
    background 180ms ease;
}

.field-shell:focus-within {
  border-color: var(--field-focus);
  box-shadow: var(--field-glow);
  background: rgba(248, 245, 255, 0.98);
  transform: translateY(-1px);
}

.field-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  color: #8b5cf6;
  opacity: 0.72;
}

.field-icon svg,
.select-caret svg {
  width: 15px;
  height: 15px;
  fill: currentColor;
  stroke: currentColor;
  stroke-width: 1.8;
}

.field,
.select {
  flex: 1;
  width: 100%;
  border: 0;
  outline: 0;
  background: transparent;
  color: var(--text-strong);
  font-size: 1rem;
  padding: 0 18px 0 0;
}

.field:focus,
.select:focus {
  border: 0;
  outline: 0;
  box-shadow: none;
}

.field::placeholder {
  color: #9d8dc0;
}

.select-shell {
  padding-right: 46px;
}

.select {
  appearance: none;
  cursor: pointer;
  padding-left: 18px;
}

.select-caret {
  position: absolute;
  right: 16px;
  top: 50%;
  color: #8b5cf6;
  transform: translateY(-50%);
  pointer-events: none;
}

.btn {
  margin-top: 8px;
  min-height: 58px;
  border: 0;
  border-radius: 18px;
  color: #fff;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  background: var(--button-bg);
  box-shadow: var(--button-shadow);
  cursor: pointer;
  transition:
    transform 180ms ease,
    box-shadow 180ms ease,
    filter 180ms ease;
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px) scale(1.01);
  filter: saturate(1.08) brightness(0.98);
  box-shadow: 0 20px 40px rgba(99, 102, 241, 0.34);
}

.btn:focus-visible,
.skip-link:focus-visible {
  outline: none;
  box-shadow: 0 0 0 4px rgba(103, 232, 249, 0.26);
}

.btn:disabled,
.skip-link:disabled {
  cursor: not-allowed;
  opacity: 0.7;
}

.skip-link {
  justify-self: start;
  padding: 0;
  border: 0;
  background: transparent;
  color: #6d5bd0;
  font-size: 0.96rem;
  font-weight: 600;
  cursor: pointer;
  transition: color 180ms ease, transform 180ms ease;
}

.skip-link:hover:not(:disabled) {
  color: #4338ca;
  transform: translateX(2px);
}

.error-text {
  margin: 2px 0 0;
  color: #b91c1c;
  background: rgba(254, 242, 242, 0.94);
  border: 1px solid rgba(248, 113, 113, 0.22);
  border-radius: 16px;
  padding: 13px 14px;
  line-height: 1.6;
}

.login-right {
  padding: 18px;
  background:
    radial-gradient(circle at 18% 22%, rgba(192, 132, 252, 0.16), transparent 28%),
    radial-gradient(circle at 80% 72%, rgba(103, 232, 249, 0.08), transparent 24%),
    linear-gradient(160deg, rgba(72, 37, 129, 0.96), rgba(76, 45, 143, 0.9) 45%, rgba(103, 80, 164, 0.88) 100%);
}

.visual-panel {
  position: relative;
  height: 100%;
  min-height: 600px;
  display: grid;
  place-items: center;
  border-radius: 28px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.12), rgba(255, 255, 255, 0.04)),
    radial-gradient(circle at top, rgba(255, 255, 255, 0.08), transparent 46%);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(22px);
}

.visual-fog {
  position: absolute;
  border-radius: 999px;
  filter: blur(52px);
  pointer-events: none;
}

.visual-fog-a {
  width: 260px;
  height: 260px;
  top: 42px;
  left: 52px;
  background: radial-gradient(circle, rgba(167, 139, 250, 0.34) 0%, rgba(167, 139, 250, 0) 72%);
}

.visual-fog-b {
  width: 300px;
  height: 300px;
  right: 36px;
  bottom: 38px;
  background: radial-gradient(circle, rgba(103, 232, 249, 0.18) 0%, rgba(103, 232, 249, 0) 72%);
}

.visual-grid {
  position: absolute;
  inset: 0;
  opacity: 0.16;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.12) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.12) 1px, transparent 1px);
  background-size: 58px 58px;
  mask-image: radial-gradient(circle at center, black 34%, transparent 85%);
}

.sphere-stage {
  position: relative;
  z-index: 1;
  width: 100%;
  height: 100%;
  padding: 92px 20px 20px;
}

.sphere-placeholder {
  width: 100%;
  height: 100%;
  min-height: 420px;
}

.visual-copy {
  position: absolute;
  top: 26px;
  left: 28px;
  right: 28px;
  z-index: 2;
  max-width: 420px;
  display: grid;
  gap: 12px;
  color: rgba(255, 255, 255, 0.96);
  pointer-events: none;
}

.visual-kicker {
  margin: 0;
  font-size: 0.78rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.62);
}

.visual-title {
  margin: 0;
  font-size: clamp(1.8rem, 2.8vw, 2.55rem);
  line-height: 1.18;
  font-weight: 700;
}

.visual-text {
  margin: 0;
  max-width: 360px;
  color: rgba(255, 255, 255, 0.74);
  font-size: 0.98rem;
  line-height: 1.7;
}

@media (prefers-reduced-motion: reduce) {
  .btn,
  .skip-link,
  .field-shell {
    animation: none !important;
    transition: none !important;
  }
}

@media (max-width: 1040px) {
  .login-page {
    padding: 14px 20px;
  }

  .login-card {
    grid-template-columns: 1fr;
    min-height: auto;
  }

  .login-left {
    border-right: 0;
    border-bottom: 1px solid rgba(139, 92, 246, 0.1);
  }

  .login-right {
    min-height: 420px;
  }

  .visual-panel {
    min-height: 390px;
  }

  .sphere-stage {
    padding: 96px 16px 16px;
  }

  .visual-copy {
    top: 20px;
    left: 20px;
    right: 20px;
  }
}

@media (max-width: 640px) {
  .login-page {
    padding: 10px 14px;
  }

  .login-card {
    border-radius: 26px;
    max-height: calc(100dvh - 20px);
  }

  .login-left {
    padding: 24px 20px;
  }

  .login-right {
    padding: 14px;
    min-height: 360px;
  }

  .visual-panel {
    min-height: 300px;
  }

  .sphere-stage {
    padding: 82px 8px 8px;
  }

  .sphere-placeholder {
    min-height: 280px;
    height: 320px;
  }

  .visual-copy {
    top: 16px;
    left: 16px;
    right: 16px;
    gap: 8px;
  }

  .visual-title {
    font-size: 1.5rem;
  }

  .visual-text {
    font-size: 0.9rem;
    line-height: 1.55;
  }
}
</style>
