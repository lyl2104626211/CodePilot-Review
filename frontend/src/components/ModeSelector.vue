<script setup lang="ts">
import type { ReviewMode } from '../types/review'

defineProps<{ mode: ReviewMode; loading: boolean }>()

const emit = defineEmits<{ 'update:mode': [mode: ReviewMode] }>()

function setMode(m: ReviewMode) { emit('update:mode', m) }
</script>

<template>
  <div class="mode-switch">
    <button :class="['mo', { on: mode === 'demo' }]" :disabled="loading" @click="setMode('demo')">MOCK</button>
    <button :class="['mo', { on: mode === 'github' }]" :disabled="loading" @click="setMode('github')">LIVE</button>
  </div>
</template>

<style scoped>
.mode-switch {
  display: flex; background: var(--bg-input);
  border: 1px solid var(--border); border-radius: var(--radius);
  padding: 3px; gap: 2px;
}
.mo {
  padding: 5px 14px; background: transparent; border: none;
  border-radius: 3px; color: var(--text-muted); cursor: pointer;
  font-family: var(--font-mono); font-size: 10px; font-weight: 600;
  letter-spacing: 1.5px; transition: all 0.2s;
}
.mo.on {
  background: var(--bg-elevated); color: var(--accent);
  border: 1px solid var(--border-hover);
}
.mo:disabled { opacity: 0.4; cursor: not-allowed; }
.mo:hover:not(:disabled):not(.on) { color: var(--text-secondary); }
</style>
