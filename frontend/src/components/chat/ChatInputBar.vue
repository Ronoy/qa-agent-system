<template>
  <div class="chat-input" :class="{ focused }">
    <textarea
      ref="textareaRef"
      v-model="inputText"
      placeholder="输入问题，Enter 发送，Shift+Enter 换行..."
      :disabled="isStreaming"
      @keydown.enter.exact.prevent="handleSend"
      @focus="focused = true"
      @blur="focused = false"
      @input="autoResize"
      rows="1"
    />
    <div class="input-toolbar">
      <div class="toolbar-left">
        <button class="tool-btn" title="附件">
          <svg viewBox="0 0 24 24" fill="none" width="14" height="14">
            <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"
              stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <button class="tool-btn selector-btn" title="模型">
          <svg viewBox="0 0 24 24" fill="none" width="12" height="12">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
              stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>DeepSeek</span>
          <svg viewBox="0 0 24 24" fill="none" width="10" height="10">
            <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
      </div>
      <div class="toolbar-right">
        <button class="tool-btn" title="语音输入">
          <svg viewBox="0 0 24 24" fill="none" width="14" height="14">
            <path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
            <path d="M19 10v2a7 7 0 01-14 0v-2M12 19v4M8 23h8" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <button class="send-btn" :disabled="!canSend" @click="handleSend">
          <svg v-if="!isStreaming" viewBox="0 0 24 24" fill="none" width="14" height="14">
            <path d="M12 19V5M5 12l7-7 7 7" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <svg v-else viewBox="0 0 24 24" fill="currentColor" width="12" height="12">
            <rect x="6" y="6" width="12" height="12" rx="2"/>
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
  el.style.height = Math.min(el.scrollHeight, 140) + 'px'
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
.chat-input {
  border-top: 1px solid var(--border);
  background: var(--surface);
  transition: box-shadow 0.2s;
}
.chat-input.focused {
  box-shadow: 0 -2px 12px rgba(99,102,241,0.06);
}

textarea {
  width: 100%;
  resize: none;
  border: none;
  outline: none;
  padding: 14px 18px 6px;
  font-size: 14px;
  font-family: inherit;
  line-height: 1.6;
  max-height: 140px;
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
  padding: 4px 12px 10px;
}

.toolbar-left, .toolbar-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

.tool-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 7px;
  border-radius: 7px;
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
  padding: 4px 8px;
}
.selector-btn:hover { border-color: #a5b4fc; color: var(--primary); background: var(--primary-light); }

.send-btn {
  width: 30px; height: 30px;
  border-radius: 50%;
  border: none;
  background: var(--primary);
  color: #fff;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  transition: all 0.15s;
  box-shadow: 0 2px 6px rgba(99,102,241,0.35);
}
.send-btn:hover:not(:disabled) {
  background: var(--primary-dark);
  transform: scale(1.08);
}
.send-btn:disabled { background: var(--border); box-shadow: none; cursor: not-allowed; }
</style>
