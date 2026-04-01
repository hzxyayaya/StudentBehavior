<template>
  <div class="panel">
    <div class="panel-inner">
      <p class="muted">{{ label }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ label: string }>()
</script>
