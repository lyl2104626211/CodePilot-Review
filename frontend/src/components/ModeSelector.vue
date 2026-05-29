<script setup lang="ts">
import type { ReviewMode } from '../types/review'

defineProps<{
  mode: ReviewMode
  loading: boolean
}>()

const emit = defineEmits<{
  'update:mode': [mode: ReviewMode]
}>()

function setMode(mode: ReviewMode) {
  emit('update:mode', mode)
}
</script>

<template>
  <div class="mode-switch">
    <button
      :class="['mode-option', { active: mode === 'demo' }]"
      :disabled="loading"
      @click="setMode('demo')"
    >
      MOCK
    </button>
    <button
      :class="['mode-option', { active: mode === 'github' }]"
      :disabled="loading"
      @click="setMode('github')"
    >
      LIVE
    </button>
  </div>
</template>

<style scoped>
.mode-switch {
  display: flex;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 3px;
  gap: 2px;
}

.mode-option {
  padding: 5px 14px;
  background: transparent;
  border: none;
  border-radius: 3px;
  color: var(--text-muted);
  cursor: pointer;
  font-family: var(--font-mono);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 1.5px;
  transition: all 0.2s;
}
.mode-option.active {
  background: var(--bg-elevated);
  color: var(--accent);
  border: 1px solid var(--border-hover);
}
.mode-option:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.mode-option:hover:not(:disabled):not(.active) {
  color: var(--text-secondary);
}
</style>
