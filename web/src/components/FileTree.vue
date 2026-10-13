<template>
  <div class="file-tree">
    <!-- 创建入口（根目录的 + 按钮） -->
    <div v-if="depth === 0" class="tree-create-entry">
      <button class="create-btn" @click="openCreateMenu(null, $event)" title="新建文件或文件夹">
        <svg viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.6"><line x1="8" y1="3" x2="8" y2="13"/><line x1="3" y1="8" x2="13" y2="8"/></svg>
        <span>新建</span>
      </button>
    </div>

    <div v-if="loading" class="tree-empty">加载中...</div>
    <div v-else-if="items.length === 0" class="tree-empty">暂无文件</div>
    <template v-else>
      <div v-for="item in items" :key="item.path" class="tree-node">
        <!-- 目录：渲染目录行 + 展开时的子项 -->
        <template v-if="item.type === 'dir'">
          <div
            class="tree-row"
            :style="{ paddingLeft: 8 + depth * 16 + 'px' }"
            @click="toggleDir(item)"
          >
            <span class="arrow" :class="{ open: item.open }">
              <svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 4 10 8 6 12" />
              </svg>
            </span>
            <span class="icon">
              <svg v-if="item.open" viewBox="0 0 16 16" width="15" height="15" fill="currentColor"><path d="M8 2.5c.7 0 1.4.2 2 .6.6.4 1 1 1.2 1.6h2.5c.7 0 1.3.6 1.3 1.3v6.7c0 .7-.6 1.3-1.3 1.3H2.3c-.7 0-1.3-.6-1.3-1.3V3.8c0-.7.6-1.3 1.3-1.3H8z"/></svg>
              <svg v-else viewBox="0 0 16 16" width="15" height="15" fill="currentColor" opacity="0.85"><path d="M1.5 3.5c0-.6.4-1 1-1h4l1.5 1.5h5.5c.6 0 1 .4 1 1v7c0 .6-.4 1-1 1h-11c-.6 0-1-.4-1-1v-8.5z"/></svg>
            </span>
            <span class="name">{{ item.name }}</span>
            <!-- 目录的创建按钮（hover 显示） -->
            <button class="row-add" @click.stop="openCreateMenu(item, $event)" title="在此目录新建">
              <svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.6"><line x1="8" y1="3" x2="8" y2="13"/><line x1="3" y1="8" x2="13" y2="8"/></svg>
            </button>
          </div>
          <div v-if="item.open" class="tree-children">
            <FileTree :path="item.path" :depth="depth + 1" :active-path="activePath" @select="$emit('select', $event)" @create-file="$emit('create-file', $event)" />
          </div>
        </template>

        <!-- 文件：渲染文件行 -->
        <div
          v-else
          class="tree-row file"
          :class="{ active: item.path === activePath, disabled: !item.readable }"
          :style="{ paddingLeft: 8 + depth * 16 + 20 + 'px' }"
          :title="item.readable ? item.path : item.name + '（不支持预览）'"
          @click="onFileClick(item)"
        >
          <span class="icon">
            <svg v-if="isPdf(item)" viewBox="0 0 16 16" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.3"><path d="M4 1.5h8c.6 0 1 .4 1 1v11c0 .6-.4 1-1 1H4c-.6 0-1-.4-1-1v-11c0-.6.4-1 1-1z"/><path d="M6.5 5.5h3M6.5 8h3M6.5 10.5h2"/></svg>
            <svg v-else-if="isImage(item)" viewBox="0 0 16 16" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.3"><rect x="2" y="2.5" width="12" height="11" rx="1.5"/><circle cx="6" cy="6.5" r="1.5"/><path d="M2.5 12l3.5-3.5 2.5 2.5 2-2 3 3"/></svg>
            <svg v-else-if="item.readable" viewBox="0 0 16 16" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.3"><path d="M4 1.5h6.5L13 4v10.5c0 .6-.4 1-1 1H4c-.6 0-1-.4-1-1v-12c0-.6.4-1 1-1z"/><path d="M10.5 1.5V4H13"/></svg>
            <svg v-else viewBox="0 0 16 16" width="15" height="15" fill="none" stroke="currentColor" stroke-width="1.3"><path d="M4 1.5h8c.6 0 1 .4 1 1v11c0 .6-.4 1-1 1H4c-.6 0-1-.4-1-1v-11c0-.6.4-1 1-1z"/><path d="M6 6h4M6 9h4"/></svg>
          </span>
          <span class="name">{{ item.name }}</span>
        </div>
      </div>
    </template>

    <!-- 创建菜单弹层 -->
    <div v-if="createMenu" class="create-menu" :style="createMenuStyle">
      <div class="menu-item" @click="showNameInput('file')">
        <span class="mi-icon">📄</span> 新建文件
      </div>
      <div class="menu-item" @click="showNameInput('dir')">
        <span class="mi-icon">📁</span> 新建文件夹
      </div>
    </div>

    <!-- 名称输入弹层 -->
    <div v-if="nameInput" class="name-input-wrap" :style="createMenuStyle">
      <input
        ref="nameInputRef"
        v-model="newName"
        class="name-input"
        :placeholder="nameInputType === 'file' ? '文件名（如 笔记.md）' : '文件夹名'"
        @keydown.enter="confirmCreate"
        @keydown.esc="cancelCreate"
        @blur="cancelCreate"
        @click.stop
      />
    </div>
  </div>
</template>

<script>
import { defineComponent, nextTick } from 'vue'
import { api } from '../api'

// 单一自递归组件：FileTree 引用自身即可递归渲染子目录
export default {
  name: 'FileTree',
  props: {
    // 根节点 depth 为 0；子节点由自身递归传入
    path: { type: String, default: '' },
    depth: { type: Number, default: 0 },
    activePath: { type: String, default: '' },
    // 是否作为根节点（根节点直接展示 ROOT_DIR，子节点需要先加载）
    isRoot: { type: Boolean, default: false },
  },
  emits: ['select', 'create-file'],
  data() {
    return {
      items: [],
      loading: false,
      // 创建菜单状态
      createMenu: false,       // 是否显示创建菜单
      nameInput: false,        // 是否显示名称输入框
      nameInputType: 'file',   // 'file' | 'dir'
      newName: '',
      // 菜单定位（相对点击的目录行）
      menuX: 0,
      menuY: 0,
      // 当前要创建的目录路径（null 表示根目录）
      targetDir: '',
    }
  },
  computed: {
    createMenuStyle() {
      return {
        left: this.menuX + 'px',
        top: this.menuY + 'px',
      }
    },
  },
  async mounted() {
    this.loading = true
    await this.loadItems()
    this.loading = false
  },
  methods: {
    async loadItems() {
      try {
        const list = await api.getTree(this.path)
        this.items = list.map((it) => ({ ...it, open: false }))
      } catch (e) {
        console.error('加载目录失败:', e)
      }
    },
    toggleDir(item) {
      item.open = !item.open
    },
    onFileClick(item) {
      if (item.readable) this.$emit('select', item)
    },
    isPdf(item) {
      return item.ext === '.pdf'
    },
    isImage(item) {
      return ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp', '.ico'].includes(item.ext)
    },
    // 打开创建菜单（item 为 null 表示根目录，否则在该目录下建）
    openCreateMenu(item, e) {
      this.targetDir = item ? item.path : this.path
      // 用鼠标点击位置定位菜单
      if (e) {
        this.menuX = e.clientX
        this.menuY = e.clientY
      } else {
        this.menuX = 16
        this.menuY = 40
      }
      this.createMenu = true
      this.nameInput = false
    },
    // 选择创建类型后，显示名称输入框
    showNameInput(type) {
      this.nameInputType = type
      this.nameInput = true
      this.createMenu = false
      this.newName = ''
      nextTick(() => {
        this.$refs.nameInputRef?.focus()
      })
    },
    async confirmCreate() {
      const name = this.newName.trim()
      if (!name) return
      try {
        if (this.nameInputType === 'dir') {
          await api.createDir(this.targetDir, name)
          // 刷新当前目录
          await this.loadItems()
        } else {
          const node = await api.createFile(this.targetDir, name, '')
          await this.loadItems()
          // 通知父组件打开新建的文件（进入编辑态）
          this.$emit('create-file', node)
        }
        this.cancelCreate()
      } catch (e) {
        alert(e.message || '创建失败')
      }
    },
    cancelCreate() {
      this.createMenu = false
      this.nameInput = false
      this.newName = ''
    },
  },
}
</script>

<style scoped>
.file-tree {
  padding: 8px 6px;
  font-size: 13px;
  position: relative;
}
.tree-empty {
  color: var(--text-muted);
  padding: 16px;
  text-align: center;
  font-size: 12px;
}
.tree-create-entry {
  padding: 2px 4px 8px;
}
.create-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 10px;
  font-size: 12px;
  color: var(--text-muted);
  background: transparent;
  border: 1px dashed var(--border);
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.15s;
}
.create-btn:hover {
  color: var(--accent);
  border-color: var(--accent);
  background: var(--bg-hover);
}
.tree-row {
  display: flex;
  align-items: center;
  padding: 4px 8px;
  cursor: pointer;
  border-radius: 5px;
  user-select: none;
  line-height: 22px;
  color: var(--text);
  position: relative;
}
.tree-row:hover {
  background: var(--bg-hover);
}
.tree-row.file.active {
  background: var(--bg-active);
  color: #fff;
}
.tree-row.file.disabled {
  cursor: default;
  opacity: 0.45;
}
.arrow {
  width: 16px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  color: var(--text-muted);
  transition: transform 0.15s;
}
.arrow.open {
  transform: rotate(90deg);
}
.icon {
  margin: 0 6px 0 2px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  color: var(--text-muted);
}
.tree-row.file.active .icon {
  color: #fff;
}
.name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
}
/* 目录行的创建按钮（hover 显示） */
.row-add {
  display: none;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  border-radius: 4px;
  cursor: pointer;
  flex-shrink: 0;
  margin-left: 4px;
}
.tree-row:hover .row-add {
  display: inline-flex;
}
.row-add:hover {
  background: var(--bg-active);
  color: #fff;
}
/* 创建菜单弹层 */
.create-menu {
  position: fixed;
  z-index: 1000;
  background: var(--bg-side);
  border: 1px solid var(--border);
  border-radius: 6px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
  padding: 4px;
  min-width: 120px;
}
.menu-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 7px 10px;
  cursor: pointer;
  border-radius: 4px;
  font-size: 13px;
  color: var(--text);
}
.menu-item:hover {
  background: var(--bg-hover);
}
.mi-icon {
  font-size: 14px;
}
/* 名称输入弹层 */
.name-input-wrap {
  position: fixed;
  z-index: 1001;
  background: var(--bg-side);
  border: 1px solid var(--accent);
  border-radius: 6px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
  padding: 4px;
}
.name-input {
  width: 180px;
  padding: 6px 8px;
  background: var(--bg);
  border: none;
  color: var(--text);
  font-size: 13px;
  outline: none;
}
</style>
