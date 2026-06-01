export type ReviewMode = 'demo' | 'github'

export interface ParsedPullRequest {
  owner: string
  repo: string
  number: number
  url: string
}

export interface PullRequestFile {
  path: string
  status: string
  additions: number
  deletions: number
  patch?: string
}

export interface PullRequestSnapshot {
  owner: string
  repo: string
  number: number
  title: string
  author: string
  base_branch: string
  head_branch: string
  changed_files: number
  additions: number
  deletions: number
  commit_count: number
  files: PullRequestFile[]
}

export interface ReviewSummary {
  overview: string
  changed_modules: string[]
  reviewer_focus: string[]
}

export interface RiskFinding {
  id: string
  severity: 'critical' | 'high' | 'medium' | 'low'
  category: string
  file_path: string
  line?: number
  title: string
  evidence: string
  reasoning: string
  confidence: number
}

export interface ReviewSuggestion {
  id: string
  finding_id?: string
  file_path?: string
  comment: string
  rationale: string
  suggested_fix: string
  blocking: boolean
}

export interface ReviewReport {
  task_id: string
  status: 'queued' | 'running' | 'succeeded' | 'failed'
  pr?: PullRequestSnapshot
  summary?: ReviewSummary
  findings: RiskFinding[]
  suggestions: ReviewSuggestion[]
  test_recommendations: string[]
  warnings: string[]
  error_message?: string
}

export interface CreateReviewTaskResponse {
  task_id: string
  status: string
}

// ===== Day 3: 模拟评论与质量类型 =====

export interface ReviewCommentDraft {
  id: string
  suggestion_id: string
  finding_id?: string
  file_path?: string
  line?: number
  body: string
  severity?: string
  blocking: boolean
}

export interface CreateReviewCommentsResponse {
  task_id: string
  comments: ReviewCommentDraft[]
  markdown: string
}

export interface ReviewTaskStatus {
  task_id: string
  status: string
  progress_events: { node: string; status: string; message: string }[]
  warnings: string[]
}

export interface ReportQuality {
  total_findings: number
  high_confidence_findings: number
  low_confidence_findings: number
  blocking_suggestions: number
  warning_count: number
  fallback_used: boolean
  notes: string[]
}
