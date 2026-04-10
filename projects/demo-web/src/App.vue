<template>
  <RouterView v-slot="{ Component, route }">
    <AppShell v-if="route.path !== '/login'">
      <component :is="Component" />
    </AppShell>
    <component :is="Component" v-else />
  </RouterView>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import AppShell from '@/components/layout/AppShell.vue'
</script>
