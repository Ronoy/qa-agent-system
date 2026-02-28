<template>
  <div class="list-wrapper">
    <!-- 可滚动区域 -->
    <div class="message-list" ref="listRef" @scroll="onScroll">
      <!-- 空状态 -->
      <div v-if="messages.length === 0" class="empty-state">
        <div class="empty-icon">
          <svg viewBox="0 0 80 80" fill="none" width="80" height="80">
            <circle cx="40" cy="40" r="38" fill="#eef2ff" stroke="#c7d2fe" stroke-width="1.5"/>
            <path d="M25 35h30M25 45h20" stroke="#6366f1" stroke-width="2.5" stroke-linecap="round"/>
            <circle cx="52" cy="52" r="10" fill="#4f46e5"/>
            <path d="M49 52l2 2 4-4" stroke="white" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h3>你好，张同学！</h3>
        <p>我可以帮你查询考勤、学情、任务进度<br>和知识点掌握情况，试试下方快捷指令吧</p>
        <div class="empty-hints">
          <button
            v-for="hint in hints"
            :key="hint"
            class="hint-chip"
            @click="$emit('select', hint)"
          >{{ hint }}</button>
        </div>
      </div>

      <!-- 消息列表 -->
      <template v-else>
        <MessageItem
          v-for="(msg, i) in messages"
          :key="msg.id"
          :message="msg"
          :is-last-assistant="msg.role === 'assistant' && i === messages.length - 1"
        />
      </template>

      <!-- 打字中占位 -->
      <div v-if="isStreaming && lastIsUser" class="typing-bubble">
        <div class="typing-avatar">
          <svg viewBox="0 0 24 24" fill="none" width="14" height="14">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
              stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <div class="typing-dots">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>

    <!-- 滚动到底部按钮（在包裹层绝对定位，不遮挡消息） -->
    <Transition name="scroll-btn">
      <button v-if="showScrollBtn" class="scroll-bottom-btn" @click="scrollToBottom()">
        <svg viewBox="0 0 24 24" fill="none" width="16" height="16">
          <path d="M12 5v14M5 12l7 7 7-7" stroke="currentColor" stroke-width="2"
            stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed, nextTick } from 'vue'
import { storeToRefs } from 'pinia'
import { useChatStore } from '@/stores/chat'
import MessageItem from './MessageItem.vue'

defineEmits<{ select: [text: string] }>()

const chatStore = useChatStore()
const { messages, isStreaming } = storeToRefs(chatStore)
const listRef = ref<HTMLElement | null>(null)
const showScrollBtn = ref(false)

const lastIsUser = computed(() =>
  messages.value.length > 0 && messages.value[messages.value.length - 1].role === 'user'
)

const hints = ['查任务进度', '查询学情', '查考勤记录', '学习建议']

function scrollToBottom(smooth = true) {
  if (!listRef.value) return
  listRef.value.scrollTo({ top: listRef.value.scrollHeight, behavior: smooth ? 'smooth' : 'auto' })
}

function onScroll() {
  if (!listRef.value) return
  const { scrollTop, scrollHeight, clientHeight } = listRef.value
  showScrollBtn.value = scrollHeight - scrollTop - clientHeight > 120
}

watch(messages, async () => {
  await nextTick()
  if (!showScrollBtn.value) scrollToBottom(false)
}, { deep: true })
</script>

<style scoped>
/* 外层包裹，用于绝对定位滚动按钮 */
.list-wrapper {
  flex: 1;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 24px 20px;
  display: flex;
  flex-direction: column;
}

/* 空状态 */
.empty-state {
  margin: auto;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 40px 20px;
}
.empty-icon { margin-bottom: 4px; }
.empty-state h3 { font-size: 18px; font-weight: 700; color: var(--text-primary); }
.empty-state p { font-size: 13px; color: var(--text-secondary); line-height: 1.8; }

.empty-hints {
  display: flex; flex-wrap: wrap; gap: 8px;
  justify-content: center; margin-top: 4px;
}
.hint-chip {
  font-size: 12px;
  padding: 5px 12px;
  border-radius: var(--radius-full);
  background: var(--primary-light);
  color: var(--primary);
  border: 1px solid #c7d2fe;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}
.hint-chip:hover {
  background: var(--primary);
  color: #fff;
  border-color: var(--primary);
  transform: translateY(-1px);
}

/* 打字气泡 */
.typing-bubble {
  display: flex; align-items: center; gap: 10px;
  margin-bottom: 20px;
  animation: fadeUp 0.2s ease;
}
.typing-avatar {
  width: 34px; height: 34px;
  border-radius: 50%;
  background: var(--primary-light);
  color: var(--primary);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.typing-dots {
  display: flex; gap: 5px;
  padding: 12px 16px;
  background: var(--surface);
  border-radius: 16px;
  border-bottom-left-radius: 4px;
  box-shadow: var(--shadow-sm);
}
.typing-dots span {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: var(--text-muted);
  animation: bounce 1.2s infinite;
}
.typing-dots span:nth-child(2) { animation-delay: 0.2s; }
.typing-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-5px); }
}
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* 滚动到底部按钮 — 绝对定位，不影响文档流 */
.scroll-bottom-btn {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  width: 36px; height: 36px;
  border-radius: 50%;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text-secondary);
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  box-shadow: var(--shadow-md);
  transition: all 0.15s;
}
.scroll-bottom-btn:hover {
  background: var(--primary); color: #fff; border-color: var(--primary);
}

.scroll-btn-enter-active, .scroll-btn-leave-active { transition: all 0.2s ease; }
.scroll-btn-enter-from, .scroll-btn-leave-to { opacity: 0; transform: translateX(-50%) translateY(8px); }
</style>
