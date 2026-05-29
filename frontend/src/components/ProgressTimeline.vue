<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  loading: boolean
  status?: string
  warnings?: string[]
}>()

const stages = [
  { key: 'parse', label: 'URL 解析' },
  { key: 'fetch', label: 'PR 获取' },
  { key: 'context', label: '上下文收集' },
  { key: 'summary', label: '总结生成' },
  { key: 'risks', label: '风险识别' },
  { key: 'suggestions', label: '建议生成' },
  { key: 'guardrail', label: '质量检查' },
  { key: 'assemble', label: '报告组装' },
]

const currentStageIndex = computed(() => {
  if (!props.loading && props.status === 'succeeded') return stages.length
  if (props.status === 'failed') return -1
  if (props.loading) return 1 // 至少前两个阶段在跑
  return 0
})
</script>

<template>
  <div v-if="loading || status === 'succeeded' || status === 'failed'" class="progress-timeline">
    <h3>分析进度</h3>
    <div class="timeline">
      <div
        v-for="(stage, i) in stages"
        :key="stage.key"
        :class="[
          'stage',
          { done: i < currentStageIndex, current: i === currentStageIndex && loading, failed: status === 'failed' && i === currentStageIndex }
        ]"
      >
        <span class="dot"></span>
        <span class="label">{{ stage.label }}</span>
      </div>
    </div>
    <div v-if="warnings && warnings.length" class="warnings-box">
      <p v-for="(w, i) in warnings" :key="i" class="warning-item">{{ w }}</p>
    </div>
  </div>
</template>

<style scoped>
.progress-timeline {
  margin-bottom: 20px;
  padding: 16px 20px;
  background: #f9fafb;
  border-radius: 8px;
}
h3 {
  margin: 0 0 12px;
  font-size: 15px;
}
.timeline {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.stage {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #aaa;
}
.stage.done {
  color: #5cb85c;
}
.stage.current {
  color: #4a90d9;
  font-weight: 600;
}
.stage.failed {
  color: #d9534f;
}
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ddd;
}
.stage.done .dot { background: #5cb85c; }
.stage.current .dot { background: #4a90d9; animation: pulse 1s infinite; }
.stage.failed .dot { background: #d9534f; }
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
.warnings-box {
  margin-top: 10px;
  padding: 8px 12px;
  background: #fff8e1;
  border-radius: 6px;
  border: 1px solid #ffe082;
}
.warning-item {
  margin: 2px 0;
  font-size: 12px;
  color: #f0ad4e;
}
</style>
