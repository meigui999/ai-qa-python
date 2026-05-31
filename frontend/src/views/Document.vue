<template>
  <div>
    <div class="content-card">
      <div class="content-card-header">
        文档管理
      </div>
      <div class="content-card-body">
        <el-upload
          class="upload-area"
          drag
          action="/api/documents/upload"
          :headers="uploadHeaders"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          :before-upload="beforeUpload"
          accept=".pdf,.txt"
        >
          <div style="padding: 12px 0; text-align: center;">
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="1.5" stroke-linecap="round" style="margin-bottom:8px;">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
            </svg>
            <div style="font-size:14px;color:#475569;">拖拽文件到此处或 <em style="color:#4f46e5;font-style:normal;font-weight:600;">点击上传</em></div>
            <div style="font-size:12px;color:#94a3b8;margin-top:4px;">仅支持 PDF / TXT，单文件不超过 50MB</div>
          </div>
        </el-upload>

        <div style="margin-top:20px;">
          <div v-if="documentList.length === 0" style="text-align:center;padding:40px 0;color:#94a3b8;font-size:14px;">
            暂无文档，请上传
          </div>
          <div v-else class="doc-table">
            <div class="doc-row doc-row-header">
              <span class="doc-col-name">文件名</span>
              <span class="doc-col-time">上传时间</span>
              <span class="doc-col-action">操作</span>
            </div>
            <div v-for="doc in documentList" :key="doc.id" class="doc-row">
              <span class="doc-col-name">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#4f46e5" stroke-width="2" stroke-linecap="round" style="flex-shrink:0;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/></svg>
                {{ doc.fileName }}
              </span>
              <span class="doc-col-time">{{ doc.createTime }}</span>
              <span class="doc-col-action">
                <button class="btn-delete" @click="handleDelete(doc)">删除</button>
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getDocumentList, deleteDocument } from '../api/document'

const documentList = ref([])

const uploadHeaders = computed(() => ({
  Authorization: `Bearer ${localStorage.getItem('token')}`
}))

const fetchDocuments = async () => {
  try {
    const res = await getDocumentList()
    documentList.value = res.data || res || []
  } catch (e) { /* handled */ }
}

const beforeUpload = (file) => {
  const isValid = file.type === 'application/pdf' || file.type === 'text/plain'
  if (!isValid) { ElMessage.error('仅支持 PDF 和 TXT 格式'); return false }
  if (file.size / 1024 / 1024 > 50) { ElMessage.error('文件不超过 50MB'); return false }
  return true
}

const handleUploadSuccess = () => { ElMessage.success('上传成功'); fetchDocuments() }
const handleUploadError = () => { ElMessage.error('上传失败') }

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定删除「${row.fileName}」？`, '提示', {
    confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
  }).then(async () => {
    await deleteDocument(row.id)
    ElMessage.success('删除成功')
    fetchDocuments()
  }).catch(() => {})
}

onMounted(() => { fetchDocuments() })
</script>

<style scoped>
.upload-area :deep(.el-upload) { width: 100%; }
.upload-area :deep(.el-upload-dragger) {
  width: 100%;
  border: 2px dashed #cbd5e1;
  border-radius: 12px;
  background: #f8fafc;
  transition: all 0.2s;
}
.upload-area :deep(.el-upload-dragger:hover) {
  border-color: var(--accent);
  background: var(--accent-bg);
}

.doc-table {
  border: 1px solid var(--border-normal);
  border-radius: 10px;
  overflow: hidden;
}

.doc-row {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  gap: 16px;
}

.doc-row + .doc-row { border-top: 1px solid var(--border-subtle); }

.doc-row-header {
  background: #f8fafc;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.doc-col-name {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--text-primary);
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.doc-col-time {
  width: 180px;
  font-size: 13px;
  color: var(--text-muted);
  flex-shrink: 0;
}

.doc-col-action {
  width: 60px;
  flex-shrink: 0;
  text-align: center;
}

.btn-delete {
  padding: 4px 12px;
  border: 1px solid var(--border-normal);
  border-radius: 6px;
  background: #fff;
  color: var(--text-muted);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s;
  font-family: inherit;
}

.btn-delete:hover {
  border-color: #d97555;
  color: #d97555;
  background: #fef2f2;
}

@media (max-width: 768px) {
  .doc-col-time { display: none; }
}
</style>
