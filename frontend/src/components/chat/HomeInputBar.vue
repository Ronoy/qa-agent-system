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

        <!-- 知识库选择器 -->
        <div v-if="bases.length" class="kb-selector">
          <button class="tool-btn selector-btn" :class="{ active: selectedKbIds.size > 0 }"
            @click="showKbPicker = !showKbPicker">
            <svg viewBox="0 0 24 24" fill="none" width="13" height="13">
              <path d="M4 19.5A2.5 2.5 0 016.5 17H20" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z" stroke="currentColor" stroke-width="1.8"/>
            </svg>
            <span>知识库{{ selectedKbIds.size ? ` (${selectedKbIds.size})` : '' }}</span>
            <svg viewBox="0 0 24 24" fill="none" width="11" height="11">
              <path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
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
            <svg viewBox="0 0 24 24" fill="none" width="13" height="13">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
                stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span>{{ selectedModel.label }}</span>
            <svg viewBox="0 0 24 24" fill="none" width="11" height="11">
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
import { ref, computed, nextTick, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useChatStore } from '@/stores/chat'
import { useKnowledgeStore } from '@/stores/knowledge'

const emit = defineEmits<{ send: [message: string, attachmentIds: string[], kbIds: { id: string; name: string }[], model: string] }>()
const { isStreaming } = storeToRefs(useChatStore())
const kbStore = useKnowledgeStore()
const { bases } = storeToRefs(kbStore)

const inputText = ref('')
const textareaRef = ref<HTMLTextAreaElement | null>(null)
const focused = ref(false)
const showKbPicker = ref(false)
const selectedKbIds = ref<Set<string>>(new Set())
const showModelPicker = ref(false)

const MODELS = [
  { id: 'deepseek-chat', label: 'DeepSeek V3.2', desc: '快速通用，适合日常问答' },
  { id: 'deepseek-reasoner', label: 'DeepSeek R2', desc: '深度推理，适合复杂分析' },
]
const selectedModel = ref(MODELS[0])

const canSend = computed(() => inputText.value.trim().length > 0 && !isStreaming.value)
const selectedKbs = computed(() => bases.value.filter(b => selectedKbIds.value.has(b.id)))

function toggleKb(id: string) {
  if (selectedKbIds.value.has(id)) selectedKbIds.value.delete(id)
  else selectedKbIds.value.add(id)
}

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
  nextTick(() => { if (textareaRef.value) textareaRef.value.style.height = 'auto' })
  emit('send', msg, [], selectedKbs.value.map(b => ({ id: b.id, name: b.name })), selectedModel.value.id)
}

onMounted(() => kbStore.fetchBases())
</script>

<style scoped>
.home-input {
  background: var(--surface); border: 1.5px solid var(--border);
  border-radius: 16px; box-shadow: var(--shadow-sm);
  transition: border-color 0.2s, box-shadow 0.2s; overflow: hidden;
}
.home-input.focused { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(99,102,241,0.1), var(--shadow-md); }
textarea {
  width: 100%; resize: none; border: none; outline: none;
  padding: 16px 18px 10px; font-size: 14px; font-family: inherit;
  line-height: 1.7; max-height: 160px; overflow-y: auto;
  background: transparent; color: var(--text-primary);
}
textarea::placeholder { color: var(--text-muted); }
textarea:disabled { opacity: 0.6; cursor: not-allowed; }
.input-toolbar { display: flex; align-items: center; justify-content: space-between; padding: 6px 10px 10px; gap: 6px; }
.toolbar-left, .toolbar-right { display: flex; align-items: center; gap: 4px; }
.tool-btn {
  display: inline-flex; align-items: center; gap: 5px; padding: 5px 8px;
  border-radius: 8px; border: none; background: none; color: var(--text-muted);
  font-size: 12px; cursor: pointer; transition: all 0.12s; white-space: nowrap;
}
.tool-btn:hover { background: var(--bg); color: var(--text-secondary); }
.selector-btn { border: 1px solid var(--border); background: var(--bg); color: var(--text-secondary); font-size: 12px; padding: 4px 9px; }
.selector-btn:hover, .selector-btn.active { border-color: var(--primary); color: var(--primary); background: var(--primary-light); }
.kb-selector { position: relative; }
.kb-dropdown {
  position: absolute; bottom: calc(100% + 6px); left: 0;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-sm); box-shadow: var(--shadow-md);
  min-width: 160px; z-index: 50; overflow: hidden;
}
.kb-option { display: flex; align-items: center; gap: 8px; padding: 8px 12px; font-size: 13px; cursor: pointer; color: var(--text-secondary); }
.kb-option:hover { background: var(--bg); }
.kb-option.selected { color: var(--primary); }
.kb-check { width: 14px; font-size: 12px; color: var(--primary); }
.model-option { justify-content: space-between; }
.model-label { font-size: 13px; font-weight: 500; }
.model-desc { font-size: 11px; color: var(--text-muted); margin-top: 1px; }
.send-btn {
  width: 32px; height: 32px; border-radius: 50%; border: none;
  background: var(--primary); color: #fff; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.15s; box-shadow: 0 2px 8px rgba(99,102,241,0.35);
}
.send-btn:hover:not(:disabled) { background: var(--primary-dark); transform: scale(1.08); }
.send-btn:disabled { background: var(--border); box-shadow: none; cursor: not-allowed; }
</style>
