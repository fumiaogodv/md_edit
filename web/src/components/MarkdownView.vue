<template>
  <div class="markdown-view">
    <div v-if="!content" class="empty-tip">选择左侧文件查看内容</div>
    <div v-else ref="body" class="markdown-body" v-html="html"></div>
  </div>
</template>

<script>
import { defineComponent, ref, watch, nextTick } from 'vue'
import { renderMarkdown } from '../utils/markdown'

export default {
  name: 'MarkdownView',
  props: {
    content: { type: String, default: '' },
    highlightText: { type: String, default: '' },
  },
  emits: ['outline'],
  setup(props, { emit }) {
    const body = ref(null)
    const html = ref('')
    let highlightedEl = null

    watch(
      () => props.content,
      (val) => {
        html.value = renderMarkdown(val)
        nextTick(() => {
          extractOutline()
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

    // 暴露跳转方法给父组件
    function jumpTo(id) {
      const el = body.value?.querySelector(`[id="${CSS.escape(id)}"]`)
      el?.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }

    return { body, html, jumpTo }
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
</style>

<style>
/* 搜索命中高亮（非 scoped，作用于 v-html 内容） */
.markdown-body .search-hit {
  background: var(--warning-dim);
  border-radius: 4px;
  box-shadow: 0 0 0 3px var(--warning-dim);
}
</style>
