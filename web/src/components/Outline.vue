<template>
  <div class="outline">
    <div v-if="items.length === 0" class="outline-empty">选择文件后显示标题</div>
    <div
      v-for="(item, i) in items"
      :key="i"
      class="outline-item"
      :class="[`level-${item.level}`, { active: activeIndex === i }]"
      :title="item.text"
      @click="$emit('jump', item.id)"
    >
      <span class="outline-marker" :class="`marker-${item.level}`"></span>
      {{ item.text }}
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'

export default {
  name: 'Outline',
  props: {
    items: { type: Array, default: () => [] },
    activeIndex: { type: Number, default: -1 },
  },
  emits: ['jump'],
}
</script>

<style scoped>
.outline {
  padding: 4px 8px 12px;
  font-size: 13px;
}
.outline-empty {
  color: var(--text-faint);
  padding: 8px;
  font-size: 12px;
}
.outline-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 8px;
  cursor: pointer;
  border-radius: var(--radius-sm);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text);
  transition: background 0.15s;
}
.outline-item:hover {
  background: var(--bg-hover);
}
.outline-item.level-1 {
  font-weight: 500;
}
.outline-item.level-2 {
  padding-left: 22px;
  color: var(--text-muted);
  font-size: 12.5px;
}
.outline-item.active {
  background: var(--bg-active);
  color: #fff;
}
.outline-marker {
  flex-shrink: 0;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--text-faint);
}
.outline-item.level-1 .outline-marker {
  width: 6px;
  height: 6px;
  background: var(--accent);
}
.outline-item.active .outline-marker {
  background: #fff;
}
</style>
