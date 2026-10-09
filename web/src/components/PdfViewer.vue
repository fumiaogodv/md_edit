<template>
  <div class="pdf-viewer">
    <!-- 工具栏 -->
    <div class="pdf-toolbar">
      <button class="pdf-btn" @click="prevPage" :disabled="page <= 1" title="上一页">
        <svg viewBox="0 0 16 16" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.6"><polyline points="10 3 5 8 10 13"/></svg>
      </button>
      <span class="pdf-page-info">
        <input
          class="pdf-page-input"
          type="number"
          min="1"
          :max="numPages"
          :value="pageInput"
          @change="onPageInput"
        />
        / {{ numPages || '…' }}
      </span>
      <button class="pdf-btn" @click="nextPage" :disabled="page >= numPages" title="下一页">
        <svg viewBox="0 0 16 16" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.6"><polyline points="6 3 11 8 6 13"/></svg>
      </button>
      <span class="pdf-sep"></span>
      <button class="pdf-btn" @click="zoomOut" title="缩小">
        <svg viewBox="0 0 16 16" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.6"><line x1="3" y1="8" x2="13" y2="8"/></svg>
      </button>
      <span class="pdf-zoom-info">{{ Math.round(scale * 100) }}%</span>
      <button class="pdf-btn" @click="zoomIn" title="放大">
        <svg viewBox="0 0 16 16" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.6"><line x1="3" y1="8" x2="13" y2="8"/><line x1="8" y1="3" x2="8" y2="13"/></svg>
      </button>
      <button class="pdf-btn" @click="fitWidth" title="适应宽度">
        <svg viewBox="0 0 16 16" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.6"><path d="M1 4V1.5h2.5M15 4V1.5h-2.5M1 12v2.5h2.5M15 12v2.5h-2.5"/></svg>
      </button>
    </div>

    <!-- 渲染区 -->
    <div class="pdf-scroll" ref="scrollEl" @scroll.passive="onScroll">
      <div v-if="loading" class="pdf-loading">加载 PDF 中…</div>
      <div v-else-if="error" class="pdf-error">{{ error }}</div>
      <div v-else class="pdf-pages">
        <div
          v-for="p in renderedPages"
          :key="p"
          class="pdf-page"
          :data-page="p"
        >
          <canvas :ref="(el) => setCanvasRef(p, el)"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, nextTick, onMounted, onBeforeUnmount } from 'vue'
import { api } from '../api'
import * as pdfjsLib from 'pdfjs-dist'
import workerUrl from 'pdfjs-dist/build/pdf.worker.min.mjs?url'

// 配置 pdf.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = workerUrl

export default {
  name: 'PdfViewer',
  props: {
    path: { type: String, required: true },
    initialPage: { type: Number, default: 1 },
  },
  emits: ['progress'],
  setup(props, { emit }) {
    const scrollEl = ref(null)
    const loading = ref(true)
    const error = ref('')
    const numPages = ref(0)
    const page = ref(1)
    const pageInput = ref(1)
    const scale = ref(1.2)

    let pdfDoc = null
    const canvasRefs = new Map()
    // 已渲染的页码（用于懒加载时展示）
    const renderedPages = ref([])
    // 已渲染完成的页码集合（去重）
    const renderedSet = new Set()
    // 渲染任务队列，避免重复渲染
    const renderingQueue = new Set()

    // 记录进度（防抖）
    let reportTimer = null
    function reportProgress() {
      if (reportTimer) clearTimeout(reportTimer)
      reportTimer = setTimeout(() => {
        emit('progress', { type: 'pdf', page: page.value })
      }, 500)
    }

    // 计算合适的初始缩放（适应容器宽度）
    function calcFitScale() {
      const container = scrollEl.value
      if (!container || !pdfDoc) return 1.0
      const width = container.clientWidth - 32
      if (width <= 0) return 1.0
      // 用第一页的原始宽度估算
      return pdfDoc.getPage(1).then((p) => {
        const vp = p.getViewport({ scale: 1 })
        return Math.min(1.6, width / vp.width)
      })
    }

    function setCanvasRef(p, el) {
      if (el) canvasRefs.set(p, el)
      else canvasRefs.delete(p)
    }

    async function renderPage(p) {
      if (!pdfDoc || renderedSet.has(p) || renderingQueue.has(p)) return
      renderingQueue.add(p)
      try {
        const pdfPage = await pdfDoc.getPage(p)
        const viewport = pdfPage.getViewport({ scale: scale.value })
        const canvas = canvasRefs.get(p)
        if (!canvas) return
        const dpr = window.devicePixelRatio || 1
        canvas.width = Math.floor(viewport.width * dpr)
        canvas.height = Math.floor(viewport.height * dpr)
        canvas.style.width = viewport.width + 'px'
        canvas.style.height = viewport.height + 'px'
        const ctx = canvas.getContext('2d')
        await pdfPage.render({
          canvasContext: ctx,
          viewport,
          transform: dpr !== 1 ? [dpr, 0, 0, dpr, 0, 0] : null,
        }).promise
        renderedSet.add(p)
      } catch (e) {
        console.error('渲染第', p, '页失败:', e)
      } finally {
        renderingQueue.delete(p)
      }
    }

    // 渲染可见区域附近的页（懒加载）
    async function renderVisible() {
      if (!pdfDoc || !scrollEl.value) return
      const container = scrollEl.value
      const pageEls = container.querySelectorAll('.pdf-page')
      const buffer = 2 // 前后各多渲染几页
      const viewTop = container.scrollTop
      const viewBottom = viewTop + container.clientHeight

      const toRender = []
      pageEls.forEach((el) => {
        const p = Number(el.dataset.page)
        const top = el.offsetTop
        const bottom = top + el.offsetHeight
        if (bottom >= viewTop - 300 && top <= viewBottom + 300) {
          toRender.push(p)
        }
      })
      // 优先渲染离视口最近的页
      const center = (viewTop + viewBottom) / 2
      toRender.sort((a, b) => {
        const elA = canvasRefs.get(a)?.parentElement
        const elB = canvasRefs.get(b)?.parentElement
        const dA = elA ? Math.abs(elA.offsetTop - center) : 0
        const dB = elB ? Math.abs(elB.offsetTop - center) : 0
        return dA - dB
      })
      for (const p of toRender) {
        if (!renderedSet.has(p)) await renderPage(p)
      }
    }

    let scrollTimer = null
    function onScroll() {
      if (scrollTimer) clearTimeout(scrollTimer)
      scrollTimer = setTimeout(() => {
        updateCurrentPage()
        renderVisible()
      }, 150)
    }

    // 根据滚动位置更新当前页
    function updateCurrentPage() {
      if (!scrollEl.value) return
      const container = scrollEl.value
      const pageEls = container.querySelectorAll('.pdf-page')
      let current = page.value
      const mid = container.scrollTop + container.clientHeight / 2
      pageEls.forEach((el) => {
        if (el.offsetTop <= mid) current = Number(el.dataset.page)
      })
      if (current !== page.value) {
        page.value = current
        pageInput.value = current
        reportProgress()
      }
    }

    // 滚动到指定页
    function scrollToPage(p) {
      const el = scrollEl.value?.querySelector(`.pdf-page[data-page="${p}"]`)
      if (el) {
        scrollEl.value.scrollTop = el.offsetTop - 8
        page.value = p
        pageInput.value = p
      } else {
        // 还没渲染，直接设置 scrollTop 大致位置（后面懒加载会补）
        page.value = p
        pageInput.value = p
        // 渲染这一页
        renderPage(p).then(() => {
          const e = scrollEl.value?.querySelector(`.pdf-page[data-page="${p}"]`)
          if (e) scrollEl.value.scrollTop = e.offsetTop - 8
        })
      }
    }

    function prevPage() {
      if (page.value > 1) scrollToPage(page.value - 1)
    }
    function nextPage() {
      if (page.value < numPages.value) scrollToPage(page.value + 1)
    }
    function onPageInput(e) {
      let v = parseInt(e.target.value, 10)
      if (isNaN(v)) v = page.value
      v = Math.max(1, Math.min(numPages.value, v))
      scrollToPage(v)
    }
    function zoomIn() { setScale(scale.value * 1.2) }
    function zoomOut() { setScale(scale.value / 1.2) }
    async function fitWidth() {
      const s = await calcFitScale()
      if (s > 0) setScale(s)
    }

    async function setScale(s) {
      scale.value = Math.max(0.4, Math.min(4, s))
      // 清空已渲染，重新渲染所有
      renderedSet.clear()
      canvasRefs.forEach((canvas, p) => {
        canvas.width = 0
        canvas.height = 0
      })
      // 重新渲染当前页附近的页
      await renderVisible()
      updateCurrentPage()
    }

    async function load() {
      loading.value = true
      error.value = ''
      try {
        const url = api.getRawFileUrl(props.path)
        const data = await fetch(url)
        if (!data.ok) throw new Error('加载 PDF 失败: ' + data.status)
        const buffer = await data.arrayBuffer()
        pdfDoc = await pdfjsLib.getDocument({ data: buffer }).promise
        numPages.value = pdfDoc.numPages
        renderedPages.value = Array.from({ length: numPages.value }, (_, i) => i + 1)

        // 初始化缩放（适应宽度）
        const s = await calcFitScale()
        if (s > 0) scale.value = s

        // 渲染初始页（或恢复的页）
        await nextTick()
        if (props.initialPage && props.initialPage > 1) {
          scrollToPage(props.initialPage)
        } else {
          await renderVisible()
        }
      } catch (e) {
        console.error('PDF 加载失败:', e)
        error.value = e.message || 'PDF 加载失败'
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      load()
      // 监听 resize 重新适配
      window.addEventListener('resize', onResize)
    })
    onBeforeUnmount(() => {
      window.removeEventListener('resize', onResize)
      if (reportTimer) clearTimeout(reportTimer)
      if (scrollTimer) clearTimeout(scrollTimer)
    })

    let resizeTimer = null
    function onResize() {
      if (resizeTimer) clearTimeout(resizeTimer)
      resizeTimer = setTimeout(() => renderVisible(), 200)
    }

    return {
      scrollEl,
      loading,
      error,
      numPages,
      page,
      pageInput,
      scale,
      renderedPages,
      setCanvasRef,
      onScroll,
      prevPage,
      nextPage,
      onPageInput,
      zoomIn,
      zoomOut,
      fitWidth,
    }
  },
}
</script>

<style scoped>
.pdf-viewer {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg);
}
.pdf-toolbar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
  background: var(--bg-side);
  flex-shrink: 0;
  flex-wrap: wrap;
}
.pdf-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  border-radius: 5px;
  cursor: pointer;
  flex-shrink: 0;
}
.pdf-btn:hover:not(:disabled) {
  background: var(--bg-hover);
  color: var(--text);
}
.pdf-btn:disabled {
  opacity: 0.35;
  cursor: default;
}
.pdf-page-info {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: var(--text-muted);
  font-size: 13px;
}
.pdf-page-input {
  width: 48px;
  text-align: center;
  background: var(--bg);
  border: 1px solid var(--border);
  color: var(--text);
  border-radius: 4px;
  padding: 3px 4px;
  font-size: 13px;
}
.pdf-sep {
  width: 1px;
  height: 18px;
  background: var(--border);
  margin: 0 4px;
}
.pdf-zoom-info {
  color: var(--text-muted);
  font-size: 12px;
  min-width: 40px;
  text-align: center;
}
.pdf-scroll {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 16px;
}
.pdf-loading,
.pdf-error {
  text-align: center;
  color: var(--text-muted);
  margin-top: 60px;
  font-size: 14px;
}
.pdf-error {
  color: var(--danger, #e06c75);
}
.pdf-pages {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
.pdf-page {
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.4);
  background: #fff;
  line-height: 0;
}
.pdf-page canvas {
  display: block;
}
</style>
