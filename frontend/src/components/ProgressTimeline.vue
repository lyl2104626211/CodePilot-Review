<script setup lang="ts">
const props = defineProps<{
  loading: boolean
  status?: string
  warnings?: string[]
}>()

const stages = ['PARSE', 'FETCH', 'CONTEXT', 'SUMMARY', 'RISKS', 'SUGGEST', 'GUARD', 'REPORT']

function ss(i: number): 'done' | 'active' | 'pending' | 'fail' {
  if (props.status === 'failed' && !props.loading) return 'fail'
  if (!props.loading && props.status === 'succeeded') return 'done'
  if (props.loading && i === 0) return 'active'
  return 'pending'
}
</script>

<template>
  <div v-if="loading || status === 'succeeded' || status === 'failed'" class="pbar">
    <div class="stages">
      <div v-for="(label, i) in stages" :key="label" :class="['st', ss(i)]">
        <span class="dot"></span>
        <span class="lbl">{{ label }}</span>
      </div>
    </div>
    <div v-if="warnings?.length" class="warn-list">
      <p v-for="(w, i) in warnings" :key="i" class="wi">{{ w }}</p>
    </div>
  </div>
</template>

<style scoped>
.pbar {
  margin-bottom: 24px; padding: 14px 18px;
  background: var(--bg-secondary); border: 1px solid var(--border);
  border-radius: var(--radius-lg);
}
.stages { display: flex; gap: 0; overflow-x: auto; }
.st {
  display: flex; align-items: center; gap: 5px;
  font-size: 9px; font-weight: 600; letter-spacing: 1px;
  color: var(--text-muted); padding: 0 8px;
}
.st:first-child { padding-left: 0; }
.st::after { content: '\2192'; margin-left: 8px; color: var(--border); font-size: 10px; }
.st:last-child::after { display: none; }
.st.done { color: var(--success); }
.st.done .dot { background: var(--success); }
.st.active { color: var(--accent); }
.st.active .dot { background: var(--accent); animation: pdot 1s infinite; }
.st.fail { color: var(--danger); }
.st.fail .dot { background: var(--danger); }
.dot { width: 6px; height: 6px; border-radius: 50%; background: var(--border-hover); flex-shrink: 0; }
@keyframes pdot {
  0%, 100% { box-shadow: 0 0 0 0 var(--accent-glow); }
  50% { box-shadow: 0 0 0 4px transparent; }
}
.warn-list { margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border); }
.wi { margin: 2px 0; font-size: 11px; color: var(--warning); font-family: var(--font-mono); }
</style>
