import { useState, type FormEvent } from 'react'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSearch, faArrowRight, faSpinner, faLightbulb, faMapMarkerAlt } from '@fortawesome/free-solid-svg-icons'

interface Props {
  onSubmit: (query: string, location?: string) => void
  loading: boolean
  query?: string
}

const examples = [
  'saya mau buka toko baju di bandung',
  'ide bisnis kuliner di jogja',
  'jualan online skincare untuk remaja',
  'buka kafe di jakarta selatan',
]

export default function ResearchForm({ onSubmit, loading, query: initialQuery }: Props) {
  const [input, setInput] = useState(initialQuery || '')
  const [location, setLocation] = useState('')

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    const biz = input.trim()
    const loc = location.trim()
    if (biz && !loading) onSubmit(biz, loc || undefined)
  }

  return (
    <div className="relative overflow-hidden rounded-2xl border bg-gradient-to-br from-white to-violet-50 dark:from-gray-900 dark:to-violet-950/20 p-6 shadow-sm mb-6">
      <div className="relative">
        <div className="inline-flex items-center gap-2 bg-white dark:bg-gray-800 border rounded-full px-3.5 py-1 text-xs text-gray-500 dark:text-gray-400 mb-3">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          Riset Pasar UMKM — AI dari Google Trends, Maps, Shopping & Tavily
        </div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Cari Ide Bisnis</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1 mb-5">
          Masukkan ide bisnis kamu, sistem akan mengumpulkan data pasar dari berbagai sumber.
        </p>

        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <FontAwesomeIcon icon={faSearch} className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Cth: toko baju"
              className="w-full rounded-xl border bg-white dark:bg-gray-800 py-3 pl-10 pr-4 text-sm text-gray-900 dark:text-white placeholder:text-gray-400 outline-none ring-violet-500/20 focus:ring-2 transition-all"
              disabled={loading}
            />
          </div>

          <div className="relative sm:w-56">
            <FontAwesomeIcon icon={faMapMarkerAlt} className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <input
              type="text"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              placeholder="Kota (opsional)"
              className="w-full rounded-xl border bg-white dark:bg-gray-800 py-3 pl-10 pr-4 text-sm text-gray-900 dark:text-white placeholder:text-gray-400 outline-none ring-violet-500/20 focus:ring-2 transition-all"
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="flex items-center justify-center gap-2 rounded-xl bg-violet-600 hover:bg-violet-700 dark:bg-violet-500 dark:hover:bg-violet-600 text-white px-6 py-3 text-sm font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
          >
            {loading ? (
              <>
                <FontAwesomeIcon icon={faSpinner} className="w-4 h-4 animate-spin" />
                Menganalisis...
              </>
            ) : (
              <>
                <FontAwesomeIcon icon={faArrowRight} className="w-4 h-4" />
                Riset Sekarang
              </>
            )}
          </button>
        </form>

        <div className="flex flex-wrap items-center gap-1.5 mt-4 text-xs text-gray-500 dark:text-gray-400">
          <span>Coba:</span>
          {examples.map((ex) => (
            <button
              key={ex}
              type="button"
              onClick={() => !loading && onSubmit(ex)}
              disabled={loading}
              className="bg-white dark:bg-gray-800 border rounded-full px-3 py-1 text-xs hover:border-violet-300 dark:hover:border-violet-600 hover:text-violet-600 dark:hover:text-violet-400 transition-all disabled:opacity-50 flex items-center gap-1 cursor-pointer"
            >
              <FontAwesomeIcon icon={faLightbulb} className="text-violet-500" />
              {ex}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
