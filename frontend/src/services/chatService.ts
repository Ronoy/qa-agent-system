import type { ChatStreamEvent } from '@/types'
import { useChatStore } from '@/stores/chat'

export async function sendMessage(
  message: string,
  conversationId: string | null
): Promise<void> {
  const chatStore = useChatStore()

  const res = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, conversation_id: conversationId })
  })

  if (!res.ok || !res.body) {
    throw new Error('请求失败')
  }

  chatStore.startAssistantMessage()

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      const raw = line.slice(6).trim()
      if (!raw) continue

      try {
        const event: ChatStreamEvent = JSON.parse(raw)
        handleEvent(event, chatStore)
      } catch {
        // ignore parse errors
      }
    }
  }

  chatStore.finishStreaming()
}

function handleEvent(event: ChatStreamEvent, chatStore: ReturnType<typeof useChatStore>) {
  switch (event.type) {
    case 'conversation_id':
      if (event.content) chatStore.setConversationId(event.content)
      break
    case 'text':
      if (event.content) chatStore.appendStreamText(event.content)
      break
    case 'tool_call':
      chatStore.addToolCall(event.tool_name ?? '', event.tool_args)
      break
    case 'tool_result':
      chatStore.completeToolCall(event.tool_name ?? '')
      break
    case 'done':
      chatStore.finishStreaming()
      break
  }
}
