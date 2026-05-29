<script setup lang="ts">
import type { ReviewMode } from '../types/review'

defineProps<{
  mode: ReviewMode
  loading: boolean
}>()

const emit = defineEmits<{
  'update:mode': [mode: ReviewMode]
}>()

function setMode(mode: ReviewMode) {
  emit('update:mode', mode)
}
</script>

<template>
  <div class="mode-selector">
    <button
      :class="['mode-btn', { active: mode === 'demo' }]"
      :disabled="loading"
      @click="setMode('demo')"
    >
      Demo 模式
    </button>
    <button
      :class="['mode-btn', { active: mode === 'github' }]"
      :disabled="loading"
      @click="setMode('github')"
    >
      GitHub 模式
    </button>
    <span class="mode-hint" v-if="mode === 'github'">
      公开仓库无需 Token，私有仓库需配置 GITHUB_TOKEN
    </span>
    <span class="mode-hint" v-else>
      使用 Mock 数据演示
    </span>
  </div>
</template>

<style scoped>
.mode-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}
.mode-btn {
  padding: 6px 16px;
  border: 1px solid #d0d0d0;
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}
.mode-btn.active {
  background: #4a90d9;
  color: #fff;
  border-color: #4a90d9;
}
.mode-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.mode-hint {
  font-size: 12px;
  color: #999;
  margin-left: 8px;
}
</style>
