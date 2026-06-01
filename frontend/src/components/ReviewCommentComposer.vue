<script setup lang="ts">
import { ref } from 'vue'
import type { ReviewSuggestion } from '../types/review'

const props = defineProps<{
  suggestions: ReviewSuggestion[]
  loading: boolean
}>()

const emit = defineEmits<{
  generate: [ids: string[]]
}>()

const selectedIds = ref<Set<string>>(new Set())

function toggle(id: string) {
  const next = new Set(selectedIds.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  selectedIds.value = next
}

function selectAll() {
  if (selectedIds.value.size === props.suggestions.length) {
    selectedIds.value = new Set()
  } else {
    selectedIds.value = new Set(props.suggestions.map(s => s.id))
  }
}

function doGenerate() {
  emit('generate', Array.from(selectedIds.value))
}
</script>

<template>
  <div v-if="suggestions.length" class="composer">
    <div class="comp-head">
      <span class="comp-title">SELECT SUGGESTIONS</span>
      <button class="select-all" @click="selectAll">
        {{ selectedIds.size === suggestions.length ? 'CLEAR' : 'ALL' }}
      </button>
    </div>

    <div v-for="s in suggestions" :key="s.id" class="sug-item" :class="{ picked: selectedIds.has(s.id) }" @click="toggle(s.id)">
      <span class="check-box">{{ selectedIds.has(s.id) ? '&#9632;' : '&#9633;' }}</span>
      <div class="sug-info">
        <span class="sug-comment">{{ s.comment.slice(0, 80) }}{{ s.comment.length > 80 ? '...' : '' }}</span>
        <div class="sug-meta">
          <span v-if="s.blocking" class="blk-tag">BLOCK</span>
          <span v-if="s.file_path" class="sug-fpath">{{ s.file_path }}</span>
        </div>
      </div>
    </div>

    <button class="gen-btn" :disabled="selectedIds.size === 0 || loading" @click="doGenerate">
      {{ loading ? 'GENERATING...' : `GENERATE (${selectedIds.size})` }}
    </button>
  </div>
  <div v-else class="composer empty-hint">No suggestions to select</div>
</template>

<style scoped>
.composer {
  margin-bottom: 20px;
  padding: 16px 18px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}
.comp-head {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 10px;
}
.comp-title {
  font-family: var(--font-heading);
  font-size: 13px; font-weight: 700; letter-spacing: 0.5px; color: var(--teal);
}
.select-all {
  font-size: 9px; font-weight: 600; letter-spacing: 1px;
  background: none; border: 1px solid var(--border); border-radius: 2px;
  color: var(--text-muted); cursor: pointer; padding: 2px 8px;
  font-family: var(--font-mono);
}
.select-all:hover { border-color: var(--border-hover); color: var(--text-secondary); }

.sug-item {
  display: flex; align-items: flex-start; gap: 10px;
  padding: 8px 10px; margin-bottom: 4px;
  border: 1px solid transparent; border-radius: var(--radius);
  cursor: pointer; transition: all 0.15s;
}
.sug-item:hover { background: var(--bg-elevated); }
.sug-item.picked { border-color: var(--border-active); background: var(--bg-elevated); }

.check-box {
  font-size: 14px; color: var(--accent); flex-shrink: 0; margin-top: 1px;
}
.sug-info { flex: 1; min-width: 0; }
.sug-comment { font-size: 12px; color: var(--text-primary); }
.sug-meta { display: flex; gap: 8px; margin-top: 3px; }
.blk-tag {
  font-size: 8px; font-weight: 700; letter-spacing: 1px;
  color: var(--danger); border: 1px solid rgba(248, 113, 113, 0.4);
  padding: 1px 4px; border-radius: 2px;
}
.sug-fpath { font-size: 10px; color: var(--teal); font-family: var(--font-mono); }

.gen-btn {
  width: 100%; margin-top: 10px; padding: 9px;
  background: var(--accent); color: #000;
  border: none; border-radius: var(--radius); cursor: pointer;
  font-family: var(--font-heading); font-size: 12px; font-weight: 700;
  letter-spacing: 0.5px; transition: all 0.2s;
}
.gen-btn:hover:not(:disabled) { background: #fcd34d; box-shadow: 0 0 20px rgba(251, 191, 36, 0.3); }
.gen-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.empty-hint { color: var(--text-muted); font-size: 12px; text-align: center; padding: 16px; }
</style>
