import { useState, useEffect, useCallback } from 'react'
import type { ResearchReport } from './types'
import { doResearch, fetchReport } from './lib/api'
import { saveLastReport, getLastReport, getLastMeta } from './lib/storage'
import ResearchForm from './components/ResearchForm'
import ReportView from './components/ReportView'
import Navbar from './components/Navbar'
import HistoryPage from './components/HistoryPage'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faTriangleExclamation, faMagnifyingGlass } from '@fortawesome/free-solid-svg-icons'

function App() {
  const [page, setPage] = useState('research')
  const [report, setReport] = useState<ResearchReport | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const [, setReportId] = useState<string | null>(null)

  // Recover last report on mount
  useEffect(() => {
    const meta = getLastMeta()
    if (meta) {
      setReportId(meta.id)
      setQuery(meta.query)
      const saved = getLastReport()
      if (saved) {
        setReport(saved as ResearchReport)
      }
    }
  }, [])

  const handleResearch = useCallback(async (q: string, loc?: string) => {
    setLoading(true)
    setError(null)
    setReport(null)
    setReportId(null)
    setQuery(q)
    setPage('research')
    try {
      const res = await doResearch(q, loc)
      const data = res.report as ResearchReport
      const id = res.id as string
      setReport(data)
      setReportId(id)
      saveLastReport(data, {
        id,
        query: q,
        location: '',
        verdict: data.decision?.verdict_label || '',
        score: data.business_score?.overall || 0,
        timestamp: new Date().toISOString(),
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Terjadi kesalahan')
    } finally {
      setLoading(false)
    }
  }, [])

  const handleOpenFromHistory = useCallback(async (id: string) => {
    setLoading(true)
    setError(null)
    setPage('research')
    try {
      const data = await fetchReport(id)
      const r = data.report as ResearchReport
      setReport(r)
      setReportId(id)
      setQuery(data.query || '')
      saveLastReport(r, {
        id,
        query: data.query || '',
        location: data.location || '',
        verdict: r.decision?.verdict_label || '',
        score: r.business_score?.overall || 0,
        timestamp: data.created_at || new Date().toISOString(),
      })
    } catch (err) {
      setError('Gagal membuka report: Report tidak ditemukan')
      setReport(null)
    } finally {
      setLoading(false)
    }
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950 text-gray-900 dark:text-gray-100">
      <Navbar page={page} onNavigate={p => { setPage(p); if (p !== 'research') { setError(null) } }} />

      <main className="w-full py-6">
        {page === 'history' ? (
          <HistoryPage onOpenReport={handleOpenFromHistory} />
        ) : (
          <>
            <div className="mx-auto max-w-6xl px-6">
              <ResearchForm onSubmit={handleResearch} loading={loading} query={query} />
            </div>

            {loading && (
              <div className="mx-auto mt-8 max-w-6xl px-6 space-y-6">
                <div className="grid grid-cols-5 gap-3">
                  {[1,2,3,4,5].map(i => <div key={i} className="h-20 animate-pulse rounded-xl bg-gray-200 dark:bg-gray-800" />)}
                </div>
                <div className="h-32 animate-pulse rounded-xl bg-gray-200 dark:bg-gray-800" />
                <div className="grid grid-cols-3 gap-5">
                  {[1,2,3].map(i => <div key={i} className="h-64 animate-pulse rounded-xl bg-gray-200 dark:bg-gray-800" />)}
                </div>
                <div className="flex items-center justify-center gap-3 text-sm text-gray-500 dark:text-gray-400 py-4">
                  <div className="w-5 h-5 animate-spin rounded-full border-2 border-gray-300 dark:border-gray-600 border-t-violet-500" />
                  Mengumpulkan & menganalisis data pasar...
                </div>
              </div>
            )}

            {error && (
              <div className="mx-auto mt-8 max-w-xl px-6">
                <div className="rounded-2xl border border-red-200 dark:border-red-900/40 bg-red-50 dark:bg-red-950/20 p-6 text-center">
                  <FontAwesomeIcon icon={faTriangleExclamation} className="text-3xl text-red-500 mb-2" />
                  <p className="text-sm text-red-600 dark:text-red-400 mb-3">{error}</p>
                  <button onClick={() => handleResearch(query)} className="rounded-lg border border-red-200 dark:border-red-900/40 px-4 py-2 text-xs font-medium text-red-600 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-950/30 transition-all cursor-pointer">
                    Coba Lagi
                  </button>
                </div>
              </div>
            )}

            {report && !loading && (
              <div className="mt-8">
                <ReportView report={report} />
              </div>
            )}

            {!report && !loading && !error && (
              <div className="mx-auto mt-24 max-w-md text-center px-6">
                <div className="mx-auto mb-6 w-16 h-16 flex items-center justify-center rounded-2xl bg-violet-100 dark:bg-violet-900/30 text-violet-500">
                  <FontAwesomeIcon icon={faMagnifyingGlass} className="text-2xl" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1.5">Belum ada riset</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Masukkan ide bisnis di atas. Data akan dikumpulkan dari Google Trends, Google Maps, Google Shopping, dan berita terkini.
                </p>
              </div>
            )}
          </>
        )}
      </main>

      <footer className="border-t py-5 text-center text-xs text-gray-400 dark:text-gray-600">
        Indorexia — UMKM Research Tool
      </footer>
    </div>
  )
}

export default App
