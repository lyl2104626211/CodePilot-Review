<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { RiskFinding } from '../types/review'

const props = defineProps<{ findings: RiskFinding[] }>()

const emit = defineEmits<{ 'update:filtered': [findings: RiskFinding[]] }>()

const sev = ref<string>('all')
const lowConf = ref(true)

const filtered = computed(() => {
  let r = props.findings
  if (sev.value !== 'all') r = r.filter(f => f.severity === sev.value)
  if (!lowConf.value) r = r.filter(f => f.confidence >= 0.5)
  return r
})

watch(filtered, (v) => emit('update:filtered', v), { immediate: true })

const filters = ['all', 'critical', 'high', 'medium', 'low']
</script>

<template>
  <div class="fbar">
    <div class="fg">
      <span class="fl">SEV</span>
      <button
        v-for="f in filters" :key="f"
        :class="['ch', { on: sev === f }]"
        @click="sev = f"
      >{{ f === 'all' ? 'ALL' : f.toUpperCase() }}</button>
    </div>
    <label class="tog">
      <input type="checkbox" v-model="lowConf" />
      <span class="tt">LOW CONF</span>
    </label>
    <span class="cnt">{{ filtered.length }} / {{ findings.length }}</span>
  </div>
</template>

<style scoped>
.fbar {
  display: flex; align-items: center; gap: 12px;
  margin-bottom: 8px; padding: 8px 0; flex-wrap: wrap;
}
.fg { display: flex; align-items: center; gap: 4px; }
.fl {
  font-size: 8px; font-weight: 700; letter-spacing: 1.5px;
  color: var(--text-muted); margin-right: 6px;
}
.ch {
  padding: 3px 10px; border: 1px solid var(--border);
  border-radius: 2px; background: transparent; color: var(--text-muted);
  cursor: pointer; font-family: var(--font-mono); font-size: 9px;
  font-weight: 600; letter-spacing: 0.5px; transition: all 0.15s;
}
.ch.on {
  background: var(--bg-elevated); border-color: var(--border-hover);
  color: var(--text-primary);
}
.ch:hover:not(.on) { border-color: var(--border-hover); }
.tog { display: flex; align-items: center; gap: 4px; cursor: pointer; user-select: none; }
.tog input { accent-color: var(--accent); }
.tt { font-size: 9px; font-weight: 600; letter-spacing: 0.5px; color: var(--text-muted); }
.cnt { margin-left: auto; font-size: 10px; color: var(--text-muted); font-family: var(--font-mono); }
</style>
