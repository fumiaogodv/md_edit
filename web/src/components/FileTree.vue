<template>
  <div class="file-tree">
    <div v-if="loading && items.length === 0" class="tree-empty">加载中...</div>
    <div v-else-if="!loading && items.length === 0" class="tree-empty">暂无文件</div>
    <template v-else>
      <div v-for="item in items" :key="item.path" class="tree-node">
        <!-- 目录 -->
        <div
          v-if="item.type === 'dir'"
          class="tree-row"
          :style="{ paddingLeft: 8 + level * 14 + 'px' }"
          @click="toggleDir(item)"
        >
          <span class="arrow" :class="{ open: item.open }">▶</span>
          <span class="icon folder">📁</span>
          <span class="name">{{ item.name }}</span>
        </div>
        <!-- 目录子项（懒加载） -->
        <div v-if="item.type === 'dir' && item.open" class="tree-children">
          <FileTreeNode :path="item.path" :level="level + 1" @select="$emit('select', $event)" />
        </div>
        <!-- 文件 -->
        <div
          v-else
          class="tree-row file"
          :class="{ active: item.path === activePath, disabled: !item.editable }"
          :style="{ paddingLeft: 8 + level * 14 + 24 + 'px' }"
          :title="item.editable ? item.path : item.name + '（不支持预览）'"
          @click="onFileClick(item)"
        >
          <span class="icon">{{ fileIcon(item) }}</span>
          <span class="name">{{ item.name }}</span>
        </div>
      </div>
    </template>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { api } from '../api'

const FileTreeNode = defineComponent({
  name: 'FileTreeNode',
  props: {
    path: { type: String, required: true },
    level: { type: Number, default: 0 },
  },
  emits: ['select'],
  data() {
    return { items: [], loading: false }
  },
  async mounted() {
    this.loading = true
    try {
      this.items = (await api.getTree(this.path)).map((it) => ({
        ...it,
        open: false,
      }))
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
      if (item.editable) this.$emit('select', item)
    },
    fileIcon(item) {
      return item.editable ? '📄' : '📃'
    },
  },
})

export default {
  name: 'FileTree',
  components: { FileTreeNode },
  props: {
    activePath: { type: String, default: '' },
  },
  emits: ['select'],
  data() {
    return { items: [], loading: false }
  },
  async mounted() {
    this.loading = true
    try {
      this.items = (await api.getTree()).map((it) => ({ ...it, open: false }))
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
      if (item.editable) this.$emit('select', item)
    },
    fileIcon(item) {
      return item.editable ? '📄' : '📃'
    },
  },
}
</script>

<style scoped>
.file-tree {
  padding: 8px 4px;
  font-size: 13px;
}
.tree-empty {
  color: var(--text-muted);
  padding: 16px;
  text-align: center;
}
.tree-row {
  display: flex;
  align-items: center;
  padding: 5px 8px;
  cursor: pointer;
  border-radius: 4px;
  user-select: none;
}
.tree-row:hover {
  background: var(--bg-hover);
}
.tree-row.file.active {
  background: var(--bg-active);
  color: #fff;
}
.tree-row.file.disabled {
  cursor: not-allowed;
  opacity: 0.6;
}
.arrow {
  width: 16px;
  font-size: 10px;
  transition: transform 0.15s;
  color: var(--text-muted);
  flex-shrink: 0;
}
.arrow.open {
  transform: rotate(90deg);
}
.icon {
  margin-right: 6px;
  font-size: 14px;
  flex-shrink: 0;
}
.name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.tree-children {
  /* 子项已通过 level 缩进，这里不再额外缩进 */
}
</style>
