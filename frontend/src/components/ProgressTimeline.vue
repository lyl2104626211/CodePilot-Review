<script setup lang="ts">
const props = defineProps<{
  loading: boolean
  status?: string
  warnings?: string[]
}>()

const stages = [
  'PARSE', 'FETCH', 'CONTEXT', 'SUMMARY',
  'RISKS', 'SUGGEST', 'GUARD', 'REPORT',
]

function stageState(i: number): 'done' | 'active' | 'pending' | 'fail' {
  if (props.status === 'failed' && !props.loading) return 'fail'
  if (i === 0 && props.loading) return 'active'
  if (!props.loading && props.status === 'succeeded') return 'done'
  if (props.loading && i === 0) return 'done'
  return 'pending'
}
</script>

<template>
  <div v-if="loading || status === 'succeeded' || status === 'failed'" class="progress-bar">
    <div class="stages">
      <div
        v-for="(label, i) in stages"
        :key="label"
        :class="['stage', stageState(i)]"
      >
        <span class="stage-dot"></span>
        <span class="stage-label">{{ label }}</span>
      </div>
    </div>
    <div v-if="warnings?.length" class="warn-list">
      <p v-for="(w, i) in warnings" :key="i" class="warn-item">{{ w }}</p>
    </div>
  </div>
</template>

<style scoped>
.progress-bar {
  margin-bottom: 24px;
  padding: 14px 18px;
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}

.stages {
  display: flex;
  gap: 0;
  overflow-x: auto;
}

.stage {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 1px;
  color: var(--text-muted);
  padding: 0 8px;
}
.stage:first-child { padding-left: 0; }
.stage::after {
  content: '\2192';
  margin-left: 8px;
  color: var(--border);
  font-size: 10px;
}
.stage:last-child::after { display: none; }

.stage.done { color: var(--success); }
.stage.done .stage-dot { background: var(--success); }

.stage.active { color: var(--accent); }
.stage.active .stage-dot {
  background: var(--accent);
  animation: pulse-dot 1s infinite;
}

.stage.fail { color: var(--danger); }
.stage.fail .stage-dot { background: var(--danger); }

.stage-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--border-hover);
  flex-shrink: 0;
}

@keyframes pulse-dot {
  0%, 100% { box-shadow: 0 0 0 0 var(--accent-glow); }
  50% { box-shadow: 0 0 0 4px transparent; }
}

.warn-list {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--border);
}
.warn-item {
  margin: 2px 0;
  font-size: 11px;
  color: var(--warning);
  font-family: var(--font-mono);
}
</style>
