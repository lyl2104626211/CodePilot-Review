<script setup lang="ts">
import type { ReviewMode } from '../types/review'

const props = defineProps<{ mode: ReviewMode; loading: boolean }>()
const emit = defineEmits<{ 'update:mode': [mode: ReviewMode] }>()

function setMode(m: ReviewMode) { if (!props.loading) emit('update:mode', m) }
</script>

<template>
  <div class="ms">
    <button :class="['mb', { on: mode === 'demo' }]" :disabled="loading" @click="setMode('demo')">MOCK</button>
    <button :class="['mb', { on: mode === 'github' }]" :disabled="loading" @click="setMode('github')">LIVE</button>
  </div>
</template>

<style scoped>
.ms { display: flex; gap: 2px; background: var(--bg-input); border: 1px solid var(--border); border-radius: var(--radius); padding: 2px; }
.mb {
  padding: 5px 16px; border: none; border-radius: 3px; cursor: pointer;
  font-family: var(--font-mono); font-size: 11px; font-weight: 600;
  letter-spacing: 1px; color: var(--text-muted); background: transparent; transition: all 0.15s;
}
.mb.on { background: var(--bg-elevated); color: var(--text-primary); }
.mb:hover:not(:disabled):not(.on) { color: var(--text-secondary); }
.mb:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
