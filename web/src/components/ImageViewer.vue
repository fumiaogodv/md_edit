<template>
  <div class="image-viewer">
    <img :src="src" :alt="path" @error="onError" />
    <div v-if="error" class="img-error">{{ error }}</div>
  </div>
</template>

<script>
import { defineComponent, ref, computed } from 'vue'
import { api } from '../api'

export default {
  name: 'ImageViewer',
  props: {
    path: { type: String, required: true },
  },
  setup(props) {
    const error = ref('')
    const src = computed(() => api.getRawFileUrl(props.path))
    function onError() {
      error.value = '图片加载失败'
    }
    return { src, error, onError }
  },
}
</script>

<style scoped>
.image-viewer {
  height: 100%;
  overflow: auto;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background: var(--bg);
}
.image-viewer img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.4);
}
.img-error {
  color: var(--text-muted);
}
</style>
