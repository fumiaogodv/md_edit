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
    highlightLine: { type: Number, default: 0 },
  },
  emits: ['outline'],
  setup(props, { emit }) {
    const body = ref(null)
    const html = ref('')

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

    // 搜索定位：高亮命中行
    function scrollToHighlight() {
      if (!props.highlightLine || !body.value) return
      // 通过文本行号定位困难，这里简单滚动到顶部并提示
      // 实际定位：遍历段落，按换行数估算
      const target = body.value.querySelector('h1, h2, h3, p, li')
      if (target) target.scrollIntoView({ behavior: 'smooth' })
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
