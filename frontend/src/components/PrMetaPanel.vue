<script setup lang="ts">
import type { PullRequestSnapshot } from '../types/review'

defineProps<{
  pr: PullRequestSnapshot | null | undefined
}>()
</script>

<template>
  <div v-if="pr" class="meta-panel">
    <div class="meta-grid">
      <div class="meta-field">
        <span class="meta-key">Title</span>
        <span class="meta-val">{{ pr.title }}</span>
      </div>
      <div class="meta-field">
        <span class="meta-key">Author</span>
        <span class="meta-val">{{ pr.author }}</span>
      </div>
      <div class="meta-field">
        <span class="meta-key">Branch</span>
        <span class="meta-val">{{ pr.head_branch }} &rarr; {{ pr.base_branch }}</span>
      </div>
      <div class="meta-field">
        <span class="meta-key">Files</span>
        <span class="meta-val num">{{ pr.changed_files }}</span>
      </div>
      <div class="meta-field">
        <span class="meta-key">Changes</span>
        <span class="meta-val">
          <span class="add">+{{ pr.additions }}</span>
          <span class="del">&minus;{{ pr.deletions }}</span>
        </span>
      </div>
      <div class="meta-field">
        <span class="meta-key">Commits</span>
        <span class="meta-val num">{{ pr.commit_count }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.meta-panel {
  margin-bottom: 24px;
  padding: 16px 20px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  border-left: 3px solid var(--accent);
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px 24px;
}

.meta-field {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.meta-key {
  font-size: 9px;
  font-weight: 600;
  letter-spacing: 1.5px;
  color: var(--text-muted);
  text-transform: uppercase;
}
.meta-val {
  font-size: 13px;
  color: var(--text-primary);
  font-family: var(--font-mono);
  word-break: break-all;
}
.meta-val.num {
  color: var(--accent);
  font-weight: 600;
}
.add { color: var(--success); }
.del { color: var(--danger); margin-left: 6px; }
</style>
