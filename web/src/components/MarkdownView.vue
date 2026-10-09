<template>
  <div class="markdown-view" ref="viewEl" @scroll.passive="onScroll">
    <div v-if="!content" class="empty-tip">选择左侧文件查看内容</div>
    <div v-else ref="body" class="markdown-body" v-html="html"></div>
  </div>
</template>

<script>
import { defineComponent, ref, watch, nextTick, onBeforeUnmount } from 'vue'
import { renderMarkdown } from '../utils/markdown'

export default {
  name: 'MarkdownView',
  props: {
    content: { type: String, default: '' },
    highlightText: { type: String, default: '' },
    baseDir: { type: String, default: '' },
    // 恢复用的进度：{ anchor: string } 或 { scroll: number }
    restore: { type: Object, default: null },
  },
  emits: ['outline', 'progress'],
  setup(props, { emit }) {
    const body = ref(null)
    const viewEl = ref(null)
    const html = ref('')
    let highlightedEl = null
    let scrollTimer = null
    let restored = false

    watch(
      () => props.content,
      (val) => {
        html.value = renderMarkdown(val, props.baseDir)
        restored = false
        nextTick(() => {
          extractOutline()
          restorePosition()
          scrollToHighlight()
        })
      }
    )

    // 提取 h1/h2 大纲
    function extractOutline() {
      if (!body.value) return
      const outline = []
      body.value.querySelectorAll('h1, h2').forEach((h) => {
        outline.push({
          level: h.tagName === 'H1' ? 1 : 2,
          text: h.textContent,
          id: h.id,
        })
      })
      emit('outline', outline)
    }

    // 恢复阅读位置：优先标题锚点，其次滚动比例
    function restorePosition() {
      if (!body.value || !props.restore || restored) return
      const r = props.restore
      if (r.anchor) {
        // 找标题锚点（匹配 id 或文本）
        let el = body.value.querySelector(`[id="${CSS.escape(r.anchor)}"]`)
        if (!el) {
          // 退而求其次按文本匹配标题
          const heads = body.value.querySelectorAll('h1, h2, h3, h4')
          for (const h of heads) {
            if (h.textContent.trim() === r.anchor.trim()) { el = h; break }
          }
        }
        if (el) {
          el.scrollIntoView({ block: 'start' })
          restored = true
          return
        }
      }
      if (typeof r.scroll === 'number' && r.scroll > 0) {
        viewEl.value.scrollTop = r.scroll * (viewEl.value.scrollHeight - viewEl.value.clientHeight)
        restored = true
      }
    }

    // 搜索定位：根据命中行文本精确匹配 DOM 元素，滚动 + 高亮
    function scrollToHighlight() {
      if (!props.highlightText || !body.value) return
      const text = props.highlightText.trim()
      if (!text) return

      // 清除上一次高亮
      clearHighlight()

      // 在块级元素中查找包含该文本的元素
      const blocks = body.value.querySelectorAll('p, li, h1, h2, h3, h4, h5, h6, blockquote, td, th')
      let target = null
      for (const el of blocks) {
        if (el.textContent.includes(text)) {
          target = el
          break
        }
      }

      if (!target) return

      // 高亮该元素
      highlightedEl = target
      target.classList.add('search-hit')
      target.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }

    function clearHighlight() {
      if (highlightedEl) {
        highlightedEl.classList.remove('search-hit')
        highlightedEl = null
      }
    }

    // 滚动时上报进度（防抖）
    function onScroll() {
      if (scrollTimer) clearTimeout(scrollTimer)
      scrollTimer = setTimeout(() => {
        reportProgress()
      }, 800)
    }

    // 计算当前进度：找当前视口顶部的最近标题作为锚点
    function reportProgress() {
      if (!body.value || !props.content) return
      const viewEl2 = viewEl.value
      const topLine = viewEl2.scrollTop
      // 找当前滚动位置之上最近的标题
      const heads = body.value.querySelectorAll('h1, h2, h3, h4')
      let anchor = ''
      for (const h of heads) {
        if (h.offsetTop <= topLine + 4) anchor = h.textContent.trim()
        else break
      }
      // 滚动比例（0~1）
      const scrollable = viewEl2.scrollHeight - viewEl2.clientHeight
      const scroll = scrollable > 0 ? viewEl2.scrollTop / scrollable : 0
      emit('progress', { type: 'md', anchor: anchor || null, scroll })
    }

    // 暴露跳转方法给父组件
    function jumpTo(id) {
      const el = body.value?.querySelector(`[id="${CSS.escape(id)}"]`)
      el?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }

    onBeforeUnmount(() => {
      if (scrollTimer) clearTimeout(scrollTimer)
    })

    return { body, viewEl, html, jumpTo }
  },
}
</script>

<style scoped>
.markdown-view {
  height: 100%;
  overflow-y: auto;
  padding: 24px 40px;
}
.empty-tip {
  color: var(--text-muted);
  text-align: center;
  margin-top: 40px;
  font-size: 15px;
}
@media (max-width: 768px) {
  .markdown-view {
    padding: 16px 16px 32px;
  }
}
</style>

<style>
/* 搜索命中高亮（非 scoped，作用于 v-html 内容） */
.markdown-body .search-hit {
  background: var(--warning-dim);
  border-radius: 4px;
  box-shadow: 0 0 0 3px var(--warning-dim);
}
</style>
