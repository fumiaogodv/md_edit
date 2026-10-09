import axios from 'axios'

const http = axios.create({
  baseURL: '',
  timeout: 30000,
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

export const api = {
  // 获取目录树（懒加载）
  getTree(path = '') {
    const p = path ? `/${encodePath(path)}` : ''
    return http.get(`/api/tree${p}`).then((r) => r.data)
  },
  // 读取文件
  getFile(path) {
    return http.get(`/api/file/${encodePath(path)}`).then((r) => r.data)
  },
  // 保存文件
  saveFile(path, content) {
    return http.put(`/api/file/${encodePath(path)}`, { content }).then((r) => r.data)
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
