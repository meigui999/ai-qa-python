import request from './request'

export function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request({
    url: '/documents/upload',
    method: 'post',
    headers: { 'Content-Type': 'multipart/form-data' },
    data: formData
  })
}

export function getDocumentList() {
  return request({
    url: '/documents/list',
    method: 'get'
  })
}

export function deleteDocument(id) {
  return request({
    url: `/documents/${id}`,
    method: 'delete'
  })
}
