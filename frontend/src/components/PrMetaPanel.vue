<script setup lang="ts">
import type { PullRequestSnapshot } from '../types/review'

defineProps<{
  pr: PullRequestSnapshot | null | undefined
}>()
</script>

<template>
  <div v-if="pr" class="meta-panel">
    <div class="section-head">PR DETAILS</div>
    <div class="meta-grid">
      <div class="field">
        <span class="key">Title</span>
        <span class="val">{{ pr.title }}</span>
      </div>
      <div class="field">
        <span class="key">Author</span>
        <span class="val">{{ pr.author }}</span>
      </div>
      <div class="field">
        <span class="key">Branch</span>
        <span class="val">{{ pr.head_branch }} &rarr; {{ pr.base_branch }}</span>
      </div>
      <div class="field">
        <span class="key">Files</span>
        <span class="val">{{ pr.changed_files }}</span>
      </div>
      <div class="field">
        <span class="key">Changes</span>
        <span class="val">+{{ pr.additions }} &minus;{{ pr.deletions }}</span>
      </div>
      <div class="field">
        <span class="key">Commits</span>
        <span class="val">{{ pr.commit_count }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.meta-panel {
  margin-bottom: 24px; padding: 16px 22px;
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius-lg); border-left: 3px solid var(--accent);
}
.section-head {
  font-family: var(--font-heading); font-size: 15px; font-weight: 700;
  letter-spacing: 0.5px; color: var(--accent); margin-bottom: 14px;
}
.meta-grid {
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 16px 28px;
}
.field { display: flex; flex-direction: column; gap: 3px; }
.key { font-size: 11px; font-weight: 600; letter-spacing: 1px; color: var(--text-muted); }
.val { font-size: 14px; color: var(--text-primary); font-weight: 500; }
</style>
