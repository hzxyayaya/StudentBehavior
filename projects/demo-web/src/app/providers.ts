import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import type { App } from 'vue'
import { createRouter } from './router'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

export function createAppPlugins() {
  return {
    install(app: App) {
      app.use(VueQueryPlugin, { queryClient })
      app.use(createRouter())
    },
  }
}
