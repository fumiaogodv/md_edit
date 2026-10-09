<template>
  <div class="app">
    <!-- 顶部工具栏 -->
    <header class="topbar">
      <!-- 手机端：文件切换按钮 -->
      <button
        class="icon-btn mobile-toggle"
        :class="{ active: showLeft }"
        @click="togglePanel('left')"
        title="文件"
      >
        <svg viewBox="0 0 16 16" width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M1.5 3.5c0-.6.4-1 1-1h4l1.5 1.5h5.5c.6 0 1 .4 1 1v7c0 .6-.4 1-1 1h-11c-.6 0-1-.4-1-1v-8.5z"/></svg>
      </button>

      <div class="brand">
        <span class="brand-icon">📖</span>
        <span class="brand-name">MD Reader</span>
      </div>

      <div class="search-wrap">
        <SearchBar @open="onSearchOpen" />
      </div>

      <div class="actions">
        <span v-if="currentPath" class="current-file" :title="currentPath">
          {{ currentName }}
        </span>
        <button
          v-if="currentPath && !editing && isEditableFile"
          class="btn btn--primary btn--sm"
          @click="startEdit"
        >
          <svg viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M11.5 2.5l2 2L5 13l-2.5.5L3 11l8.5-8.5z"/></svg>
          编辑
        </button>

        <!-- 手机端：目录切换按钮 -->
        <button
          class="icon-btn mobile-toggle"
          :class="{ active: showRight }"
          @click="togglePanel('right')"
          title="目录"
        >
          <svg viewBox="0 0 16 16" width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.5"><line x1="4" y1="3" x2="15" y2="3"/><line x1="4" y1="8" x2="15" y2="8"/><line x1="4" y1="13" x2="15" y2="13"/><line x1="1.5" y1="3" x2="1.5" y2="3.01"/><line x1="1.5" y1="8" x2="1.5" y2="8.01"/><line x1="1.5" y1="13" x2="1.5" y2="13.01"/></svg>
        </button>
      </div>
    </header>

    <div class="main">
      <!-- 左侧文件树 -->
      <aside class="sidebar left" :class="{ open: showLeft }" :style="leftStyle">
        <div class="panel-head">
          <span class="panel-title">文件</span>
          <button class="icon-btn panel-close" @click="togglePanel('left')" title="关闭">
            <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="4" y1="4" x2="12" y2="12"/><line x1="12" y1="4" x2="4" y2="12"/></svg>
          </button>
        </div>
        <div class="panel-body">
          <FileTree :active-path="currentPath" @select="openFile" />
        </div>
      </aside>

      <!-- 左侧拖拽条（桌面端） -->
      <div class="resize-handle desktop-only" @mousedown="startResize('left', $event)"></div>

      <!-- 中间内容区 -->
      <section class="content">
        <!-- 编辑模式 -->
        <MarkdownEditor
          v-if="editing"
          :content="fileContent"
          :saving="saving"
          @save="saveFile"
          @cancel="cancelEdit"
        />
        <!-- PDF 阅读 -->
        <PdfViewer
          v-else-if="isPdf"
          :path="currentPath"
          :initial-page="restoreProgress?.page || 1"
          @progress="onProgress"
        />
        <!-- 图片查看 -->
        <ImageViewer
          v-else-if="isImage"
          :path="currentPath"
        />
        <!-- 阅读模式（md/txt） -->
        <MarkdownView
          v-else
          ref="viewRef"
          :content="fileContent"
          :highlight-text="highlightText"
          :base-dir="baseDir"
          :restore="restoreProgress"
          @outline="onOutline"
          @progress="onProgress"
        />
      </section>

      <!-- 右侧拖拽条（桌面端） -->
      <div class="resize-handle desktop-only" @mousedown="startResize('right', $event)"></div>

      <!-- 右侧大纲（当前文件一二级标题） -->
      <aside class="sidebar right" :class="{ open: showRight }" :style="rightStyle">
        <div class="panel-head">
          <span class="panel-title">目录</span>
          <span v-if="outline.length" class="badge badge--muted">{{ outline.length }}</span>
          <button class="icon-btn panel-close" @click="togglePanel('right')" title="关闭">
            <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="4" y1="4" x2="12" y2="12"/><line x1="12" y1="4" x2="4" y2="12"/></svg>
          </button>
        </div>
        <div class="panel-body">
          <Outline
            :items="outline"
            :active-index="activeOutline"
            @jump="onJump"
          />
        </div>
      </aside>

      <!-- 手机端遮罩 -->
      <div v-if="isMobile && (showLeft || showRight)" class="mobile-scrim" @click="closePanels"></div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, computed, onMounted, onBeforeUnmount } from 'vue'
import FileTree from './components/FileTree.vue'
import MarkdownView from './components/MarkdownView.vue'
import MarkdownEditor from './components/MarkdownEditor.vue'
import PdfViewer from './components/PdfViewer.vue'
import ImageViewer from './components/ImageViewer.vue'
import Outline from './components/Outline.vue'
import SearchBar from './components/SearchBar.vue'
import { api } from './api'

export default {
  name: 'App',
  components: {
    FileTree,
    MarkdownView,
    MarkdownEditor,
    PdfViewer,
    ImageViewer,
    Outline,
    SearchBar,
  },
  setup() {
    const viewRef = ref(null)
    const currentPath = ref('')
    const currentName = ref('')
    const fileContent = ref('')
    const editing = ref(false)
    const saving = ref(false)
    const outline = ref([])
    const activeOutline = ref(-1)
    const highlightText = ref('')
    const originalContent = ref('')
    // 当前文件的恢复进度（从后端读取）
    const restoreProgress = ref(null)

    // 进度上报防抖
    let saveTimer = null
    // 待保存的进度（切换文件/离开时保存）
    let pendingProgress = null

    // 侧栏宽度（桌面端可拖拽调整）
    const leftWidth = ref(264)
    const rightWidth = ref(240)

    // 响应式：手机端判定
    const isMobile = ref(false)
    const showLeft = ref(false)
    const showRight = ref(false)

    function checkMobile() {
      isMobile.value = window.innerWidth <= 768
      // 切到桌面端时默认展开两个侧栏
      if (!isMobile.value) {
        showLeft.value = true
        showRight.value = true
      } else {
        showLeft.value = false
        showRight.value = false
      }
    }

    onMounted(() => {
      checkMobile()
      window.addEventListener('resize', checkMobile)
      window.addEventListener('beforeunload', onBeforeUnload)
    })

    onBeforeUnmount(() => {
      window.removeEventListener('resize', checkMobile)
      window.removeEventListener('beforeunload', onBeforeUnload)
    })

    // 离开页面时保存进度（用 sendBeacon 尽量送达）
    function onBeforeUnload() {
      if (!currentPath.value || !pendingProgress) return
      const entry = { ...pendingProgress, updatedAt: Math.floor(Date.now() / 1000) }
      const url = api.getProgressUrl(currentPath.value)
      const blob = new Blob([JSON.stringify({ entry })], { type: 'application/json' })
      try {
        navigator.sendBeacon(url, blob)
      } catch (e) {
        /* ignore */
      }
    }

    function togglePanel(type) {
      if (type === 'left') {
        showLeft.value = !showLeft.value
        // 打开文件栏时关闭目录栏（手机上互斥）
        if (isMobile.value && showLeft.value) showRight.value = false
      } else if (type === 'right') {
        showRight.value = !showRight.value
        if (isMobile.value && showRight.value) showLeft.value = false
      }
    }

    function closePanels() {
      showLeft.value = false
      showRight.value = false
    }

    // 侧栏样式：桌面端用固定宽度，手机端用抽屉宽度
    const leftStyle = computed(() => {
      if (isMobile.value) {
        return { width: '80%', maxWidth: '320px', position: 'absolute', left: '0', top: '0', bottom: '0', zIndex: 20 }
      }
      return { width: leftWidth.value + 'px' }
    })

    // 文件类型判断
    const isPdf = computed(() => currentPath.value.toLowerCase().endsWith('.pdf'))
    const isImage = computed(() => {
      const p = currentPath.value.toLowerCase()
      return ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp', '.ico'].some((e) => p.endsWith(e))
    })
    const isEditableFile = computed(() => {
      const p = currentPath.value.toLowerCase()
      return ['.md', '.markdown', '.txt'].some((e) => p.endsWith(e))
    })
    // 当前文件所在目录（用于图片相对路径解析）
    const baseDir = computed(() => {
      const p = currentPath.value
      const idx = p.lastIndexOf('/')
      return idx >= 0 ? p.slice(0, idx) : ''
    })

    const rightStyle = computed(() => {
      if (isMobile.value) {
        return { width: '80%', maxWidth: '320px', position: 'absolute', right: '0', top: '0', bottom: '0', zIndex: 20 }
      }
      return { width: rightWidth.value + 'px' }
    })

    let resizeType = null
    let startX = 0
    let startWidth = 0

    // 拖拽调整侧栏宽度（仅桌面端）
    function startResize(type, e) {
      if (isMobile.value) return
      resizeType = type
      startX = e.clientX
      startWidth = type === 'left' ? leftWidth.value : rightWidth.value
      document.addEventListener('mousemove', onResizeMove)
      document.addEventListener('mouseup', onResizeEnd)
      document.body.style.cursor = 'col-resize'
      document.body.style.userSelect = 'none'
      e.preventDefault()
    }

    function onResizeMove(e) {
      const delta = e.clientX - startX
      let newWidth = startWidth + delta
      newWidth = Math.max(160, Math.min(600, newWidth))
      if (resizeType === 'left') {
        leftWidth.value = newWidth
      } else if (resizeType === 'right') {
        rightWidth.value = startWidth - delta
        rightWidth.value = Math.max(160, Math.min(600, rightWidth.value))
      }
    }

    function onResizeEnd() {
      resizeType = null
      document.removeEventListener('mousemove', onResizeMove)
      document.removeEventListener('mouseup', onResizeEnd)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }

    async function openFile(item) {
      await flushBeforeSwitch()
      currentPath.value = item.path
      currentName.value = item.name
      editing.value = false
      highlightText.value = ''
      restoreProgress.value = null
      // 手机端点开文件后自动收起文件栏
      if (isMobile.value) closePanels()
      await loadCurrentFile()
    }

    async function openByPath(path, line = 0, text = '') {
      await flushBeforeSwitch()
      const name = path.split('/').pop()
      currentPath.value = path
      currentName.value = name
      editing.value = false
      highlightText.value = text || ''
      restoreProgress.value = null
      if (isMobile.value) closePanels()
      await loadCurrentFile()
    }

    // 加载当前文件内容（按类型分发）
    async function loadCurrentFile() {
      const path = currentPath.value
      if (!path) return
      try {
        // 读取进度（md/txt/pdf 都读；图片不需要）
        if (isEditableFile.value || isPdf.value) {
          const prog = await api.getProgress(path)
          restoreProgress.value = prog.entry || null
        }
        // md/txt 才读文本内容
        if (isEditableFile.value) {
          const data = await api.getFile(path)
          fileContent.value = data.content
        } else if (isImage.value || isPdf.value) {
          fileContent.value = ''
        }
      } catch (e) {
        console.error('读取文件失败:', e)
        alert(e.message || '读取文件失败')
      }
    }

    function onSearchOpen(path, line, text) {
      openByPath(path, line, text)
    }

    // 接收子组件上报的进度，防抖保存到后端
    function onProgress(entry) {
      pendingProgress = entry
      if (saveTimer) clearTimeout(saveTimer)
      saveTimer = setTimeout(() => {
        flushProgress()
      }, 1000)
    }

    // 真正写进度到后端
    async function flushProgress() {
      if (!currentPath.value || !pendingProgress) return
      const path = currentPath.value
      const entry = { ...pendingProgress, updatedAt: Math.floor(Date.now() / 1000) }
      pendingProgress = null
      try {
        await api.saveProgress(path, entry)
      } catch (e) {
        console.error('保存进度失败:', e)
      }
    }

    // 切换文件前，先把上一个文件的进度存掉
    async function flushBeforeSwitch() {
      if (saveTimer) clearTimeout(saveTimer)
      await flushProgress()
    }

    function startEdit() {
      if (!currentPath.value) return
      originalContent.value = fileContent.value
      editing.value = true
    }

    function cancelEdit() {
      editing.value = false
      fileContent.value = originalContent.value
    }

    async function saveFile(content) {
      saving.value = true
      try {
        await api.saveFile(currentPath.value, content)
        fileContent.value = content
        editing.value = false
      } catch (e) {
        console.error('保存失败:', e)
        alert(e.message || '保存失败')
      } finally {
        saving.value = false
      }
    }

    function onOutline(items) {
      outline.value = items
    }

    function onJump(id) {
      viewRef.value?.jumpTo(id)
      // 手机端点标题跳转后收起目录栏
      if (isMobile.value) closePanels()
    }

    return {
      currentPath,
      currentName,
      fileContent,
      editing,
      saving,
      outline,
      activeOutline,
      highlightText,
      viewRef,
      leftWidth,
      rightWidth,
      isMobile,
      showLeft,
      showRight,
      leftStyle,
      rightStyle,
      isPdf,
      isImage,
      isEditableFile,
      baseDir,
      restoreProgress,
      startResize,
      togglePanel,
      closePanels,
      openFile,
      onSearchOpen,
      onProgress,
      startEdit,
      cancelEdit,
      saveFile,
      onOutline,
      onJump,
    }
  },
}
</script>

<style scoped>
.app {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg);
}
.topbar {
  height: 50px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 12px;
  background: var(--bg-side);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 15px;
  white-space: nowrap;
  color: var(--text);
}
.brand-icon {
  font-size: 16px;
}
.search-wrap {
  flex: 1;
  max-width: 440px;
  min-width: 0;
}
.actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
  flex-shrink: 0;
}
.current-file {
  color: var(--text-muted);
  font-size: 12px;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 图标按钮 */
.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  border-radius: var(--radius-sm);
  cursor: pointer;
  flex-shrink: 0;
  transition: background 0.15s, color 0.15s;
}
.icon-btn:hover {
  background: var(--bg-hover);
  color: var(--text);
}
.icon-btn.active {
  background: var(--accent-dim);
  color: var(--accent);
}

/* 手机端切换按钮默认隐藏 */
.mobile-toggle {
  display: none;
}

.main {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
}
.sidebar {
  background: var(--bg-side);
  overflow: hidden;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  transition: transform 0.25s ease;
}
.sidebar.left {
  border-right: 1px solid var(--border);
}
.sidebar.right {
  border-left: 1px solid var(--border);
}
.resize-handle {
  width: 5px;
  flex-shrink: 0;
  cursor: col-resize;
  background: transparent;
  transition: background 0.15s;
}
.resize-handle:hover,
.resize-handle:active {
  background: var(--accent);
}
.panel-head {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px 8px;
  flex-shrink: 0;
}
.panel-title {
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: var(--text-faint);
  flex: 1;
}
.panel-close {
  display: none;
}
.panel-body {
  flex: 1;
  overflow-y: auto;
}
.content {
  flex: 1;
  overflow: hidden;
  background: var(--bg);
}

/* 手机端遮罩 */
.mobile-scrim {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 15;
}

/* ===== 手机端适配 ===== */
@media (max-width: 768px) {
  .topbar {
    gap: 6px;
    padding: 0 8px;
  }
  .brand-name {
    display: none;
  }
  .mobile-toggle {
    display: inline-flex;
  }
  .desktop-only {
    display: none;
  }
  .current-file {
    max-width: 90px;
  }
  .panel-close {
    display: inline-flex;
  }

  /* 侧栏变抽屉 */
  .sidebar {
    position: absolute;
    top: 0;
    bottom: 0;
    z-index: 20;
    box-shadow: 0 0 24px rgba(0, 0, 0, 0.5);
  }
  .sidebar.left {
    left: 0;
    transform: translateX(-100%);
  }
  .sidebar.left.open {
    transform: translateX(0);
  }
  .sidebar.right {
    right: 0;
    transform: translateX(100%);
  }
  .sidebar.right.open {
    transform: translateX(0);
  }
}
</style>
