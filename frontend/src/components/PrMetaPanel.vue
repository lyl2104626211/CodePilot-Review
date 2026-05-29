<script setup lang="ts">
import type { PullRequestSnapshot } from '../types/review'

defineProps<{
  pr: PullRequestSnapshot | null | undefined
}>()
</script>

<template>
  <div v-if="pr" class="pr-meta-panel">
    <h3>PR 元数据</h3>
    <div class="meta-grid">
      <div class="meta-item">
        <span class="label">标题</span>
        <span class="value">{{ pr.title }}</span>
      </div>
      <div class="meta-item">
        <span class="label">作者</span>
        <span class="value">{{ pr.author }}</span>
      </div>
      <div class="meta-item">
        <span class="label">分支</span>
        <span class="value">{{ pr.head_branch }} → {{ pr.base_branch }}</span>
      </div>
      <div class="meta-item">
        <span class="label">变更文件</span>
        <span class="value">{{ pr.changed_files }} 个文件</span>
      </div>
      <div class="meta-item">
        <span class="label">代码变更</span>
        <span class="value">+{{ pr.additions }} −{{ pr.deletions }}</span>
      </div>
      <div class="meta-item">
        <span class="label">提交数</span>
        <span class="value">{{ pr.commit_count }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.pr-meta-panel {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 16px 20px;
  margin-bottom: 20px;
}
h3 {
  margin: 0 0 12px;
  font-size: 16px;
}
.meta-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}
.meta-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.label {
  font-size: 12px;
  color: #888;
}
.value {
  font-size: 14px;
}
</style>
