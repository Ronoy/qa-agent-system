<template>
  <div class="quick-commands">
    <div class="cmds">
      <button
        v-for="cmd in commands"
        :key="cmd.text"
        class="cmd-btn"
        :disabled="isStreaming"
        @click="$emit('select', cmd.text)"
      >
        <span class="cmd-icon">{{ cmd.icon }}</span>
        <span>{{ cmd.text }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { useChatStore } from '@/stores/chat'

defineEmits<{ select: [text: string] }>()
const { isStreaming } = storeToRefs(useChatStore())

const commands = [
  { icon: '🌐', text: '搜索今日学习资讯' },
  { icon: '📊', text: '查询学情' },
  { icon: '📋', text: '查任务进度' },
  { icon: '🧮', text: '帮我解一道数学题' },
  { icon: '📖', text: '讲解一个知识点' },
  { icon: '✏️', text: '给我出几道练习题' },
  { icon: '📅', text: '制定本周学习计划' },
  { icon: '💡', text: '学习建议' },
]
</script>

<style scoped>
.quick-commands {
  padding: 8px 16px 4px;
  overflow-x: auto;
}
.quick-commands::-webkit-scrollbar { display: none; }

.cmds { display: flex; gap: 6px; }

.cmd-btn {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 12px;
  padding: 5px 11px;
  border-radius: var(--radius-full);
  border: 1.5px solid var(--border);
  background: var(--bg);
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.15s;
  white-space: nowrap;
  font-weight: 500;
}
.cmd-btn:hover:not(:disabled) {
  background: var(--primary-light);
  border-color: #a5b4fc;
  color: var(--primary);
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(79,70,229,0.12);
}
.cmd-btn:active:not(:disabled) { transform: translateY(0); }
.cmd-btn:disabled { opacity: 0.45; cursor: not-allowed; }
.cmd-icon { font-size: 13px; }
</style>
