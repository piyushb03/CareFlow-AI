import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 90000,
  headers: { 'Content-Type': 'application/json' },
})

// Cases
export const createCase = (data = {}) => api.post('/api/cases', data)
export const listCases = (params = {}) => api.get('/api/cases', { params })
export const getCase = (caseId) => api.get(`/api/cases/${caseId}`)
export const startInterview = (caseId) => api.post(`/api/cases/${caseId}/start-interview`)
export const sendMessage = (caseId, content, coveredAreas = [], collectedFields = {}) =>
  api.post(`/api/cases/${caseId}/messages`, { content, covered_areas: coveredAreas, collected_fields: collectedFields })
export const processCase = (caseId) => api.post(`/api/cases/${caseId}/process`)
export const getConversation = (caseId) => api.get(`/api/cases/${caseId}/conversation`)
export const getEvidence = (caseId) => api.get(`/api/cases/${caseId}/evidence`)
export const getVerification = (caseId) => api.get(`/api/cases/${caseId}/verification`)
export const getTrajectory = (caseId) => api.get(`/api/cases/${caseId}/trajectory`)
export const getAgentRuns = (caseId) => api.get(`/api/cases/${caseId}/agent-runs`)
export const getAudit = (caseId) => api.get(`/api/cases/${caseId}/audit`)
export const approveCase = (caseId, data) => api.post(`/api/cases/${caseId}/approve`, data)
export const rejectCase = (caseId, data) => api.post(`/api/cases/${caseId}/reject`, data)
export const reviewCase = (caseId, data) => api.post(`/api/cases/${caseId}/review`, data)

// Evaluation
export const listEvalCases = () => api.get('/api/evaluation/cases')
export const getEvalResults = () => api.get('/api/evaluation/results')
export const runEvaluation = (mode = 'agent') => api.post('/api/evaluation/run', { mode })

export default api
