<script setup lang="ts">
import type { ReviewSuggestion } from '../types/review'

defineProps<{
  suggestions: ReviewSuggestion[]
  testRecommendations: string[]
}>()
</script>

<template>
  <div class="suggestion-area">
    <div v-if="suggestions.length" class="suggestion-section">
      <div class="section-header">
        <span class="section-icon">&#9998;</span>
        <span>SUGGESTIONS</span>
        <span class="section-count">{{ suggestions.length }}</span>
      </div>

      <div v-for="s in suggestions" :key="s.id" class="sug-card">
        <div class="sug-top">
          <span :class="['block-tag', s.blocking ? 'block' : 'allow']">
            {{ s.blocking ? 'BLOCK' : 'OK' }}
          </span>
          <span v-if="s.file_path" class="sug-file">{{ s.file_path }}</span>
        </div>

        <div class="sug-body">
          <p class="sug-line"><span class="sug-label">COMMENT</span>{{ s.comment }}</p>
          <p class="sug-line"><span class="sug-label">WHY</span>{{ s.rationale }}</p>
          <p class="sug-line"><span class="sug-label">FIX</span>{{ s.suggested_fix }}</p>
        </div>
      </div>
    </div>

    <div v-if="testRecommendations.length" class="test-section">
      <div class="section-header">
        <span class="section-icon">&#9878;</span>
        <span>TESTS</span>
      </div>
      <ul class="test-list">
        <li v-for="(t, i) in testRecommendations" :key="i">{{ t }}</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.suggestion-section, .test-section {
  margin-bottom: 24px;
}
.test-section {
  padding-top: 20px;
  border-top: 1px solid var(--border);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 2px;
  color: var(--teal);
  margin-bottom: 12px;
}
.section-icon { font-size: 13px; }
.section-count {
  margin-left: auto;
  font-size: 11px;
  color: var(--text-muted);
}

.sug-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 14px 18px;
  margin-bottom: 8px;
  transition: border-color 0.15s;
}
.sug-card:hover { border-color: var(--border-hover); }

.sug-top {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.block-tag {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 1px;
  padding: 2px 6px;
  border-radius: 2px;
  font-family: var(--font-mono);
}
.block-tag.block {
  color: var(--danger);
  border: 1px solid rgba(248, 113, 113, 0.4);
}
.block-tag.allow {
  color: var(--success);
  border: 1px solid rgba(74, 222, 128, 0.4);
}

.sug-file {
  font-size: 11px;
  color: var(--teal);
  font-family: var(--font-mono);
}

.sug-body {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.sug-line {
  font-size: 11px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0;
}
.sug-label {
  font-size: 8px;
  font-weight: 700;
  letter-spacing: 1.2px;
  color: var(--text-muted);
  margin-right: 8px;
}

.test-list {
  margin: 0;
  padding-left: 18px;
  list-style: square;
}
.test-list li {
  margin-bottom: 4px;
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.5;
}
.test-list li::marker { color: var(--accent); }
</style>
