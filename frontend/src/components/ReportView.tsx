import type { ResearchReport } from '../types'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { 
  faCircleCheck, faTriangleExclamation, faCircleXmark, faChartBar, faArrowTrendUp,
  faCheck, faTimes, faBuilding, faStar, faClipboardCheck, faMapMarkerAlt,
  faGlobe, faNewspaper, faArrowUpRightFromSquare, faLightbulb, faBullseye,
  faCalendarDays
} from '@fortawesome/free-solid-svg-icons'

interface Props { report: ResearchReport }

function sum(a: number[]) { return a.reduce((x, y) => x + y, 0) }

export default function ReportView({ report: r }: Props) {
  const { decision: dc, business_score: bs, ai, trends, competitors, prices, price_stats, review_stats, news } = r
  const trend = trends[0]
  const tv = trend?.interest_values || []
  const tvAvg = tv.length ? Math.round(sum(tv) / tv.length) : 0

  return (
    <div className="w-full px-4 pb-12 space-y-6">

      {/* ===== ROW 1: Keputusan Bisnis | Ringkasan Eksekutif | SWOT ===== */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {/* Keputusan Bisnis */}
        <div className={`rounded-2xl border shadow-sm p-5 ${
          dc.verdict === 'GO' ? 'bg-gradient-to-br from-emerald-700 to-emerald-900 text-white' :
          dc.verdict === 'CAUTION' ? 'bg-gradient-to-br from-amber-700 to-amber-900 text-white' :
          'bg-gradient-to-br from-rose-700 to-rose-900 text-white'
        }`}>
          <p className="text-white/80 text-xs font-semibold uppercase tracking-wider">Keputusan Bisnis</p>
          <div className="flex items-center gap-2 mt-1">
            <FontAwesomeIcon icon={dc.verdict === 'GO' ? faCircleCheck : dc.verdict === 'CAUTION' ? faTriangleExclamation : faCircleXmark} className="text-white text-xl" />
            <p className="text-2xl font-bold mt-1">{dc.verdict_label.replace(/^[✅⚠️❌]\s*/, '')}</p>
          </div>
          <p className="text-white text-xs mt-0.5">Confidence: {dc.confidence}%</p>
          <div className="flex gap-3 mt-3">
            <div><p className="text-lg font-bold">{dc.opportunity_score}</p><p className="text-[10px] text-white/80">Peluang</p></div>
            <div><p className="text-lg font-bold">{dc.saturation_score}</p><p className="text-[10px] text-white/80">Kejenuhan</p></div>
            <div><p className="text-lg font-bold">{bs.overall}</p><p className="text-[10px] text-white/80">Skor</p></div>
          </div>
          <div className="flex flex-wrap gap-1.5 mt-3">
            {dc.reasons_go.map((r, i) => <span key={i} className="bg-black/20 text-white text-[10px] px-2 py-1 rounded-full">{r}</span>)}
            {dc.reasons_caution.map((r, i) => <span key={i} className="bg-black/20 text-white/90 text-[10px] px-2 py-1 rounded-full">{r}</span>)}
          </div>
        </div>

        {/* Ringkasan Eksekutif */}
        <div className="rounded-2xl border bg-white dark:bg-gray-900 shadow-sm p-5">
          <h2 className="text-base font-bold text-gray-900 dark:text-white mb-2">Ringkasan Eksekutif</h2>
          <p className="text-sm leading-relaxed text-gray-600 dark:text-gray-300">{ai.executive_summary || 'Data tidak mencukupi untuk ringkasan eksekutif.'}</p>
        </div>

        {/* SWOT */}
        <div className="rounded-2xl border bg-white dark:bg-gray-900 shadow-sm p-5">
          <h2 className="text-base font-bold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
            <FontAwesomeIcon icon={faChartBar} className="text-violet-600" />
            SWOT
          </h2>
          <div className="grid grid-cols-2 gap-1.5">
            <div className="bg-emerald-50 dark:bg-emerald-950/20 rounded-lg p-2 border border-emerald-200 dark:border-emerald-900/30">
              <p className="text-[10px] font-bold text-emerald-700 dark:text-emerald-400 flex items-center gap-1">
                <FontAwesomeIcon icon={faArrowTrendUp} className="text-emerald-500" /> S
              </p>
              <ul className="text-[10px] text-emerald-600 dark:text-emerald-300 space-y-0.5 mt-0.5">{dc.swot.strength.slice(0,2).map((s, i) => <li key={i}><FontAwesomeIcon icon={faCheck} className="mr-1 text-emerald-500" /> {s}</li>)}</ul>
            </div>
            <div className="bg-rose-50 dark:bg-rose-950/20 rounded-lg p-2 border border-rose-200 dark:border-rose-900/30">
              <p className="text-[10px] font-bold text-rose-700 dark:text-rose-400">W</p>
              <ul className="text-[10px] text-rose-600 dark:text-rose-300 space-y-0.5 mt-0.5">{dc.swot.weakness.slice(0,2).map((w, i) => <li key={i}><FontAwesomeIcon icon={faTimes} className="mr-1 text-rose-500" /> {w}</li>)}</ul>
            </div>
            <div className="bg-blue-50 dark:bg-blue-950/20 rounded-lg p-2 border border-blue-200 dark:border-blue-900/30">
              <p className="text-[10px] font-bold text-blue-700 dark:text-blue-400">O</p>
              <ul className="text-[10px] text-blue-600 dark:text-blue-300 space-y-0.5 mt-0.5">{dc.swot.opportunity.slice(0,2).map((o, i) => <li key={i}><FontAwesomeIcon icon={faArrowTrendUp} className="mr-1 text-blue-500" /> {o}</li>)}</ul>
            </div>
            <div className="bg-amber-50 dark:bg-amber-950/20 rounded-lg p-2 border border-amber-200 dark:border-amber-900/30">
              <p className="text-[10px] font-bold text-amber-700 dark:text-amber-400">T</p>
              <ul className="text-[10px] text-amber-600 dark:text-amber-300 space-y-0.5 mt-0.5">{dc.swot.threat.slice(0,2).map((t, i) => <li key={i}><FontAwesomeIcon icon={faTriangleExclamation} className="mr-1 text-amber-500" /> {t}</li>)}</ul>
            </div>
          </div>
        </div>
      </div>

      {/* ===== ROW 2: Google Trends | Benchmark Skor | Statistik Pasar ===== */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
<div className="rounded-2xl border bg-white dark:bg-gray-900 shadow-sm p-5">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-bold text-gray-900 dark:text-white">Google Trends</h2>
          </div>
          {!trend ? (
            <p className="text-sm text-gray-500 dark:text-gray-400">Data Google Trends tidak tersedia untuk kata kunci ini.</p>
          ) : (
            <>
            <div className="mb-3">
              <p className="text-[10px] text-gray-500 dark:text-gray-400 uppercase tracking-wider font-semibold">Keyword</p>
              <p className="text-lg font-bold text-gray-900 dark:text-white mt-0.5">{trend.keyword}</p>
            </div>
            <hr className="border-gray-200 dark:border-gray-700 mb-4" />
            <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">Ringkasan</p>
            <div className="space-y-3 mb-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Permintaan</span>
                <span className={`text-sm font-semibold px-3 py-0.5 rounded-full ${
                  tvAvg >= 55 ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' :
                  tvAvg >= 40 ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400' :
                  'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400'
                }`}>{tvAvg >= 55 ? 'Tinggi' : tvAvg >= 40 ? 'Sedang' : 'Rendah'}</span>
              </div>
              <div className="flex items-center justify-between border-b border-gray-100 dark:border-gray-800 pb-2">
                <span className="text-sm text-gray-600 dark:text-gray-400">Rata-rata</span>
                <span className="text-sm font-bold text-gray-900 dark:text-white">{tvAvg}</span>
              </div>
              <div className="flex items-center justify-between border-b border-gray-100 dark:border-gray-800 pb-2">
                <span className="text-sm text-gray-600 dark:text-gray-400">Puncak</span>
                <span className="text-sm font-bold text-violet-600 dark:text-violet-400">{tv.length ? Math.max(...tv) : 0}</span>
              </div>
              <div className="flex items-center justify-between border-b border-gray-100 dark:border-gray-800 pb-2">
                <span className="text-sm text-gray-600 dark:text-gray-400">Terendah</span>
                <span className="text-sm font-bold text-rose-500">{tv.length ? Math.min(...tv) : 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600 dark:text-gray-400">Periode Data</span>
                <span className="text-sm font-bold text-gray-900 dark:text-white">{tv.length || 0} minggu</span>
              </div>
            </div>
            <hr className="border-gray-200 dark:border-gray-700 mb-4" />
            <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2">Insight</p>
            <p className="text-sm leading-relaxed text-gray-600 dark:text-gray-300">{ai.market_trend_description || 'Tidak ada insight yang tersedia.'}</p>
            {trend.rising_queries.length > 0 && (
              <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
                <p className="text-[11px] font-semibold text-gray-500 mb-1.5">Query Naik Daun</p>
                <div className="flex flex-wrap gap-1.5">{trend.rising_queries.slice(0, 6).map((q, i) => <span key={i} className="bg-emerald-50 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-300 text-xs px-2.5 py-1 rounded-full border border-emerald-200 dark:border-emerald-800">{q}</span>)}</div>
              </div>
            )}
            {trend.related_queries.length > 0 && (
              <div className="mt-3">
                <p className="text-[11px] font-semibold text-gray-500 mb-1.5">Query Terkait</p>
                <div className="flex flex-wrap gap-1.5">{trend.related_queries.slice(0, 6).map((q, i) => <span key={i} className="bg-violet-50 dark:bg-violet-950/30 text-violet-700 dark:text-violet-300 text-xs px-2.5 py-1 rounded-full border border-violet-200 dark:border-violet-800">{q}</span>)}</div>
              </div>
            )}
            </>
          )}
        </div>
        <div className="rounded-2xl border bg-white dark:bg-gray-900 shadow-sm p-5">
          <h2 className="text-base font-bold text-gray-900 dark:text-white mb-4">Benchmark Skor</h2>
          <div className="space-y-4">
            {[
              { label: 'Permintaan', score: bs.demand, level: dc.demand_benchmark.level },
              { label: 'Persaingan', score: bs.competition, level: dc.competition_benchmark.level, invert: true },
              { label: 'Potensi Profit', score: bs.profit_potential, level: dc.profit_benchmark.level, invert: false },
              { label: 'Tren', score: bs.trend, level: dc.trend_benchmark.level, invert: false },
              { label: 'Risiko', score: bs.risk, level: dc.risk_benchmark.level, invert: true },
            ].map(m => {
              const s = m.score ?? 0
              const level = m.level || ''
              const isBadHigh = m.invert
              const color = isBadHigh 
                ? (s >= 70 ? 'text-rose-600' : s >= 50 ? 'text-amber-600' : 'text-emerald-600')
                : (s >= 70 ? 'text-emerald-600' : s >= 50 ? 'text-amber-600' : 'text-rose-600')
              const barColor = isBadHigh
                ? (s >= 70 ? 'bg-rose-500' : s >= 50 ? 'bg-amber-500' : 'bg-emerald-500')
                : (s >= 70 ? 'bg-emerald-500' : s >= 50 ? 'bg-amber-500' : 'bg-rose-500')
              return (
                <div key={m.label}>
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-gray-700 dark:text-gray-300">{m.label}</span>
                    <span className={`font-semibold ${color}`}>{m.score ?? '—'} — {level}</span>
                  </div>
                  <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                    <div className={`h-full rounded-full ${barColor}`} style={{ width: `${s}%` }} />
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        <div className="rounded-2xl border bg-white dark:bg-gray-900 shadow-sm p-5">
          <h2 className="text-base font-bold text-gray-900 dark:text-white mb-4">Statistik Pasar</h2>
          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-3 text-center"><p className="text-xs text-gray-500">Kompetitor</p><p className="text-xl font-bold text-gray-900 dark:text-white mt-0.5">{review_stats.competitor_count}</p></div>
            <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-3 text-center"><p className="text-xs text-gray-500">Total Review</p><p className="text-xl font-bold text-gray-900 dark:text-white mt-0.5">{review_stats.total_reviews.toLocaleString()}</p></div>
            <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-3 text-center"><p className="text-xs text-gray-500">Rata Rating</p><p className="text-xl font-bold text-amber-500 mt-0.5"><FontAwesomeIcon icon={faStar} className="text-amber-400 mr-1" /> {review_stats.avg_rating}</p></div>
            <div className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-3 text-center"><p className="text-xs text-gray-500">Produk</p><p className="text-xl font-bold text-gray-900 dark:text-white mt-0.5">{price_stats.total}</p></div>
          </div>
          <div className="space-y-3 mb-3">
            <div>
              <div className="flex items-center justify-between text-sm"><span className="font-semibold text-gray-900 dark:text-white">Peluang Pasar</span><span className="text-violet-600 font-bold">{dc.opportunity_score}/100</span></div>
              <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full mt-1 overflow-hidden"><div className="h-full rounded-full bg-violet-500" style={{width:`${dc.opportunity_score}%`}} /></div>
              <div className="flex flex-wrap gap-1 mt-1.5">
                {dc.opportunity_reasons_positive?.slice(0,2).map((r,i) => <span key={i} className="text-[10px] text-emerald-600 dark:text-emerald-400">{r}</span>)}
                {dc.opportunity_reasons_negative?.slice(0,2).map((r,i) => <span key={i} className="text-[10px] text-rose-500">{r}</span>)}
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between text-sm"><span className="font-semibold text-gray-900 dark:text-white">Kejenuhan Pasar</span><span className="text-amber-600 font-bold">{dc.saturation_score}/100</span></div>
              <div className="h-2 bg-gray-100 dark:bg-gray-800 rounded-full mt-1 overflow-hidden"><div className={`h-full rounded-full ${dc.saturation_score < 50 ? 'bg-emerald-500' : dc.saturation_score < 75 ? 'bg-amber-500' : 'bg-rose-500'}`} style={{width:`${dc.saturation_score}%`}} /></div>
              <p className="text-[10px] text-gray-500 dark:text-gray-400 mt-0.5">{dc.saturation_score < 50 ? 'Rendah — masih ada ruang untuk pemain baru' : dc.saturation_score < 75 ? 'Sedang — perlu diferensiasi' : 'Tinggi — pasar hampir penuh'}</p>
            </div>
            <div className="border-t pt-2 space-y-0.5">
              {dc.saturation_reasons?.map((r,i) => {
                const isCheck = r.startsWith('✔') || r.startsWith('✅');
                const cleanText = r.replace(/^[✔✅❌✘✗]\s*/, '').trim();
                return (
                  <p key={i} className={`text-[10px] flex items-center gap-1.5 ${isCheck ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-500'}`}>
                    <FontAwesomeIcon icon={isCheck ? faCheck : faTimes} className="text-[9px] shrink-0" />
                    {cleanText}
                  </p>
                )
              })}
            </div>
          </div>
        </div>
      </div>

      {/* ===== ROW 3: Kompetitor | Harga Produk | Berita Terkait ===== */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="rounded-2xl border bg-white dark:bg-gray-900 shadow-sm p-5">
          <h2 className="text-base font-bold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
            <FontAwesomeIcon icon={faBuilding} className="text-violet-600" />
            Kompetitor
          </h2>
          <div className="flex items-center gap-2 mb-3 text-xs text-gray-500 dark:text-gray-400">
            <span className="font-semibold text-gray-900 dark:text-white">{competitors.length} utama</span>
            {r.total_competitors > competitors.length && <span>· {r.total_competitors.toLocaleString()} total listing terkait</span>}
          </div>
          {competitors.length === 0 ? (
            <p className="text-sm text-gray-500 dark:text-gray-400">Tidak ada data kompetitor untuk kata kunci ini.</p>
          ) : (
            <div className="space-y-2.5 max-h-96 overflow-y-auto">
              {competitors.map((c, i) => (
                <div key={i} className="bg-gray-50 dark:bg-gray-800/50 rounded-xl border p-3.5 text-sm">
                  <div className="flex items-start justify-between">
                    <p className="font-semibold text-gray-900 dark:text-white">{c.name}</p>
                    {c.rating && <span className="text-amber-500 shrink-0 ml-2 flex items-center gap-1"><FontAwesomeIcon icon={faStar} className="text-amber-400" /> {c.rating}</span>}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-1 space-y-0.5">
                    {c.reviews !== null && <p><FontAwesomeIcon icon={faClipboardCheck} className="mr-1 text-gray-400" /> {c.reviews.toLocaleString()} review</p>}
                    {c.address && <p className="truncate"><FontAwesomeIcon icon={faMapMarkerAlt} className="mr-1 text-gray-400" /> {c.address}</p>}
                    {c.website && <a href={c.website} target="_blank" rel="noopener noreferrer" className="text-violet-600 dark:text-violet-400 hover:underline block"><FontAwesomeIcon icon={faGlobe} className="mr-1" /> {c.website}</a>}
                    {c.maps_link && <a href={c.maps_link} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 text-xs bg-violet-100 dark:bg-violet-900/30 text-violet-700 dark:text-violet-300 px-2.5 py-1 rounded-full hover:bg-violet-200 dark:hover:bg-violet-900/50 transition-colors mt-1"><FontAwesomeIcon icon={faMapMarkerAlt} className="mr-1" /> Google Maps</a>}
                  </div>
                </div>
              ))}
            </div>
          )}
          {ai.competitor_insights && <p className="text-xs text-gray-500 dark:text-gray-400 border-t pt-3 mt-3">{ai.competitor_insights}</p>}
        </div>

        <div className="rounded-2xl border bg-white dark:bg-gray-900 shadow-sm p-5">
          <h2 className="text-base font-bold text-gray-900 dark:text-white mb-3">Harga Produk</h2>
          {prices.length === 0 ? (
            <p className="text-sm text-gray-500 dark:text-gray-400">Tidak ada data harga untuk kata kunci ini.</p>
          ) : (
            <>
            {price_stats.total > 0 && (
              <div className="grid grid-cols-2 gap-2 mb-4 text-sm">
                <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-2.5"><p className="text-[11px] text-gray-500">Termurah</p><p className="font-bold text-gray-900 dark:text-white">{price_stats.min}</p></div>
                <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-2.5"><p className="text-[11px] text-gray-500">Termahal</p><p className="font-bold text-gray-900 dark:text-white">{price_stats.max}</p></div>
                <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-2.5"><p className="text-[11px] text-gray-500">Rata-rata</p><p className="font-bold text-violet-600">{price_stats.avg}</p></div>
                <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-2.5"><p className="text-[11px] text-gray-500">Median</p><p className="font-bold text-gray-900 dark:text-white">{price_stats.median}</p></div>
                {price_stats.p25 && <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-2.5"><p className="text-[11px] text-gray-500">P25</p><p className="font-bold text-gray-900 dark:text-white">{price_stats.p25}</p></div>}
                {price_stats.p75 && <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-2.5"><p className="text-[11px] text-gray-500">P75</p><p className="font-bold text-gray-900 dark:text-white">{price_stats.p75}</p></div>}
              </div>
            )}
            {Object.keys(price_stats.distribution).length > 0 && (
              <div className="mb-4">
                <p className="text-xs font-semibold text-gray-500 mb-2">Distribusi Harga</p>
                <div className="space-y-1.5">{Object.entries(price_stats.distribution).map(([k, v]) => (
                  <div key={k} className="flex items-center gap-2 text-xs">
                    <span className="w-16 text-gray-600 dark:text-gray-400">{k}</span>
                    <div className="flex-1 h-3 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden"><div className="h-full rounded-full bg-violet-500" style={{width:`${v}%`}} /></div>
                    <span className="w-8 text-right font-medium text-gray-900 dark:text-white">{v}%</span>
                  </div>
                ))}</div>
              </div>
            )}
            <div className="divide-y text-sm max-h-60 overflow-y-auto">
              {prices.slice(0, 15).map((p, i) => (
                <div key={i} className="flex items-center justify-between py-2 first:pt-0 last:pb-0 gap-2">
                  <span className="text-gray-700 dark:text-gray-300 truncate min-w-0">{p.product}</span>
                  <span className="font-bold text-violet-600 dark:text-violet-400 shrink-0">{p.price}</span>
                </div>
              ))}
            </div>
            {ai.price_insights && <p className="text-xs text-gray-500 dark:text-gray-400 border-t pt-3 mt-3">{ai.price_insights}</p>}
            </>
          )}
        </div>

        <div className="rounded-2xl border bg-white dark:bg-gray-900 shadow-sm p-5">
          <h2 className="text-base font-bold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
            <FontAwesomeIcon icon={faNewspaper} className="text-violet-600" />
            Berita Terkait
          </h2>
          {news.length === 0 ? (
            <p className="text-sm text-gray-500 dark:text-gray-400">Tidak ditemukan artikel relevan untuk kata kunci ini.</p>
          ) : (
            <div className="space-y-3">
              {news.slice(0, 4).map((n, i) => (
                <div key={i} className="bg-gray-50 dark:bg-gray-800/50 rounded-xl p-3 border">
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">{n.title}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 line-clamp-2">{n.content.slice(0, 150)}</p>
                  {n.url && <a href={n.url} target="_blank" rel="noopener noreferrer" className="text-violet-600 dark:text-violet-400 text-xs hover:underline mt-1 inline-block flex items-center gap-1"><FontAwesomeIcon icon={faArrowUpRightFromSquare} className="text-xs" /> Baca selengkapnya</a>}
                </div>
              ))}
            </div>
          )}
          {ai.news_summary && <p className="text-xs text-gray-500 dark:text-gray-400 border-t pt-3 mt-3">{ai.news_summary}</p>}
        </div>
      </div>

      {/* ===== ROW 4: Peluang | Risiko | Rekomendasi ===== */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="rounded-2xl border bg-white dark:bg-gray-900 shadow-sm p-5">
          <h2 className="text-base font-bold text-emerald-700 dark:text-emerald-400 mb-3 flex items-center gap-2">
            <FontAwesomeIcon icon={faLightbulb} className="text-emerald-500" />
            Analisis Peluang
          </h2>
          <p className="text-sm leading-relaxed text-gray-600 dark:text-gray-300">{ai.opportunity_analysis || 'Belum cukup data untuk analisis peluang.'}</p>
        </div>
        <div className="rounded-2xl border bg-white dark:bg-gray-900 shadow-sm p-5">
          <h2 className="text-base font-bold text-rose-700 dark:text-rose-400 mb-3 flex items-center gap-2">
            <FontAwesomeIcon icon={faTriangleExclamation} className="text-rose-500" />
            Analisis Risiko
          </h2>
          <p className="text-sm leading-relaxed text-gray-600 dark:text-gray-300">{ai.risk_analysis || 'Belum cukup data untuk analisis risiko.'}</p>
        </div>
        <div className="rounded-2xl border bg-gradient-to-br from-amber-50 to-white dark:from-amber-950/20 dark:to-gray-900 shadow-sm p-5">
          <h2 className="text-base font-bold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
            <FontAwesomeIcon icon={faBullseye} className="text-amber-500" />
            Rekomendasi
          </h2>
          <p className="text-sm leading-relaxed text-gray-600 dark:text-gray-300">{ai.recommendation || 'Belum cukup data untuk rekomendasi.'}</p>
        </div>
      </div>

      {/* ===== ROW 5: Action Plan ===== */}
      <div className="rounded-2xl border bg-white dark:bg-gray-900 shadow-sm p-5">
        <h2 className="text-base font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
          <FontAwesomeIcon icon={faCalendarDays} className="text-violet-600" />
          Rencana Tindakan 30 Hari
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {dc.action_plan.map((a, i) => (
            <div key={i} className="bg-gray-50 dark:bg-gray-800/50 rounded-xl border p-3.5">
              <div className="inline-block bg-violet-100 dark:bg-violet-900/50 text-violet-700 dark:text-violet-300 text-xs font-semibold px-2.5 py-1 rounded-full mb-2">{a.phase}</div>
              <ul className="space-y-1">
                {a.tasks.map((t, j) => <li key={j} className="text-xs text-gray-600 dark:text-gray-400 flex items-start gap-1.5"><FontAwesomeIcon icon={faCheck} className="text-violet-500 mt-0.5" /> {t}</li>)}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* ===== Sources ===== */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { name: 'Google Maps', on: competitors.length > 0, label: competitors.length > 0 ? `${competitors.length} kompetitor · ${review_stats.total_reviews.toLocaleString()} review` : 'Tidak ada data' },
          { name: 'Google Trends', on: trends.length > 0, label: trends.length > 0 ? `${trends.length} kata kunci · ${tv.length} data points` : 'Tidak ada data' },
          { name: 'Google Shopping', on: prices.length > 0, label: prices.length > 0 ? `${prices.length} produk · ${price_stats.total} dianalisis` : 'Tidak ada data' },
          { name: 'Tavily', on: news.length > 0, label: news.length > 0 ? `${news.length} artikel berita` : 'Tidak ada data' },
        ].map(s => (
          <div key={s.name} className={`rounded-xl border px-4 py-3 ${s.on ? 'bg-emerald-50 dark:bg-emerald-950/10 border-emerald-200 dark:border-emerald-900/30' : 'bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-700'}`}>
            <div className="flex items-center justify-between"><span className="text-sm font-medium text-gray-900 dark:text-white">{s.name}</span><span className={`text-base ${s.on ? 'text-emerald-500' : 'text-gray-400'}`}><FontAwesomeIcon icon={s.on ? faCheck : faTimes} className="text-xs" /></span></div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{s.label}</p>
          </div>
        ))}
      </div>

    </div>
  )
}
