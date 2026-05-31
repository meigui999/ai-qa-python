<template>
  <div>
    <div class="content-card">
      <div class="content-card-header">
        <span>对话历史</span>
        <div style="display:flex;gap:10px;align-items:center;">
          <div class="search-box">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input v-model="searchText" placeholder="搜索对话..." class="search-input" />
          </div>
          <button class="btn-batch-delete" :class="{ active: selectedIds.length > 0 }" :disabled="selectedIds.length === 0" @click="batchDelete">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
            {{ selectedIds.length > 0 ? `删除 (${selectedIds.length})` : '删除' }}
          </button>
        </div>
      </div>
      <div class="content-card-body" style="padding:0;">
        <div v-if="!tableLoading && historyList.length === 0" style="text-align:center;padding:48px 0;color:#94a3b8;font-size:14px;">
          暂无对话记录
        </div>
        <div v-else class="history-table" v-loading="tableLoading">
          <!-- 按文档分组显示 -->
          <template v-for="group in groupedHistory" :key="group.docName">
            <div class="group-header" @click="toggleGroup(group.docName)">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" :style="{ transform: collapsedGroups.has(group.docName) ? 'rotate(-90deg)' : 'rotate(0deg)', transition: 'transform 0.15s' }"><polyline points="6 9 12 15 18 9"/></svg>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" style="flex-shrink:0;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/></svg>
              <span class="group-name">{{ group.docName }}</span>
              <span class="group-count">{{ group.items.length }} 条对话</span>
              <span class="group-toggle">{{ collapsedGroups.has(group.docName) ? '展开' : '收起' }}</span>
            </div>
            <template v-if="!collapsedGroups.has(group.docName)">
              <div class="h-row h-row-header">
                <span class="h-col-check">
                  <input type="checkbox" :checked="isGroupAllSelected(group)" @change="toggleGroupSelect(group)" />
                </span>
                <span class="h-col-q">问题</span>
                <span class="h-col-time">时间</span>
              </div>
              <div v-for="row in group.items" :key="row.id"
                class="h-row" :class="{ selected: selectedIds.includes(row.id) }"
                @click="toggleExpand(row)">
                <span class="h-col-check" @click.stop>
                  <input type="checkbox" :checked="selectedIds.includes(row.id)" @change="toggleSelect(row.id)" />
                </span>
                <span class="h-col-q">{{ row.question }}</span>
                <span class="h-col-time">{{ row.createTime }}</span>
              </div>
              <!-- 展开详情 -->
              <div v-if="expandedId && group.items.some(r => r.id === expandedId)" class="h-expand">
                <template v-for="row in group.items" :key="'exp-'+row.id">
                  <template v-if="expandedId === row.id">
                    <div class="expand-section">
                      <div class="expand-label">问题</div>
                      <div class="expand-text q-text">{{ row.question }}</div>
                    </div>
                    <div class="expand-section">
                      <div class="expand-label">回答</div>
                      <div class="expand-text a-text">{{ row.answer }}</div>
                    </div>
                  </template>
                </template>
              </div>
            </template>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getChatHistory, deleteChatHistory } from '../api/chat'

const historyList = ref([])
const searchText = ref('')
const tableLoading = ref(false)
const expandedId = ref(null)
const selectedIds = ref([])
const collapsedGroups = ref(new Set())

const filteredHistory = computed(() => {
  if (!searchText.value) return historyList.value
  const kw = searchText.value.toLowerCase()
  return historyList.value.filter(i =>
    (i.question && i.question.toLowerCase().includes(kw)) ||
    (i.answer && i.answer.toLowerCase().includes(kw))
  )
})

// 按文档分组
const groupedHistory = computed(() => {
  const groups = new Map()
  for (const item of filteredHistory.value) {
    const name = item.documentName || '未关联文档'
    if (!groups.has(name)) groups.set(name, [])
    groups.get(name).push(item)
  }
  return Array.from(groups, ([docName, items]) => ({ docName, items }))
})

const fetchHistory = async () => {
  tableLoading.value = true
  try {
    const res = await getChatHistory()
    historyList.value = res.data || res || []
  } catch (e) { /* handled */ }
  finally { tableLoading.value = false }
}

const toggleExpand = (row) => {
  expandedId.value = expandedId.value === row.id ? null : row.id
}

const toggleSelect = (id) => {
  const idx = selectedIds.value.indexOf(id)
  if (idx >= 0) selectedIds.value.splice(idx, 1)
  else selectedIds.value.push(id)
}

const toggleGroupSelect = (group) => {
  const ids = group.items.map(i => i.id)
  const allSelected = ids.every(id => selectedIds.value.includes(id))
  if (allSelected) {
    selectedIds.value = selectedIds.value.filter(id => !ids.includes(id))
  } else {
    for (const id of ids) {
      if (!selectedIds.value.includes(id)) selectedIds.value.push(id)
    }
  }
}

const isGroupAllSelected = (group) => {
  return group.items.length > 0 && group.items.every(i => selectedIds.value.includes(i.id))
}

const toggleGroup = (docName) => {
  const s = new Set(collapsedGroups.value)
  if (s.has(docName)) s.delete(docName)
  else s.add(docName)
  collapsedGroups.value = s
}

const batchDelete = () => {
  ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.length} 条对话记录？`, '批量删除', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
  }).then(async () => {
    tableLoading.value = true
    let success = 0
    for (const id of selectedIds.value) {
      try { await deleteChatHistory(id); success++ } catch (e) {}
    }
    selectedIds.value = []; expandedId.value = null
    ElMessage.success(`已删除 ${success} 条记录`)
    fetchHistory()
  }).catch(() => {})
}

onMounted(() => { fetchHistory() })
</script>

<style scoped>
.search-box {
  display: flex; align-items: center; gap: 8px;
  background: #f1f5f9; border: 1px solid var(--border-normal);
  border-radius: 10px; padding: 7px 14px; width: 220px; transition: border-color 0.2s;
}
.search-box:focus-within { border-color: var(--accent); }
.search-input {
  border: none; outline: none; background: transparent;
  font-size: 13px; color: var(--text-primary); font-family: inherit; width: 100%;
}
.search-input::placeholder { color: var(--text-placeholder); }

.btn-batch-delete {
  display: flex; align-items: center; gap: 6px;
  padding: 7px 14px; border: 1px solid var(--border-normal); border-radius: 8px;
  background: #f8fafc; color: #c4b8a7; font-size: 12px; font-weight: 600;
  cursor: not-allowed; font-family: inherit; transition: all 0.15s;
}
.btn-batch-delete.active {
  border-color: #f0c8b0; background: #fef9f7; color: #c15f3c; cursor: pointer;
}
.btn-batch-delete.active:hover { background: #fdf0ea; border-color: #e8b8a0; }

.history-table :deep(.el-loading-mask) { background: rgba(255,255,255,0.6); backdrop-filter: blur(2px); }

/* 分组标题 */
.group-header {
  display: flex; align-items: center; gap: 10px;
  padding: 12px 20px; background: #faf7f3; border-bottom: 1px solid var(--border-subtle);
  cursor: pointer; user-select: none; transition: background 0.1s;
}
.group-header:hover { background: #f5f1eb; }
.group-name { font-size: 14px; font-weight: 700; color: var(--text-primary); }
.group-count { font-size: 12px; color: var(--text-muted); }
.group-toggle { font-size: 11px; color: var(--accent); font-weight: 500; margin-left: auto; }

/* 行 */
.h-row {
  display: flex; align-items: center; padding: 12px 20px; gap: 16px;
  cursor: pointer; transition: background 0.1s;
}
.h-row + .h-row { border-top: 1px solid var(--border-subtle); }
.h-row:hover { background: #fafbfc; }
.h-row.selected { background: #fdf5ef; }
.h-row-header {
  background: #f8fafc; font-size: 12px; font-weight: 600;
  color: var(--text-muted); letter-spacing: 0.3px; cursor: default;
}
.h-row-header:hover { background: #f8fafc; }

.h-col-check { width: 36px; flex-shrink: 0; display: flex; align-items: center; }
.h-col-check input[type="checkbox"] {
  width: 15px; height: 15px; accent-color: var(--accent); cursor: pointer;
}
.h-col-q { flex: 1; font-size: 13px; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; min-width: 0; }
.h-col-time { width: 170px; font-size: 13px; color: var(--text-muted); flex-shrink: 0; }

/* 展开 */
.h-expand {
  padding: 18px 24px 18px 56px;
  background: #fafbfc; border-top: 1px solid var(--border-subtle);
  display: flex; flex-direction: column; gap: 14px;
}
.expand-section { display: flex; gap: 10px; }
.expand-label { font-size: 12px; font-weight: 600; color: var(--text-muted); white-space: nowrap; padding-top: 2px; }
.expand-text { font-size: 14px; color: var(--text-primary); line-height: 1.6; }
.q-text { color: var(--accent); }
.a-text { background: #fff; padding: 12px 16px; border-radius: 8px; border: 1px solid var(--border-normal); white-space: pre-wrap; }

@media (max-width: 768px) {
  .h-col-time { display: none; }
  .search-box { width: 140px; }
}
</style>
