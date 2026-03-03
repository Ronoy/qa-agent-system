<template>
  <div class="sidebar">
    <!-- Brand -->
    <div class="sidebar-brand">
      <div class="brand-logo">
        <svg viewBox="0 0 24 24" fill="none" width="16" height="16">
          <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
            stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <span class="brand-name">智学助手</span>
    </div>

    <!-- New Chat -->
    <div class="sidebar-top">
      <button class="new-chat-btn" @click="$emit('newChat')">
        <svg viewBox="0 0 24 24" fill="none" width="14" height="14">
          <path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"/>
        </svg>
        新建对话
      </button>
    </div>

    <div class="sidebar-body">
      <!-- 功能 section -->
      <div class="section-group">
        <div class="section-label">功能</div>
        <div class="nav-items">
          <div v-for="item in navItems" :key="item.key"
            class="nav-item" :class="{ active: section === item.key }"
            @click="$emit('changeSection', item.key)">
            <span class="nav-icon" :style="{ background: item.bg }">
              <component :is="item.icon" :color="item.color" />
            </span>
            <span class="nav-text">{{ item.label }}</span>
          </div>
        </div>
      </div>

      <!-- 历史对话 section -->
      <div class="section-group">
        <div class="section-label">历史对话</div>
        <ConversationList
          :conversations="conversations"
          :active-id="activeId"
          @select="$emit('selectConv', $event)"
          @delete="$emit('deleteConv', $event)"
        />
      </div>
    </div>

    <!-- Bottom user -->
    <div class="sidebar-footer">
      <div class="user-row">
        <div class="user-avatar">张</div>
        <div class="user-info">
          <div class="user-name">张同学</div>
          <div class="user-role">高三 · 理科班</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineComponent, h } from 'vue'
import type { Conversation } from '@/types'
import ConversationList from './ConversationList.vue'

defineProps<{ conversations: Conversation[]; activeId: string | null; section: string }>()
defineEmits<{ newChat: []; selectConv: [id: string]; deleteConv: [id: string]; changeSection: [key: string] }>()

const makeIcon = (paths: Array<{ tag: string; attrs: Record<string, string> }>) =>
  defineComponent({
    props: { color: { type: String, default: '#6366f1' } },
    render(ctx: any) {
      return h('svg', { viewBox: '0 0 24 24', fill: 'none', width: 15, height: 15 },
        paths.map(p => h(p.tag, { ...p.attrs, stroke: ctx.color, 'stroke-width': '1.8', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }))
      )
    }
  })

const IconChart = makeIcon([
  { tag: 'path', attrs: { d: 'M18 20V10M12 20V4M6 20v-6' } }
])
const IconBook = makeIcon([
  { tag: 'path', attrs: { d: 'M4 19.5A2.5 2.5 0 016.5 17H20' } },
  { tag: 'path', attrs: { d: 'M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z' } }
])
const IconClipboard = makeIcon([
  { tag: 'path', attrs: { d: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2' } },
  { tag: 'rect', attrs: { x: '9', y: '3', width: '6', height: '4', rx: '1' } },
  { tag: 'path', attrs: { d: 'M9 12h6M9 16h4' } }
])
const IconReport = makeIcon([
  { tag: 'path', attrs: { d: 'M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z' } },
  { tag: 'path', attrs: { d: 'M14 2v6h6M8 13h8M8 17h5' } }
])

const navItems = [
  { key: 'analysis', label: '学情分析', icon: IconChart, bg: '#eef2ff', color: '#6366f1' },
  { key: 'knowledge', label: '知识库', icon: IconBook, bg: '#f0fdf4', color: '#16a34a' },
  { key: 'task', label: '任务中心', icon: IconClipboard, bg: '#fff7ed', color: '#ea580c' },
  { key: 'report', label: '学情报告', icon: IconReport, bg: '#fdf4ff', color: '#9333ea' },
]
</script>

<style scoped>
.sidebar {
  width: 240px;
  height: 100%;
  background: var(--surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 16px 16px 12px;
  border-bottom: 1px solid var(--border-light);
}
.brand-logo {
  width: 30px; height: 30px;
  border-radius: 9px;
  background: linear-gradient(135deg, var(--primary), #818cf8);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.brand-name {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.01em;
}

.sidebar-top { padding: 12px 12px 8px; }

.new-chat-btn {
  width: 100%;
  display: flex; align-items: center; justify-content: center; gap: 7px;
  padding: 9px 16px;
  border-radius: var(--radius-full);
  border: none;
  background: var(--primary);
  color: #fff;
  font-size: 13px; font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  box-shadow: 0 2px 8px rgba(99,102,241,0.3);
}
.new-chat-btn:hover { background: var(--primary-dark); box-shadow: 0 4px 12px rgba(99,102,241,0.4); }

.sidebar-body { flex: 1; overflow-y: auto; padding: 4px 8px 8px; }

.section-group { margin-bottom: 16px; }
.section-label {
  font-size: 10.5px; font-weight: 600;
  color: var(--text-muted);
  letter-spacing: 0.07em; text-transform: uppercase;
  padding: 8px 8px 5px;
}

.nav-items { display: flex; flex-direction: column; gap: 1px; }
.nav-item {
  display: flex; align-items: center; gap: 10px;
  padding: 7px 10px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 0.12s;
  color: var(--text-secondary);
  font-size: 13px;
}
.nav-item:hover, .nav-item.active { background: var(--bg); color: var(--text-primary); }

.nav-icon {
  width: 28px; height: 28px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.nav-text { font-weight: 500; }

.sidebar-footer {
  padding: 10px 12px 14px;
  border-top: 1px solid var(--border-light);
}
.user-row {
  display: flex; align-items: center; gap: 9px;
  padding: 6px 8px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 0.12s;
}
.user-row:hover { background: var(--bg); }
.user-avatar {
  width: 30px; height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), #818cf8);
  color: #fff;
  font-size: 12px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.user-name { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.user-role { font-size: 11px; color: var(--text-muted); margin-top: 1px; }
</style>
