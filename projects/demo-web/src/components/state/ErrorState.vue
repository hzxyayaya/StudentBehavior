<template>
  <div class="panel">
    <div class="panel-inner stack">
      <p class="eyebrow">错误状态</p>
      <strong>{{ title }}</strong>
      <p class="muted">{{ description }}</p>
      <button class="btn" type="button" @click="$emit('retry')">重试</button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string; description: string }>()
defineEmits<{ retry: [] }>()
</script>
