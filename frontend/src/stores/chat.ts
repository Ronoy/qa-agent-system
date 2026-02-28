import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Message, ToolCallEvent } from '@/types'
const uuidv4 = () => crypto.randomUUID()

export const useChatStore = defineStore('chat', () => {
  const messages = ref<Message[]>([])
  const isStreaming = ref(false)
  const currentConversationId = ref<string | null>(null)
  const streamingContent = ref('')
  const pendingToolCalls = ref<ToolCallEvent[]>([])

  function setConversationId(id: string) {
    currentConversationId.value = id
  }

  function loadMessages(msgs: Message[]) {
    messages.value = msgs
  }

  function addUserMessage(content: string) {
    messages.value.push({
      id: uuidv4(),
      role: 'user',
      content,
      createdAt: new Date().toISOString()
    })
  }

  function startAssistantMessage() {
    isStreaming.value = true
    streamingContent.value = ''
    pendingToolCalls.value = []
    messages.value.push({
      id: uuidv4(),
      role: 'assistant',
      content: '',
      toolCalls: [],
      createdAt: new Date().toISOString()
    })
  }

  function appendStreamText(text: string) {
    streamingContent.value += text
    const last = messages.value[messages.value.length - 1]
    if (last && last.role === 'assistant') {
      last.content = streamingContent.value
    }
  }

  function addToolCall(toolName: string, toolArgs?: Record<string, unknown>) {
    const tc: ToolCallEvent = { toolName, toolArgs, status: 'calling' }
    pendingToolCalls.value.push(tc)
    const last = messages.value[messages.value.length - 1]
    if (last && last.role === 'assistant') {
      last.toolCalls = [...(last.toolCalls || []), tc]
    }
  }

  function completeToolCall(toolName: string) {
    const last = messages.value[messages.value.length - 1]
    if (!last?.toolCalls) return
    // 找最后一个同名且还在 calling 状态的工具调用，标记为 done
    const tc = [...last.toolCalls].reverse().find(t => t.toolName === toolName && t.status === 'calling')
    if (tc) tc.status = 'done'
  }

  function finishStreaming() {
    isStreaming.value = false
    pendingToolCalls.value = []
  }

  function clearMessages() {
    messages.value = []
    streamingContent.value = ''
    currentConversationId.value = null
  }

  return {
    messages, isStreaming, currentConversationId,
    streamingContent, pendingToolCalls,
    setConversationId, loadMessages, addUserMessage,
    startAssistantMessage, appendStreamText, addToolCall,
    completeToolCall, finishStreaming, clearMessages
  }
})
