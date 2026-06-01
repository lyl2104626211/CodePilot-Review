<script setup lang="ts">
import type { SuggestedPatch } from '../types/review'
import { ref } from 'vue'

const props = defineProps<{ patch: SuggestedPatch }>()

const copied = ref(false)
const diffCopied = ref(false)

async function copySuggestion() {
  try {
    await navigator.clipboard.writeText(props.patch.github_suggestion || '')
    copied.value = true; setTimeout(() => copied.value = false, 2000)
  } catch { /* noop */ }
}
async function copyDiff() {
  try {
    await navigator.clipboard.writeText(props.patch.unified_diff || '')
    diffCopied.value = true; setTimeout(() => diffCopied.value = false, 2000)
  } catch { /* noop */ }
}

function getLineClass(line: string) {
  if (line.startsWith('+') && !line.startsWith('+++')) return 'add'
  if (line.startsWith('-') && !line.startsWith('---')) return 'rem'
  if (line.startsWith('@@')) return 'hunk'
  return ''
}
</script>

<template>
  <div v-if="patch.patch_type !== 'none'" class="dv-wrap">
    <div class="dv-head">
      <span class="dv-file">{{ patch.file_path }}</span>
      <span :class="['dv-tag', patch.applicable ? 'ok' : 'warn']">
        {{ patch.applicable ? 'APPLICABLE' : 'REFERENCE ONLY' }}
      </span>
    </div>

    <p class="dv-expl">{{ patch.explanation }}</p>

    <div v-if="patch.unified_diff" class="dv-diff">
      <div v-for="(line, i) in patch.unified_diff.split('\n')" :key="i" :class="['dv-line', getLineClass(line)]">
        <span class="dv-lno">{{ i + 1 }}</span>
        <span class="dv-code">{{ line }}</span>
      </div>
    </div>

    <div v-if="patch.validation_warnings.length" class="dv-warn">
      <span v-for="(w, i) in patch.validation_warnings" :key="i">! {{ w }}</span>
    </div>

    <div class="dv-actions">
      <button class="act-btn" @click="copySuggestion" v-if="patch.github_suggestion">
        {{ copied ? 'COPIED' : 'COPY SUGGESTION' }}
      </button>
      <button class="act-btn" @click="copyDiff" v-if="patch.unified_diff">
        {{ diffCopied ? 'COPIED' : 'COPY DIFF' }}
      </button>
    </div>
  </div>

  <div v-else class="dv-none">
    <p>{{ patch.explanation }}</p>
  </div>
</template>

<style scoped>
.dv-wrap {
  margin-bottom: 14px; background: var(--bg-card);
  border: 1px solid var(--border); border-radius: var(--radius-lg);
  padding: 14px 16px;
}
.dv-head {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 8px;
}
.dv-file {
  font-size: 11px; color: var(--teal); font-family: var(--font-mono);
}
.dv-tag {
  font-size: 8px; font-weight: 700; letter-spacing: 1px;
  padding: 2px 6px; border-radius: 2px; font-family: var(--font-mono);
}
.dv-tag.ok { color: var(--success); border: 1px solid rgba(74, 222, 128, 0.4); }
.dv-tag.warn { color: var(--warning); border: 1px solid rgba(251, 191, 36, 0.4); }
.dv-expl { font-size: 11px; color: var(--text-secondary); margin: 6px 0; }

.dv-diff {
  background: #0d1117; border: 1px solid #21262d; border-radius: 4px;
  overflow-x: auto; font-family: var(--font-mono); font-size: 11px;
  margin: 8px 0; max-height: 360px; overflow-y: auto;
}
.dv-line {
  display: flex; line-height: 1.5; min-height: 20px;
}
.dv-line.add { background: rgba(74, 222, 128, 0.06); }
.dv-line.rem { background: rgba(248, 113, 113, 0.06); }
.dv-line.hunk { color: var(--accent); }
.dv-lno {
  width: 30px; text-align: right; padding-right: 8px;
  color: var(--text-muted); user-select: none; flex-shrink: 0;
}
.dv-code { white-space: pre; }
.dv-line.add .dv-code { color: #4ade80; }
.dv-line.rem .dv-code { color: #f87171; }
.dv-line.hunk .dv-code { color: var(--accent); }

.dv-warn { margin: 6px 0; }
.dv-warn span {
  display: block; font-size: 10px; color: var(--warning);
  margin: 2px 0;
}
.dv-actions { display: flex; gap: 6px; margin-top: 8px; }
.act-btn {
  font-size: 9px; font-weight: 600; letter-spacing: 1px;
  background: var(--bg-elevated); border: 1px solid var(--border);
  border-radius: 2px; color: var(--text-secondary); cursor: pointer;
  padding: 4px 10px; font-family: var(--font-mono);
}
.act-btn:hover { border-color: var(--border-hover); color: var(--accent); }

.dv-none {
  padding: 12px 16px; color: var(--text-muted);
  font-size: 11px; text-align: center;
}
</style>
