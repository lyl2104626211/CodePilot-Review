<script setup lang="ts">
defineProps<{
  icon?: string
  title: string
  detail?: string
}>()
</script>

<template>
  <div class="empty">
    <span class="empty-icon">{{ icon || '—' }}</span>
    <p class="empty-title">{{ title }}</p>
    <p v-if="detail" class="empty-detail">{{ detail }}</p>
  </div>
</template>

<style scoped>
.empty {
  display: flex; flex-direction: column; align-items: center;
  padding: 40px 20px;
  color: var(--text-muted);
  text-align: center;
}
.empty-icon { font-size: 24px; margin-bottom: 8px; opacity: 0.4; }
.empty-title { font-family: var(--font-heading); font-size: 14px; font-weight: 600; margin: 0; color: var(--text-secondary); }
.empty-detail { font-size: 11px; margin: 6px 0 0; }
</style>
