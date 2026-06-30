import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (response) => {
    const res = response.data
    // 统一响应格式: {code, message, data}
    if (res.code !== undefined) {
      if (res.code === 200) {
        return res.data
      }
      ElMessage.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message))
    }
    // 兼容旧格式（直接返回数据）
    return res
  },
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      if (location.pathname !== '/login') {
        location.href = '/login'
      }
      return Promise.reject(error)
    }
    const message = error.response?.data?.detail || '请求失败，请稍后重试'
    ElMessage.error(message)
    return Promise.reject(error)
  },
)

export default http
