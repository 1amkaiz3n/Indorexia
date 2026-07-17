import { getVisitorId } from './visitor'

const BASE = '/api'

async function post(path: string, body: unknown) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

async function get(path: string, params?: Record<string, string>) {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  const res = await fetch(`${BASE}${path}${qs}`)
  if (!res.ok) {
    if (res.status === 404) throw new Error('Not found')
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Request failed')
  }
  return res.json()
}

async function del(path: string, params?: Record<string, string>) {
  const qs = params ? '?' + new URLSearchParams(params).toString() : ''
  const res = await fetch(`${BASE}${path}${qs}`, { method: 'DELETE' })
  return res.ok
}

async function patch(path: string, body: unknown) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error('Update failed')
  return res.json()
}

// ── API ──

export async function doResearch(query: string, location?: string) {
  return post('/research', { query, location, visitor_id: getVisitorId() })
}

export async function fetchHistory(params: {
  search?: string; verdict?: string; sort?: string
}) {
  return post('/research/history', { visitor_id: getVisitorId(), ...params })
}

export async function fetchReport(id: string) {
  return get(`/research/${id}`, { visitor_id: getVisitorId() })
}

export async function removeReport(id: string) {
  return del(`/research/${id}`, { visitor_id: getVisitorId() })
}

export async function clearHistory() {
  return del('/research', { visitor_id: getVisitorId() })
}

export async function updateReport(id: string, data: { title?: string; pinned?: boolean }) {
  return patch(`/research/${id}`, { visitor_id: getVisitorId(), ...data })
}

export async function duplicateReport(id: string) {
  return post(`/research/${id}/duplicate`, { visitor_id: getVisitorId() })
}
