<script setup lang="ts">
import type { ReviewSummary } from '../types/review'

defineProps<{
  summary: ReviewSummary | null | undefined
}>()
</script>

<template>
  <div v-if="summary" class="review-summary">
    <h3>变更总结</h3>
    <p class="overview">{{ summary.overview }}</p>

    <div class="modules">
      <span class="section-label">变更模块：</span>
      <span v-for="m in summary.changed_modules" :key="m" class="tag">{{ m }}</span>
    </div>

    <div class="focus">
      <span class="section-label">评审重点：</span>
      <ul>
        <li v-for="(f, i) in summary.reviewer_focus" :key="i">{{ f }}</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.review-summary {
  margin-bottom: 20px;
}
h3 {
  margin: 0 0 8px;
  font-size: 16px;
}
.overview {
  margin: 0 0 12px;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
}
.modules, .focus {
  margin-bottom: 8px;
  font-size: 13px;
}
.section-label {
  color: #666;
}
.tag {
  display: inline-block;
  background: #e8f0fe;
  color: #4a90d9;
  padding: 2px 8px;
  border-radius: 4px;
  margin-right: 6px;
  font-size: 12px;
}
.focus ul {
  margin: 4px 0 0;
  padding-left: 20px;
}
.focus li {
  margin-bottom: 2px;
  color: #555;
}
</style>
