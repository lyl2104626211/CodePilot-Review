import type { CreateReviewCommentsResponse, CreateReviewTaskResponse, ReportQuality, ReviewMode, ReviewReport, ReviewTaskStatus, SuggestedPatch, CreateSuggestedPatchesResponse } from '../types/review'

async function readError(response: Response): Promise<string> {
  try {
    const data = await response.json()
    return data.detail || `Request failed (${response.status})`
  } catch {
    return `Request failed (${response.status})`
  }
}

export async function createReviewTask(url: string, mode: ReviewMode = 'demo'): Promise<CreateReviewTaskResponse> {
  const response = await fetch('/api/reviews', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, mode }),
  })
  if (!response.ok) throw new Error(await readError(response))
  return response.json()
}

export async function getReviewReport(taskId: string): Promise<ReviewReport> {
  const response = await fetch(`/api/reviews/${taskId}`)
  if (!response.ok) throw new Error(await readError(response))
  return response.json()
}

export async function getReviewStatus(taskId: string): Promise<ReviewTaskStatus> {
  const response = await fetch(`/api/reviews/${taskId}/status`)
  if (!response.ok) throw new Error(await readError(response))
  return response.json()
}

export async function getReviewQuality(taskId: string): Promise<ReportQuality> {
  const response = await fetch(`/api/reviews/${taskId}/quality`)
  if (!response.ok) throw new Error(await readError(response))
  return response.json()
}

export async function createReviewComments(taskId: string, suggestionIds: string[]): Promise<CreateReviewCommentsResponse> {
  const response = await fetch(`/api/reviews/${taskId}/comments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ suggestion_ids: suggestionIds, include_summary: true, include_test_recommendations: true }),
  })
  if (!response.ok) throw new Error(await readError(response))
  return response.json()
}

export async function createSuggestedPatches(taskId: string, suggestionIds: string[]): Promise<CreateSuggestedPatchesResponse> {
  const response = await fetch(`/api/reviews/${taskId}/suggested-patches`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ suggestion_ids: suggestionIds }),
  })
  if (!response.ok) throw new Error(await readError(response))
  return response.json()
}

export async function exportMarkdown(taskId: string): Promise<string> {
  const response = await fetch(`/api/reviews/${taskId}/export.md`)
  if (!response.ok) throw new Error(await readError(response))
  return response.text()
}
