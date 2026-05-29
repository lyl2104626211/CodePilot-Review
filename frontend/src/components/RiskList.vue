<script setup lang="ts">
import type { RiskFinding } from '../types/review'

defineProps<{
  findings: RiskFinding[]
}>()

function severityClass(severity: string): string {
  return `severity-${severity}`
}

function severityLabel(severity: string): string {
  const map: Record<string, string> = {
    critical: '严重',
    high: '高',
    medium: '中',
    low: '低',
  }
  return map[severity] || severity
}
</script>

<template>
  <div v-if="findings.length" class="risk-list">
    <h3>风险发现 ({{ findings.length }})</h3>
    <div v-for="f in findings" :key="f.id" class="risk-card">
      <div class="risk-header">
        <span :class="['severity-badge', severityClass(f.severity)]">
          {{ severityLabel(f.severity) }}
        </span>
        <span class="risk-category">{{ f.category }}</span>
        <span class="risk-confidence">置信度 {{ (f.confidence * 100).toFixed(0) }}%</span>
      </div>
      <h4>{{ f.title }}</h4>
      <p class="risk-file">{{ f.file_path }}{{ f.line ? `:${f.line}` : '' }}</p>
      <p class="risk-evidence"><strong>证据：</strong>{{ f.evidence }}</p>
      <p class="risk-reasoning"><strong>分析：</strong>{{ f.reasoning }}</p>
    </div>
  </div>
</template>

<style scoped>
.risk-list {
  margin-bottom: 20px;
}
h3 {
  margin: 0 0 12px;
  font-size: 16px;
}
.risk-card {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 14px 16px;
  margin-bottom: 10px;
}
.risk-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.severity-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  color: #fff;
}
.severity-critical { background: #d9534f; }
.severity-high { background: #f0ad4e; }
.severity-medium { background: #5bc0de; }
.severity-low { background: #999; }
.risk-category {
  font-size: 12px;
  color: #888;
}
.risk-confidence {
  font-size: 12px;
  color: #aaa;
  margin-left: auto;
}
h4 {
  margin: 0 0 4px;
  font-size: 14px;
}
.risk-file {
  font-size: 12px;
  color: #4a90d9;
  font-family: monospace;
  margin: 0 0 8px;
}
.risk-evidence, .risk-reasoning {
  font-size: 13px;
  color: #555;
  margin: 0 0 4px;
  line-height: 1.5;
}
</style>
