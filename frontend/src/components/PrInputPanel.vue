<script setup lang="ts">
import { ref } from 'vue'
import type { ReviewMode } from '../types/review'

defineProps<{
  loading: boolean
  error?: string
  mode?: ReviewMode
}>()

const emit = defineEmits<{
  submit: [url: string]
}>()

const url = ref('')
const localError = ref('')

function handleSubmit() {
  localError.value = ''
  const trimmed = url.value.trim()
  if (!trimmed) {
    localError.value = 'Please enter a GitHub PR URL'
    return
  }
  emit('submit', trimmed)
}
</script>

<template>
  <div class="input-section">
    <div class="input-row">
      <span class="prompt">$</span>
      <input
        v-model="url"
        type="text"
        placeholder="github.com/{owner}/{repo}/pull/{number}"
        :disabled="loading"
        @keyup.enter="handleSubmit"
      />
      <button :disabled="loading || !url.trim()" @click="handleSubmit">
        <template v-if="!loading">Run Review</template>
        <template v-else>
          <span class="spinner"></span> Analyzing...
        </template>
      </button>
    </div>
    <div class="input-meta">
      <span class="mode-tag" v-if="mode === 'demo'">MOCK DATA</span>
      <span class="mode-tag live" v-else>LIVE GITHUB</span>
      <span class="input-hint">Paste a PR URL and press Enter</span>
    </div>
    <p v-if="localError || error" class="error-line">
      <span class="error-prefix">!</span> {{ localError || error }}
    </p>
  </div>
</template>

<style scoped>
.input-section { margin-bottom: 24px; }

.input-row {
  display: flex; align-items: center; gap: 10px;
  background: var(--bg-input); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: 10px 14px;
  transition: border-color 0.2s;
}
.input-row:focus-within {
  border-color: var(--border-active);
  box-shadow: 0 0 0 3px var(--accent-glow);
}

.prompt { color: var(--accent); font-weight: 600; font-size: 15px; user-select: none; }

.input-row input {
  flex: 1; background: transparent; border: none; outline: none;
  color: var(--text-primary); font-family: var(--font-mono);
  font-size: 13px; letter-spacing: 0.2px;
}
.input-row input::placeholder { color: var(--text-muted); }
.input-row input:disabled { opacity: 0.5; }

.input-row button {
  padding: 8px 20px; background: var(--accent); color: #000;
  border: none; border-radius: var(--radius); cursor: pointer;
  font-family: var(--font-heading); font-size: 13px; font-weight: 700;
  letter-spacing: 0.3px; white-space: nowrap; transition: all 0.2s;
  display: flex; align-items: center; gap: 6px;
}
.input-row button:hover:not(:disabled) {
  background: #fcd34d;
  box-shadow: 0 0 20px rgba(251, 191, 36, 0.3);
}
.input-row button:disabled { opacity: 0.5; cursor: not-allowed; }

.spinner {
  width: 12px; height: 12px;
  border: 2px solid #000; border-top-color: transparent;
  border-radius: 50%; animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.input-meta {
  display: flex; align-items: center; gap: 10px;
  margin-top: 8px; padding: 0 4px;
}

.mode-tag {
  font-size: 9px; font-weight: 600; letter-spacing: 1.5px;
  padding: 2px 6px; border: 1px solid var(--border);
  border-radius: 2px; color: var(--text-muted);
}
.mode-tag.live { color: var(--teal); border-color: var(--teal); }
.input-hint { font-size: 11px; color: var(--text-muted); }

.error-line {
  display: flex; align-items: center; gap: 8px;
  margin: 8px 0 0; padding: 8px 12px;
  background: var(--danger-glow);
  border: 1px solid rgba(248, 113, 113, 0.25);
  border-radius: var(--radius); font-size: 12px; color: var(--danger);
}
.error-prefix { font-weight: 700; font-size: 14px; }
</style>
