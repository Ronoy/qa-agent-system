<template>
  <div class="chat-input" :class="{ focused }">
    <!-- 待上传文件预览 -->
    <div v-if="pendingFiles.length" class="file-chips">
      <span v-for="f in pendingFiles" :key="f.id" class="file-chip">
        📎 {{ f.name }}
        <button @click="removeFile(f.id)">×</button>
      </span>
    </div>
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
        <input ref="fileInputRef" type="file" accept="image/*,.pdf" multiple style="display:none" @change="handleFileChange" />
        <button class="tool-btn" title="附件" :disabled="isStreaming" @click="fileInputRef?.click()">
          <svg viewBox="0 0 24 24" fill="none" width="14" height="14">
            <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"
              stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span v-if="uploading" style="font-size:11px">上传中...</span>
        </button>

        <!-- 知识库选择器 -->
        <div class="kb-selector" v-if="bases.length">
          <button class="tool-btn selector-btn" :class="{ active: selectedKbIds.size > 0 }"
            @click="showKbPicker = !showKbPicker">
            <svg viewBox="0 0 24 24" fill="none" width="12" height="12">
              <path d="M4 19.5A2.5 2.5 0 016.5 17H20" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z" stroke="currentColor" stroke-width="1.8"/>
            </svg>
            <span>知识库{{ selectedKbIds.size ? ` (${selectedKbIds.size})` : '' }}</span>
          </button>
          <div v-if="showKbPicker" class="kb-dropdown">
            <div v-for="kb in bases" :key="kb.id" class="kb-option"
              :class="{ selected: selectedKbIds.has(kb.id) }"
              @click="toggleKb(kb.id)">
              <span class="kb-check">{{ selectedKbIds.has(kb.id) ? '✓' : '' }}</span>
              {{ kb.name }}
            </div>
          </div>
        </div>

        <!-- 模型选择器 -->
        <div class="kb-selector">
          <button class="tool-btn selector-btn" @click="showModelPicker = !showModelPicker">
            <svg viewBox="0 0 24 24" fill="none" width="12" height="12">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
                stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>{{ selectedModel.label }}</span>
            <svg viewBox="0 0 24 24" fill="none" width="10" height="10">
              <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </button>
          <div v-if="showModelPicker" class="kb-dropdown">
            <div v-for="m in MODELS" :key="m.id" class="kb-option model-option"
              :class="{ selected: selectedModel.id === m.id }"
              @click="selectedModel = m; showModelPicker = false">
              <div>
                <div class="model-label">{{ m.label }}</div>
                <div class="model-desc">{{ m.desc }}</div>
              </div>
              <span class="kb-check">{{ selectedModel.id === m.id ? '✓' : '' }}</span>
            </div>
          </div>
        </div>
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
import { ref, computed, nextTick, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useChatStore } from '@/stores/chat'
import { useKnowledgeStore } from '@/stores/knowledge'
import { uploadFile } from '@/services/chatService'

const emit = defineEmits<{ send: [message: string, attachmentIds: string[], kbIds: { id: string; name: string }[], model: string] }>()
const { isStreaming } = storeToRefs(useChatStore())
const kbStore = useKnowledgeStore()
const { bases } = storeToRefs(kbStore)

const inputText = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const fileInputRef = ref<HTMLInputElement | null>(null)
const focused = ref(false)
const pendingFiles = ref<{ name: string; id: string }[]>([])
const uploading = ref(false)
const showKbPicker = ref(false)
const selectedKbIds = ref<Set<string>>(new Set())

const MODELS = [
  { id: 'deepseek-chat', label: 'DeepSeek V3.2', desc: '快速通用，适合日常问答' },
  { id: 'deepseek-reasoner', label: 'DeepSeek R2', desc: '深度推理，适合复杂分析' },
]
const selectedModel = ref(MODELS[0])
const showModelPicker = ref(false)

const canSend = computed(() => inputText.value.trim().length > 0 && !isStreaming.value && !uploading.value)
const selectedKbs = computed(() => bases.value.filter(b => selectedKbIds.value.has(b.id)))

function autoResize() {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 140) + 'px'
}

async function handleFileChange(e: Event) {
  const files = (e.target as HTMLInputElement).files
  if (!files?.length) return
  uploading.value = true
  try {
    for (const file of Array.from(files)) {
      const id = await uploadFile(file)
      pendingFiles.value.push({ name: file.name, id })
    }
  } finally {
    uploading.value = false
    if (fileInputRef.value) fileInputRef.value.value = ''
  }
}

function removeFile(id: string) {
  pendingFiles.value = pendingFiles.value.filter(f => f.id !== id)
}

onMounted(() => kbStore.fetchBases())

function toggleKb(id: string) {  if (selectedKbIds.value.has(id)) selectedKbIds.value.delete(id)
  else selectedKbIds.value.add(id)
}

function handleSend() {
  if (!canSend.value) return
  const msg = inputText.value.trim()
  const ids = pendingFiles.value.map(f => f.id)
  const kbs = selectedKbs.value.map(b => ({ id: b.id, name: b.name }))
  inputText.value = ''
  pendingFiles.value = []
  nextTick(() => {
    if (textareaRef.value) textareaRef.value.style.height = 'auto'
  })
  emit('send', msg, ids, kbs, selectedModel.value.id)
}
</script>

<style scoped>
.file-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  padding: 8px 18px 0;
}
.file-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  background: var(--primary-light);
  color: var(--primary);
  border-radius: 6px;
  font-size: 12px;
}
.file-chip button {
  border: none;
  background: none;
  cursor: pointer;
  color: var(--primary);
  font-size: 14px;
  line-height: 1;
  padding: 0 2px;
}

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

.selector-btn.active { border-color: var(--primary); color: var(--primary); background: var(--primary-light); }

.kb-selector { position: relative; }
.kb-dropdown {
  position: absolute; bottom: calc(100% + 6px); left: 0;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-sm); box-shadow: var(--shadow-md);
  min-width: 160px; z-index: 50; overflow: hidden;
}
.kb-option {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 12px; font-size: 13px; cursor: pointer;
  color: var(--text-secondary);
}
.kb-option:hover { background: var(--bg); }
.kb-option.selected { color: var(--primary); }
.kb-check { width: 14px; font-size: 12px; color: var(--primary); }
.model-option { flex-direction: row; justify-content: space-between; align-items: center; }
.model-label { font-size: 13px; font-weight: 500; }
.model-desc { font-size: 11px; color: var(--text-muted); margin-top: 1px; }

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
