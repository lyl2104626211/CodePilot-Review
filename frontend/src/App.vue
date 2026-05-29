<script setup lang="ts">
import { ref } from 'vue'
import type { ReviewMode, ReviewReport, RiskFinding } from './types/review'
import { createReviewTask, getReviewReport } from './api/reviews'
import PrInputPanel from './components/PrInputPanel.vue'
import PrMetaPanel from './components/PrMetaPanel.vue'
import ReviewSummary from './components/ReviewSummary.vue'
import RiskList from './components/RiskList.vue'
import SuggestionList from './components/SuggestionList.vue'
import ModeSelector from './components/ModeSelector.vue'
import ProgressTimeline from './components/ProgressTimeline.vue'
import FindingFilters from './components/FindingFilters.vue'

const mode = ref<ReviewMode>('demo')
const loading = ref(false)
const error = ref('')
const report = ref<ReviewReport | null>(null)
const filteredFindings = ref<RiskFinding[]>([])

async function handleSubmit(url: string) {
  loading.value = true
  error.value = ''
  report.value = null
  filteredFindings.value = []
  try {
    const { task_id } = await createReviewTask(url, mode.value)
    const result = await getReviewReport(task_id)
    if (result.status === 'failed') {
      error.value = result.error_message || '分析失败，请重试'
    } else {
      report.value = result
      filteredFindings.value = result.findings ?? []
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
    <PrInputPanel :loading="loading" :error="error" :mode="mode" @submit="handleSubmit" />

    <ModeSelector v-model:mode="mode" :loading="loading" />

    <ProgressTimeline
      :loading="loading"
      :status="report?.status"
      :warnings="report?.warnings"
    />

    <PrMetaPanel :pr="report?.pr" />

    <ReviewSummary :summary="report?.summary" />

    <FindingFilters
      v-if="report?.findings"
      :findings="report.findings"
      @update:filtered="filteredFindings = $event"
    />

    <RiskList :findings="filteredFindings" />

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
