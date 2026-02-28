export type MessageRole = 'user' | 'assistant' | 'system'

export interface Message {
  id: string
  role: MessageRole
  content: string
  createdAt?: string
  // 工具调用事件（仅前端展示用）
  toolCalls?: ToolCallEvent[]
}

export interface ToolCallEvent {
  toolName: string
  toolArgs?: Record<string, unknown>
  result?: string
  status: 'calling' | 'done'
}

export interface Conversation {
  id: string
  title: string
  createdAt: string
  updatedAt: string
  messages?: Message[]
}

export interface ChatStreamEvent {
  type: 'conversation_id' | 'text' | 'tool_call' | 'tool_result' | 'done' | 'error'
  content?: string
  tool_name?: string
  tool_args?: Record<string, unknown>
}
