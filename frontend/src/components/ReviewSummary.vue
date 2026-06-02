<script setup lang="ts">
import type { ReviewSummary } from '../types/review'

defineProps<{
  summary: ReviewSummary | null | undefined
}>()
</script>

<template>
  <div v-if="summary" class="sum-card">
    <div class="sec-head">SUMMARY</div>
    <p class="overview">{{ summary.overview }}</p>
    <div class="row">
      <span class="rl">MODULES</span>
      <div class="tags">
        <span v-for="m in summary.changed_modules" :key="m" class="tag">{{ m }}</span>
      </div>
    </div>
    <div class="row">
      <span class="rl">FOCUS</span>
      <ul class="flist">
        <li v-for="(f, i) in summary.reviewer_focus" :key="i">{{ f }}</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.sum-card {
  margin-bottom: 24px; background: var(--bg-card);
  border: 1px solid var(--border); border-radius: var(--radius-lg);
  padding: 20px 22px;
}
.sec-head {
  font-family: var(--font-heading); font-size: 15px;
  font-weight: 700; letter-spacing: 0.5px;
  color: var(--teal); margin-bottom: 14px;
}
.overview { margin: 0 0 16px; font-size: 14px; line-height: 1.7; color: var(--text-primary); }
.row { margin-bottom: 12px; }
.rl { font-size: 10px; font-weight: 700; letter-spacing: 1.5px; color: var(--text-muted); margin-right: 10px; }
.tags { display: inline-flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
.tag {
  font-size: 12px; padding: 3px 10px;
  background: var(--bg-elevated); border: 1px solid var(--border);
  border-radius: 2px; color: var(--text-secondary); font-family: var(--font-mono);
}
.flist { margin: 4px 0 0; padding-left: 20px; list-style: square; }
.flist li { margin-bottom: 4px; font-size: 13px; color: var(--text-secondary); }
.flist li::marker { color: var(--accent); }
</style>
