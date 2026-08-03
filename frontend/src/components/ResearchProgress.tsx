import { useState, useEffect, useRef } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faChartLine, faTag, faNewspaper,
  faBrain, faCircleCheck, faGlobe,
  faSpinner, faCheck, faHourglassHalf, faRobot, faFilter
} from '@fortawesome/free-solid-svg-icons'

interface Props {
  query: string
}

interface Stage {
  id: string
  label: string
  description: string
  icon: any
  progressEnd: number
}

const STAGES: Stage[] = [
  { id: 'prepare', label: 'Mempersiapkan analisis', description: 'Menyiapkan parameter riset pasar...', icon: faSpinner, progressEnd: 6 },
  { id: 'understand', label: 'AI memahami ide bisnis Anda', description: 'Menganalisis input untuk memahami produk dan lokasi...', icon: faRobot, progressEnd: 12 },
  { id: 'queries', label: 'AI menghasilkan query riset', description: 'Membuat query khusus untuk setiap sumber data...', icon: faFilter, progressEnd: 16 },
  { id: 'search', label: 'Mengumpulkan data kompetitor', description: 'Mencari kompetitor dari Google Search & Maps...', icon: faGlobe, progressEnd: 30 },
  { id: 'trends', label: 'Menganalisis Google Trends', description: 'Menganalisis semua keyword relevan untuk tren pasar...', icon: faChartLine, progressEnd: 48 },
  { id: 'shopping', label: 'Menganalisis Google Shopping', description: 'Mengumpulkan data harga produk...', icon: faTag, progressEnd: 63 },
  { id: 'news', label: 'Mengumpulkan berita terkait', description: 'Mencari berita dan artikel terkini...', icon: faNewspaper, progressEnd: 73 },
  { id: 'dedup', label: 'Menormalisasi & membersihkan data', description: 'Mendeteksi dan menghapus duplikasi data...', icon: faFilter, progressEnd: 78 },
  { id: 'ai', label: 'AI menganalisis & menyusun laporan', description: 'Menganalisis data yang terkumpul...', icon: faBrain, progressEnd: 90 },
  { id: 'validating', label: 'Memvalidasi hasil', description: 'Memeriksa konsistensi dan kualitas data...', icon: faCircleCheck, progressEnd: 97 },
]

const SOURCES = [
  { id: 'search', label: 'Google Search', icon: faGlobe },
  { id: 'trends', label: 'Google Trends', icon: faChartLine },
  { id: 'shopping', label: 'Google Shopping', icon: faTag },
  { id: 'news', label: 'Tavily', icon: faNewspaper },
  { id: 'ai', label: 'AI Analysis', icon: faBrain },
]

type SourceStatus = 'waiting' | 'processing' | 'done'

export default function ResearchProgress({ query }: Props) {
  const [stageIndex, setStageIndex] = useState(0)
  const [progress, setProgress] = useState(2)
  const [sourceStatus, setSourceStatus] = useState<Record<string, SourceStatus>>(() => {
    const s: Record<string, SourceStatus> = {}
    for (const src of SOURCES) s[src.id] = 'waiting'
    return s
  })
  const startTime = useRef(Date.now())

  useEffect(() => {
    startTime.current = Date.now()
    setStageIndex(0)
    setProgress(2)

    const base = startTime.current
    const duration = 70000
    const initialSourceStatus: Record<string, SourceStatus> = {}
    for (const src of SOURCES) initialSourceStatus[src.id] = 'waiting'
    setSourceStatus(initialSourceStatus)

    const interval = setInterval(() => {
      const elapsed = Date.now() - base
      const pct = Math.min(97, (elapsed / duration) * 95)

      let idx = 0
      for (let i = STAGES.length - 1; i >= 0; i--) {
        if (pct >= STAGES[i].progressEnd - 2) { idx = i; break }
      }

      const newSourceStatus: Record<string, SourceStatus> = {}
      const stageMap: Record<string, string[]> = {
        'prepare': [], 'understand': [], 'queries': [], 'dedup': [],
        'search': ['search'],
        'trends': ['search', 'trends'],
        'shopping': ['search', 'trends', 'shopping'],
        'news': ['search', 'trends', 'shopping', 'news'],
        'ai': ['search', 'trends', 'shopping', 'news', 'ai'],
        'validating': ['search', 'trends', 'shopping', 'news', 'ai'],
      }
      const doneSources = stageMap[STAGES[idx].id] || []

      for (const src of SOURCES) {
        if (doneSources.includes(src.id)) {
          newSourceStatus[src.id] = 'done'
        } else if (src.id === STAGES[idx].id) {
          newSourceStatus[src.id] = 'processing'
        } else {
          newSourceStatus[src.id] = 'waiting'
        }
      }

      setProgress(pct)
      setStageIndex(idx)
      setSourceStatus(newSourceStatus)
    }, 200)

    return () => clearInterval(interval)
  }, [])

  const stage = STAGES[Math.min(stageIndex, STAGES.length - 1)]

  return (
    <div className="mx-auto mt-6 max-w-2xl px-4">
      <div className="text-center mb-6">
        <h2 className="text-lg font-bold text-gray-900 dark:text-white">Menganalisis Peluang Bisnis</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 truncate">"{query}"</p>
      </div>

      <div className="mb-6">
        <div className="h-3 bg-gray-200 dark:bg-gray-800 rounded-full overflow-hidden">
          <div className="h-full rounded-full bg-gradient-to-r from-violet-500 to-violet-400 transition-all duration-700 ease-out" style={{ width: `${progress}%` }} />
        </div>
        <div className="flex items-center justify-between mt-1.5">
          <span className="text-xs text-gray-500 dark:text-gray-400">{Math.round(progress)}%</span>
          <span className="text-xs font-medium text-violet-600 dark:text-violet-400">
            {progress < 97 ? 'Analisis sedang berjalan' : 'Menunggu hasil akhir...'}
          </span>
        </div>
      </div>

      <div className="rounded-xl border bg-white dark:bg-gray-900 shadow-sm p-4 mb-4">
        <div className="flex items-center gap-3">
          <span className="w-8 h-8 flex items-center justify-center rounded-lg bg-violet-100 dark:bg-violet-900/30 text-violet-600 dark:text-violet-400">
            <FontAwesomeIcon icon={stage.icon} className={progress < 97 ? 'animate-spin' : ''} />
          </span>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-gray-900 dark:text-white">{stage.label}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{stage.description}</p>
          </div>
        </div>
      </div>

      <div className="rounded-xl border bg-white dark:bg-gray-900 shadow-sm p-4">
        <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">Sumber Data</p>
        <div className="space-y-2">
          {SOURCES.map(src => {
            const status = sourceStatus[src.id] || 'waiting'
            return (
              <div key={src.id} className="flex items-center gap-3 text-sm">
                <span className={`w-5 h-5 flex items-center justify-center rounded-full text-[10px] ${
                  status === 'done' ? 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400' :
                  status === 'processing' ? 'bg-violet-100 dark:bg-violet-900/30 text-violet-600 dark:text-violet-400' :
                  'bg-gray-100 dark:bg-gray-800 text-gray-400 dark:text-gray-500'
                }`}>
                  {status === 'done' ? <FontAwesomeIcon icon={faCheck} /> :
                   status === 'processing' ? <FontAwesomeIcon icon={faSpinner} className="animate-spin" /> :
                   <FontAwesomeIcon icon={faHourglassHalf} />}
                </span>
                <span className={`font-medium ${
                  status === 'done' ? 'text-gray-900 dark:text-white' :
                  status === 'processing' ? 'text-gray-900 dark:text-white' :
                  'text-gray-400 dark:text-gray-500'
                }`}>{src.label}</span>
                <span className={`ml-auto text-[11px] ${
                  status === 'done' ? 'text-emerald-600 dark:text-emerald-400' :
                  status === 'processing' ? 'text-violet-600 dark:text-violet-400' :
                  'text-gray-400 dark:text-gray-500'
                }`}>
                  {status === 'done' ? 'Selesai' : status === 'processing' ? 'Diproses' : 'Menunggu'}
                </span>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
