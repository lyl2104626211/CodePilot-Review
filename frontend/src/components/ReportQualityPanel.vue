<script setup lang="ts">
import type { ReportQuality } from '../types/review'

defineProps<{
  quality: ReportQuality | null
  warnings: string[]
}>()
</script>

<template>
  <div v-if="quality" class="qual-panel">
    <div class="qual-grid">
      <div class="qual-item">
        <span class="qual-num">{{ quality.total_findings }}</span>
        <span class="qual-label">Findings</span>
      </div>
      <div class="qual-item hi">
        <span class="qual-num">{{ quality.high_confidence_findings }}</span>
        <span class="qual-label">High Conf</span>
      </div>
      <div class="qual-item lo">
        <span class="qual-num">{{ quality.low_confidence_findings }}</span>
        <span class="qual-label">Low Conf</span>
      </div>
      <div class="qual-item bl">
        <span class="qual-num">{{ quality.blocking_suggestions }}</span>
        <span class="qual-label">Blocking</span>
      </div>
    </div>

    <div v-if="quality.notes.length" class="qual-notes">
      <p v-for="(n, i) in quality.notes" :key="i" class="note-item">{{ n }}</p>
    </div>

    <div v-if="warnings.length" class="qual-warn">
      <p v-for="(w, i) in warnings" :key="i" class="warn-line">{{ w }}</p>
    </div>
  </div>
</template>

<style scoped>
.qual-panel {
  margin-bottom: 20px;
  padding: 14px 18px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}
.qual-grid { display: flex; gap: 24px; margin-bottom: 8px; }
.qual-item { display: flex; flex-direction: column; align-items: center; }
.qual-num {
  font-size: 18px; font-weight: 700; font-family: var(--font-heading);
  color: var(--text-primary);
}
.hi .qual-num { color: var(--success); }
.lo .qual-num { color: var(--text-muted); }
.bl .qual-num { color: var(--danger); }
.qual-label {
  font-size: 8px; font-weight: 600; letter-spacing: 1.2px;
  color: var(--text-muted); text-transform: uppercase;
}
.qual-notes { margin-bottom: 8px; }
.note-item { font-size: 11px; color: var(--text-secondary); margin: 3px 0; }
.qual-warn { padding-top: 8px; border-top: 1px solid var(--border); }
.warn-line { font-size: 11px; color: var(--warning); margin: 2px 0; font-family: var(--font-mono); }
</style>
