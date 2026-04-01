import { computed, ref } from 'vue'

const token = ref<string | null>(sessionStorage.getItem('demo-token'))
const displayName = ref(sessionStorage.getItem('demo-display-name') ?? '系统管理员')

export function useAuthStore() {
  const isAuthenticated = computed(() => token.value !== null)

  function signIn(nextToken: string, nextDisplayName: string | null | undefined, term: string) {
    const safeDisplayName = nextDisplayName?.trim() ? nextDisplayName : '系统管理员'
    token.value = nextToken
    displayName.value = safeDisplayName
    sessionStorage.setItem('demo-token', nextToken)
    sessionStorage.setItem('demo-display-name', safeDisplayName)
    sessionStorage.setItem('demo-term', term)
  }

  function signOut() {
    token.value = null
    displayName.value = '系统管理员'
    sessionStorage.removeItem('demo-token')
    sessionStorage.removeItem('demo-display-name')
  }

  return { token, displayName, isAuthenticated, signIn, signOut }
}
