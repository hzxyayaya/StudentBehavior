import { computed, ref } from 'vue'

const DEFAULT_DISPLAY_NAME = '系统管理员'

const token = ref<string | null>(sessionStorage.getItem('demo-token'))
const displayName = ref(sessionStorage.getItem('demo-display-name') ?? DEFAULT_DISPLAY_NAME)

export function useAuthStore() {
  const isAuthenticated = computed(() => token.value !== null)

  function signIn(nextToken: string, nextDisplayName: string | null | undefined, term: string) {
    const safeDisplayName = nextDisplayName?.trim() ? nextDisplayName : DEFAULT_DISPLAY_NAME
    token.value = nextToken
    displayName.value = safeDisplayName
    sessionStorage.setItem('demo-token', nextToken)
    sessionStorage.setItem('demo-display-name', safeDisplayName)
    sessionStorage.setItem('demo-term', term)
  }

  function signOut() {
    token.value = null
    displayName.value = DEFAULT_DISPLAY_NAME
    sessionStorage.removeItem('demo-token')
    sessionStorage.removeItem('demo-display-name')
  }

  return { token, displayName, isAuthenticated, signIn, signOut }
}
