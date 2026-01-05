/** Centralized API client for backend communication */
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001/api'

// Log the API URL for debugging (only in development)
if (import.meta.env.DEV) {
  console.log('API Base URL:', API_BASE_URL)
}

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add response interceptor for better error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status
    // Log 4xx errors (client errors) at warn level - these are expected validation errors
    // Log 5xx errors (server errors) at error level - these are unexpected system errors
    if (status >= 400 && status < 500) {
      // Client errors (validation, not found, etc.) - expected, log at debug level
      if (import.meta.env.DEV) {
        console.warn('API Client Error:', {
          message: error.message,
          url: error.config?.url,
          status: status,
          detail: error.response?.data?.detail,
        })
      }
    } else {
      // Server errors or network errors - unexpected, log at error level
      console.error('API Server Error:', {
        message: error.message,
        url: error.config?.url,
        status: status,
        data: error.response?.data,
      })
    }
    return Promise.reject(error)
  }
)

export const apiClient = {
  analyze: (repoUrl: string, depth: number = 3, passphrase: string) =>
    api.post('/analyze', { repo_url: repoUrl, depth, passphrase }),

  getStatus: (taskId: string) =>
    api.get(`/status/${taskId}`),

  getTree: (repoId: string) =>
    api.get(`/tree/${repoId}`),

  search: (query: string, repoId?: string) =>
    api.get('/search', { params: { q: query, repo_id: repoId } }),

  askQuestion: (repoId: string, question: string, passphrase: string) =>
    api.post('/qa', { repo_id: repoId, question, passphrase }),

  browse: (repoId: string, path: string = '') =>
    api.get(`/browse/${repoId}`, { params: { path } }),

  listCachedRepos: () =>
    api.get('/cache'),
}

export default apiClient

