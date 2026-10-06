<template>
  <div class="search-bar">
    <n-input
      v-model:value="keyword"
      placeholder="搜索文件内容..."
      clearable
      @keyup.enter="doSearch"
      @clear="clearSearch"
    >
      <template #prefix>🔍</template>
    </n-input>

    <div v-if="searched" class="search-results">
      <div v-if="loading" class="result-tip">搜索中...</div>
      <div v-else-if="results.length === 0" class="result-tip">未找到相关文件</div>
      <div v-else class="result-list">
        <div v-for="r in results" :key="r.path" class="result-file">
          <div class="result-filename" @click="$emit('open', r.path)">
            📄 {{ r.name }}
          </div>
          <div
            v-for="(m, i) in r.matches"
            :key="i"
            class="result-line"
            @click="$emit('open', r.path, m.line)"
          >
            <span class="line-no">{{ m.line }}</span>
            <span class="line-text" v-html="highlight(m.text)"></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref } from 'vue'
import { NInput } from 'naive-ui'
import { api } from '../api'

export default {
  name: 'SearchBar',
  components: { NInput },
  emits: ['open'],
  setup() {
    const keyword = ref('')
    const results = ref([])
    const loading = ref(false)
    const searched = ref(false)

    async function doSearch() {
      const q = keyword.value.trim()
      if (!q) return
      loading.value = true
      searched.value = true
      try {
        const data = await api.search(q)
        results.value = data.results
      } catch (e) {
        results.value = []
      } finally {
        loading.value = false
      }
    }

    function clearSearch() {
      searched.value = false
      results.value = []
    }

    function highlight(text) {
      const q = keyword.value.trim()
      if (!q) return text
      const re = new RegExp(q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi')
      return text.replace(re, (m) => `<mark>${m}</mark>`)
    }

    return { keyword, results, loading, searched, doSearch, clearSearch, highlight }
  },
}
</script>

<style scoped>
.search-bar {
  padding: 8px;
}
.search-results {
  margin-top: 8px;
  max-height: 400px;
  overflow-y: auto;
}
.result-tip {
  color: var(--text-muted);
  font-size: 12px;
  padding: 8px;
  text-align: center;
}
.result-file {
  margin-bottom: 10px;
}
.result-filename {
  font-weight: 600;
  font-size: 13px;
  padding: 4px 8px;
  cursor: pointer;
  border-radius: 4px;
}
.result-filename:hover {
  background: var(--bg-hover);
}
.result-line {
  display: flex;
  gap: 8px;
  padding: 3px 8px 3px 16px;
  cursor: pointer;
  font-size: 12px;
  color: var(--text-muted);
  border-radius: 4px;
}
.result-line:hover {
  background: var(--bg-hover);
}
.line-no {
  flex-shrink: 0;
  color: #6a9955;
  font-family: monospace;
}
.line-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.line-text :deep(mark) {
  background: #6b5200;
  color: #fff;
  border-radius: 2px;
}
</style>
