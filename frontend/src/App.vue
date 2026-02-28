<template>
  <div class="app-layout">
    <Sidebar
      :conversations="conversations"
      :active-id="activeConvId"
      @new-chat="handleNewChat"
      @select-conv="handleSelectConv"
      @delete-conv="handleDeleteConv"
    />
    <ChatWindow />
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useChatStore } from '@/stores/chat'
import { useConversationStore } from '@/stores/conversation'
import { conversationService } from '@/services/conversationService'
import Sidebar from '@/components/sidebar/Sidebar.vue'
import ChatWindow from '@/components/chat/ChatWindow.vue'

const chatStore = useChatStore()
const convStore = useConversationStore()
const { conversations } = storeToRefs(convStore)
const { currentConversationId } = storeToRefs(chatStore)
const activeConvId = computed(() => currentConversationId.value)

onMounted(() => convStore.fetchAll())

function handleNewChat() { chatStore.clearMessages() }

async function handleSelectConv(id: string) {
  chatStore.clearMessages()
  const conv = await conversationService.get(id)
  chatStore.setConversationId(id)
  if (conv.messages) {
    chatStore.loadMessages(
      conv.messages.map(m => ({
        id: String(m.id ?? Math.random()),
        role: m.role as 'user' | 'assistant',
        content: m.content,
        createdAt: m.createdAt
      }))
    )
  }
}

async function handleDeleteConv(id: string) {
  await convStore.remove(id)
  if (currentConversationId.value === id) chatStore.clearMessages()
}
</script>

<style>
:root {
  --primary: #6366f1;
  --primary-light: #eef2ff;
  --primary-dark: #4f46e5;
  --bg: #f7f8fa;
  --surface: #ffffff;
  --border: #e5e7eb;
  --border-light: #f3f4f6;
  --text-primary: #111827;
  --text-secondary: #6b7280;
  --text-muted: #9ca3af;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md: 0 4px 16px rgba(0,0,0,0.08);
  --shadow-lg: 0 8px 32px rgba(0,0,0,0.10);
  --radius: 12px;
  --radius-sm: 8px;
  --radius-full: 9999px;
  --rail-width: 52px;
  --sidebar-width: 240px;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', 'Segoe UI', sans-serif;
  background: var(--bg);
  color: var(--text-primary);
  -webkit-font-smoothing: antialiased;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #e5e7eb; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #d1d5db; }
</style>

<style scoped>
.app-layout { display: flex; height: 100vh; overflow: hidden; background: var(--bg); }
</style>
