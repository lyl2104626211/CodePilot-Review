<script setup lang="ts">
import { ref } from 'vue'

import type { ReviewMode } from '../types/review'

defineProps<{
  loading: boolean
  error?: string
  mode?: ReviewMode
}>()

const emit = defineEmits<{
  submit: [url: string]
}>()

const url = ref('')
const localError = ref('')

function handleSubmit() {
  localError.value = ''
  const trimmed = url.value.trim()
  if (!trimmed) {
    localError.value = '请输入 GitHub PR URL'
    return
  }
  emit('submit', trimmed)
}
</script>

<template>
  <div class="pr-input-panel">
    <h2>CodePilot Review</h2>
    <p class="subtitle">AI 辅助 PR 评审助手 — 快速获取变更总结、风险识别与 Review 建议</p>

    <div class="input-row">
      <input
        v-model="url"
        type="text"
        placeholder="https://github.com/{owner}/{repo}/pull/{number}"
        :disabled="loading"
        @keyup.enter="handleSubmit"
      />
      <button :disabled="loading || !url.trim()" @click="handleSubmit">
        {{ loading ? '分析中...' : '开始分析' }}
      </button>
    </div>

    <div class="demo-hint" v-if="mode === 'demo'">Demo 模式 — 使用 Mock 数据演示</div>
    <div class="demo-hint" v-else-if="mode === 'github'">GitHub 模式 — 真实 PR 数据 + AI 分析</div>

    <p v-if="localError || error" class="error-msg">{{ localError || error }}</p>
  </div>
</template>

<style scoped>
.pr-input-panel {
  margin-bottom: 24px;
}
h2 {
  margin: 0 0 4px;
  font-size: 22px;
}
.subtitle {
  color: #666;
  margin: 0 0 16px;
  font-size: 14px;
}
.input-row {
  display: flex;
  gap: 8px;
}
.input-row input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #d0d0d0;
  border-radius: 6px;
  font-size: 14px;
}
.input-row input:focus {
  outline: none;
  border-color: #4a90d9;
}
.input-row button {
  padding: 8px 20px;
  background: #4a90d9;
  color: #fff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  white-space: nowrap;
}
.input-row button:disabled {
  background: #a0c4e8;
  cursor: not-allowed;
}
.demo-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #999;
}
.error-msg {
  color: #d9534f;
  margin-top: 8px;
  font-size: 13px;
}
</style>
