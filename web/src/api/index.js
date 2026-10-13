import axios from 'axios'

const http = axios.create({
  baseURL: '',
  timeout: 30000,
  // 304 也视为成功响应（用于 ETag 缓存命中），不在拦截器里报错
  validateStatus: (status) => (status >= 200 && status < 300) || status === 304,
})

// 统一错误提示
http.interceptors.response.use(
  (res) => res,
  (err) => {
    const detail = err?.response?.data?.detail || err.message || '请求失败'
    return Promise.reject(new Error(detail))
  }
)

// 对路径按段编码，保留斜杠分隔符（避免 %2F 导致后端路由匹配问题）
function encodePath(path) {
  return path
    .split('/')
    .map((seg) => encodeURIComponent(seg))
    .join('/')
}

// ===== md 文件内容的 ETag 缓存（内存级，命中 304 直接用缓存） =====
const fileCache = new Map() // path -> { content, etag }

export const api = {
  // 获取目录树（懒加载）
  getTree(path = '') {
    const p = path ? `/${encodePath(path)}` : ''
    return http.get(`/api/tree${p}`).then((r) => r.data)
  },
  // 读取文件（带 ETag 缓存：云端未变则用本地缓存，秒开）
  async getFile(path) {
    const cached = fileCache.get(path)
    const headers = cached?.etag ? { 'If-None-Match': cached.etag } : {}
    const res = await http.get(`/api/file/${encodePath(path)}`, { headers })
    if (res.status === 304 && cached) {
      // 云端未变，直接用本地缓存
      return { path, content: cached.content, fromCache: true }
    }
    // 200：新内容，更新缓存
    const content = res.data.content
    const etag = res.headers['etag'] || ''
    if (etag) fileCache.set(path, { content, etag })
    return { path, content, fromCache: false }
  },
  // 清除某文件的缓存（编辑保存后调用，确保下次读最新）
  clearFileCache(path) {
    fileCache.delete(path)
  },
  // 保存文件
  async saveFile(path, content) {
    const res = await http.put(`/api/file/${encodePath(path)}`, { content })
    // 保存后清除本地缓存，强制下次重新拉取
    fileCache.delete(path)
    return res.data
  },
  // 创建文件（在 parentPath 目录下）
  createFile(parentPath, name, content = '') {
    return http
      .post(`/api/file/${encodePath(parentPath)}`, { name, content })
      .then((r) => r.data)
  },
  // 创建文件夹（在 parentPath 目录下）
  createDir(parentPath, name) {
    return http
      .post(`/api/tree/${encodePath(parentPath)}`, { name })
      .then((r) => r.data)
  },
  // 全文搜索
  search(q) {
    return http.get('/api/search', { params: { q } }).then((r) => r.data)
  },
  // 二进制文件（PDF/图片）的访问 URL
  getRawFileUrl(path) {
    return `/api/file/raw/${encodePath(path)}`
  },
  // 读取某文件的阅读进度
  getProgress(path) {
    return http.get(`/api/progress/${encodePath(path)}`).then((r) => r.data)
  },
  // 保存某文件的阅读进度
  saveProgress(path, entry) {
    return http.put(`/api/progress/${encodePath(path)}`, { entry }).then((r) => r.data)
  },
  // 进度接口的 URL（用于 sendBeacon）
  getProgressUrl(path) {
    return `/api/progress/${encodePath(path)}`
  },
}
