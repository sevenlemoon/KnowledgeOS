import http from './http'

export const authApi = {
  register: (data) => http.post('/auth/register', data),
  login: (data) => http.post('/auth/login', data),
}

export const userApi = {
  profile: () => http.get('/user/profile'),
}

export const knowledgeApi = {
  list: (params) => http.get('/knowledge/list', { params }),
  detail: (id) => http.get(`/knowledge/detail/${id}`),
  publish: (data) => http.post('/knowledge/add', data),
  comment: (data) => http.post('/knowledge/comment', data),
  interact: (data) => http.post('/knowledge/interact', data),
  delete: (id) => http.delete(`/knowledge/${id}`),
}

export const pointsApi = {
  records: (params) => http.get('/points/records', { params }),
  ranking: (params) => http.get('/points/ranking', { params }),
}

export const adminApi = {
  pendingKnowledge: () => http.get('/admin/knowledge/pending'),
  auditKnowledge: (data) => http.post('/admin/knowledge/audit', data),
  getConfig: () => http.get('/admin/points/config'),
  updateConfig: (data) => http.post('/admin/points/config', data),
  auditHistory: (params) => http.get('/admin/audit/history', { params }),
}

export const growthApi = {
  checkin: () => http.post('/growth/checkin'),
  checkinStatus: () => http.get('/growth/checkin/status'),
  badges: () => http.get('/growth/badges'),
  skillTree: () => http.get('/growth/skill-tree'),
  aiCoach: () => http.get('/growth/ai-coach'),
  knowledgeHealth: (id) => http.get(`/growth/knowledge-health/${id}`),
  stats: () => http.get('/growth/stats'),
}

export const externalApi = {
  articles: (params) => http.get('/external/articles', { params }),
  tags: () => http.get('/external/tags'),
}
