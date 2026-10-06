import MarkdownIt from 'markdown-it'
import anchor from 'markdown-it-anchor'
import katex from 'markdown-it-katex'
import taskLists from 'markdown-it-task-lists'
import hljs from 'highlight.js'
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
  .use(katex, {
    // 允许 \text{中文} 等非 ASCII 内容，忽略 strict 警告
    throwOnError: false,
    strict: false,
    trust: true,
    // 处理 \boxed、\xrightarrow 等，需要更宽的宏支持
    errorColor: '#f06a6a',
  })
  .use(taskLists, { enabled: true })

export function renderMarkdown(content) {
  return md.render(content || '')
}

export { hljs }
