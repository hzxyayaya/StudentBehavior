import { computed, ref } from 'vue'

const token = ref<string | null>(sessionStorage.getItem('demo-token'))
const displayName = ref(sessionStorage.getItem('demo-display-name') ?? '演示管理员')

export function useAuthStore() {
  const isAuthenticated = computed(() => token.value !== null)

  function signIn(nextToken: string, nextDisplayName: string, term: string) {
    token.value = nextToken
    displayName.value = nextDisplayName
    sessionStorage.setItem('demo-token', nextToken)
    sessionStorage.setItem('demo-display-name', nextDisplayName)
    sessionStorage.setItem('demo-term', term)
  }

  function signOut() {
    token.value = null
    displayName.value = '演示管理员'
    sessionStorage.removeItem('demo-token')
    sessionStorage.removeItem('demo-display-name')
  }

  return { token, displayName, isAuthenticated, signIn, signOut }
}
