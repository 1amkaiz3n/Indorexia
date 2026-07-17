import { useEffect, useState } from 'react'
import {
  fetchHistory, removeReport, clearHistory, updateReport, duplicateReport,
} from '../lib/api'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { 
  faTrash, faPen, faCopy, 
  faThumbtack, faMapMarkerAlt, faFolderOpen,
  faCheck, faTriangleExclamation, faTimes
} from '@fortawesome/free-solid-svg-icons'

interface HistoryItem {
  id: string
  title: string
  query: string
  location: string
  verdict: string
  score: number
  pinned: boolean
  created_at: string
}

interface Props {
  onOpenReport: (id: string) => void
}

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime()
  const days = Math.floor(diff / 86400000)
  if (days === 0) return 'Hari ini'
  if (days === 1) return 'Kemarin'
  if (days < 7) return `${days} hari lalu`
  return new Date(dateStr).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })
}

function verdictBadge(v: string): string {
  if (v.includes('Layak')) return 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
  if (v.includes('Pertimbangan')) return 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400'
  return 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400'
}

export default function HistoryPage({ onOpenReport }: Props) {
  const [items, setItems] = useState<HistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [verdict, setVerdict] = useState('')
  const [sort, setSort] = useState('newest')
  const [selected, setSelected] = useState<string[]>([])

  const load = async () => {
    setLoading(true)
    try {
      const res = await fetchHistory({ search, verdict, sort })
      setItems(res.data || [])
    } catch { setItems([]) }
    setLoading(false)
  }

  useEffect(() => { load() }, [search, verdict, sort])

  const handleDelete = async (id: string) => {
    await removeReport(id)
    load()
  }

  const handleClearAll = async () => {
    if (!confirm('Hapus seluruh history?')) return
    await clearHistory()
    load()
  }

  const handlePin = async (id: string, pinned: boolean) => {
    await updateReport(id, { pinned: !pinned })
    load()
  }

  const handleRename = async (id: string) => {
    const item = items.find(i => i.id === id)
    if (!item) return
    const title = prompt('Nama baru:', item.title)
    if (title && title !== item.title) {
      await updateReport(id, { title })
      load()
    }
  }

  const handleDuplicate = async (id: string) => {
    await duplicateReport(id)
    load()
  }

  const toggleSelect = (id: string) => {
    setSelected(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id])
  }

  const handleBulkDelete = async () => {
    if (!confirm(`Hapus ${selected.length} report?`)) return
    for (const id of selected) await removeReport(id)
    setSelected([])
    load()
  }

  return (
    <div className="w-full px-4 pb-12">
      <div className="max-w-7xl mx-auto space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">History</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">{items.length} report tersimpan</p>
          </div>
          <div className="flex gap-2">
            {selected.length > 0 && (
              <button onClick={handleBulkDelete} className="text-sm px-3 py-1.5 rounded-lg bg-rose-100 dark:bg-rose-900/30 text-rose-700 dark:text-rose-400 hover:bg-rose-200 dark:hover:bg-rose-900/50 transition-colors cursor-pointer">
                Hapus {selected.length} terpilih
              </button>
            )}
            {items.length > 0 && (
              <button onClick={handleClearAll} className="text-sm px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors cursor-pointer">
                Hapus Semua
              </button>
            )}
          </div>
        </div>

        {/* Search & Filters */}
        <div className="flex flex-wrap gap-3 items-center">
          <input
            type="text"
            placeholder="Cari berdasarkan keyword atau lokasi..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="flex-1 min-w-[200px] rounded-xl border bg-white dark:bg-gray-900 px-4 py-2 text-sm text-gray-900 dark:text-white placeholder:text-gray-400 outline-none ring-violet-500/20 focus:ring-2"
          />
          <select value={verdict} onChange={e => setVerdict(e.target.value)}
            className="rounded-xl border bg-white dark:bg-gray-900 px-3 py-2 text-sm text-gray-900 dark:text-white outline-none cursor-pointer hover:border-gray-400 transition-colors">
            <option value="">Semua Status</option>
            <option value="Layak">Layak</option>
            <option value="Pertimbangan">Pertimbangan</option>
            <option value="Tidak">Tidak Disarankan</option>
          </select>
          <select value={sort} onChange={e => setSort(e.target.value)}
            className="rounded-xl border bg-white dark:bg-gray-900 px-3 py-2 text-sm text-gray-900 dark:text-white outline-none cursor-pointer hover:border-gray-400 transition-colors">
            <option value="newest">Terbaru</option>
            <option value="oldest">Terlama</option>
            <option value="score">Skor Tertinggi</option>
          </select>
        </div>

        {/* List */}
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1,2,3,4,5,6].map(i => <div key={i} className="h-40 animate-pulse rounded-2xl bg-gray-200 dark:bg-gray-800" />)}
          </div>
        ) : items.length === 0 ? (
          <div className="text-center py-20">
            <FontAwesomeIcon icon={faFolderOpen} className="text-5xl text-gray-300 dark:text-gray-700 mb-4" />
            <p className="text-gray-500 dark:text-gray-400">Belum ada history riset</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {items.map(item => (
              <div key={item.id} className={`group relative rounded-2xl border bg-white dark:bg-gray-900 shadow-sm p-5 transition-all duration-300 hover:shadow-md hover:border-violet-300 dark:hover:border-violet-700 ${item.pinned ? 'ring-2 ring-violet-300 dark:ring-violet-700' : ''}`}>
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <input type="checkbox" checked={selected.includes(item.id)} onChange={() => toggleSelect(item.id)} className="rounded accent-violet-600 shrink-0 cursor-pointer" />
                    <span className={`text-[10px] font-semibold px-2.5 py-0.5 rounded-full flex items-center gap-1.5 shrink-0 ${verdictBadge(item.verdict)}`}>
                      {item.verdict && (
                        <FontAwesomeIcon 
                          icon={item.verdict.includes('Layak') ? faCheck : item.verdict.includes('Pertimbangan') ? faTriangleExclamation : faTimes} 
                          className="text-[10px]" 
                        />
                      )}
                      {item.verdict ? item.verdict.replace(/^[✅⚠️❌]\s*/, '') : '—'}
                    </span>
                  </div>
                  <div className="flex gap-1 shrink-0">
                    <button onClick={() => handlePin(item.id, item.pinned)} className={`cursor-pointer text-xs px-2.5 py-1.5 rounded-lg transition-colors ${item.pinned ? 'text-violet-600 bg-violet-100 dark:bg-violet-900/30' : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'}`} title={item.pinned ? 'Unpin' : 'Pin'}>
                      <FontAwesomeIcon icon={faThumbtack} className={item.pinned ? 'rotate-45 text-violet-600' : 'text-gray-400'} />
                    </button>
                    <button onClick={() => handleRename(item.id)} className="cursor-pointer text-xs px-2.5 py-1.5 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800" title="Ubah Nama">
                      <FontAwesomeIcon icon={faPen} />
                    </button>
                    <button onClick={() => handleDuplicate(item.id)} className="cursor-pointer text-xs px-2.5 py-1.5 rounded-lg text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800" title="Duplikat">
                      <FontAwesomeIcon icon={faCopy} />
                    </button>
                    <button onClick={() => handleDelete(item.id)} className="cursor-pointer text-xs px-2.5 py-1.5 rounded-lg text-gray-400 hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/20" title="Hapus">
                      <FontAwesomeIcon icon={faTrash} />
                    </button>
                  </div>
                </div>

                <button onClick={() => onOpenReport(item.id)} className="text-left w-full cursor-pointer focus:outline-none">
                  <p className="text-sm font-semibold text-gray-900 dark:text-white truncate group-hover:text-violet-600 dark:group-hover:text-violet-400 transition-colors">{item.title || item.query}</p>
                  {item.location && (
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 flex items-center gap-1.5">
                      <FontAwesomeIcon icon={faMapMarkerAlt} className="text-gray-400" />
                      {item.location}
                    </p>
                  )}
                  <div className="flex items-center gap-3 mt-3 text-xs text-gray-500 dark:text-gray-400">
                    <span>Skor: <strong className="text-gray-900 dark:text-white">{item.score}</strong></span>
                    <span>{timeAgo(item.created_at)}</span>
                  </div>
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
