<script setup lang="ts">
import type { ReviewSuggestion } from '../types/review'

defineProps<{
  suggestions: ReviewSuggestion[]
  testRecommendations: string[]
}>()
</script>

<template>
  <div class="sg-area">
    <div v-if="suggestions.length" class="sg-sec">
      <div class="sec-head">
        <span class="sec-icon">&#9998;</span>
        <span>SUGGESTIONS</span>
        <span class="sec-count">{{ suggestions.length }}</span>
      </div>
      <div v-for="s in suggestions" :key="s.id" class="sg-card">
        <div class="sg-top">
          <span :class="['blk-tag', s.blocking ? 'block' : 'allow']">
            {{ s.blocking ? 'BLOCK' : 'OK' }}
          </span>
          <span v-if="s.file_path" class="sg-file">{{ s.file_path }}</span>
        </div>
        <div class="sg-body">
          <p class="sg-line"><span class="sg-label">COMMENT</span>{{ s.comment }}</p>
          <p class="sg-line"><span class="sg-label">WHY</span>{{ s.rationale }}</p>
          <p class="sg-line"><span class="sg-label">FIX</span>{{ s.suggested_fix }}</p>
        </div>
      </div>
    </div>
    <div v-if="testRecommendations.length" class="test-sec">
      <div class="sec-head">
        <span class="sec-icon">&#9878;</span>
        <span>TESTS</span>
      </div>
      <ul class="test-list">
        <li v-for="(t, i) in testRecommendations" :key="i">{{ t }}</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.sg-sec, .test-sec { margin-bottom: 24px; }
.test-sec { padding-top: 20px; border-top: 1px solid var(--border); }

.sec-head {
  display: flex; align-items: center; gap: 8px;
  font-family: var(--font-heading); font-size: 15px;
  font-weight: 700; letter-spacing: 0.5px;
  color: var(--teal); margin-bottom: 14px;
}
.sec-icon { font-size: 15px; }
.sec-count { margin-left: auto; font-size: 12px; color: var(--text-muted); }

.sg-card {
  background: var(--bg-card); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: 14px 18px;
  margin-bottom: 8px; transition: border-color 0.15s;
}
.sg-card:hover { border-color: var(--border-hover); }
.sg-top { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; }
.blk-tag {
  font-size: 10px; font-weight: 700; letter-spacing: 1px;
  padding: 2px 8px; border-radius: 2px; font-family: var(--font-mono);
}
.blk-tag.block { color: var(--danger); border: 1px solid rgba(248, 113, 113, 0.4); }
.blk-tag.allow { color: var(--success); border: 1px solid rgba(74, 222, 128, 0.4); }
.sg-file { font-size: 12px; color: var(--teal); font-family: var(--font-mono); }
.sg-body { display: flex; flex-direction: column; gap: 5px; }
.sg-line { font-size: 12px; color: var(--text-secondary); line-height: 1.5; margin: 0; }
.sg-label {
  font-size: 10px; font-weight: 700; letter-spacing: 1.2px;
  color: var(--text-muted); margin-right: 8px;
}

.test-list { margin: 0; padding-left: 18px; list-style: square; }
.test-list li { margin-bottom: 4px; font-size: 13px; color: var(--text-secondary); line-height: 1.5; }
.test-list li::marker { color: var(--accent); }
</style>
