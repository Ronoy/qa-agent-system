<template>
  <div class="home-input" :class="{ focused }">
    <textarea
      ref="textareaRef"
      v-model="inputText"
      placeholder="您可以在这里开启对话，问我任何学习问题..."
      :disabled="isStreaming"
      @keydown.enter.exact.prevent="handleSend"
      @focus="focused = true"
      @blur="focused = false"
      @input="autoResize"
      rows="2"
    />
    <div class="input-toolbar">
      <div class="toolbar-left">
        <button class="tool-btn" title="附件">
          <svg viewBox="0 0 24 24" fill="none" width="15" height="15">
            <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"
              stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <button class="tool-btn selector-btn" title="知识库">
          <svg viewBox="0 0 24 24" fill="none" width="13" height="13">
            <path d="M4 19.5A2.5 2.5 0 016.5 17H20" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
          <span>请选择知识库</span>
          <svg viewBox="0 0 24 24" fill="none" width="11" height="11">
            <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <button class="tool-btn selector-btn" title="模型">
          <svg viewBox="0 0 24 24" fill="none" width="13" height="13">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
              stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>DeepSeek</span>
          <svg viewBox="0 0 24 24" fill="none" width="11" height="11">
            <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
      <div class="toolbar-right">
        <button class="tool-btn" title="语音输入">
          <svg viewBox="0 0 24 24" fill="none" width="15" height="15">
            <path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            <path d="M19 10v2a7 7 0 01-14 0v-2M12 19v4M8 23h8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <button class="send-btn" :disabled="!canSend" @click="handleSend">
          <svg viewBox="0 0 24 24" fill="currentColor" width="15" height="15">
            <path d="M12 19V5M5 12l7-7 7 7" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useChatStore } from '@/stores/chat'

const emit = defineEmits<{ send: [message: string] }>()
const { isStreaming } = storeToRefs(useChatStore())
const inputText = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const focused = ref(false)

const canSend = computed(() => inputText.value.trim().length > 0 && !isStreaming.value)

function autoResize() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 160) + 'px'
}

function handleSend() {
  if (!canSend.value) return
  const msg = inputText.value.trim()
  inputText.value = ''
  nextTick(() => {
    if (textareaRef.value) textareaRef.value.style.height = 'auto'
  })
  emit('send', msg)
}
</script>

<style scoped>
.home-input {
  background: var(--surface);
  border: 1.5px solid var(--border);
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
  transition: border-color 0.2s, box-shadow 0.2s;
  overflow: hidden;
}
.home-input.focused {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(99,102,241,0.1), var(--shadow-md);
}

textarea {
  width: 100%;
  resize: none;
  border: none;
  outline: none;
  padding: 16px 18px 10px;
  font-size: 14px;
  font-family: inherit;
  line-height: 1.7;
  max-height: 160px;
  overflow-y: auto;
  background: transparent;
  color: var(--text-primary);
}
textarea::placeholder { color: var(--text-muted); }
textarea:disabled { opacity: 0.6; cursor: not-allowed; }

.input-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 10px 10px;
  gap: 6px;
}

.toolbar-left, .toolbar-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

.tool-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 8px;
  border-radius: 8px;
  border: none;
  background: none;
  color: var(--text-muted);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.12s;
  white-space: nowrap;
}
.tool-btn:hover { background: var(--bg); color: var(--text-secondary); }

.selector-btn {
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text-secondary);
  font-size: 12px;
  padding: 4px 9px;
}
.selector-btn:hover { border-color: #a5b4fc; color: var(--primary); background: var(--primary-light); }

.send-btn {
  width: 32px; height: 32px;
  border-radius: 50%;
  border: none;
  background: var(--primary);
  color: #fff;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  transition: all 0.15s;
  box-shadow: 0 2px 8px rgba(99,102,241,0.35);
}
.send-btn:hover:not(:disabled) {
  background: var(--primary-dark);
  transform: scale(1.08);
  box-shadow: 0 4px 12px rgba(99,102,241,0.45);
}
.send-btn:disabled { background: var(--border); box-shadow: none; cursor: not-allowed; }
</style>
