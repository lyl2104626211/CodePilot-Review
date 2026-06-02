<script setup lang="ts">
import type { ReportQuality } from '../types/review'

defineProps<{ quality: ReportQuality | null; warnings: string[] }>()
</script>

<template>
  <div v-if="quality" class="qp">
    <div class="sec-head">QUALITY</div>
    <div class="qp-grid">
      <div class="qi"><span class="qn">{{ quality.total_findings }}</span><span class="ql">Findings</span></div>
      <div class="qi hi"><span class="qn">{{ quality.high_confidence_findings }}</span><span class="ql">High Conf</span></div>
      <div class="qi lo"><span class="qn">{{ quality.low_confidence_findings }}</span><span class="ql">Low Conf</span></div>
      <div class="qi bl"><span class="qn">{{ quality.blocking_suggestions }}</span><span class="ql">Blocking</span></div>
    </div>
    <div v-if="quality.notes.length" class="qn-notes">
      <p v-for="(n, i) in quality.notes" :key="i" class="ni">{{ n }}</p>
    </div>
    <div v-if="warnings.length" class="qw">
      <p v-for="(w, i) in warnings" :key="i" class="wl">{{ w }}</p>
    </div>
  </div>
</template>

<style scoped>
.qp {
  margin-bottom: 24px; padding: 16px 22px;
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}
.sec-head {
  font-family: var(--font-heading); font-size: 15px;
  font-weight: 700; letter-spacing: 0.5px;
  color: var(--accent); margin-bottom: 14px;
}
.qp-grid { display: flex; gap: 28px; margin-bottom: 10px; }
.qi { display: flex; flex-direction: column; align-items: center; }
.qn { font-size: 20px; font-weight: 700; font-family: var(--font-heading); color: var(--text-primary); }
.hi .qn { color: var(--success); }
.lo .qn { color: var(--text-muted); }
.bl .qn { color: var(--danger); }
.ql { font-size: 10px; font-weight: 600; letter-spacing: 1.2px; color: var(--text-muted); }
.qn-notes { margin-bottom: 8px; }
.ni { font-size: 12px; color: var(--text-secondary); margin: 3px 0; }
.qw { padding-top: 10px; border-top: 1px solid var(--border); }
.wl { font-size: 12px; color: var(--warning); margin: 2px 0; font-family: var(--font-mono); }
</style>
