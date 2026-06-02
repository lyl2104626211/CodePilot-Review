<script setup lang="ts">
import type { RiskFinding } from '../types/review'

defineProps<{ findings: RiskFinding[] }>()

function sevColor(s: string): string {
  const m: Record<string, string> = { critical: '#f87171', high: '#fbbf24', medium: '#60a5fa', low: '#8e929b' }
  return m[s] || '#8e929b'
}

function sevLabel(s: string): string {
  const m: Record<string, string> = { critical: 'CRIT', high: 'HIGH', medium: 'MED', low: 'LOW' }
  return m[s] || s.toUpperCase()
}
</script>

<template>
  <div v-if="findings.length" class="rk-section">
    <div class="sec-head">
      <span class="sec-icon">&#9888;</span>
      <span>RISKS</span>
      <span class="sec-count">{{ findings.length }}</span>
    </div>
    <div v-for="f in findings" :key="f.id" class="rk-card">
      <div class="rk-top">
        <span class="rk-badge" :style="{ color: sevColor(f.severity), borderColor: sevColor(f.severity) }">
          {{ sevLabel(f.severity) }}
        </span>
        <span class="rk-cat">{{ f.category }}</span>
        <span class="rk-conf">{{ Math.round(Math.min(Math.max(f.confidence, 0), 1) * 100) }}%</span>
      </div>
      <h4 class="rk-title">{{ f.title }}</h4>
      <div class="rk-loc">
        <span class="loc-icon">&gt;</span>
        <span class="loc-path">{{ f.file_path }}</span>
        <span v-if="f.line !== undefined && f.line !== null" class="loc-line">:{{ f.line }}</span>
      </div>
      <div class="rk-detail">
        <p class="rk-line"><span class="rk-lbl">EVIDENCE</span>{{ f.evidence }}</p>
        <p class="rk-line"><span class="rk-lbl">REASON</span>{{ f.reasoning }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.rk-section { margin-bottom: 24px; }
.sec-head {
  display: flex; align-items: center; gap: 8px;
  font-family: var(--font-heading); font-size: 15px;
  font-weight: 700; letter-spacing: 0.5px;
  color: var(--danger); margin-bottom: 14px;
}
.sec-icon { font-size: 15px; }
.sec-count { margin-left: auto; font-size: 12px; color: var(--text-muted); }

.rk-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: 14px 18px;
  margin-bottom: 8px; transition: border-color 0.15s;
}
.rk-card:hover { border-color: var(--border-hover); }
.rk-top { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.rk-badge {
  font-size: 10px; font-weight: 700; letter-spacing: 1px;
  padding: 2px 8px; border: 1px solid; border-radius: 2px;
  font-family: var(--font-mono);
}
.rk-cat { font-size: 11px; color: var(--text-muted); letter-spacing: 0.8px; }
.rk-conf { margin-left: auto; font-size: 12px; color: var(--text-muted); font-family: var(--font-mono); }
.rk-title { margin: 0 0 6px; font-size: 14px; font-weight: 600; color: var(--text-primary); }

.rk-loc {
  display: flex; align-items: center; gap: 4px;
  margin-bottom: 10px; font-size: 12px; font-family: var(--font-mono);
}
.loc-icon { color: var(--accent); }
.loc-path { color: var(--teal); }
.loc-line { color: var(--text-muted); }

.rk-detail { display: flex; flex-direction: column; gap: 5px; }
.rk-line { font-size: 12px; color: var(--text-secondary); line-height: 1.5; margin: 0; }
.rk-lbl {
  font-size: 10px; font-weight: 700; letter-spacing: 1.2px;
  color: var(--text-muted); margin-right: 8px;
}
</style>
