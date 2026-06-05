import axios from 'axios'

/**
 * Shared Axios instance for all API calls.
 * Vite dev server proxies /api to the FastAPI backend.
 */
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
})

function formatError(error) {
  const detail = error.response?.data?.detail
  if (Array.isArray(detail)) {
    return detail.map((d) => d.msg || JSON.stringify(d)).join(', ')
  }
  return detail || error.response?.data?.message || error.message || 'An unexpected error occurred'
}

api.interceptors.response.use(
  (response) => response,
  (error) => Promise.reject(new Error(formatError(error)))
)

export const getStats = () => api.get('/api/emails/stats')
export const getCreators = () => api.get('/api/creators')
export const uploadCreatorsCSV = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/api/creators/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
export const getCampaigns = () => api.get('/api/campaigns')
export const getCampaignTemplates = () => api.get('/api/campaigns/templates')
export const createCampaign = (data) => api.post('/api/campaigns', data)
export const sendCampaign = (campaignId, category = null) =>
  api.post(`/api/campaigns/${campaignId}/send`, category ? { category } : {})

export const previewCampaign = (file, templateType, htmlTemplate = '') => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('template_type', templateType)
  if (htmlTemplate) formData.append('html_template', htmlTemplate)
  return api.post('/api/campaigns/preview', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const launchCampaign = ({ file, name, subject, templateType, htmlTemplate = '', categoryFilter = '' }) => {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('name', name)
  formData.append('subject', subject)
  formData.append('template_type', templateType)
  if (htmlTemplate) formData.append('html_template', htmlTemplate)
  if (categoryFilter) formData.append('category_filter', categoryFilter)
  return api.post('/api/campaigns/launch', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const getEmailLogs = (status = null) =>
  api.get('/api/emails/logs', { params: status ? { status } : {} })

export default api
