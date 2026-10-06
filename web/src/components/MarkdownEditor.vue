<template>
  <div class="md-editor">
    <div ref="editorHost" class="editor-host"></div>
    <div class="editor-toolbar">
      <button class="btn btn--primary btn--sm" :disabled="saving" @click="save">
        {{ saving ? '保存中...' : '保存' }}
      </button>
      <button class="btn btn--sm" @click="$emit('cancel')">取消</button>
      <span class="editor-hint">Markdown 语法编辑，Ctrl+S 保存</span>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, onBeforeUnmount } from 'vue'
import { EditorView, keymap } from '@codemirror/view'
import { basicSetup } from 'codemirror'
import { markdown } from '@codemirror/lang-markdown'

export default {
  name: 'MarkdownEditor',
  props: {
    content: { type: String, default: '' },
    saving: { type: Boolean, default: false },
  },
  emits: ['save', 'cancel'],
  setup(props, { emit }) {
    const editorHost = ref(null)
    let view = null

    function doSave() {
      if (view) emit('save', view.state.doc.toString())
    }

    onMounted(() => {
      view = new EditorView({
        parent: editorHost.value,
        doc: props.content,
        extensions: [
          basicSetup,
          markdown(),
          keymap.of([
            { key: 'Mod-s', run: () => { doSave(); return true } },
          ]),
          EditorView.theme({
            '&': {
              height: '100%',
              fontSize: '14px',
              backgroundColor: 'var(--bg)',
              color: 'var(--text)',
            },
            '.cm-scroller': {
              fontFamily: "'SFMono-Regular', Consolas, 'Courier New', monospace",
              lineHeight: '1.6',
            },
            '.cm-content': { caretColor: 'var(--accent)' },
            '.cm-cursor': { borderLeftColor: 'var(--accent)' },
            '.cm-gutters': {
              backgroundColor: 'var(--bg)',
              color: 'var(--text-faint)',
              border: 'none',
            },
            '.cm-activeLine': { backgroundColor: 'var(--bg-hover)' },
            '.cm-activeLineGutter': { backgroundColor: 'var(--bg-hover)' },
            '&.cm-focused': { outline: 'none' },
          }),
        ],
      })
    })

    onBeforeUnmount(() => {
      view?.destroy()
    })

    return { editorHost, save: doSave }
  },
}
</script>

<style scoped>
.md-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--bg);
}
.editor-host {
  flex: 1;
  overflow: hidden;
}
.editor-toolbar {
  padding: 10px 16px;
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--bg-side);
  border-top: 1px solid var(--border);
}
.editor-hint {
  margin-left: auto;
  font-size: 11px;
  color: var(--text-faint);
}
</style>
