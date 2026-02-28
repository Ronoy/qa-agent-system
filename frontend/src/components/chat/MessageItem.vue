<template>
  <div class="message-item" :class="message.role">
    <div class="avatar">
      <template v-if="message.role === 'user'">我</template>
      <template v-else>
        <svg viewBox="0 0 24 24" fill="none" width="16" height="16">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
            stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </template>
    </div>

    <div class="bubble-wrap">

      <!-- 工具调用过程面板 -->
      <div v-if="message.toolCalls?.length" class="tool-panel">
        <div class="tool-panel-header">
          <svg viewBox="0 0 24 24" fill="none" width="13" height="13">
            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.8"/>
            <path d="M12 8v4l3 3" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/>
          </svg>
          <span>思考过程</span>
        </div>
        <div class="tool-steps">
          <div
            v-for="(tc, i) in message.toolCalls"
            :key="i"
            class="tool-step"
            :class="tc.status"
          >
            <!-- 状态图标 -->
            <div class="step-icon">
              <!-- calling: 旋转圆圈 -->
              <svg v-if="tc.status === 'calling'" class="spin" viewBox="0 0 24 24" fill="none" width="14" height="14">
                <circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="2.5"
                  stroke-dasharray="28 56" stroke-linecap="round"/>
              </svg>
              <!-- done: 对勾 -->
              <svg v-else viewBox="0 0 24 24" fill="none" width="14" height="14">
                <circle cx="12" cy="12" r="9" fill="currentColor" opacity="0.15"/>
                <path d="M8 12l3 3 5-5" stroke="currentColor" stroke-width="2"
                  stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="step-body">
              <span class="step-label">{{ toolLabel(tc.toolName) }}</span>
              <span class="step-status">{{ tc.status === 'calling' ? '查询中...' : '已完成' }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 消息气泡 -->
      <div class="bubble" :class="{ 'is-user': message.role === 'user' }">
        <!-- 思考中（工具调用阶段，内容还没来） -->
        <div v-if="showThinking" class="thinking-state">
          <span class="thinking-text">正在生成回答</span>
          <span class="thinking-dots"><span></span><span></span><span></span></span>
        </div>
        <!-- 正常内容 -->
        <template v-else>
          <div class="md-content" v-html="renderedContent"></div>
          <span v-if="isLastAssistant && isStreaming && message.content" class="cursor"></span>
        </template>
      </div>

      <div class="meta">{{ timeStr }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useChatStore } from '@/stores/chat'
import type { Message } from '@/types'

const props = defineProps<{ message: Message; isLastAssistant?: boolean }>()
const { isStreaming } = storeToRefs(useChatStore())

// 工具调用还在进行中 或 工具调用完成但文字还没来
const showThinking = computed(() =>
  props.isLastAssistant &&
  isStreaming.value &&
  !props.message.content
)

const TOOL_LABELS: Record<string, string> = {
  get_attendance_records: '查询考勤记录',
  get_learning_status: '查询学情数据',
  get_task_progress: '查询任务进度',
  get_knowledge_mastery: '查询知识点掌握度',
  get_learning_recommendations: '生成学习建议'
}
function toolLabel(name: string) { return TOOL_LABELS[name] ?? name }

const timeStr = computed(() => {
  const d = props.message.createdAt ? new Date(props.message.createdAt) : new Date()
  return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
})

const renderedContent = computed(() => {
  let text = props.message.content
  text = text.replace(/```(\w*)\n?([\s\S]*?)```/g, (_, lang, code) =>
    `<pre><code class="lang-${lang}">${escHtml(code.trim())}</code></pre>`)
  text = text.replace(/`([^`]+)`/g, '<code>$1</code>')
  text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  text = text.replace(/\*(.+?)\*/g, '<em>$1</em>')
  text = text.replace(/^### (.+)$/gm, '<h4>$1</h4>')
  text = text.replace(/^## (.+)$/gm, '<h3>$1</h3>')
  text = text.replace(/^# (.+)$/gm, '<h3>$1</h3>')
  text = text.replace(/^[-*] (.+)$/gm, '<li>$1</li>')
  text = text.replace(/(<li>.*<\/li>\n?)+/g, s => `<ul>${s}</ul>`)
  text = text.replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
  text = text.replace(/\n/g, '<br>')
  text = text.replace(/<br>(<\/?(?:ul|ol|li|h[1-6]|pre))/g, '$1')
  text = text.replace(/(<\/(?:ul|ol|li|h[1-6]|pre)>)<br>/g, '$1')
  return text
})

function escHtml(s: string) {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
}
</script>

<style scoped>
.message-item {
  display: flex; gap: 10px;
  margin-bottom: 20px; align-items: flex-start;
  animation: fadeUp 0.2s ease;
}
.message-item.user { flex-direction: row-reverse; }

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

.avatar {
  width: 34px; height: 34px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700; flex-shrink: 0;
  background: var(--primary-light); color: var(--primary);
}
.message-item.user .avatar {
  background: linear-gradient(135deg, var(--primary), #818cf8); color: #fff;
}

.bubble-wrap { max-width: 72%; display: flex; flex-direction: column; gap: 6px; }
.message-item.user .bubble-wrap { align-items: flex-end; }

/* ── 工具调用面板 ── */
.tool-panel {
  background: #f8faff;
  border: 1px solid #e0e7ff;
  border-radius: 12px;
  overflow: hidden;
  font-size: 12px;
}
.tool-panel-header {
  display: flex; align-items: center; gap: 5px;
  padding: 7px 12px;
  background: #eef2ff;
  color: var(--primary);
  font-weight: 600;
  border-bottom: 1px solid #e0e7ff;
}
.tool-steps { padding: 6px 8px; display: flex; flex-direction: column; gap: 2px; }

.tool-step {
  display: flex; align-items: center; gap: 8px;
  padding: 5px 6px; border-radius: 8px;
  transition: background 0.2s;
}
.tool-step.calling { background: #fffbeb; }
.tool-step.done { background: transparent; }

.step-icon {
  width: 20px; height: 20px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.tool-step.calling .step-icon { color: #f59e0b; }
.tool-step.done .step-icon { color: #10b981; }

.step-body { display: flex; align-items: center; gap: 8px; flex: 1; }
.step-label { color: var(--text-primary); font-weight: 500; }
.step-status { color: var(--text-muted); margin-left: auto; font-size: 11px; }
.tool-step.calling .step-status { color: #f59e0b; }
.tool-step.done .step-status { color: #10b981; }

/* 旋转动画 */
.spin { animation: spin 0.9s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ── 气泡 ── */
.bubble {
  padding: 11px 15px;
  border-radius: 16px; border-bottom-left-radius: 4px;
  font-size: 14px; line-height: 1.7; word-break: break-word;
  background: var(--surface); color: var(--text-primary);
  box-shadow: var(--shadow-sm);
}
.bubble.is-user {
  background: linear-gradient(135deg, var(--primary), #6366f1);
  color: #fff;
  border-bottom-left-radius: 16px; border-bottom-right-radius: 4px;
  box-shadow: 0 2px 12px rgba(79,70,229,0.3);
}

/* 思考中状态 */
.thinking-state {
  display: flex; align-items: center; gap: 8px;
  color: var(--text-muted); font-size: 13px;
}
.thinking-dots { display: flex; gap: 4px; }
.thinking-dots span {
  width: 5px; height: 5px; border-radius: 50%;
  background: var(--text-muted);
  animation: bounce 1.2s infinite;
}
.thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); }
  30% { transform: translateY(-4px); }
}

/* 打字光标 */
.cursor {
  display: inline-block; width: 2px; height: 14px;
  background: var(--primary); margin-left: 2px;
  vertical-align: middle; animation: blink 0.8s infinite;
}
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }

.meta { font-size: 11px; color: var(--text-muted); padding: 0 4px; }

/* Markdown */
.md-content :deep(h3), .md-content :deep(h4) {
  font-size: 14px; font-weight: 700; margin: 8px 0 4px;
}
.md-content :deep(strong) { font-weight: 700; }
.md-content :deep(em) { font-style: italic; }
.md-content :deep(code) {
  font-family: 'SF Mono', 'Fira Code', monospace; font-size: 12px;
  background: rgba(79,70,229,0.08); color: var(--primary);
  padding: 1px 5px; border-radius: 4px;
}
.bubble.is-user .md-content :deep(code) { background: rgba(255,255,255,0.2); color: #fff; }
.md-content :deep(pre) {
  background: #1e1b4b; border-radius: var(--radius-sm);
  padding: 12px 14px; overflow-x: auto; margin: 8px 0;
}
.md-content :deep(pre code) { background: none; color: #e2e8f0; font-size: 12px; padding: 0; }
.md-content :deep(ul), .md-content :deep(ol) { padding-left: 18px; margin: 4px 0; }
.md-content :deep(li) { margin: 2px 0; }
</style>
