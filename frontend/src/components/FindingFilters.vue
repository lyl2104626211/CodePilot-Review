<script setup lang="ts">
import { computed, ref } from 'vue'
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

// 实时通知父组件
import { watch } from 'vue'
watch(filtered, (val) => emit('update:filtered', val), { immediate: true })

const severities = [
  { value: 'all', label: '全部' },
  { value: 'critical', label: '严重' },
  { value: 'high', label: '高' },
  { value: 'medium', label: '中' },
  { value: 'low', label: '低' },
]
</script>

<template>
  <div v-if="findings.length > 0" class="finding-filters">
    <div class="filter-row">
      <span class="filter-label">严重程度：</span>
      <button
        v-for="s in severities"
        :key="s.value"
        :class="['filter-btn', { active: selectedSeverity === s.value }]"
        @click="selectedSeverity = s.value"
      >
        {{ s.label }}
      </button>
    </div>
    <label class="confidence-toggle">
      <input type="checkbox" v-model="showLowConfidence" />
      显示低置信度 (&lt; 50%)
    </label>
    <span class="filter-count">显示 {{ filtered.length }} / {{ findings.length }} 条</span>
  </div>
</template>

<style scoped>
.finding-filters {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
  padding: 8px 0;
}
.filter-row {
  display: flex;
  align-items: center;
  gap: 4px;
}
.filter-label {
  font-size: 13px;
  color: #666;
}
.filter-btn {
  padding: 2px 10px;
  border: 1px solid #d0d0d0;
  border-radius: 4px;
  background: #fff;
  cursor: pointer;
  font-size: 12px;
}
.filter-btn.active {
  background: #4a90d9;
  color: #fff;
  border-color: #4a90d9;
}
.confidence-toggle {
  font-size: 12px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}
.filter-count {
  font-size: 12px;
  color: #999;
  margin-left: auto;
}
</style>
