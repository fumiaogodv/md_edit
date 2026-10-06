import MarkdownIt from 'markdown-it'
import anchor from 'markdown-it-anchor'
import taskLists from 'markdown-it-task-lists'
import hljs from 'highlight.js'
import katex from 'katex'
import 'highlight.js/styles/github-dark.css'
import 'katex/dist/katex.min.css'

const md = new MarkdownIt({
  html: true,
  linkify: true,
  breaks: false,
  highlight(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value
      } catch (e) {
        /* ignore */
      }
    }
    try {
      return hljs.highlightAuto(code).value
    } catch (e) {
      return ''
    }
  },
})
  .use(anchor, {
    slugify: (s) => s,
    level: [1, 2, 3, 4, 5, 6],
    permalink: false,
  })
  .use(taskLists, { enabled: true })

// ===== KaTeX 公式渲染（自实现，使用新版 katex，支持 \text{中文}、\boxed 等） =====
const katexOptions = {
  throwOnError: false,
  strict: false,   // 忽略 strict 警告（允许中文、非标准宏）
  trust: true,     // 允许 \text 等命令渲染 Unicode 文本
}

function renderKatexInline(tex) {
  try {
    return katex.renderToString(tex, { ...katexOptions, displayMode: false })
  } catch (e) {
    return '<code class="katex-error">' + escapeHtml(tex) + '</code>'
  }
}

function renderKatexBlock(tex) {
  try {
    return katex.renderToString(tex, { ...katexOptions, displayMode: true })
  } catch (e) {
    return '<pre class="katex-error">' + escapeHtml(tex) + '</pre>'
  }
}

function escapeHtml(s) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}

// ---- 块级公式 $$...$$（跨行或单行） ----
function mathBlock(state, startLine, endLine, silent) {
  let pos = state.bMarks[startLine] + state.tShift[startLine]
  const max = state.eMarks[startLine]

  // 必须以 $$ 开头
  if (state.src.slice(pos, pos + 2) !== '$$') return false

  let next = startLine
  let content = state.src.slice(pos + 2, max)

  // 单行 $$...$$ 或跨行
  let endPos = -1

  if (content.trim().endsWith('$$')) {
    // 单行：$$ ... $$
    content = content.trim()
    content = content.slice(0, content.length - 2)
    endPos = state.eMarks[startLine]
    next = startLine + 1
  } else {
    // 跨行：$$\n...\n$$
    const lines = [content]
    let found = false
    for (let i = startLine + 1; i < endLine; i++) {
      const lineStart = state.bMarks[i] + state.tShift[i]
      const lineMax = state.eMarks[i]
      const line = state.src.slice(lineStart, lineMax)
      if (line.trim() === '$$') {
        next = i + 1
        found = true
        break
      }
      lines.push(line)
    }
    if (!found) return false
    content = lines.join('\n')
  }

  if (silent) return true

  const token = state.push('math_block', 'math', 0)
  token.block = true
  token.content = content.trim()
  token.map = [startLine, next]
  token.markup = '$$'

  state.line = next
  return true
}

// ---- 行内公式 $...$ ----
function mathInline(state, silent) {
  if (state.src[state.pos] !== '$') return false
  // 排除 $$ 块级（交给 block 规则处理）
  if (state.src[state.pos + 1] === '$') return false

  // 找闭合的 $
  let end = state.pos + 1
  while (end < state.posMax && state.src[end] !== '$') end++
  if (end >= state.posMax) return false

  // 空内容不处理
  if (end - state.pos === 1) return false

  const tex = state.src.slice(state.pos + 1, end)

  if (!silent) {
    const token = state.push('math_inline', 'math', 0)
    token.content = tex
    token.markup = '$'
  }
  state.pos = end + 1
  return true
}

// 注册规则
md.block.ruler.before('paragraph', 'math_block', mathBlock, {
  alt: ['paragraph', 'reference', 'blockquote', 'list'],
})
md.inline.ruler.after('escape', 'math_inline', mathInline)

// 注册渲染器
md.renderer.rules.math_block = (tokens, idx) =>
  renderKatexBlock(tokens[idx].content) + '\n'
md.renderer.rules.math_inline = (tokens, idx) =>
  renderKatexInline(tokens[idx].content)

export function renderMarkdown(content) {
  return md.render(content || '')
}

export { hljs }
