<template>
  <div class="file-tree">
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
          </div>
          <div v-if="item.open" class="tree-children">
            <FileTree :path="item.path" :depth="depth + 1" :active-path="activePath" @select="$emit('select', $event)" />
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
  </div>
</template>

<script>
import { defineComponent } from 'vue'
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
  emits: ['select'],
  data() {
    return { items: [], loading: false }
  },
  async mounted() {
    this.loading = true
    try {
      const list = await api.getTree(this.path)
      this.items = list.map((it) => ({ ...it, open: false }))
    } catch (e) {
      console.error('加载目录失败:', e)
    } finally {
      this.loading = false
    }
  },
  methods: {
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
  },
}
</script>

<style scoped>
.file-tree {
  padding: 8px 6px;
  font-size: 13px;
}
.tree-empty {
  color: var(--text-muted);
  padding: 16px;
  text-align: center;
  font-size: 12px;
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
}
</style>
