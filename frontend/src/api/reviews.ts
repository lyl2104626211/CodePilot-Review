import type { CreateReviewCommentsResponse, CreateReviewTaskResponse, ReportQuality, ReviewMode, ReviewReport, ReviewTaskStatus, CreateSuggestedPatchesResponse } from '../types/review'

const DEFAULT_TIMEOUT_MS = 30_000
const REVIEW_TIMEOUT_MS = 120_000    // 完整 Review（含 GitHub API + LLM）
const PATCH_TIMEOUT_MS = 90_000      // Patch 生成（含 LLM）

async function fetchWithTimeout(url: string, options: RequestInit = {}, timeoutMs = DEFAULT_TIMEOUT_MS): Promise<Response> {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)
  try {
    const response = await fetch(url, { ...options, signal: controller.signal })
    return response
  } catch (e: unknown) {
    if (e instanceof DOMException && e.name === 'AbortError') {
      throw new Error('请求超时，请稍后重试')
    }
    throw e
  } finally {
    clearTimeout(timer)
  }
}

async function readError(response: Response): Promise<string> {
  try {
    const data = await response.json()
    return data.detail || `Request failed (${response.status})`
  } catch {
    return `Request failed (${response.status})`
  }
}

// 创建 Review 任务（可能涉及 GitHub API + LLM，超时 120s）
export async function createReviewTask(url: string, mode: ReviewMode = 'demo'): Promise<CreateReviewTaskResponse> {
  const response = await fetchWithTimeout('/api/reviews', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, mode }),
  }, REVIEW_TIMEOUT_MS)
  if (!response.ok) throw new Error(await readError(response))
  return response.json()
}

export async function getReviewReport(taskId: string): Promise<ReviewReport> {
  const response = await fetchWithTimeout(`/api/reviews/${taskId}`)
  if (!response.ok) throw new Error(await readError(response))
  return response.json()
}

export async function getReviewStatus(taskId: string): Promise<ReviewTaskStatus> {
  const response = await fetchWithTimeout(`/api/reviews/${taskId}/status`)
  if (!response.ok) throw new Error(await readError(response))
  return response.json()
}

export async function getReviewQuality(taskId: string): Promise<ReportQuality> {
  const response = await fetchWithTimeout(`/api/reviews/${taskId}/quality`)
  if (!response.ok) throw new Error(await readError(response))
  return response.json()
}

export async function createReviewComments(taskId: string, suggestionIds: string[]): Promise<CreateReviewCommentsResponse> {
  const response = await fetchWithTimeout(`/api/reviews/${taskId}/comments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ suggestion_ids: suggestionIds, include_summary: true, include_test_recommendations: true }),
  })
  if (!response.ok) throw new Error(await readError(response))
  return response.json()
}

export async function createSuggestedPatches(taskId: string, suggestionIds: string[]): Promise<CreateSuggestedPatchesResponse> {
  const response = await fetchWithTimeout(`/api/reviews/${taskId}/suggested-patches`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ suggestion_ids: suggestionIds }),
  }, PATCH_TIMEOUT_MS)
  if (!response.ok) throw new Error(await readError(response))
  return response.json()
}

export async function exportMarkdown(taskId: string): Promise<string> {
  const response = await fetchWithTimeout(`/api/reviews/${taskId}/export.md`)
  if (!response.ok) throw new Error(await readError(response))
  return response.text()
}
