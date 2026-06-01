<script setup lang="ts">
import { ref } from 'vue'
import type { ReviewMode, ReviewReport, RiskFinding, ReviewCommentDraft, ReportQuality } from './types/review'
import { createReviewTask, getReviewReport, getReviewQuality, createReviewComments } from './api/reviews'
import PrInputPanel from './components/PrInputPanel.vue'
import PrMetaPanel from './components/PrMetaPanel.vue'
import ReviewSummary from './components/ReviewSummary.vue'
import RiskList from './components/RiskList.vue'
import SuggestionList from './components/SuggestionList.vue'
import ModeSelector from './components/ModeSelector.vue'
import ProgressTimeline from './components/ProgressTimeline.vue'
import FindingFilters from './components/FindingFilters.vue'
import ReviewCommentComposer from './components/ReviewCommentComposer.vue'
import ReviewCommentPreview from './components/ReviewCommentPreview.vue'
import ReportQualityPanel from './components/ReportQualityPanel.vue'
import EmptyState from './components/EmptyState.vue'
import ErrorState from './components/ErrorState.vue'
import SuggestedPatchPanel from './components/SuggestedPatchPanel.vue'

const mode = ref<ReviewMode>('demo')
const loading = ref(false)
const error = ref('')
const report = ref<ReviewReport | null>(null)
const filteredFindings = ref<RiskFinding[]>([])
const quality = ref<ReportQuality | null>(null)
const genLoading = ref(false)
const comments = ref<ReviewCommentDraft[]>([])
const markdown = ref('')

async function handleSubmit(url: string) {
  loading.value = true
  error.value = ''
  report.value = null
  filteredFindings.value = []
  quality.value = null
  comments.value = []
  markdown.value = ''
  try {
    const { task_id } = await createReviewTask(url, mode.value)
    const result = await getReviewReport(task_id)
    if (result.status === 'failed') {
      error.value = result.error_message || '分析失败，请重试'
    } else {
      report.value = result
      filteredFindings.value = result.findings ?? []
      try {
        quality.value = await getReviewQuality(task_id)
      } catch { /* quality is optional */ }
    }
  } catch (e: any) {
    error.value = e.message || '请求失败'
  } finally {
    loading.value = false
  }
}

async function handleGenerate(ids: string[]) {
  if (!report.value) return
  genLoading.value = true
  try {
    const resp = await createReviewComments(report.value.task_id, ids)
    comments.value = resp.comments
    markdown.value = resp.markdown
  } catch (e: any) {
    error.value = e.message || '评论生成失败'
  } finally {
    genLoading.value = false
  }
}
</script>

<template>
  <div class="app-shell">
    <aside class="sidebar">
      <div class="brand">
        <span class="brand-icon">&#9670;</span>
        <span class="brand-text">CodePilot</span>
        <span class="brand-version">v0.3</span>
      </div>
      <nav class="sidebar-nav">
        <span class="nav-label">REVIEW</span>
      </nav>
      <div class="sidebar-status">
        <span class="status-dot" :class="{ live: report }"></span>
        <span class="status-text">{{ report ? 'READY' : 'IDLE' }}</span>
      </div>
    </aside>

    <main class="main-content">
      <header class="topbar">
        <h1 class="page-title">PR Review</h1>
        <ModeSelector v-model:mode="mode" :loading="loading" />
      </header>

      <PrInputPanel :loading="loading" :error="error" :mode="mode" @submit="handleSubmit" />

      <ErrorState v-if="error" :message="error" :hint="error.includes('Token') || error.includes('权限') ? '请检查 .env 中的 GITHUB_TOKEN 配置' : undefined" @retry="() => error = ''" />

      <ProgressTimeline :loading="loading" :status="report?.status" :warnings="report?.warnings" />

      <EmptyState v-if="!loading && !error && !report" title="Enter a PR URL to start analysis" detail="Paste a GitHub pull request URL and click Run Review" />

      <PrMetaPanel :pr="report?.pr" />

      <ReviewSummary :summary="report?.summary" />

      <ReportQualityPanel v-if="quality" :quality="quality" :warnings="report?.warnings ?? []" />

      <FindingFilters
        v-if="report?.findings?.length"
        :findings="report.findings"
        @update:filtered="filteredFindings = $event"
      />

      <EmptyState v-if="report && !report.findings?.length" title="No risks detected" detail="The analysis did not find any significant risk patterns in this PR" />

      <RiskList :findings="filteredFindings" />

      <SuggestionList
        :suggestions="report?.suggestions ?? []"
        :test-recommendations="report?.test_recommendations ?? []"
      />

      <ReviewCommentComposer
        v-if="report?.suggestions?.length"
        :suggestions="report.suggestions"
        :loading="genLoading"
        @generate="handleGenerate"
      />

      <ReviewCommentPreview
        v-if="comments.length"
        :comments="comments"
        :markdown="markdown"
      />

      <SuggestedPatchPanel
        v-if="report?.task_id && report?.suggestions?.length"
        :task-id="report.task_id"
        :suggestions="report.suggestions"
      />
    </main>
  </div>
</template>

<style scoped>
.app-shell { display: flex; min-height: 100vh; }

.sidebar {
  width: 64px; min-height: 100vh;
  background: var(--bg-primary);
  border-right: 1px solid var(--border);
  display: flex; flex-direction: column; align-items: center;
  padding: 16px 0; gap: 24px; flex-shrink: 0;
}

.brand { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.brand-icon { font-size: 20px; color: var(--accent); }
.brand-text {
  font-family: var(--font-heading);
  font-size: 11px; font-weight: 700;
  letter-spacing: 0.5px; color: var(--text-primary);
}
.brand-version { font-size: 9px; color: var(--text-muted); letter-spacing: 1px; }

.sidebar-nav { flex: 1; display: flex; align-items: flex-start; }
.nav-label {
  font-size: 9px; letter-spacing: 2px; color: var(--text-muted);
  transform: rotate(-90deg); white-space: nowrap;
}

.sidebar-status { display: flex; flex-direction: column; align-items: center; gap: 4px; }
.status-dot {
  width: 6px; height: 6px; border-radius: 50%; background: var(--text-muted);
}
.status-dot.live { background: var(--success); box-shadow: 0 0 8px var(--success); }
.status-text { font-size: 8px; color: var(--text-muted); letter-spacing: 1px; }

.main-content {
  flex: 1; max-width: 960px; padding: 32px 40px 64px; overflow-y: auto;
}

.topbar {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 28px; padding-bottom: 20px;
  border-bottom: 1px solid var(--border);
}

.page-title {
  font-family: var(--font-heading);
  font-size: 22px; font-weight: 700; margin: 0;
  letter-spacing: -0.3px; color: var(--text-primary);
}
</style>
