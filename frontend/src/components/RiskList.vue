<script setup lang="ts">
import type { RiskFinding } from '../types/review'

defineProps<{ findings: RiskFinding[] }>()

function sevColor(s: string): string {
  const m: Record<string, string> = {
    critical: '#f87171', high: '#fbbf24', medium: '#60a5fa', low: '#8e929b',
  }
  return m[s] || '#8e929b'
}

function sevLabel(s: string): string {
  const m: Record<string, string> = {
    critical: 'CRIT', high: 'HIGH', medium: 'MED', low: 'LOW',
  }
  return m[s] || s.toUpperCase()
}
</script>

<template>
  <div v-if="findings.length" class="risk-section">
    <div class="section-header">
      <span class="section-icon">&#9888;</span>
      <span>RISKS</span>
      <span class="section-count">{{ findings.length }}</span>
    </div>
    <div v-for="f in findings" :key="f.id" class="risk-row">
      <div class="risk-top">
        <span class="risk-badge" :style="{ color: sevColor(f.severity), borderColor: sevColor(f.severity) }">
          {{ sevLabel(f.severity) }}
        </span>
        <span class="risk-category">{{ f.category }}</span>
        <span class="risk-confidence">{{ Math.round(Math.min(Math.max(f.confidence, 0), 1) * 100) }}%</span>
      </div>
      <h4 class="risk-title">{{ f.title }}</h4>
      <div class="risk-location">
        <span class="loc-icon">&gt;</span>
        <span class="loc-path">{{ f.file_path }}</span>
        <span v-if="f.line !== undefined && f.line !== null" class="loc-line">:{{ f.line }}</span>
      </div>
      <div class="risk-details">
        <p class="detail-line"><span class="detail-label">EVIDENCE</span>{{ f.evidence }}</p>
        <p class="detail-line"><span class="detail-label">REASON</span>{{ f.reasoning }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.risk-section { margin-bottom: 24px; }
.section-header {
  display: flex; align-items: center; gap: 8px;
  font-family: var(--font-heading); font-size: 13px;
  font-weight: 700; letter-spacing: 0.5px;
  color: var(--danger); margin-bottom: 12px;
}
.section-icon { font-size: 13px; }
.section-count { margin-left: auto; font-size: 11px; color: var(--text-muted); }
.risk-row {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: 14px 18px;
  margin-bottom: 8px; transition: border-color 0.15s;
}
.risk-row:hover { border-color: var(--border-hover); }
.risk-top { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.risk-badge {
  font-size: 9px; font-weight: 700; letter-spacing: 1px;
  padding: 2px 6px; border: 1px solid; border-radius: 2px;
  font-family: var(--font-mono);
}
.risk-category { font-size: 10px; color: var(--text-muted); letter-spacing: 0.8px; }
.risk-confidence { margin-left: auto; font-size: 10px; color: var(--text-muted); font-family: var(--font-mono); }
.risk-title { margin: 0 0 6px; font-size: 13px; font-weight: 600; color: var(--text-primary); }
.risk-location {
  display: flex; align-items: center; gap: 4px;
  margin-bottom: 10px; font-size: 11px; font-family: var(--font-mono);
}
.loc-icon { color: var(--accent); }
.loc-path { color: var(--teal); }
.loc-line { color: var(--text-muted); }
.risk-details { display: flex; flex-direction: column; gap: 4px; }
.detail-line { font-size: 11px; color: var(--text-secondary); line-height: 1.5; margin: 0; }
.detail-label {
  font-size: 8px; font-weight: 700; letter-spacing: 1.2px;
  color: var(--text-muted); margin-right: 8px;
}
</style>
