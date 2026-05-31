<template>
  <div class="home-container">
    <header class="home-header">
      <div class="logo">
        <div class="logo-icon">AI</div>
        AI 智能问答
      </div>
    </header>
    <div class="home-body">
      <aside class="home-aside">
        <button class="new-chat-btn" @click="newChat">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          新建对话
        </button>
        <nav class="sidebar-nav">
          <div class="sidebar-label">功能</div>
          <div class="nav-item" :class="{ active: activeMenu === '/chat' }" @click="goTo('/chat')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            智能问答
          </div>
          <div class="nav-item" :class="{ active: activeMenu === '/document' }" @click="goTo('/document')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
            文档管理
          </div>
          <div class="nav-item" :class="{ active: activeMenu === '/history' }" @click="goTo('/history')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            对话历史
          </div>
        </nav>
        <div class="sidebar-footer">
          <div class="sidebar-user">{{ username.charAt(0).toUpperCase() }}</div>
          <span class="sidebar-username">{{ username }}</span>
          <button class="sidebar-logout" @click="handleLogout">退出</button>
        </div>
      </aside>
      <main class="home-main">
        <router-view v-slot="{ Component }">
          <keep-alive include="Chat">
            <component :is="Component" />
          </keep-alive>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, provide } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessageBox } from 'element-plus'

const router = useRouter(); const route = useRoute()
const username = localStorage.getItem('username') || '用户'
const activeMenu = computed(() => route.path)
const goTo = (path) => { router.push(path) }

const newChatCount = ref(0)
provide('newChatTrigger', newChatCount)

const newChat = () => {
  newChatCount.value++
  router.push('/chat')
}

const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
  }).then(() => {
    localStorage.removeItem('token'); localStorage.removeItem('username'); router.push('/login')
  }).catch(() => {})
}
</script>
