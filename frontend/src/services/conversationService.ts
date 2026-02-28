import type { Conversation } from '@/types'

const BASE = '/api/conversations'

export const conversationService = {
  async list(): Promise<Conversation[]> {
    const res = await fetch(BASE)
    if (!res.ok) throw new Error('获取对话列表失败')
    return res.json()
  },

  async create(title?: string): Promise<Conversation> {
    const res = await fetch(BASE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: title || '新对话' })
    })
    if (!res.ok) throw new Error('创建对话失败')
    return res.json()
  },

  async get(id: string): Promise<Conversation> {
    const res = await fetch(`${BASE}/${id}`)
    if (!res.ok) throw new Error('获取对话详情失败')
    return res.json()
  },

  async remove(id: string): Promise<void> {
    const res = await fetch(`${BASE}/${id}`, { method: 'DELETE' })
    if (!res.ok) throw new Error('删除对话失败')
  }
}
