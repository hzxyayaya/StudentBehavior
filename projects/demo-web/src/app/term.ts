import { computed, ref } from 'vue'

const currentTerm = ref(sessionStorage.getItem('demo-term') ?? '2024-2')

export function useTermStore() {
  const term = computed(() => currentTerm.value)

  function setTerm(nextTerm: string) {
    currentTerm.value = nextTerm
    sessionStorage.setItem('demo-term', nextTerm)
  }

  return { term, setTerm }
}
