import { computed, ref } from 'vue'

export const DEFAULT_TERM = '2024-2'
export const AVAILABLE_TERMS = ['2024-2', '2024-1', '2023-2'] as const

function normalizeTerm(term: string | null) {
  if (term && AVAILABLE_TERMS.includes(term as (typeof AVAILABLE_TERMS)[number])) {
    return term
  }
  return DEFAULT_TERM
}

const currentTerm = ref(normalizeTerm(sessionStorage.getItem('demo-term')))

export function useTermStore() {
  const term = computed(() => currentTerm.value)

  function setTerm(nextTerm: string) {
    const normalized = normalizeTerm(nextTerm)
    currentTerm.value = normalized
    sessionStorage.setItem('demo-term', normalized)
  }

  return { term, setTerm }
}
