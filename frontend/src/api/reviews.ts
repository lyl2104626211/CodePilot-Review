import type { CreateReviewTaskResponse, ReviewMode, ReviewReport } from '../types/review'

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
