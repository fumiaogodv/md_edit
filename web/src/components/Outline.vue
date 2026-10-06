<template>
  <div class="outline">
    <div class="outline-title">目录</div>
    <div v-if="items.length === 0" class="outline-empty">暂无标题</div>
    <div
      v-for="(item, i) in items"
      :key="i"
      class="outline-item"
      :class="[`level-${item.level}`, { active: activeIndex === i }]"
      :title="item.text"
      @click="$emit('jump', item.id)"
    >
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
  padding: 12px 8px;
  font-size: 13px;
}
.outline-title {
  font-weight: 600;
  color: var(--text-muted);
  padding: 4px 8px 8px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.outline-empty {
  color: var(--text-muted);
  padding: 4px 8px;
  font-size: 12px;
}
.outline-item {
  padding: 5px 8px;
  cursor: pointer;
  border-radius: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text);
}
.outline-item:hover {
  background: var(--bg-hover);
}
.outline-item.level-2 {
  padding-left: 24px;
  color: var(--text-muted);
}
.outline-item.active {
  background: var(--bg-active);
  color: #fff;
}
</style>
