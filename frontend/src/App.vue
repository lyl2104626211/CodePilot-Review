<script setup lang="ts">
import { ref } from 'vue'
import type { ReviewReport } from './types/review'
import { createReviewTask, getReviewReport } from './api/reviews'
import PrInputPanel from './components/PrInputPanel.vue'
import PrMetaPanel from './components/PrMetaPanel.vue'
import ReviewSummary from './components/ReviewSummary.vue'
import RiskList from './components/RiskList.vue'
import SuggestionList from './components/SuggestionList.vue'

const loading = ref(false)
const error = ref('')
const report = ref<ReviewReport | null>(null)

async function handleSubmit(url: string) {
  loading.value = true
  error.value = ''
  report.value = null
  try {
    const { task_id } = await createReviewTask(url)
    const result = await getReviewReport(task_id)
    if (result.status === 'failed') {
      error.value = result.error_message || '分析失败，请重试'
    } else {
      report.value = result
    }
  } catch (e: any) {
    error.value = e.message || '请求失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="app-container">
    <PrInputPanel :loading="loading" :error="error" @submit="handleSubmit" />

    <PrMetaPanel :pr="report?.pr" />

    <ReviewSummary :summary="report?.summary" />

    <RiskList :findings="report?.findings ?? []" />

    <SuggestionList
      :suggestions="report?.suggestions ?? []"
      :test-recommendations="report?.test_recommendations ?? []"
    />
  </div>
</template>

<style scoped>
.app-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 32px 24px;
}
</style>
