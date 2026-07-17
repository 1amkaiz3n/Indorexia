const KEY = 'indorexia_last_report'
const META_KEY = 'indorexia_last_meta'

export interface ReportMeta {
  id: string
  query: string
  location: string
  verdict: string
  score: number
  timestamp: string
}

export function saveLastReport(report: unknown, meta: ReportMeta) {
  try {
    localStorage.setItem(KEY, JSON.stringify(report))
    localStorage.setItem(META_KEY, JSON.stringify(meta))
  } catch {
    // storage full — ignore
  }
}

export function getLastReport(): unknown | null {
  try {
    const raw = localStorage.getItem(KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function getLastMeta(): ReportMeta | null {
  try {
    const raw = localStorage.getItem(META_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function clearLastReport() {
  localStorage.removeItem(KEY)
  localStorage.removeItem(META_KEY)
}
