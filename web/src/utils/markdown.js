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
  .use(katex)
  .use(taskLists, { enabled: true })

export function renderMarkdown(content) {
  return md.render(content || '')
}

export { hljs }
