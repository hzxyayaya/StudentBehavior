<template>
  <div class="panel">
    <div class="panel-inner stack">
      <strong>{{ title }}</strong>
      <p class="muted">{{ description }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string; description: string }>()
</script>
