<template>
  <div class="search-bar">
    <div class="search-input-wrap">
      <svg class="search-icon" viewBox="0 0 16 16" width="14" height="14" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
        <circle cx="7" cy="7" r="4.5"></circle>
        <line x1="11" y1="11" x2="14.5" y2="14.5"></line>
      </svg>
      <input
        v-model="keyword"
        class="input search-input"
        type="text"
        placeholder="搜索文件内容..."
        autocomplete="off"
        spellcheck="false"
        @keyup.enter="doSearch"
        @input="onInput"
      />
      <button
        v-if="keyword"
        class="search-clear"
        title="清空"
        @click="clearSearch"
      >
        <svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="4" y1="4" x2="12" y2="12"/><line x1="12" y1="4" x2="4" y2="12"/></svg>
      </button>
    </div>

    <div v-if="searched" class="search-results">
      <div v-if="loading" class="result-tip">搜索中...</div>
      <div v-else-if="results.length === 0" class="result-tip">未找到相关文件</div>
      <div v-else class="result-list">
        <div v-for="r in results" :key="r.path" class="result-file">
          <div class="result-filename" @click="$emit('open', r.path)">
            <svg viewBox="0 0 16 16" width="13" height="13" fill="none" stroke="currentColor" stroke-width="1.3"><path d="M4 1.5h6.5L13 4v10.5c0 .6-.4 1-1 1H4c-.6 0-1-.4-1-1v-12c0-.6.4-1 1-1z"/><path d="M10.5 1.5V4H13"/></svg>
            {{ r.name }}
            <span class="badge badge--muted">{{ r.matches.length }}</span>
          </div>
          <div
            v-for="(m, i) in r.matches"
            :key="i"
            class="result-line"
            @click="$emit('open', r.path, m.line, m.text)"
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
import { api } from '../api'

export default {
  name: 'SearchBar',
  emits: ['open'],
  setup() {
    const keyword = ref('')
    const results = ref([])
    const loading = ref(false)
    const searched = ref(false)
    let timer = null

    async function doSearch() {
      const q = keyword.value.trim()
      if (!q) {
        clearSearch()
        return
      }
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

    // 输入防抖
    function onInput() {
      clearTimeout(timer)
      if (!keyword.value.trim()) {
        clearSearch()
        return
      }
      timer = setTimeout(doSearch, 400)
    }

    function clearSearch() {
      searched.value = false
      results.value = []
      keyword.value = ''
    }

    function highlight(text) {
      const q = keyword.value.trim()
      if (!q) return text
      const re = new RegExp(q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi')
      return text.replace(re, (m) => `<mark>${m}</mark>`)
    }

    return { keyword, results, loading, searched, doSearch, onInput, clearSearch, highlight }
  },
}
</script>

<style scoped>
.search-bar {
  position: relative;
}
.search-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}
.search-icon {
  position: absolute;
  left: 10px;
  color: var(--text-faint);
  pointer-events: none;
}
.search-input {
  padding-left: 32px;
  padding-right: 30px;
  height: 32px;
  font-size: 13px;
}
.search-clear {
  position: absolute;
  right: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border: none;
  background: transparent;
  color: var(--text-faint);
  cursor: pointer;
  border-radius: 4px;
}
.search-clear:hover {
  background: var(--bg-hover);
  color: var(--text);
}

.search-results {
  position: absolute;
  top: 38px;
  left: 0;
  right: 0;
  z-index: 100;
  max-height: 420px;
  overflow-y: auto;
  background: var(--bg-panel);
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-lg);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}
.result-tip {
  color: var(--text-faint);
  font-size: 12px;
  padding: 14px;
  text-align: center;
}
.result-file {
  padding: 6px 0;
}
.result-file + .result-file {
  border-top: 1px solid var(--border);
}
.result-filename {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  font-size: 13px;
  padding: 6px 14px;
  cursor: pointer;
  color: var(--text);
}
.result-filename:hover {
  background: var(--bg-hover);
}
.result-filename .badge {
  margin-left: auto;
}
.result-line {
  display: flex;
  gap: 8px;
  padding: 3px 14px 3px 28px;
  cursor: pointer;
  font-size: 12px;
  color: var(--text-muted);
}
.result-line:hover {
  background: var(--bg-hover);
}
.line-no {
  flex-shrink: 0;
  color: var(--text-faint);
  font-family: ui-monospace, Consolas, monospace;
  min-width: 22px;
  text-align: right;
}
.line-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.line-text :deep(mark) {
  background: var(--warning-dim);
  color: var(--warning);
  border-radius: 2px;
  padding: 0 1px;
}
</style>
