// frontend/src/api/client.js
const BASE = import.meta.env.VITE_API_URL || ''

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, options)
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(JSON.stringify(err.detail) || `HTTP ${res.status}`)
  }
  return res.json()
}

export const submitApplication = (formData) =>
  request('/api/v1/kyc/submit', { method: 'POST', body: formData })  // FormData — no Content-Type header

export const getCase = (id) => request(`/api/v1/kyc/cases/${id}`)
export const listCases = (limit = 100) => request(`/api/v1/kyc/cases?limit=${limit}`)
export const getStats = () => request('/api/v1/kyc/stats')
export const overrideDecision = (payload) =>
  request('/api/v1/kyc/override', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
export const checkHealth = () => request('/health')