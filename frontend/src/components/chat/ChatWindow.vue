<template>
  <div class="chat-window">
    <!-- 空状态：Hero Banner + 大输入框 -->
    <div v-if="isEmpty" class="home-view">
      <div class="hero-banner">
        <div class="hero-bg">
          <div class="hero-orb hero-orb-1"></div>
          <div class="hero-orb hero-orb-2"></div>
          <div class="hero-orb hero-orb-3"></div>
        </div>
        <div class="hero-content">
          <h1 class="hero-title">智学助手</h1>
          <p class="hero-sub">AI 驱动的个性化学习伙伴</p>
          <div class="hero-tag">
            <span class="tag-dot"></span>
            随时解答你的学习问题
          </div>
        </div>
        <div class="hero-deco">
          <div class="deco-card">
            <span>📊</span>
            <span>学情分析</span>
          </div>
          <div class="deco-card">
            <span>🧠</span>
            <span>知识点</span>
          </div>
          <div class="deco-card">
            <span>📋</span>
            <span>任务追踪</span>
          </div>
        </div>
      </div>

      <div class="home-input-wrap">
        <HomeInputBar @send="handleSend" />
        <QuickCommands @select="handleSend" />
        <div class="feature-cards">
          <div v-for="card in featureCards" :key="card.title" class="feature-card">
            <span class="card-icon" :style="{ background: card.bg }">{{ card.icon }}</span>
            <div>
              <div class="card-title">{{ card.title }}</div>
              <div class="card-desc">{{ card.desc }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 对话视图 -->
    <template v-else>
      <div class="chat-header">
        <div class="header-left">
          <div class="header-avatar">
            <svg viewBox="0 0 24 24" fill="none" width="15" height="15">
              <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
                stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div>
            <div class="header-title">{{ currentTitle }}</div>
            <div class="header-status">
              <span class="status-dot" :class="{ thinking: isStreaming }"></span>
              {{ isStreaming ? '正在思考...' : 'AI 助手已就绪' }}
            </div>
          </div>
        </div>
        <button class="new-btn" @click="handleNewChat">
          <svg viewBox="0 0 24 24" fill="none" width="14" height="14">
            <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
          </svg>
          新对话
        </button>
      </div>

      <MessageList @select="handleSend" />

      <div class="chat-input-area">
        <QuickCommands @select="handleSend" />
        <ChatInputBar @send="handleSend" />
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useChatStore } from '@/stores/chat'
import { useConversationStore } from '@/stores/conversation'
import { sendMessage } from '@/services/chatService'
import MessageList from './MessageList.vue'
import HomeInputBar from './HomeInputBar.vue'
import ChatInputBar from './ChatInputBar.vue'
import QuickCommands from '@/components/quick/QuickCommands.vue'

const chatStore = useChatStore()
const convStore = useConversationStore()
const { currentConversationId, isStreaming, messages } = storeToRefs(chatStore)
const { conversations } = storeToRefs(convStore)

const isEmpty = computed(() => messages.value.length === 0)

const currentTitle = computed(() => {
  if (!currentConversationId.value) return '新对话'
  return conversations.value.find(c => c.id === currentConversationId.value)?.title ?? '对话'
})

const featureCards = [
  { icon: '📊', title: '学情分析', desc: '查看各科成绩与进度', bg: '#eef2ff' },
  { icon: '📋', title: '任务管理', desc: '跟踪作业完成情况', bg: '#f0fdf4' },
  { icon: '🧠', title: '知识点', desc: '掌握薄弱知识点', bg: '#fff7ed' },
  { icon: '📅', title: '考勤记录', desc: '查看出勤情况', bg: '#fdf4ff' },
]

function handleNewChat() { chatStore.clearMessages() }

async function handleSend(message: string) {
  chatStore.addUserMessage(message)
  try {
    await sendMessage(message, currentConversationId.value)
    await convStore.fetchAll()
  } catch (err) {
    chatStore.finishStreaming()
    console.error('发送失败', err)
  }
}
</script>

<style scoped>
.chat-window {
  flex: 1; display: flex; flex-direction: column;
  height: 100%; overflow: hidden; background: var(--bg);
  min-width: 0;
}

/* ── Hero Banner ── */
.home-view { flex: 1; overflow-y: auto; display: flex; flex-direction: column; }

.hero-banner {
  position: relative; overflow: hidden;
  min-height: 220px;
  display: flex; align-items: flex-end; justify-content: space-between;
  padding: 36px 48px;
  flex-shrink: 0;
}
.hero-bg {
  position: absolute; inset: 0;
  background: linear-gradient(135deg,
    #0f172a 0%, #1e1b4b 30%, #312e81 60%, #4338ca 80%, #6366f1 100%);
}
.hero-orb {
  position: absolute; border-radius: 50%;
  filter: blur(60px); opacity: 0.5;
}
.hero-orb-1 {
  width: 300px; height: 300px;
  background: radial-gradient(circle, #818cf8, transparent);
  top: -80px; right: 10%;
}
.hero-orb-2 {
  width: 200px; height: 200px;
  background: radial-gradient(circle, #a78bfa, transparent);
  bottom: -60px; left: 30%;
}
.hero-orb-3 {
  width: 160px; height: 160px;
  background: radial-gradient(circle, #38bdf8, transparent);
  top: 20px; left: 5%;
  opacity: 0.25;
}

.hero-content { position: relative; z-index: 1; }
.hero-title {
  font-size: 40px; font-weight: 900;
  color: #fff; line-height: 1.1;
  margin-bottom: 10px;
  letter-spacing: -0.02em;
}
.hero-sub {
  font-size: 14px; color: rgba(255,255,255,0.6);
  margin-bottom: 14px;
}
.hero-tag {
  display: inline-flex; align-items: center; gap: 7px;
  padding: 5px 14px; border-radius: var(--radius-full);
  background: rgba(255,255,255,0.12);
  border: 1px solid rgba(255,255,255,0.18);
  color: rgba(255,255,255,0.85);
  font-size: 12px; font-weight: 500;
  backdrop-filter: blur(8px);
}
.tag-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: #4ade80;
  box-shadow: 0 0 6px #4ade80;
}

.hero-deco {
  position: relative; z-index: 1;
  display: flex; flex-direction: column; gap: 8px;
  align-items: flex-end;
}
.deco-card {
  display: flex; align-items: center; gap: 8px;
  padding: 7px 14px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.15);
  border-radius: 10px;
  backdrop-filter: blur(10px);
  color: rgba(255,255,255,0.85);
  font-size: 12px; font-weight: 500;
  white-space: nowrap;
}

/* ── Home Input Area ── */
.home-input-wrap {
  flex: 1; padding: 28px 40px 32px;
  display: flex; flex-direction: column; gap: 16px;
  max-width: 800px; width: 100%; margin: 0 auto;
  align-self: stretch;
}

.feature-cards {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;
}
.feature-card {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 14px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  cursor: pointer;
  transition: all 0.15s;
}
.feature-card:hover {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(99,102,241,0.08);
  transform: translateY(-1px);
}
.card-icon {
  width: 36px; height: 36px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; flex-shrink: 0;
}
.card-title { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.card-desc { font-size: 11px; color: var(--text-muted); margin-top: 2px; }

/* ── Chat Header ── */
.chat-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 20px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.header-left { display: flex; align-items: center; gap: 10px; }
.header-avatar {
  width: 32px; height: 32px; border-radius: 10px;
  background: linear-gradient(135deg, var(--primary), #818cf8);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.header-title { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.header-status {
  display: flex; align-items: center; gap: 5px;
  font-size: 11px; color: var(--text-muted); margin-top: 1px;
}
.status-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: #10b981; flex-shrink: 0;
}
.status-dot.thinking { background: var(--primary); animation: pulse 1s infinite; }
@keyframes pulse { 0%,100%{opacity:1;transform:scale(1)} 50%{opacity:0.5;transform:scale(0.8)} }

.new-btn {
  display: flex; align-items: center; gap: 5px;
  padding: 6px 12px; border-radius: var(--radius-full);
  border: 1px solid var(--border); background: var(--surface);
  color: var(--text-secondary); font-size: 12px; font-weight: 500;
  cursor: pointer; transition: all 0.15s;
}
.new-btn:hover { border-color: var(--primary); color: var(--primary); background: var(--primary-light); }

/* ── Chat Input Area ── */
.chat-input-area {
  background: var(--surface);
  border-top: 1px solid var(--border);
  flex-shrink: 0;
}
</style>
