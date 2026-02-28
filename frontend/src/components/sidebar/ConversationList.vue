<template>
  <div class="conversation-list">
    <TransitionGroup name="conv">
      <div
        v-for="conv in conversations" :key="conv.id"
        class="conv-item" :class="{ active: activeId === conv.id }"
        @click="$emit('select', conv.id)"
      >
        <div class="conv-icon">
          <svg viewBox="0 0 24 24" fill="none" width="13" height="13">
            <path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"
              stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <span class="conv-title">{{ conv.title }}</span>
        <button class="del-btn" @click.stop="$emit('delete', conv.id)">
          <svg viewBox="0 0 24 24" fill="none" width="11" height="11">
            <path d="M18 6L6 18M6 6l12 12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </button>
      </div>
    </TransitionGroup>
    <div v-if="conversations.length === 0" class="empty">暂无历史对话</div>
  </div>
</template>

<script setup lang="ts">
import type { Conversation } from '@/types'
defineProps<{ conversations: Conversation[]; activeId: string | null }>()
defineEmits<{ select: [id: string]; delete: [id: string] }>()
</script>

<style scoped>
.conversation-list { display: flex; flex-direction: column; gap: 1px; }

.conv-item {
  display: flex; align-items: center; gap: 8px;
  padding: 7px 10px; border-radius: var(--radius-sm);
  cursor: pointer; transition: background 0.12s;
  color: var(--text-secondary); font-size: 13px;
}
.conv-item:hover { background: var(--bg); }
.conv-item.active { background: var(--primary-light); color: var(--primary); }

.conv-icon { flex-shrink: 0; opacity: 0.5; }
.conv-item.active .conv-icon { opacity: 1; }

.conv-title {
  flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  font-weight: 500;
}

.del-btn {
  opacity: 0; border: none; background: none; cursor: pointer;
  color: var(--text-muted); padding: 2px; border-radius: 4px;
  display: flex; align-items: center; transition: all 0.12s;
}
.conv-item:hover .del-btn { opacity: 1; }
.del-btn:hover { color: #ef4444; background: #fee2e2; }

.empty { font-size: 12px; color: var(--text-muted); text-align: center; padding: 16px 0; }

.conv-enter-active, .conv-leave-active { transition: all 0.18s ease; }
.conv-enter-from, .conv-leave-to { opacity: 0; transform: translateX(-6px); }
</style>
