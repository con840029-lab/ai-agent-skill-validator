import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  me: () => api.get('/auth/me')
}

export const skillAPI = {
  upload: (formData) => {
    return api.post('/skills/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  list: (params) => api.get('/skills/', { params }),
  get: (id) => api.get(`/skills/${id}`),
  getReportJson: (id) => api.get(`/skills/${id}/report/json`),
  getReportHtml: (id) => api.get(`/skills/${id}/report/html`),
  getReportMarkdown: (id) => api.get(`/skills/${id}/report/markdown`),
  delete: (id) => api.delete(`/skills/${id}`)
}

export default api
