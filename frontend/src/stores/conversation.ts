import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Conversation } from '@/types'
import { conversationService } from '@/services/conversationService'

export const useConversationStore = defineStore('conversation', () => {
  const conversations = ref<Conversation[]>([])
  const loading = ref(false)

  async function fetchAll() {
    loading.value = true
    try {
      conversations.value = await conversationService.list()
    } finally {
      loading.value = false
    }
  }

  async function createNew(title?: string) {
    const conv = await conversationService.create(title)
    conversations.value.unshift(conv)
    return conv
  }

  async function remove(id: string) {
    await conversationService.remove(id)
    conversations.value = conversations.value.filter(c => c.id !== id)
  }

  function prependOrUpdate(conv: Conversation) {
    const idx = conversations.value.findIndex(c => c.id === conv.id)
    if (idx >= 0) {
      conversations.value[idx] = conv
    } else {
      conversations.value.unshift(conv)
    }
  }

  return { conversations, loading, fetchAll, createNew, remove, prependOrUpdate }
})
