<template>
  <div class="panel">
    <div class="panel-inner stack">
      <p class="eyebrow">空状态</p>
      <strong>{{ title }}</strong>
      <p class="muted">{{ description }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string; description: string }>()
</script>
