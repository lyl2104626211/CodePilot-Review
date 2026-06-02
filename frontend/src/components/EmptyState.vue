<script setup lang="ts">
defineProps<{ icon?: string; title: string; detail?: string }>()
</script>

<template>
  <div class="es">
    <span class="ei">{{ icon || '—' }}</span>
    <p class="et">{{ title }}</p>
    <p v-if="detail" class="ed">{{ detail }}</p>
  </div>
</template>

<style scoped>
.es {
  display: flex; flex-direction: column; align-items: center;
  padding: 48px 20px; color: var(--text-muted); text-align: center;
}
.ei { font-size: 28px; margin-bottom: 10px; opacity: 0.35; }
.et { font-family: var(--font-heading); font-size: 15px; font-weight: 600; margin: 0; color: var(--text-secondary); }
.ed { font-size: 13px; margin: 8px 0 0; }
</style>
