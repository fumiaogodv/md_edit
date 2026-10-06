<template>
  <n-config-provider :theme="darkTheme">
    <n-message-provider>
      <div class="app">
        <!-- 顶部工具栏 -->
        <header class="topbar">
          <div class="brand">📖 MD Reader</div>
          <div class="search-wrap">
            <SearchBar @open="onSearchOpen" />
          </div>
          <div class="actions">
            <n-button
              v-if="currentPath && !editing"
              size="small"
              @click="startEdit"
            >
              ✏️ 编辑
            </n-button>
            <span v-if="currentPath" class="current-file" :title="currentPath">
              {{ currentName }}
            </span>
          </div>
        </header>

        <div class="main">
          <!-- 左侧文件树 -->
          <aside class="sidebar left">
            <FileTree :active-path="currentPath" @select="openFile" />
          </aside>

          <!-- 中间内容区 -->
          <section class="content">
            <!-- 编辑模式 -->
            <MarkdownEditor
              v-if="editing"
              :content="fileContent"
              :saving="saving"
              @save="saveFile"
              @cancel="editing = false"
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

          <!-- 右侧大纲 -->
          <aside class="sidebar right">
            <Outline
              :items="outline"
              :active-index="activeOutline"
              @jump="onJump"
            />
          </aside>
        </div>
      </div>
    </n-message-provider>
  </n-config-provider>
</template>

<script>
import { defineComponent, ref, nextTick } from 'vue'
import { darkTheme, NConfigProvider, NMessageProvider, NButton, useMessage } from 'naive-ui'
import FileTree from './components/FileTree.vue'
import MarkdownView from './components/MarkdownView.vue'
import MarkdownEditor from './components/MarkdownEditor.vue'
import Outline from './components/Outline.vue'
import SearchBar from './components/SearchBar.vue'
import { api } from './api'

export default {
  name: 'App',
  components: {
    NConfigProvider,
    NMessageProvider,
    NButton,
    FileTree,
    MarkdownView,
    MarkdownEditor,
    Outline,
    SearchBar,
  },
  setup() {
    const message = useMessage()
    const viewRef = ref(null)
    const currentPath = ref('')
    const currentName = ref('')
    const fileContent = ref('')
    const editing = ref(false)
    const saving = ref(false)
    const outline = ref([])
    const activeOutline = ref(-1)
    const highlightLine = ref(0)

    async function openFile(item) {
      currentPath.value = item.path
      currentName.value = item.name
      editing.value = false
      highlightLine.value = 0
      try {
        const data = await api.getFile(item.path)
        fileContent.value = data.content
      } catch (e) {
        message.error(e.message || '读取文件失败')
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
          // 搜索定位：滚动到对应行（粗略定位到对应段落）
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
        message.error(e.message || '读取文件失败')
      }
    }

    function onSearchOpen(path, line) {
      openByPath(path, line)
    }

    function startEdit() {
      if (!currentPath.value) return
      editing.value = true
    }

    async function saveFile(content) {
      saving.value = true
      try {
        await api.saveFile(currentPath.value, content)
        message.success('已保存')
        fileContent.value = content
        editing.value = false
      } catch (e) {
        message.error(e.message || '保存失败')
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
      darkTheme,
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
}
.topbar {
  height: 48px;
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 0 16px;
  background: var(--bg-side);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.brand {
  font-weight: 700;
  font-size: 15px;
  white-space: nowrap;
}
.search-wrap {
  flex: 1;
  max-width: 480px;
}
.actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: auto;
}
.current-file {
  color: var(--text-muted);
  font-size: 12px;
  max-width: 240px;
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
  overflow-y: auto;
  flex-shrink: 0;
}
.sidebar.left {
  width: 260px;
  border-right: 1px solid var(--border);
}
.sidebar.right {
  width: 240px;
  border-left: 1px solid var(--border);
}
.content {
  flex: 1;
  overflow: hidden;
  background: var(--bg);
}
</style>
