<script setup lang="ts">
import type { ReviewSummary } from '../types/review'

defineProps<{
  summary: ReviewSummary | null | undefined
}>()
</script>

<template>
  <div v-if="summary" class="summary-card">
    <div class="card-header">
      <span class="card-icon">&#9636;</span>
      <span>SUMMARY</span>
    </div>
    <p class="overview">{{ summary.overview }}</p>
    <div class="summary-row">
      <span class="row-label">MODULES</span>
      <div class="tag-list">
        <span v-for="m in summary.changed_modules" :key="m" class="tag">{{ m }}</span>
      </div>
    </div>
    <div class="summary-row">
      <span class="row-label">FOCUS</span>
      <ul class="focus-list">
        <li v-for="(f, i) in summary.reviewer_focus" :key="i">{{ f }}</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.summary-card {
  margin-bottom: 24px; background: var(--bg-card);
  border: 1px solid var(--border); border-radius: var(--radius-lg);
  padding: 18px 20px;
}
.card-header {
  display: flex; align-items: center; gap: 8px;
  font-family: var(--font-heading); font-size: 13px;
  font-weight: 700; letter-spacing: 0.5px;
  color: var(--teal); margin-bottom: 14px;
}
.card-icon { font-size: 12px; }
.overview {
  margin: 0 0 16px; font-size: 13px;
  line-height: 1.7; color: var(--text-primary);
}
.summary-row { margin-bottom: 10px; }
.row-label {
  font-size: 9px; font-weight: 600; letter-spacing: 1.5px;
  color: var(--text-muted); margin-right: 10px;
}
.tag-list { display: inline-flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
.tag {
  font-size: 10px; padding: 2px 8px;
  background: var(--bg-elevated); border: 1px solid var(--border);
  border-radius: 2px; color: var(--text-secondary); font-family: var(--font-mono);
}
.focus-list { margin: 4px 0 0; padding-left: 18px; list-style: square; }
.focus-list li { margin-bottom: 3px; font-size: 12px; color: var(--text-secondary); }
.focus-list li::marker { color: var(--accent); }
</style>
