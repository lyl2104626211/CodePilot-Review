<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import type { ReviewCommentDraft } from '../types/review'

const props = defineProps<{
  comments: ReviewCommentDraft[]
  markdown: string
}>()

const copied = ref(false)
const dlDone = ref(false)
let copyTimer: ReturnType<typeof setTimeout> | null = null
let dlTimer: ReturnType<typeof setTimeout> | null = null

onUnmounted(() => {
  if (copyTimer) clearTimeout(copyTimer)
  if (dlTimer) clearTimeout(dlTimer)
})

/** 安全渲染 Markdown 正文 */
function renderSafeBody(body: string): string {
  // 1. 保护代码块（``` 或 4空格缩进），用占位符替换
  const codeBlocks: string[] = []
  let safe = body
    // 先保护 ``` fences
    .replace(/```(\w*)\n([\s\S]*?)```/g, (_m, _lang, code) => {
      codeBlocks.push(`<pre class="cb">${esc(code.trim())}</pre>`)
      return `%%CODEBLOCK_${codeBlocks.length - 1}%%`
    })
    // 再保护 4 空格缩进代码块（连续行）
    .replace(/(?:^|\n)(    [^\n]+(?:\n    [^\n]+)*)/g, (_full, code) => {
      const unindented = code.replace(/^    /gm, '')
      codeBlocks.push(`<pre class="cb">${esc(unindented)}</pre>`)
      return `\n%%CODEBLOCK_${codeBlocks.length - 1}%%\n`
    })

  // 2. 转义 HTML
  safe = esc(safe)

  // 3. 应用 inline 格式
  safe = safe
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code class="ic">$1</code>')
    .replace(/^&gt; (.*)$/gm, '<em class="qt">$1</em>')

  // 4. 段落：双换行 → </p><p>，单换行 → <br>
  safe = safe
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
  safe = `<p>${safe}</p>`

  // 5. 还原代码块占位符
  safe = safe.replace(/%%CODEBLOCK_(\d+)%%/g, (_, i) => codeBlocks[parseInt(i)])

  return safe
}

function esc(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
}

async function copyAll() {
  try {
    await navigator.clipboard.writeText(props.markdown)
    copied.value = true
    copyTimer = setTimeout(() => copied.value = false, 2000)
  } catch {
    // fallback: no clipboard support
  }
}

function downloadMd() {
  const blob = new Blob([props.markdown], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url; a.download = 'codepilot-review.md'; a.click()
  URL.revokeObjectURL(url)
  dlDone.value = true
  dlTimer = setTimeout(() => dlDone.value = false, 2000)
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
        <!-- 使用 renderSafeBody 防 XSS -->
        <div class="cmt-body" v-html="renderSafeBody(c.body)"></div>
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
.cmt-body { font-size: 13px; line-height: 1.75; }
.cmt-body :deep(p) { margin: 0 0 8px; }
.cmt-body :deep(p:last-child) { margin-bottom: 0; }
.cmt-body :deep(.cb) {
  background: #0d1117; border: 1px solid #21262d; border-radius: 4px;
  padding: 12px 14px; margin: 10px 0; overflow-x: auto;
  font-family: var(--font-mono); font-size: 12px; line-height: 1.6;
  color: #c9d1d9; white-space: pre; tab-size: 4;
}
.cmt-body :deep(.ic) {
  background: #1c1f28; padding: 1px 5px; border-radius: 3px;
  font-family: var(--font-mono); font-size: 12px;
}
.cmt-body :deep(.qt) { color: #8b9099; }

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
