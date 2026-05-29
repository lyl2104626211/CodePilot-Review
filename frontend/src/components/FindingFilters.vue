<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { RiskFinding } from '../types/review'

const props = defineProps<{
  findings: RiskFinding[]
}>()

const emit = defineEmits<{
  'update:filtered': [findings: RiskFinding[]]
}>()

const selectedSeverity = ref<string>('all')
const showLowConfidence = ref(true)

const filtered = computed(() => {
  let result = props.findings
  if (selectedSeverity.value !== 'all') {
    result = result.filter(f => f.severity === selectedSeverity.value)
  }
  if (!showLowConfidence.value) {
    result = result.filter(f => f.confidence >= 0.5)
  }
  return result
})

watch(filtered, (val) => emit('update:filtered', val), { immediate: true })

const filters = ['all', 'critical', 'high', 'medium', 'low']
</script>

<template>
  <div class="filter-bar">
    <div class="filter-group">
      <span class="filter-label">SEV</span>
      <button
        v-for="f in filters"
        :key="f"
        :class="['chip', { on: selectedSeverity === f }]"
        @click="selectedSeverity = f"
      >
        {{ f === 'all' ? 'ALL' : f.toUpperCase() }}
      </button>
    </div>

    <label class="toggle">
      <input type="checkbox" v-model="showLowConfidence" />
      <span class="toggle-text">LOW CONF</span>
    </label>

    <span class="count">{{ filtered.length }} / {{ findings.length }}</span>
  </div>
</template>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
  padding: 8px 0;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 4px;
}
.filter-label {
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 1.5px;
  color: var(--text-muted);
  margin-right: 6px;
}

.chip {
  padding: 3px 10px;
  border: 1px solid var(--border);
  border-radius: 2px;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  font-family: var(--font-mono);
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 0.5px;
  transition: all 0.15s;
}
.chip.on {
  background: var(--bg-elevated);
  border-color: var(--border-hover);
  color: var(--text-primary);
}
.chip:hover:not(.on) { border-color: var(--border-hover); }

.toggle {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
  user-select: none;
}
.toggle input { accent-color: var(--accent); }
.toggle-text {
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 0.5px;
  color: var(--text-muted);
}

.count {
  margin-left: auto;
  font-size: 10px;
  color: var(--text-muted);
  font-family: var(--font-mono);
}
</style>
