<template>
  <div class="app">
    <!-- 顶部工具栏 -->
    <header class="topbar">
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
          v-if="currentPath && !editing"
          class="btn btn--primary btn--sm"
          @click="startEdit"
        >
          <svg viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M11.5 2.5l2 2L5 13l-2.5.5L3 11l8.5-8.5z"/></svg>
          编辑
        </button>
      </div>
    </header>

    <div class="main">
      <!-- 左侧文件树 -->
      <aside class="sidebar left">
        <div class="panel-head">
          <span class="panel-title">文件</span>
        </div>
        <div class="panel-body">
          <FileTree :active-path="currentPath" @select="openFile" />
        </div>
      </aside>

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
        <!-- 阅读模式 -->
        <MarkdownView
          v-else
          ref="viewRef"
          :content="fileContent"
          :highlight-line="highlightLine"
          @outline="onOutline"
        />
      </section>

      <!-- 右侧大纲（当前文件一二级标题） -->
      <aside class="sidebar right">
        <div class="panel-head">
          <span class="panel-title">目录</span>
          <span v-if="outline.length" class="badge badge--muted">{{ outline.length }}</span>
        </div>
        <div class="panel-body">
          <Outline
            :items="outline"
            :active-index="activeOutline"
            @jump="onJump"
          />
        </div>
      </aside>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, nextTick } from 'vue'
import FileTree from './components/FileTree.vue'
import MarkdownView from './components/MarkdownView.vue'
import MarkdownEditor from './components/MarkdownEditor.vue'
import Outline from './components/Outline.vue'
import SearchBar from './components/SearchBar.vue'
import { api } from './api'

export default {
  name: 'App',
  components: {
    FileTree,
    MarkdownView,
    MarkdownEditor,
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
    const highlightLine = ref(0)
    const originalContent = ref('')

    async function openFile(item) {
      currentPath.value = item.path
      currentName.value = item.name
      editing.value = false
      highlightLine.value = 0
      try {
        const data = await api.getFile(item.path)
        fileContent.value = data.content
      } catch (e) {
        console.error('读取文件失败:', e)
        alert(e.message || '读取文件失败')
      }
    }

    async function openByPath(path, line = 0) {
      const name = path.split('/').pop()
      currentPath.value = path
      currentName.value = name
      editing.value = false
      highlightLine.value = line
      try {
        const data = await api.getFile(path)
        fileContent.value = data.content
        if (line) {
          nextTick(() => {
            const el = viewRef.value?.$el?.querySelector('.markdown-body')
            if (el) {
              const lines = el.innerText.split('\n')
              const ratio = Math.min(line / Math.max(lines.length, 1), 1)
              el.scrollTop = ratio * el.scrollHeight
            }
          })
        }
      } catch (e) {
        console.error('读取文件失败:', e)
        alert(e.message || '读取文件失败')
      }
    }

    function onSearchOpen(path, line) {
      openByPath(path, line)
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
    }

    return {
      currentPath,
      currentName,
      fileContent,
      editing,
      saving,
      outline,
      activeOutline,
      highlightLine,
      viewRef,
      openFile,
      onSearchOpen,
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
  gap: 16px;
  padding: 0 16px;
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
}
.actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: auto;
}
.current-file {
  color: var(--text-muted);
  font-size: 12px;
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.main {
  flex: 1;
  display: flex;
  overflow: hidden;
}
.sidebar {
  background: var(--bg-side);
  overflow: hidden;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}
.sidebar.left {
  width: 264px;
  border-right: 1px solid var(--border);
}
.sidebar.right {
  width: 240px;
  border-left: 1px solid var(--border);
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
</style>
