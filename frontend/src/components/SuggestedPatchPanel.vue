<script setup lang="ts">
import { ref } from 'vue'
import type { ReviewSuggestion, SuggestedPatch } from '../types/review'
import { createSuggestedPatches } from '../api/reviews'
import DiffViewer from './DiffViewer.vue'

const props = defineProps<{
  taskId: string
  suggestions: ReviewSuggestion[]
}>()

const selectedIds = ref<Set<string>>(new Set())
const patches = ref<SuggestedPatch[]>([])
const loading = ref(false)
const error = ref('')

function toggle(id: string) {
  const next = new Set(selectedIds.value)
  next.has(id) ? next.delete(id) : next.add(id)
  selectedIds.value = next
}

async function generate() {
  if (selectedIds.value.size === 0) return
  loading.value = true; error.value = ''
  try {
    const resp = await createSuggestedPatches(props.taskId, Array.from(selectedIds.value))
    patches.value = resp.patches
  } catch (e: any) {
    error.value = e.message || '生成失败'
  } finally { loading.value = false }
}
</script>

<template>
  <div v-if="suggestions.length" class="patch-panel">
    <div class="pp-head">
      <span class="pp-title">FIX PREVIEW</span>
    </div>

    <div v-for="s in suggestions" :key="s.id" class="pp-sug-item" :class="{ picked: selectedIds.has(s.id) }" @click="toggle(s.id)">
      <span class="pp-check">{{ selectedIds.has(s.id) ? '&#9632;' : '&#9633;' }}</span>
      <span class="pp-comment">{{ s.comment.slice(0, 60) }}{{ s.comment.length > 60 ? '...' : '' }}</span>
      <span v-if="s.file_path" class="pp-fpath">{{ s.file_path }}</span>
    </div>

    <button class="pp-btn" :disabled="selectedIds.size === 0 || loading" @click="generate">
      {{ loading ? 'GENERATING...' : `PREVIEW FIX (${selectedIds.size})` }}
    </button>

    <p v-if="error" class="pp-err">! {{ error }}</p>

    <DiffViewer v-for="p in patches" :key="p.id" :patch="p" />
  </div>
</template>

<style scoped>
.patch-panel {
  margin-bottom: 20px; padding: 16px 18px;
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}
.pp-head { margin-bottom: 10px; }
.pp-title {
  font-family: var(--font-heading); font-size: 13px;
  font-weight: 700; letter-spacing: 0.5px; color: var(--accent);
}
.pp-sug-item {
  display: flex; align-items: center; gap: 8px;
  padding: 6px 10px; margin-bottom: 3px;
  border: 1px solid transparent; border-radius: var(--radius);
  cursor: pointer; transition: all 0.15s;
}
.pp-sug-item:hover { background: var(--bg-elevated); }
.pp-sug-item.picked { border-color: var(--border-active); background: var(--bg-elevated); }
.pp-check { font-size: 13px; color: var(--accent); flex-shrink: 0; }
.pp-comment { font-size: 11px; color: var(--text-primary); flex: 1; min-width: 0; }
.pp-fpath { font-size: 10px; color: var(--teal); font-family: var(--font-mono); flex-shrink: 0; }

.pp-btn {
  width: 100%; margin-top: 10px; margin-bottom: 16px; padding: 8px;
  background: var(--accent); color: #000;
  border: none; border-radius: var(--radius); cursor: pointer;
  font-family: var(--font-heading); font-size: 12px; font-weight: 700;
  letter-spacing: 0.5px; transition: all 0.2s;
}
.pp-btn:hover:not(:disabled) { background: #fcd34d; box-shadow: 0 0 20px rgba(251, 191, 36, 0.3); }
.pp-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.pp-err { color: var(--danger); font-size: 11px; margin: 4px 0; }
</style>
