<template>
  <div class="input-bar" :class="{ focused }">
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
    <button class="send-btn" :disabled="!canSend" @click="handleSend">
      <svg v-if="!isStreaming" viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
        <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
      </svg>
      <svg v-else viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
        <rect x="6" y="6" width="12" height="12" rx="2"/>
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useChatStore } from '@/stores/chat'

const emit = defineEmits<{ send: [message: string] }>()
const chatStore = useChatStore()
const { isStreaming } = storeToRefs(chatStore)
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
.input-bar {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  padding: 12px 16px 14px;
  background: var(--surface);
  border-top: 1px solid var(--border);
  transition: box-shadow 0.2s;
}
.input-bar.focused {
  box-shadow: 0 -2px 12px rgba(79,70,229,0.06);
}

textarea {
  flex: 1;
  resize: none;
  border: 1.5px solid var(--border);
  border-radius: 14px;
  padding: 10px 14px;
  font-size: 14px;
  font-family: inherit;
  outline: none;
  line-height: 1.6;
  max-height: 140px;
  overflow-y: auto;
  background: var(--bg);
  color: var(--text-primary);
  transition: border-color 0.2s, background 0.2s;
}
textarea::placeholder { color: var(--text-muted); }
textarea:focus { border-color: var(--primary); background: var(--surface); }
textarea:disabled { opacity: 0.6; cursor: not-allowed; }

.send-btn {
  width: 40px; height: 40px;
  border-radius: 12px;
  border: none;
  background: var(--primary);
  color: #fff;
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  transition: all 0.15s;
  box-shadow: 0 2px 8px rgba(79,70,229,0.35);
}
.send-btn:hover:not(:disabled) {
  background: var(--primary-dark);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79,70,229,0.45);
}
.send-btn:active:not(:disabled) { transform: translateY(0); }
.send-btn:disabled { background: var(--border); box-shadow: none; cursor: not-allowed; }
</style>
