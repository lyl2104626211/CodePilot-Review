<script setup lang="ts">
defineProps<{
  message: string
  hint?: string
}>()

const emit = defineEmits<{
  retry: []
}>()
</script>

<template>
  <div class="err">
    <span class="err-icon">!</span>
    <p class="err-msg">{{ message }}</p>
    <p v-if="hint" class="err-hint">{{ hint }}</p>
    <button class="retry-btn" @click="emit('retry')">RETRY</button>
  </div>
</template>

<style scoped>
.err {
  display: flex; flex-direction: column; align-items: center;
  padding: 32px 20px; text-align: center;
  background: var(--danger-glow);
  border: 1px solid rgba(248, 113, 113, 0.25);
  border-radius: var(--radius-lg);
  margin-bottom: 20px;
}
.err-icon {
  font-size: 28px; font-weight: 700; color: var(--danger);
  width: 48px; height: 48px; border: 2px solid var(--danger);
  border-radius: 50%; display: flex; align-items: center; justify-content: center;
  margin-bottom: 12px;
}
.err-msg { font-size: 13px; color: var(--danger); margin: 0; font-weight: 600; }
.err-hint { font-size: 11px; color: var(--text-muted); margin: 6px 0 0; }
.retry-btn {
  margin-top: 12px; padding: 6px 20px;
  background: transparent; border: 1px solid var(--danger); border-radius: var(--radius);
  color: var(--danger); cursor: pointer; font-family: var(--font-mono);
  font-size: 10px; font-weight: 600; letter-spacing: 1px;
}
.retry-btn:hover { background: rgba(248, 113, 113, 0.1); }
</style>
