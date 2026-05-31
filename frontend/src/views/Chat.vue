<template>
  <div class="chat-page">
    <aside class="chat-sidebar">
      <div class="chat-sidebar-header">文档列表</div>
      <div class="doc-list">
        <div v-for="doc in documentList" :key="doc.id"
          class="doc-item" :class="{ active: selectedDocId === doc.id }"
          @click="selectDoc(doc.id)">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          <span class="doc-name">{{ doc.fileName }}</span>
        </div>
        <div v-if="documentList.length === 0" class="doc-empty">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#b0a590" stroke-width="1" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/></svg>
          <span>暂无文档</span>
          <span style="font-size:11px;color:#c4b8a7;">请先在文档管理页上传</span>
        </div>
      </div>
    </aside>

    <div class="chat-main">
      <div class="chat-messages" ref="messageContainer">
        <!-- 未选文档 -->
        <div class="chat-welcome" v-if="!selectedDocId">
          <div class="welcome-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
          </div>
          <h3>AI 智能问答</h3>
          <p>在左侧选择一个文档，开始对话</p>
        </div>

        <!-- 已选文档但无消息 -->
        <div class="chat-welcome" v-else-if="messages.length === 0">
          <div class="welcome-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/></svg>
          </div>
          <h3>{{ currentDocName }}</h3>
          <p>输入你的问题，基于此文档进行问答</p>
        </div>

        <div v-for="(msg, index) in messages" :key="index">
          <div v-if="msg.role === 'user'" class="msg-row user-row">
            <div class="msg-bubble user-bubble">{{ msg.content }}</div>
          </div>
          <div v-else class="msg-row ai-row">
            <div class="ai-avatar">AI</div>
            <div v-if="!msg.content && loading" class="msg-bubble ai-bubble thinking-bubble">
              <span class="dot"></span><span class="dot d2"></span><span class="dot d3"></span>
            </div>
            <div v-else class="msg-bubble ai-bubble" v-html="formatMessage(msg.content)"></div>
          </div>
        </div>
      </div>

      <div class="chat-input-area">
        <div class="input-box">
          <input ref="inputRef" v-model="inputQuestion" class="input-field"
            :placeholder="selectedDocId ? '输入你的问题，Enter 发送...' : '请先在左侧选择文档'"
            :disabled="!selectedDocId || loading"
            @keyup.enter="sendMessage" />
          <button class="send-btn" :class="{ on: inputQuestion.trim() && selectedDocId && !loading }"
            :disabled="!inputQuestion.trim() || !selectedDocId || loading" @click="sendMessage">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
          </button>
        </div>
        <div class="input-tip" v-if="selectedDocId && !loading">当前文档：{{ currentDocName }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onActivated, nextTick, inject } from 'vue'
import { getDocumentList } from '../api/document'
import { streamChat } from '../api/chat'

const newChatTrigger = inject('newChatTrigger', null)

const documentList = ref([])
const selectedDocId = ref(null)
const messages = ref([])
const inputQuestion = ref('')
const loading = ref(false)
const messageContainer = ref(null)
const inputRef = ref(null)
const docMessages = ref({})
let currentEventSource = null

const currentDocName = computed(() => {
  if (!selectedDocId.value) return ''
  const doc = documentList.value.find(d => d.id === selectedDocId.value)
  return doc ? doc.fileName : '(文档已删除)'
})

const scrollToBottom = () => {
  nextTick(() => {
    if (messageContainer.value) messageContainer.value.scrollTop = messageContainer.value.scrollHeight
  })
}

const formatMessage = (text) => {
  if (!text) return ''
  // 转义 HTML 防 XSS，再换行转 <br>
  const escaped = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
  return escaped.replace(/\n/g, '<br>')
}

const clearAll = () => {
  if (currentEventSource) { currentEventSource.close(); currentEventSource = null }
  loading.value = false; messages.value = []; selectedDocId.value = null; inputQuestion.value = ''
  docMessages.value = {}
}

const selectDoc = (docId) => {
  if (selectedDocId.value === docId) return
  // 保存当前文档对话
  if (selectedDocId.value && messages.value.length > 0) {
    docMessages.value[selectedDocId.value] = [...messages.value]
  }
  // 切换
  selectedDocId.value = docId
  messages.value = docMessages.value[docId] || []
  inputQuestion.value = ''
  nextTick(() => { inputRef.value?.focus(); scrollToBottom() })
}

const fetchDocuments = async () => {
  try {
    const res = await getDocumentList()
    documentList.value = res.data || res || []
    // 如果当前选中的文档已被删除，清除状态
    if (selectedDocId.value && !documentList.value.find(d => d.id === selectedDocId.value)) {
      messages.value = []
      selectedDocId.value = null
    }
  } catch (e) {}
}

const sendMessage = () => {
  const q = inputQuestion.value.trim()
  if (!q || !selectedDocId.value) return

  // 构建对话历史（最近几轮问答，用于多轮上下文）
  const chatHistory = []
  for (let i = 0; i < messages.value.length; i += 2) {
    const user = messages.value[i]
    const ai = messages.value[i + 1]
    if (user && user.role === 'user' && ai && ai.role === 'ai' && ai.content) {
      chatHistory.push({ user: user.content, ai: ai.content })
    }
  }

  messages.value.push({ role: 'user', content: q })
  inputQuestion.value = ''; loading.value = true; scrollToBottom()
  let aiContent = ''; messages.value.push({ role: 'ai', content: '' })
  const docId = selectedDocId.value
  currentEventSource = streamChat(docId, q, chatHistory,
    (d) => { aiContent += d; messages.value[messages.value.length - 1].content = aiContent; scrollToBottom() },
    () => {
      loading.value = false; currentEventSource = null
      if (docId && messages.value.length > 0) docMessages.value[docId] = [...messages.value]
    },
    () => {
      loading.value = false; currentEventSource = null
      if (!aiContent) messages.value[messages.value.length - 1].content = '抱歉，AI 服务暂时不可用，请稍后重试。'
      if (docId && messages.value.length > 0) docMessages.value[docId] = [...messages.value]
    }
  )
}

onMounted(() => { fetchDocuments() })
onActivated(() => { fetchDocuments(); nextTick(() => scrollToBottom()) })

watch(() => newChatTrigger?.value, () => {
  if (newChatTrigger?.value > 0) clearAll()
})
</script>

<style scoped>
.chat-page { height: calc(100vh - 48px - 48px); display: flex; margin: -24px -28px; }

.chat-sidebar {
  width: 215px; background: var(--bg-sidebar); border-right: 1px solid var(--border-subtle);
  display: flex; flex-direction: column; flex-shrink: 0;
}
.chat-sidebar-header { padding: 16px 16px 12px; font-size: 13px; font-weight: 700; color: var(--text-secondary); }
.doc-list { flex: 1; overflow-y: auto; padding: 0 8px 8px; }
.doc-item {
  display: flex; align-items: center; gap: 8px; padding: 8px 12px;
  border-radius: 8px; cursor: pointer; font-size: 13px; color: var(--text-secondary); transition: all 0.12s;
}
.doc-item:hover { background: var(--bg-hover); }
.doc-item.active { background: #fff; color: var(--text-primary); font-weight: 600; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
.doc-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.doc-empty { padding: 24px 16px; text-align: center; font-size: 13px; color: var(--text-muted); display:flex;flex-direction:column;align-items:center;gap:6px; }

.chat-main { flex: 1; display: flex; flex-direction: column; background: #faf8f5; min-width: 0; }
.chat-messages { flex: 1; overflow-y: auto; padding: 32px 18% 0; }

.chat-welcome { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; gap: 10px; text-align: center; }
.welcome-icon { width: 56px; height: 56px; background: #f5ede5; border-radius: 16px; display: flex; align-items: center; justify-content: center; color: var(--accent); }
.chat-welcome h3 { font-size: 18px; font-weight: 700; color: var(--text-primary); max-width: 300px; overflow:hidden;text-overflow:ellipsis;white-space:nowrap; }
.chat-welcome p { font-size: 14px; color: var(--text-muted); }

.msg-row { display: flex; margin-bottom: 26px; max-width: 90%; }
.user-row { margin-left: auto; justify-content: flex-end; }
.ai-row { gap: 10px; }

.ai-avatar {
  width: 28px; height: 28px; background: var(--accent); border-radius: 8px;
  display: flex; align-items: center; justify-content: center; color: #fff;
  font-size: 10px; font-weight: 700; flex-shrink: 0;
}
.msg-bubble { padding: 11px 16px; border-radius: 14px; font-size: 14px; line-height: 1.6; word-break: break-word; }
.user-bubble { background: #ede4d9; color: var(--text-primary); border-bottom-right-radius: 4px; }
.ai-bubble { color: var(--text-primary); border-bottom-left-radius: 4px; }

.thinking-bubble { display: flex; align-items: center; gap: 4px; padding: 13px 20px; }
.dot { width: 5px; height: 5px; background: #c4b8a7; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out; }
.dot.d2 { animation-delay: 0.2s; }
.dot.d3 { animation-delay: 0.4s; }
@keyframes bounce { 0%,80%,100% { opacity: 0.15; transform: scale(0.7); } 40% { opacity: 1; transform: scale(1); } }

.chat-input-area { padding: 14px 18% 22px; }
.input-box {
  display: flex; align-items: center; gap: 8px;
  background: #fff; border: 1px solid var(--border-normal); border-radius: 14px;
  padding: 5px 5px 5px 16px; transition: all 0.2s;
}
.input-box:focus-within { border-color: var(--accent); box-shadow: 0 0 0 3px rgba(193,95,60,0.06); }
.input-field {
  flex: 1; border: none; outline: none; background: transparent;
  font-size: 14px; color: var(--text-primary); font-family: inherit; padding: 9px 0;
}
.input-field::placeholder { color: var(--text-muted); }
.send-btn {
  width: 34px; height: 34px; border-radius: 10px; border: none;
  background: #e8e0d5; color: #b0a590; cursor: pointer;
  display: flex; align-items: center; justify-content: center; transition: all 0.2s; flex-shrink: 0;
}
.send-btn.on { background: var(--accent); color: #fff; }
.send-btn.on:hover { background: var(--accent-light); }
.input-tip { text-align: center; font-size: 12px; color: var(--text-muted); margin-top: 6px; }

@media (max-width: 900px) {
  .chat-messages { padding: 20px 16px; }
  .chat-input-area { padding: 12px 16px 20px; }
  .chat-sidebar { display: none; }
}
</style>
