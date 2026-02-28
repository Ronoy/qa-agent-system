<template>
  <div class="icon-rail">
    <div class="rail-logo">
      <svg viewBox="0 0 24 24" fill="none" width="22" height="22">
        <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
          stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </div>

    <nav class="rail-nav">
      <button
        v-for="item in navItems" :key="item.key"
        class="rail-btn"
        :class="{ active: activeSection === item.key }"
        :title="item.label"
        @click="$emit('change', item.key)"
      >
        <component :is="item.icon" />
      </button>
    </nav>

    <div class="rail-bottom">
      <div class="rail-avatar">张</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { defineComponent, h } from 'vue'

defineProps<{ activeSection: string }>()
defineEmits<{ change: [key: string] }>()

const IconChat = defineComponent({ render: () => h('svg', { viewBox:'0 0 24 24', fill:'none', width:18, height:18 }, [
  h('path', { d:'M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z', stroke:'currentColor', 'stroke-width':'1.8', 'stroke-linecap':'round', 'stroke-linejoin':'round' })
]) })

const IconHistory = defineComponent({ render: () => h('svg', { viewBox:'0 0 24 24', fill:'none', width:18, height:18 }, [
  h('circle', { cx:'12', cy:'12', r:'10', stroke:'currentColor', 'stroke-width':'1.8' }),
  h('path', { d:'M12 6v6l4 2', stroke:'currentColor', 'stroke-width':'1.8', 'stroke-linecap':'round' })
]) })

const IconStar = defineComponent({ render: () => h('svg', { viewBox:'0 0 24 24', fill:'none', width:18, height:18 }, [
  h('path', { d:'M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z', stroke:'currentColor', 'stroke-width':'1.8', 'stroke-linecap':'round', 'stroke-linejoin':'round' })
]) })

const IconSettings = defineComponent({ render: () => h('svg', { viewBox:'0 0 24 24', fill:'none', width:18, height:18 }, [
  h('circle', { cx:'12', cy:'12', r:'3', stroke:'currentColor', 'stroke-width':'1.8' }),
  h('path', { d:'M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-4 0v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 010-4h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 012.83-2.83l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 014 0v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 010 4h-.09a1.65 1.65 0 00-1.51 1z', stroke:'currentColor', 'stroke-width':'1.8' })
]) })

const navItems = [
  { key: 'chat', label: '对话', icon: IconChat },
  { key: 'history', label: '历史', icon: IconHistory },
  { key: 'favorites', label: '收藏', icon: IconStar },
  { key: 'settings', label: '设置', icon: IconSettings },
]
</script>

<style scoped>
.icon-rail {
  width: var(--rail-width);
  height: 100%;
  background: var(--surface);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 0;
  flex-shrink: 0;
  z-index: 10;
}

.rail-logo {
  width: 34px; height: 34px;
  border-radius: 10px;
  background: linear-gradient(135deg, var(--primary), #818cf8);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 20px;
  flex-shrink: 0;
}

.rail-nav {
  display: flex; flex-direction: column;
  align-items: center; gap: 4px;
  flex: 1;
}

.rail-btn {
  width: 36px; height: 36px;
  border-radius: var(--radius-sm);
  border: none; background: none;
  color: var(--text-muted);
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.15s;
  position: relative;
}
.rail-btn:hover { background: var(--bg); color: var(--text-secondary); }
.rail-btn.active {
  background: var(--primary-light);
  color: var(--primary);
}
.rail-btn.active::before {
  content: '';
  position: absolute;
  left: -1px; top: 50%;
  transform: translateY(-50%);
  width: 3px; height: 20px;
  background: var(--primary);
  border-radius: 0 3px 3px 0;
}

.rail-bottom { margin-top: auto; }
.rail-avatar {
  width: 30px; height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), #818cf8);
  color: #fff;
  font-size: 12px; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
}
</style>
