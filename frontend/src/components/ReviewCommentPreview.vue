<script setup lang="ts">
import { ref } from 'vue'
import type { ReviewCommentDraft } from '../types/review'

defineProps<{
  comments: ReviewCommentDraft[]
  markdown: string
}>()

const copied = ref(false)
const dlDone = ref(false)

async function copyAll() {
  try {
    await navigator.clipboard.writeText(markdown.value)
    copied.value = true
    setTimeout(() => copied.value = false, 2000)
  } catch {
    // fallback: no clipboard support
  }
}

function downloadMd() {
  const blob = new Blob([markdown.value], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = 'codepilot-review.md'; a.click()
  URL.revokeObjectURL(url)
  dlDone.value = true
  setTimeout(() => dlDone.value = false, 2000)
}
</script>

<template>
  <div v-if="comments.length" class="preview">
    <div class="prev-head">
      <span class="prev-title">REVIEW COMMENTS</span>
      <div class="prev-actions">
        <button class="act-btn" @click="copyAll">{{ copied ? 'COPIED' : 'COPY MD' }}</button>
        <button class="act-btn" @click="downloadMd">{{ dlDone ? 'DONE' : 'DOWNLOAD' }}</button>
      </div>
    </div>

    <div class="prev-card">
      <div class="gh-header">
        <span class="gh-icon">&#9670;</span>
        <span>CodePilot Review — Simulated</span>
      </div>

      <div v-for="c in comments" :key="c.id" class="comment-block">
        <div class="cmt-top">
          <span :class="['cmt-tag', c.blocking ? 'blk' : 'ok']">
            {{ c.blocking ? 'BLOCK' : 'SUGGEST' }}
          </span>
          <span v-if="c.file_path" class="cmt-file">{{ c.file_path }}</span>
          <span v-if="c.severity" class="cmt-sev">{{ c.severity }}</span>
        </div>
        <div class="cmt-body" v-html="c.body.replace(/\n/g, '<br>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/`(.*?)`/g, '<code style=\'background:#1c1f28;padding:1px 4px;border-radius:2px;font-family:monospace\'>$1</code>').replace(/^> (.*)$/gm, '<em style=\'color:#8b9099\'>$1</em>')"></div>
      </div>

      <div v-if="markdown" class="md-full">
        <div class="md-label">FULL MARKDOWN</div>
        <pre class="md-code">{{ markdown.slice(0, 2000) }}{{ markdown.length > 2000 ? '...' : '' }}</pre>
      </div>
    </div>
  </div>
</template>

<style scoped>
.preview { margin-bottom: 24px; }
.prev-head {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 10px;
}
.prev-title {
  font-family: var(--font-heading);
  font-size: 13px; font-weight: 700; letter-spacing: 0.5px; color: var(--teal);
}
.prev-actions { display: flex; gap: 6px; }
.act-btn {
  font-size: 9px; font-weight: 600; letter-spacing: 1px;
  background: var(--bg-elevated); border: 1px solid var(--border);
  border-radius: 2px; color: var(--text-secondary); cursor: pointer;
  padding: 4px 10px; font-family: var(--font-mono);
}
.act-btn:hover { border-color: var(--border-hover); color: var(--accent); }

.prev-card {
  background: #0d1117; border: 1px solid #30363d; border-radius: 6px;
  padding: 16px 18px; font-family: -apple-system, BlinkMacSystemFont, sans-serif;
  font-size: 13px; color: #c9d1d9; line-height: 1.6;
}
.gh-header {
  display: flex; align-items: center; gap: 8px;
  padding-bottom: 12px; margin-bottom: 12px;
  border-bottom: 1px solid #21262d; font-weight: 600;
}
.gh-icon { color: var(--accent); font-size: 16px; }

.comment-block {
  background: #161b22; border: 1px solid #21262d; border-radius: 6px;
  padding: 12px 14px; margin-bottom: 10px;
}
.cmt-top { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; }
.cmt-tag {
  font-size: 9px; font-weight: 700; letter-spacing: 0.8px;
  padding: 1px 6px; border-radius: 3px; font-family: var(--font-mono);
}
.cmt-tag.blk { color: #f87171; border: 1px solid rgba(248, 113, 113, 0.4); }
.cmt-tag.ok { color: #4ade80; border: 1px solid rgba(74, 222, 128, 0.4); }
.cmt-file { font-size: 11px; color: var(--teal); font-family: var(--font-mono); }
.cmt-sev { font-size: 9px; color: var(--text-muted); letter-spacing: 1px; font-family: var(--font-mono); }
.cmt-body { font-size: 12px; line-height: 1.7; }

.md-full { margin-top: 14px; padding-top: 12px; border-top: 1px solid #21262d; }
.md-label {
  font-size: 9px; font-weight: 600; letter-spacing: 1.5px;
  color: var(--text-muted); margin-bottom: 6px;
}
.md-code {
  background: #0d1117; padding: 12px; border-radius: 4px;
  font-size: 11px; font-family: var(--font-mono); line-height: 1.5;
  color: var(--text-secondary); overflow-x: auto; white-space: pre-wrap;
  max-height: 400px; overflow-y: auto; margin: 0;
}
</style>
