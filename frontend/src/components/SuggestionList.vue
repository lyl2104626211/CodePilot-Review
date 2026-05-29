<script setup lang="ts">
import type { ReviewSuggestion } from '../types/review'

defineProps<{
  suggestions: ReviewSuggestion[]
  testRecommendations: string[]
}>()
</script>

<template>
  <div class="suggestion-area">
    <div v-if="suggestions.length" class="suggestion-list">
      <h3>Review 建议 ({{ suggestions.length }})</h3>
      <div v-for="s in suggestions" :key="s.id" class="suggestion-card">
        <div class="suggestion-header">
          <span v-if="s.blocking" class="blocking-badge">阻塞合并</span>
          <span v-else class="non-blocking-badge">建议修复</span>
          <span v-if="s.file_path" class="suggestion-file">{{ s.file_path }}</span>
        </div>
        <p class="suggestion-comment"><strong>评论：</strong>{{ s.comment }}</p>
        <p class="suggestion-rationale"><strong>原因：</strong>{{ s.rationale }}</p>
        <p class="suggestion-fix"><strong>修复建议：</strong>{{ s.suggested_fix }}</p>
      </div>
    </div>

    <div v-if="testRecommendations.length" class="test-section">
      <h3>测试建议</h3>
      <ul>
        <li v-for="(t, i) in testRecommendations" :key="i">{{ t }}</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
h3 {
  margin: 0 0 12px;
  font-size: 16px;
}
.suggestion-list {
  margin-bottom: 20px;
}
.suggestion-card {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  padding: 14px 16px;
  margin-bottom: 10px;
}
.suggestion-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}
.blocking-badge {
  background: #d9534f;
  color: #fff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}
.non-blocking-badge {
  background: #5cb85c;
  color: #fff;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}
.suggestion-file {
  font-size: 12px;
  color: #4a90d9;
  font-family: monospace;
}
.suggestion-comment, .suggestion-rationale, .suggestion-fix {
  font-size: 13px;
  color: #555;
  margin: 0 0 4px;
  line-height: 1.5;
}
.test-section ul {
  padding-left: 20px;
  margin: 4px 0 0;
}
.test-section li {
  margin-bottom: 4px;
  font-size: 13px;
  color: #555;
}
</style>
