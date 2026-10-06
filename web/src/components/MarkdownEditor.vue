<template>
  <div class="md-editor">
    <div ref="editorHost" class="editor-host"></div>
    <div class="editor-toolbar">
      <n-button size="small" type="primary" :loading="saving" @click="save">
        保存
      </n-button>
      <n-button size="small" @click="$emit('cancel')">取消</n-button>
    </div>
  </div>
</template>

<script>
import { defineComponent, ref, onMounted, onBeforeUnmount } from 'vue'
import { EditorView, basicSetup } from 'codemirror'
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

    onMounted(() => {
      view = new EditorView({
        parent: editorHost.value,
        doc: props.content,
        extensions: [
          basicSetup,
          markdown(),
          EditorView.theme({
            '&': { height: '100%', fontSize: '14px' },
            '.cm-scroller': {
              fontFamily: "'SFMono-Regular', Consolas, monospace",
            },
          }),
          EditorView.updateListener.of(() => {}),
        ],
      })
    })

    onBeforeUnmount(() => {
      view?.destroy()
    })

    function save() {
      emit('save', view.state.doc.toString())
    }

    return { editorHost, save }
  },
}
</script>

<style scoped>
.md-editor {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.editor-host {
  flex: 1;
  overflow: hidden;
  border-bottom: 1px solid var(--border);
}
.editor-host :deep(.cm-editor) {
  height: 100%;
  background: var(--bg);
}
.editor-host :deep(.cm-editor.cm-focused) {
  outline: none;
}
.editor-toolbar {
  padding: 10px 16px;
  display: flex;
  gap: 10px;
  background: var(--bg-panel);
}
</style>
