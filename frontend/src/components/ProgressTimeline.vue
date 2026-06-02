<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  loading: boolean
  status?: string
  warnings?: string[]
}>()

const stages = [
  { key: 'parse_pr_url', label: 'Parse URL' },
  { key: 'fetch_pr', label: 'Fetch PR' },
  { key: 'collect_context', label: 'Context' },
  { key: 'generate_summary', label: 'Summary' },
  { key: 'detect_risks', label: 'Risks' },
  { key: 'generate_suggestions', label: 'Suggestions' },
  { key: 'guardrail_check', label: 'Guardrail' },
  { key: 'assemble_report', label: 'Report' },
]

const activeIdx = computed(() => {
  if (!props.loading && props.status === 'succeeded') return stages.length
  if (props.loading) return 1
  return 0
})
</script>

<template>
  <div class="tl">
    <div class="tl-bar">
      <div class="tl-fill" :style="{ width: (activeIdx / stages.length) * 100 + '%' }"></div>
    </div>
    <div class="tl-labels">
      <div v-for="(s, i) in stages" :key="s.key" :class="['tl-stage', { done: i < activeIdx, active: i === activeIdx - 1 && loading }]">
        <span class="tl-dot"></span>
        <span class="tl-name">{{ s.label }}</span>
      </div>
    </div>
    <div v-if="warnings?.length" class="tl-warn">
      <span v-for="(w, i) in warnings" :key="i" class="wl">! {{ w }}</span>
    </div>
  </div>
</template>

<style scoped>
.tl { margin-bottom: 24px; padding: 12px 0; }
.tl-bar {
  height: 3px; background: var(--border); border-radius: 2px;
  margin-bottom: 10px; overflow: hidden;
}
.tl-fill {
  height: 100%; background: var(--teal);
  border-radius: 2px; transition: width 0.5s ease;
}
.tl-labels {
  display: flex; justify-content: space-between; gap: 4px;
}
.tl-stage {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  opacity: 0.35; transition: opacity 0.3s;
}
.tl-stage.done { opacity: 1; }
.tl-stage.active { opacity: 1; }
.tl-dot {
  width: 6px; height: 6px; border-radius: 50%; background: var(--text-muted);
}
.tl-stage.done .tl-dot { background: var(--teal); }
.tl-stage.active .tl-dot { background: var(--accent); box-shadow: 0 0 6px var(--accent); }
.tl-name {
  font-size: 10px; font-weight: 500; letter-spacing: 0.3px;
  color: var(--text-muted); white-space: nowrap;
}
.tl-stage.done .tl-name { color: var(--text-secondary); }
.tl-stage.active .tl-name { color: var(--accent); font-weight: 600; }

.tl-warn { margin-top: 10px; }
.wl { display: block; font-size: 11px; color: var(--warning); margin: 2px 0; }
</style>
