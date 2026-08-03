import { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import type { ResearchReport } from '../types'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import {
  faCircleCheck, faTriangleExclamation, faCircleXmark, faChartBar, faArrowTrendUp,
  faCheck, faTimes, faBuilding, faStar, faMapMarkerAlt,
  faGlobe, faNewspaper, faLightbulb, faBullseye,
  faCalendarDays, faInfoCircle, faChartLine, faStore, faTag, faListCheck,
  faShield, faChartPie, faBrain, faFilter, faChevronRight, faArrowRight,
  faScaleBalanced, faPersonWalking, faUsers, faClipboardList,
  faExclamationTriangle, faMoneyBillWave, faGripVertical,
  faLayerGroup, faArrowUpWideShort, faSliders,
} from '@fortawesome/free-solid-svg-icons'
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line,
  PieChart, Pie, Cell,
} from 'recharts'

interface Props { report: ResearchReport }

function sum(a: number[]) { return a.reduce((x, y) => x + y, 0) }

const TABS = [
  { id: 'ringkasan', label: 'Ringkasan', icon: faInfoCircle },
  { id: 'keputusan', label: 'Keputusan', icon: faCircleCheck },
  { id: 'pasar', label: 'Analisis Pasar', icon: faStore },
  { id: 'kompetitor', label: 'Kompetitor', icon: faBuilding },
  { id: 'harga', label: 'Harga & Produk', icon: faTag },
  { id: 'persona', label: 'Persona', icon: faUsers },
  { id: 'risiko', label: 'Risiko', icon: faShield },
  { id: 'tren', label: 'Tren', icon: faChartLine },
  { id: 'validasi', label: 'Validasi', icon: faClipboardList },
  { id: 'ekonomi_unit', label: 'Unit Economics', icon: faMoneyBillWave },
  { id: 'rekomendasi', label: 'Rekomendasi', icon: faListCheck },
  { id: 'data', label: 'Data & Metodologi', icon: faFilter },
]

const CHART_COLORS = ['#7c3aed', '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#84cc16']

const CONFIDENCE_COLORS: Record<string, string> = { tinggi: 'bg-emerald-100 text-emerald-700', sedang: 'bg-amber-100 text-amber-700', rendah: 'bg-rose-100 text-rose-700' }

function CircleScore({ score, size = 72 }: { score: number; size?: number }) {
  const r = (size - 8) / 2
  const circumference = 2 * Math.PI * r
  const offset = circumference - (score / 100) * circumference
  const color = score >= 70 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444'
  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="currentColor" strokeWidth={4} className="text-white/20" />
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color} strokeWidth={4} strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round" className="transition-all duration-1000 ease-out" />
      </svg>
      <span className="absolute text-lg font-bold" style={{ color }}>{score}</span>
    </div>
  )
}

function ScoreBar({ score, invert = false }: { score: number; invert?: boolean }) {
  const color = invert
    ? (score >= 70 ? 'bg-rose-500' : score >= 50 ? 'bg-amber-500' : 'bg-emerald-500')
    : (score >= 70 ? 'bg-emerald-500' : score >= 50 ? 'bg-amber-500' : 'bg-rose-500')
  return (
    <div className="h-2.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
      <div className={`h-full rounded-full transition-all duration-700 ${color}`} style={{ width: `${score}%` }} />
    </div>
  )
}

function Badge({ children, color }: { children: React.ReactNode; color?: string }) {
  return (
    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${color || 'bg-violet-100 text-violet-700 dark:bg-violet-900/30 dark:text-violet-300'}`}>
      {children}
    </span>
  )
}

interface SectionProps { id: string; title: string; icon: any; className?: string; children: React.ReactNode }

function Section({ id, title, icon, className = '', children }: SectionProps) {
  return (
    <section id={`section-${id}`} className={`scroll-mt-28 ${className}`}>
      <div className="rounded-xl border border-gray-200/60 dark:border-gray-800/60 bg-white dark:bg-gray-900 shadow-sm overflow-hidden">
        <div className="px-5 sm:px-6 py-4 border-b border-gray-100 dark:border-gray-800">
          <h2 className="text-base sm:text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2.5">
            <span className="w-7 h-7 rounded-lg bg-violet-100 dark:bg-violet-900/40 flex items-center justify-center text-violet-600 dark:text-violet-400 text-xs shrink-0">
              <FontAwesomeIcon icon={icon} />
            </span>
            {title}
          </h2>
        </div>
        <div className="px-5 sm:px-6 py-5">{children}</div>
      </div>
    </section>
  )
}

export default function ReportView({ report: r }: Props) {
  const { decision: dc, business_score: bs, ai, trends, competitors, prices, price_stats, review_stats, news, trends_analysis: ta, market_statistics: ms, score_methodology: sm, data_coverage: dcov } = r
  const trend = trends[0]
  const tv = trend?.interest_values || []
  const tvAvg = tv.length ? Math.round(sum(tv) / tv.length) : 0

  const [activeTab, setActiveTab] = useState('ringkasan')
  const tabBarRef = useRef<HTMLDivElement>(null)
  const [showAllCompetitors, setShowAllCompetitors] = useState(false)
  const [trendPeriod, setTrendPeriod] = useState<'monthly' | 'yearly'>('monthly')

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) { setActiveTab(entry.target.id.replace('section-', '')); break }
        }
      },
      { rootMargin: '-104px 0px -60% 0px', threshold: 0 }
    )
    const els: Element[] = []
    for (const tab of TABS) { const el = document.getElementById(`section-${tab.id}`); if (el) { observer.observe(el); els.push(el) } }
    return () => { observer.disconnect(); els.forEach(el => observer.unobserve(el)) }
  }, [])

  const scrollTo = useCallback((id: string) => {
    const el = document.getElementById(`section-${id}`)
    if (el) { const top = el.getBoundingClientRect().top + window.scrollY - 112; window.scrollTo({ top, behavior: 'smooth' }) }
  }, [])

  // ── CHART DATA HELPERS ──

  const getTimeline = () => {
    // Use the new timeline data from trends_analysis
    if (ta?.keywords_analyzed?.[0]?.timeline?.length) {
      return ta.keywords_analyzed[0].timeline
    }
    // Fallback: create from interest_values with week labels
    if (tv.length) {
      return tv.map((v, i) => ({ date: `M${i + 1}`, value: v, month: '', year: 0 }))
    }
    return []
  }

  const getTrendChartData = useMemo(() => {
    const timeline = getTimeline()
    if (!timeline.length) return []

    if (trendPeriod === 'yearly') {
      // Group by year
      const byYear: Record<number, { values: number[]; year: number }> = {}
      for (const entry of timeline) {
        const yr = entry.year || 0
        if (!byYear[yr]) byYear[yr] = { values: [], year: yr }
        if (entry.value > 0) byYear[yr].values.push(entry.value)
      }
      return Object.values(byYear)
        .filter(g => g.year > 0)
        .sort((a, b) => a.year - b.year)
        .map(g => ({
          label: `${g.year}`,
          value: Math.round(g.values.reduce((a, b) => a + b, 0) / g.values.length),
          count: g.values.length,
        }))
    }

    // Monthly: group by month+year
    const byMonth: Record<string, { values: number[]; label: string }> = {}
    for (const entry of timeline) {
      const key = entry.month && entry.year ? `${entry.month} ${entry.year}` : 'Unknown'
      if (!byMonth[key]) byMonth[key] = { values: [], label: key }
      if (entry.value > 0) byMonth[key].values.push(entry.value)
    }
    return Object.entries(byMonth)
      .filter(([k]) => k !== 'Unknown')
      .slice(0, 36) // Max 3 years
      .map(([, g]) => ({
        label: g.label,
        value: Math.round(g.values.reduce((a, b) => a + b, 0) / g.values.length),
        count: g.values.length,
      }))
  }, [trendPeriod, ta?.keywords_analyzed?.[0]?.timeline, tv])

  const getPriceDistChartData = () => {
    if (!price_stats.distribution) return []
    return Object.entries(price_stats.distribution).map(([k, v]) => ({ name: k, value: v }))
  }

  const getRatingDistChartData = () => {
    if (!review_stats.rating_distribution) return []
    return Object.entries(review_stats.rating_distribution).map(([k, v]) => ({ name: k, value: v }))
  }

  const getCoverageChartData = () => {
    if (!dcov) return []
    const keys = ['google_trends', 'google_maps', 'google_shopping', 'google_search', 'tavily_news']
    return keys.filter(k => dcov[k] !== undefined).map(k => ({
      name: k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
      value: Number(dcov[k]),
    }))
  }

  const getScoreCompareChartData = () => [
    { name: 'Demand', value: bs.demand ?? 0 },
    { name: 'Kompetisi', value: bs.competition ?? 0 },
    { name: 'Profit', value: bs.profit_potential ?? 0 },
    { name: 'Tren', value: bs.trend ?? 0 },
    { name: 'Risiko', value: bs.risk ?? 0 },
  ]

  const displayCompetitors = showAllCompetitors ? competitors : competitors.slice(0, 10)

  const coverageLevel = (dcov?.level as string) || 'Medium'
  const coverageColor = coverageLevel === 'High' ? 'text-emerald-600' : coverageLevel === 'Medium' ? 'text-amber-600' : 'text-rose-600'
  const coverageBg = coverageLevel === 'High' ? 'bg-emerald-50 dark:bg-emerald-950/10 border-emerald-200' : coverageLevel === 'Medium' ? 'bg-amber-50 dark:bg-amber-950/10 border-amber-200' : 'bg-rose-50 dark:bg-rose-950/10 border-rose-200'

  const signalsPositive = [...(dc.reasons_why_feasible || []), ...(dc.opportunity_reasons_positive || [])].slice(0, 4)
  const signalsWarning = [...(dc.reasons_why_not_feasible || []), ...(dc.opportunity_reasons_negative || [])].slice(0, 4)

  // Data from new fields
  const s = r as any
  const demandSub = s.demand_sub_scores || {}
  const demandBd = s.demand_breakdown || {}
  const opportunities = s.market_opportunities || []
  const competitorStrengths = s.competitor_strengths || []
  const competitiveMap = s.competitive_map || {}
  const customerPersonas = s.customer_personas || []
  const painPointAnalysis = s.pain_point_analysis || {}
  const productOpps = s.product_opportunities || []
  const pricePositioning = s.price_positioning || {}
  const contradictions = s.contradictions || []
  const dataLimitations = s.data_limitations || []
  const validationChecklist = s.validation_checklist || {}
  const actionPlanV2 = s.action_plan_v2 || []
  const insightConfidences = s.insight_confidences || []
  const decisionCriteria = dc.decision_criteria || []

  return (
    <div className="w-full px-4 sm:px-6 pb-12">
      {/* Sticky Tabs */}
      <div ref={tabBarRef} className="sticky top-14 z-20 bg-white/90 dark:bg-gray-950/90 backdrop-blur-md border-b border-gray-200 dark:border-gray-800 -mx-4 sm:-mx-6 px-4 sm:px-6">
        <div className="max-w-6xl mx-auto">
          <nav className="flex gap-0.5 overflow-x-auto py-2.5 scrollbar-hide">
            {TABS.map(tab => (
              <button key={tab.id} onClick={() => scrollTo(tab.id)}
                className={`shrink-0 flex items-center gap-1.5 px-3.5 py-2 rounded-lg text-sm font-medium transition-all cursor-pointer whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'bg-violet-100 dark:bg-violet-900/40 text-violet-700 dark:text-violet-300 shadow-sm'
                    : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}>
                <FontAwesomeIcon icon={tab.icon} className="text-xs" />
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      <div className="max-w-6xl mx-auto mt-6 space-y-8">
        {/* ═══ 1. Executive Summary ═══ */}
        <section id="section-ringkasan" className="scroll-mt-28">
          <div className="rounded-xl border border-gray-200/60 dark:border-gray-800/60 bg-white dark:bg-gray-900 shadow-sm overflow-hidden">
            <div className="bg-gradient-to-br from-violet-50 to-indigo-50 dark:from-violet-950/30 dark:to-indigo-950/30 border-b border-violet-100 dark:border-violet-900/30 px-5 sm:px-6 py-6 sm:py-8">
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-5">
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-semibold uppercase tracking-widest text-violet-500 dark:text-violet-400">Laporan Riset Pasar</p>
                  <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 dark:text-white mt-2 leading-tight">{r.query_context?.product || r.query}</h1>
                  {r.query_context?.location_city && (
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1.5 flex items-center gap-1.5">
                      <FontAwesomeIcon icon={faMapMarkerAlt} className="text-violet-400" />
                      {r.query_context.location_city}{r.query_context.location_province ? `, ${r.query_context.location_province}` : ''}
                    </p>
                  )}
                </div>
                <div className="flex items-center gap-5 shrink-0">
                  <div className="text-center"><CircleScore score={bs.overall} size={72} /><p className="text-xs font-medium text-gray-500 dark:text-gray-400 mt-1.5">Skor Keseluruhan</p></div>
                  <div className="text-center"><div className={`text-3xl sm:text-4xl font-bold ${dc.confidence >= 70 ? 'text-emerald-600' : dc.confidence >= 50 ? 'text-amber-600' : 'text-rose-600'}`}>{dc.confidence}%</div><p className="text-xs font-medium text-gray-500 dark:text-gray-400 mt-1">Confidence</p></div>
                </div>
              </div>
              <div className="mt-6">
                <div className={`inline-flex items-center gap-2.5 px-5 py-2.5 rounded-xl font-bold text-base sm:text-lg shadow-sm ${
                  dc.verdict === 'SANGAT_LAYAK' || dc.verdict === 'GO' ? 'bg-emerald-600 text-white' :
                  dc.verdict === 'LAYAK' ? 'bg-emerald-500 text-white' :
                  dc.verdict === 'LAYAK_DENGAN_SYARAT' || dc.verdict === 'CAUTION' ? 'bg-amber-500 text-white' :
                  dc.verdict === 'PERLU_VALIDASI' ? 'bg-amber-400 text-white' :
                  dc.verdict === 'BERISIKO_TINGGI' ? 'bg-orange-500 text-white' :
                  'bg-rose-600 text-white'
                }`}>
                  <FontAwesomeIcon icon={
                    dc.verdict === 'SANGAT_LAYAK' || dc.verdict === 'LAYAK' || dc.verdict === 'GO' ? faCircleCheck :
                    dc.verdict === 'BERISIKO_TINGGI' || dc.verdict === 'TIDAK_DIREKOMENDASIKAN' || dc.verdict === 'STOP' ? faCircleXmark :
                    faTriangleExclamation
                  } className="text-lg" />
                  {dc.verdict_label.replace(/^[✅⚠️🔴]?\s*/, '')}
                </div>
              </div>
            </div>
            <div className="px-5 sm:px-6 py-5 space-y-5">
              <p className="text-sm sm:text-base leading-relaxed text-gray-600 dark:text-gray-300">{ai.executive_summary || 'Data tidak mencukupi untuk ringkasan eksekutif.'}</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {signalsPositive.length > 0 && (
                  <div className="bg-emerald-50/60 dark:bg-emerald-950/10 rounded-lg border border-emerald-200/60 dark:border-emerald-900/30 p-3.5">
                    <p className="text-xs font-semibold text-emerald-700 dark:text-emerald-400 mb-2 flex items-center gap-1.5"><FontAwesomeIcon icon={faCircleCheck} className="text-emerald-500" /> Sinyal Positif</p>
                    <div className="flex flex-wrap gap-1.5">{signalsPositive.map((s, i) => (<span key={i} className="text-xs text-emerald-600 dark:text-emerald-300 bg-emerald-100 dark:bg-emerald-900/30 px-2.5 py-1 rounded-md">{s.replace(/^[✔✅●\s]/, '').trim()}</span>))}</div>
                  </div>
                )}
                {signalsWarning.length > 0 && (
                  <div className="bg-amber-50/60 dark:bg-amber-950/10 rounded-lg border border-amber-200/60 dark:border-amber-900/30 p-3.5">
                    <p className="text-xs font-semibold text-amber-700 dark:text-amber-400 mb-2 flex items-center gap-1.5"><FontAwesomeIcon icon={faTriangleExclamation} className="text-amber-500" /> Sinyal Peringatan</p>
                    <div className="flex flex-wrap gap-1.5">{signalsWarning.map((s, i) => (<span key={i} className="text-xs text-amber-600 dark:text-amber-300 bg-amber-100 dark:bg-amber-900/30 px-2.5 py-1 rounded-md">{s.replace(/^[⚠️●\s]/, '').trim()}</span>))}</div>
                  </div>
                )}
              </div>
              <div>
                <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-2.5 uppercase tracking-wider">Ketersediaan Sumber Data</p>
                <div className="grid grid-cols-2 sm:grid-cols-5 gap-2.5">
                  {[
                    { name: 'Google Maps', on: competitors.length > 0, label: competitors.length > 0 ? `${competitors.length} kompetitor` : 'Tidak ada data', icon: faMapMarkerAlt },
                    { name: 'Google Trends', on: tv.length > 0, label: ta?.has_any_data ? `${ta.keywords_analyzed.length} kata kunci` : 'Tidak ada data', icon: faChartLine },
                    { name: 'Google Shopping', on: prices.length > 0, label: prices.length > 0 ? `${prices.length} produk` : 'Tidak ada data', icon: faTag },
                    { name: 'Google Search', on: true, label: `${competitors.length} listing`, icon: faGlobe },
                    { name: 'Tavily News', on: news.length > 0, label: news.length > 0 ? `${news.length} artikel` : 'Tidak ada data', icon: faNewspaper },
                  ].map(s => (
                    <div key={s.name} className={`rounded-lg border px-3 py-2.5 ${s.on ? 'bg-emerald-50/60 dark:bg-emerald-950/10 border-emerald-200/60 dark:border-emerald-900/30' : 'bg-gray-50 dark:bg-gray-900 border-gray-200 dark:border-gray-700'}`}>
                      <div className="flex items-center justify-between"><span className={`text-xs font-medium ${s.on ? 'text-gray-900 dark:text-white' : 'text-gray-500 dark:text-gray-400'}`}>{s.name}</span><span className={`text-sm ${s.on ? 'text-emerald-500' : 'text-gray-400'}`}><FontAwesomeIcon icon={s.on ? faCheck : faTimes} className="text-[10px]" /></span></div>
                      <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5 truncate">{s.label}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ═══ 2. AI Understanding ═══ */}
        <Section id="pemahaman" title="Pemahaman AI terhadap Ide Bisnis Anda" icon={faBrain}>
          <p className="text-sm sm:text-base leading-relaxed text-gray-600 dark:text-gray-300">{ai.ai_understanding || 'AI memahami input Anda sebagai riset untuk produk yang Anda sebutkan.'}</p>
          {r.query_context && (
            <div className="mt-4 grid grid-cols-2 sm:grid-cols-4 gap-3">
              {r.query_context.product && <DataCard label="Produk Terdeteksi" value={r.query_context.product} />}
              {r.query_context.location_city && <DataCard label="Lokasi" value={`${r.query_context.location_city}${r.query_context.location_province ? `, ${r.query_context.location_province}` : ''}`} />}
              {r.query_context.intent && <DataCard label="Tujuan Riset" value={r.query_context.intent.replace(/_/g, ' ')} />}
              {r.query_context.product_variants && r.query_context.product_variants.length > 1 && <DataCard label="Varian Produk" value={(r.query_context.product_variants as string[]).join(', ')} />}
            </div>
          )}
        </Section>

        {/* ═══ 3. Decision & Opportunity (GABUNGAN) ═══ */}
        <Section id="keputusan" title="Keputusan Bisnis & Peluang" icon={faCircleCheck}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className={`rounded-lg border-2 p-4 sm:p-5 ${dc.verdict === 'SANGAT_LAYAK' || dc.verdict === 'GO' || dc.verdict === 'LAYAK' ? 'border-emerald-200 dark:border-emerald-900/40 bg-emerald-50/60 dark:bg-emerald-950/10' : dc.verdict === 'CAUTION' || dc.verdict === 'LAYAK_DENGAN_SYARAT' || dc.verdict === 'PERLU_VALIDASI' ? 'border-amber-200 dark:border-amber-900/40 bg-amber-50/60 dark:bg-amber-950/10' : 'border-rose-200 dark:border-rose-900/40 bg-rose-50/60 dark:bg-rose-950/10'}`}>
              <p className="text-xs font-semibold uppercase tracking-wider text-gray-500 dark:text-gray-400 mb-2">Keputusan</p>
              <div className="flex items-center gap-3">
                <FontAwesomeIcon icon={dc.verdict === 'SANGAT_LAYAK' || dc.verdict === 'LAYAK' || dc.verdict === 'GO' ? faCircleCheck : dc.verdict === 'BERISIKO_TINGGI' || dc.verdict === 'TIDAK_DIREKOMENDASIKAN' || dc.verdict === 'STOP' ? faCircleXmark : faTriangleExclamation}
                  className={`text-2xl ${dc.verdict === 'SANGAT_LAYAK' || dc.verdict === 'LAYAK' || dc.verdict === 'GO' ? 'text-emerald-600' : dc.verdict === 'BERISIKO_TINGGI' || dc.verdict === 'TIDAK_DIREKOMENDASIKAN' || dc.verdict === 'STOP' ? 'text-rose-600' : 'text-amber-600'}`} />
                <p className="text-lg font-bold text-gray-900 dark:text-white">{dc.verdict_label.replace(/^[✅⚠️🔴]?\s*/, '')}</p>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="bg-violet-50 dark:bg-violet-950/20 rounded-lg p-4 border border-violet-200 dark:border-violet-900/30 text-center">
                <p className="text-2xl font-bold text-violet-600">{bs.overall}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Skor Overall</p>
              </div>
              <div className={`rounded-lg p-4 border text-center ${dc.confidence >= 70 ? 'bg-emerald-50 dark:bg-emerald-950/10 border-emerald-200' : dc.confidence >= 50 ? 'bg-amber-50 dark:bg-amber-950/10 border-amber-200' : 'bg-rose-50 dark:bg-rose-950/10 border-rose-200'}`}>
                <p className={`text-2xl font-bold ${dc.confidence >= 70 ? 'text-emerald-600' : dc.confidence >= 50 ? 'text-amber-600' : 'text-rose-600'}`}>{dc.confidence}%</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">Confidence</p>
              </div>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            <div className="bg-violet-50 dark:bg-violet-950/20 rounded-lg p-4 sm:p-5 border border-violet-200 dark:border-violet-900/30">
              <div className="flex items-center justify-between mb-2"><span className="text-sm font-semibold text-gray-900 dark:text-white">Skor Peluang</span><span className="text-lg font-bold text-violet-600">{dc.opportunity_score}/100</span></div>
              <ScoreBar score={dc.opportunity_score} />
            </div>
            <div className="bg-amber-50 dark:bg-amber-950/20 rounded-lg p-4 sm:p-5 border border-amber-200 dark:border-amber-900/30">
              <div className="flex items-center justify-between mb-2"><span className="text-sm font-semibold text-gray-900 dark:text-white">Kejenuhan Pasar</span><span className="text-lg font-bold text-amber-600">{dc.saturation_score}/100</span></div>
              <ScoreBar score={dc.saturation_score} invert />
            </div>
          </div>
          {dc.decision_reasoning && dc.decision_reasoning.length > 0 && (
            <div className="mb-5 bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4 border">
              <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Alasan Keputusan</p>
              <ul className="space-y-1">{dc.decision_reasoning.map((r, i) => (<li key={i} className="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2"><span className="w-1.5 h-1.5 rounded-full bg-violet-400 mt-1.5 shrink-0" />{r}</li>))}</ul>
            </div>
          )}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-5">
            <div className="rounded-lg border-2 border-emerald-200 dark:border-emerald-900/40 bg-emerald-50/60 dark:bg-emerald-950/10 p-4">
              <p className="text-sm font-bold text-emerald-700 dark:text-emerald-400 mb-3 flex items-center gap-2"><FontAwesomeIcon icon={faCircleCheck} className="text-emerald-500" /> Mengapa Layak</p>
              {dc.reasons_why_feasible?.length > 0 ? (<ul className="space-y-1.5">{dc.reasons_why_feasible.map((r, i) => (<li key={i} className="text-sm text-emerald-700 dark:text-emerald-300 flex items-start gap-2"><FontAwesomeIcon icon={faCheck} className="text-emerald-500 mt-0.5 shrink-0 text-[10px]" />{r.replace(/^[✔✅]?\s*/, '')}</li>))}</ul>) : <p className="text-sm text-gray-500 dark:text-gray-400 italic">Belum cukup data.</p>}
            </div>
            <div className="rounded-lg border-2 border-amber-200 dark:border-amber-900/40 bg-amber-50/60 dark:bg-amber-950/10 p-4">
              <p className="text-sm font-bold text-amber-700 dark:text-amber-400 mb-3 flex items-center gap-2"><FontAwesomeIcon icon={faTriangleExclamation} className="text-amber-500" /> Mengapa Tidak Layak</p>
              {dc.reasons_why_not_feasible?.length > 0 ? (<ul className="space-y-1.5">{dc.reasons_why_not_feasible.map((r, i) => (<li key={i} className="text-sm text-amber-700 dark:text-amber-300 flex items-start gap-2"><FontAwesomeIcon icon={faTriangleExclamation} className="text-amber-500 mt-0.5 shrink-0 text-[10px]" />{r.replace(/^[⚠]?\s*/, '')}</li>))}</ul>) : <p className="text-sm text-gray-500 dark:text-gray-400 italic">Belum cukup data.</p>}
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {dc.strongest_evidence && dc.strongest_evidence.length > 0 && (
              <div className="bg-blue-50 dark:bg-blue-950/20 rounded-lg p-4 border border-blue-200 dark:border-blue-900/30">
                <p className="text-xs font-semibold text-blue-700 dark:text-blue-400 mb-2">Bukti Terkuat</p>
                <ul className="space-y-1">{dc.strongest_evidence.map((r, i) => (<li key={i} className="text-sm text-blue-600 dark:text-blue-300 flex items-start gap-2"><span className="w-1.5 h-1.5 rounded-full bg-blue-400 mt-1.5 shrink-0" />{r}</li>))}</ul>
              </div>
            )}
            {dc.biggest_risk && dc.biggest_risk.length > 0 && (
              <div className="bg-rose-50 dark:bg-rose-950/20 rounded-lg p-4 border border-rose-200 dark:border-rose-900/30">
                <p className="text-xs font-semibold text-rose-700 dark:text-rose-400 mb-2">Risiko Terbesar</p>
                <ul className="space-y-1">{dc.biggest_risk.map((r, i) => (<li key={i} className="text-sm text-rose-600 dark:text-rose-300 flex items-start gap-2"><span className="w-1.5 h-1.5 rounded-full bg-rose-400 mt-1.5 shrink-0" />{r}</li>))}</ul>
              </div>
            )}
          </div>
        </Section>

        {/* ═══ 4. ANALISIS PASAR (GABUNGAN: Pasar + Statistik + Skor + Metodologi) ═══ */}
        <Section id="pasar" title="Analisis Pasar" icon={faStore}>
          {ms?.data_limitation_note && (
            <div className="bg-amber-50 dark:bg-amber-950/20 rounded-lg border border-amber-200 dark:border-amber-900/30 p-3.5 mb-5">
              <p className="text-sm text-amber-700 dark:text-amber-400 flex items-start gap-2"><FontAwesomeIcon icon={faInfoCircle} className="mt-0.5 shrink-0" />{ms.data_limitation_note}</p>
            </div>
          )}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
            <StatCard label="Kompetitor" value={`${ms?.total_competitors_detected || competitors.length}`} sub={`${ms?.direct_competitors || 0} langsung`} />
            <StatCard label="Total Review" value={review_stats.total_reviews.toLocaleString()} sub={`Rata-rata ${ms?.avg_reviews_per_competitor || 0}`} />
            <StatCard label="Rata-rata Rating" value={<><FontAwesomeIcon icon={faStar} className="text-amber-400 mr-1" />{review_stats.avg_rating}</>} />
            <StatCard label="Cakupan Data" value={`${dcov?.overall || 0}%`} sub={coverageLevel} />
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
            {[
              { label: 'Permintaan', score: bs.demand, icon: faArrowTrendUp, invert: false },
              { label: 'Persaingan', score: bs.competition, icon: faBuilding, invert: true },
              { label: 'Potensi Harga', score: bs.profit_potential, icon: faChartLine, invert: false },
              { label: 'Tren', score: bs.trend, icon: faChartBar, invert: false },
              { label: 'Risiko', score: bs.risk, icon: faShield, invert: true },
            ].map(m => {
              const s = m.score ?? 0; const isBadHigh = m.invert
              const color = isBadHigh ? (s >= 70 ? 'text-rose-600' : s >= 50 ? 'text-amber-600' : 'text-emerald-600') : (s >= 70 ? 'text-emerald-600' : s >= 50 ? 'text-amber-600' : 'text-rose-600')
              return (
                <div key={m.label} className="bg-gray-50 dark:bg-gray-800/50 rounded-lg border p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm ${isBadHigh ? (s >= 70 ? 'bg-rose-100 dark:bg-rose-900/30 text-rose-600' : s >= 50 ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-600' : 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600') : (s >= 70 ? 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600' : s >= 50 ? 'bg-amber-100 dark:bg-amber-900/30 text-amber-600' : 'bg-rose-100 dark:bg-rose-900/30 text-rose-600')}`}><FontAwesomeIcon icon={m.icon} /></span>
                      <p className="text-sm font-semibold text-gray-900 dark:text-white">{m.label}</p>
                    </div>
                    <span className={`text-xl font-bold ${color}`}>{s}</span>
                  </div>
                  <ScoreBar score={s} invert={m.invert} />
                </div>
              )
            })}
          </div>
          {dc.insights.length > 0 && (
            <div className="bg-violet-50 dark:bg-violet-950/20 rounded-lg border border-violet-200 dark:border-violet-900/30 p-4 sm:p-5">
              <p className="text-sm font-semibold text-violet-700 dark:text-violet-400 mb-3 flex items-center gap-1.5"><FontAwesomeIcon icon={faLightbulb} className="text-violet-500" /> Insight Pasar</p>
              <ul className="space-y-1.5">{dc.insights.map((insight, i) => (<li key={i} className="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2"><span className="w-1.5 h-1.5 rounded-full bg-violet-400 mt-1.5 shrink-0" />{insight}</li>))}</ul>
            </div>
          )}
        </Section>

        {/* ═══ 5. KOMPETITOR (GABUNGAN: Database + Kekuatan + Statistik) ═══ */}
        <Section id="kompetitor" title="Analisis Kompetitor" icon={faBuilding}>
          {competitors.length === 0 ? (
            <p className="text-sm text-gray-500 dark:text-gray-400">Tidak ada data kompetitor.</p>
          ) : (
            <>
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
                <div className="flex items-center gap-3 text-sm">
                  <span className="font-semibold text-gray-900 dark:text-white">{competitors.length} kompetitor</span>
                  <span className="text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/20 px-2 py-0.5 rounded text-xs">{ms?.direct_competitors || 0} langsung</span>
                  <span className="text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/20 px-2 py-0.5 rounded text-xs">{ms?.indirect_competitors || 0} tidak langsung</span>
                </div>
                {competitors.length > 6 && (
                  <button onClick={() => setShowAllCompetitors(!showAllCompetitors)} className="text-sm text-violet-600 dark:text-violet-400 hover:underline cursor-pointer flex items-center gap-1">
                    {showAllCompetitors ? 'Tampilkan 6 teratas' : `Tampilkan semua (${competitors.length})`}
                    <FontAwesomeIcon icon={faChevronRight} className="text-xs" />
                  </button>
                )}
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-5">
                {displayCompetitors.slice(0, 6).map((c, i) => (
                  <div key={i} className={`rounded-lg border p-4 ${c.competitor_type === 'direct' ? 'bg-emerald-50/30 dark:bg-emerald-950/5 border-emerald-200 dark:border-emerald-900/30' : 'bg-gray-50 dark:bg-gray-800/50 border-gray-200 dark:border-gray-700'}`}>
                    <div className="flex items-start justify-between gap-2">
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <p className="font-semibold text-gray-900 dark:text-white truncate">{c.name}</p>
                          {c.competitor_type === 'direct' ? <span className="text-xs px-2 py-0.5 rounded bg-emerald-100 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400 shrink-0">Langsung</span> : <span className="text-xs px-2 py-0.5 rounded bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400 shrink-0">Tidak langsung</span>}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400 mt-2 space-y-1">
                          {c.rating && <p><FontAwesomeIcon icon={faStar} className="text-amber-400 mr-1.5" />{c.rating} {c.reviews !== null && ` · ${c.reviews.toLocaleString()} review`}</p>}
                          {c.address && <p className="truncate flex items-center gap-1.5"><FontAwesomeIcon icon={faMapMarkerAlt} className="text-gray-400 text-xs" /> {c.address}</p>}
                        </div>
                      </div>
                      {c.rating && <div className="text-center shrink-0"><div className="text-lg font-bold text-amber-500">{c.rating}</div><p className="text-xs text-gray-400">rating</p></div>}
                    </div>
                  </div>
                ))}
              </div>
              {competitorStrengths.length > 0 && (
                <div className="mt-4">
                  <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Analisis Kekuatan Kompetitor</p>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-gray-200 dark:border-gray-700">
                          <th className="text-left py-2 px-3 font-semibold text-gray-600 dark:text-gray-400">Nama</th>
                          <th className="text-center py-2 px-3 font-semibold text-gray-600 dark:text-gray-400">Rating</th>
                          <th className="text-center py-2 px-3 font-semibold text-gray-600 dark:text-gray-400">Popularitas</th>
                          <th className="text-center py-2 px-3 font-semibold text-gray-600 dark:text-gray-400">Posisi Harga</th>
                          <th className="text-center py-2 px-3 font-semibold text-gray-600 dark:text-gray-400">Strength</th>
                        </tr>
                      </thead>
                      <tbody>
                        {(competitorStrengths as any[]).slice(0, 5).map((cs: any, i: number) => (
                          <tr key={i} className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50">
                            <td className="py-2.5 px-3 font-medium text-gray-900 dark:text-white">{cs.name}</td>
                            <td className="text-center py-2.5 px-3">{cs.rating > 0 ? <span className="text-amber-500">{cs.rating}</span> : '-'}</td>
                            <td className="text-center py-2.5 px-3">
                              <span className={`text-xs px-2 py-0.5 rounded-full ${cs.popularity === 'tinggi' ? 'bg-emerald-100 text-emerald-700' : cs.popularity === 'sedang' ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-500'}`}>{cs.popularity}</span>
                            </td>
                            <td className="text-center py-2.5 px-3">
                              <span className={`text-xs px-2 py-0.5 rounded-full ${cs.price_positioning === 'premium' ? 'bg-violet-100 text-violet-700' : cs.price_positioning === 'ekonomis' ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-600'}`}>{cs.price_positioning}</span>
                            </td>
                            <td className="text-center py-2.5 px-3">
                              <div className="flex items-center gap-2 justify-center">
                                <div className="w-16 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                                  <div className={`h-full rounded-full ${cs.strength_score >= 60 ? 'bg-emerald-500' : cs.strength_score >= 40 ? 'bg-amber-500' : 'bg-rose-500'}`} style={{ width: `${cs.strength_score}%` }} />
                                </div>
                                <span className="text-xs font-semibold">{cs.strength_score}</span>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
              {ai.competitor_insights && (
                <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">{ai.competitor_insights}</p>
                </div>
              )}
            </>
          )}
        </Section>

        {/* ═══ 10. Google Trends (UPGRADED with proper timeline chart) ═══ */}
        <Section id="tren" title="Analisis Google Trends" icon={faChartLine}>
          {ta && ta.keywords_analyzed && ta.keywords_analyzed.length > 0 && (
            <div className="mb-5">
              <p className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">Semua Keyword yang Dianalisis</p>
              <div className="space-y-2">
                {ta.keywords_analyzed.map((kw: any, i: number) => (
                  <div key={i} className="flex items-center gap-3 text-sm bg-gray-50 dark:bg-gray-800/50 rounded-lg px-4 py-3 border">
                    <span className={`text-sm ${kw.has_data ? 'text-emerald-500' : 'text-amber-500'}`}><FontAwesomeIcon icon={kw.has_data ? faCheck : faTriangleExclamation} /></span>
                    <span className="font-semibold text-gray-900 dark:text-white">{kw.keyword}</span>
                    {kw.has_data ? (
                      <div className="flex items-center gap-3 ml-auto text-xs">
                        <span className="text-emerald-600 dark:text-emerald-400">{kw.data_points} data points</span>
                        <span className="text-gray-400">Rata-rata: {Math.round(kw.avg_interest || 0)}</span>
                        {kw.trend_direction && <span className={`font-medium ${kw.trend_direction === 'rising' ? 'text-emerald-600' : kw.trend_direction === 'declining' ? 'text-rose-500' : 'text-amber-500'}`}>{kw.trend_direction === 'rising' ? '↑ Naik' : kw.trend_direction === 'declining' ? '↓ Turun' : '→ Stabil'}</span>}
                      </div>
                    ) : (<span className="text-xs text-amber-600 dark:text-amber-400 ml-auto">Data tidak tersedia</span>)}
                  </div>
                ))}
              </div>
              {ta.fallback_used && (
                <div className="mt-3 bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900/30 rounded-lg px-4 py-2.5 text-sm text-amber-700 dark:text-amber-400 flex items-center gap-2">
                  <FontAwesomeIcon icon={faInfoCircle} className="shrink-0" />
                  {ta.fallback_reason}
                </div>
              )}
            </div>
          )}

          {!getTrendChartData.length ? (
            <p className="text-sm text-gray-500 dark:text-gray-400">Data Google Trends tidak tersedia.</p>
          ) : (
            <>
              {/* UPGRADED: proper timeline chart with per-bulan/per-tahun toggle */}
              <div className="mb-5 bg-gray-50 dark:bg-gray-800/50 rounded-lg border p-4 sm:p-5">
                <div className="flex items-center justify-between mb-3">
                  <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">Tren Pencarian dari Waktu ke Waktu</p>
                  <div className="flex gap-1">
                    <button onClick={() => setTrendPeriod('monthly')}
                      className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-all cursor-pointer ${trendPeriod === 'monthly' ? 'bg-violet-100 dark:bg-violet-900/40 text-violet-700 dark:text-violet-300' : 'text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'}`}>Per Bulan</button>
                    <button onClick={() => setTrendPeriod('yearly')}
                      className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-all cursor-pointer ${trendPeriod === 'yearly' ? 'bg-violet-100 dark:bg-violet-900/40 text-violet-700 dark:text-violet-300' : 'text-gray-500 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-700'}`}>Per Tahun</button>
                  </div>
                </div>
                <ResponsiveContainer width="100%" height={280}>
                  <LineChart data={getTrendChartData}>
                    <XAxis dataKey="label" tick={{ fontSize: 10 }} interval="preserveStartEnd" />
                    <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} label={{ value: 'Interest (0-100)', angle: -90, position: 'insideLeft', style: { fontSize: 11 } }} />
                    <Tooltip formatter={(v: any) => [`${v}/100`, 'Interest']} labelFormatter={(l: string) => `Periode: ${l}`} />
                    <Line type="monotone" dataKey="value" stroke="#7c3aed" strokeWidth={2.5} dot={{ r: 2 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className="mb-4">
                <p className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider font-semibold">Keyword Terpilih</p>
                <p className="text-xl font-bold text-violet-600 dark:text-violet-400 mt-0.5">{trend?.keyword || ta?.selected_keyword || '-'}</p>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
                <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-3.5 border">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Permintaan</p>
                  <span className={`text-sm font-semibold mt-1 inline-block px-2.5 py-0.5 rounded-full ${tvAvg >= 55 ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' : tvAvg >= 40 ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400' : 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400'}`}>{tvAvg >= 55 ? 'Tinggi' : tvAvg >= 40 ? 'Sedang' : 'Rendah'}</span>
                </div>
                <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-3.5 border">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Rata-rata Interest</p>
                  <p className="text-xl font-bold text-gray-900 dark:text-white mt-0.5">{tvAvg}</p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-3.5 border">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Puncak</p>
                  <p className="text-xl font-bold text-violet-600 dark:text-violet-400 mt-0.5">{tv.length ? Math.max(...tv) : 0}</p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-3.5 border">
                  <p className="text-xs text-gray-500 dark:text-gray-400">Periode</p>
                  <p className="text-xl font-bold text-gray-900 dark:text-white mt-0.5">{getTimeline().length > 0 ? `${getTimeline().length} periode` : `${tv.length || 0} bln`}</p>
                </div>
              </div>

              {ai.market_trend_description && (
                <div className="bg-violet-50 dark:bg-violet-950/20 rounded-lg p-4 sm:p-5 border border-violet-200 dark:border-violet-900/30 mb-4">
                  <p className="text-sm font-semibold text-violet-700 dark:text-violet-400 mb-2 flex items-center gap-1.5"><FontAwesomeIcon icon={faChartLine} className="text-violet-500" /> Analisis Tren</p>
                  <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">{ai.market_trend_description}</p>
                </div>
              )}

              {trend?.rising_queries?.length > 0 && (
                <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                  <p className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-2.5">Query Naik Daun</p>
                  <div className="flex flex-wrap gap-2">{trend.rising_queries.slice(0, 8).map((q: string, i: number) => (
                    <span key={i} className="bg-emerald-50 dark:bg-emerald-950/30 text-emerald-700 dark:text-emerald-300 text-sm px-3 py-1 rounded-full border border-emerald-200 dark:border-emerald-800">{q}</span>
                  ))}</div>
                </div>
              )}
            </>
          )}
        </Section>

        {/* ═══ 5. HARGA & PRODUK (GABUNGAN: Price + Positioning) ═══ */}
        <Section id="harga" title="Harga & Produk" icon={faTag}>
          {prices.length === 0 ? (<p className="text-sm text-gray-500 dark:text-gray-400">Tidak ada data harga.</p>) : (
            <>
              {price_stats.total > 0 && (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-5">
                  <StatCard label="Termurah" value={price_stats.min} />
                  <StatCard label="Termahal" value={price_stats.max} />
                  <StatCard label="Rata-rata" value={price_stats.avg} valueColor="text-violet-600" />
                  <StatCard label="Median" value={price_stats.median} />
                </div>
              )}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {getPriceDistChartData().length > 0 && (
                  <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg border p-4 sm:p-5">
                    <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Distribusi Harga</p>
                    <ResponsiveContainer width="100%" height={240}>
                      <PieChart>
                        <Pie data={getPriceDistChartData()} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80}
                          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}>
                          {getPriceDistChartData().map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
                        </Pie>
                        <Tooltip formatter={(v: any) => `${v}% produk`} />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                )}
                {pricePositioning.segments?.length > 0 && (
                  <div className="space-y-3">
                    <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">Segmentasi Harga</p>
                    <div className="grid grid-cols-3 gap-2">
                      {(pricePositioning as any).segments.map((seg: any, i: number) => (
                        <div key={i} className={`rounded-lg border p-3 text-center ${seg.percentage >= 40 ? 'bg-violet-50 dark:bg-violet-950/20 border-violet-200' : seg.percentage >= 15 ? 'bg-gray-50 dark:bg-gray-800/50 border-gray-200' : 'bg-amber-50/50 dark:bg-amber-950/10 border-amber-200'}`}>
                          <p className="text-xs text-gray-500 dark:text-gray-400">{seg.name}</p>
                          <p className="text-lg font-bold text-gray-900 dark:text-white">{seg.percentage}%</p>
                        </div>
                      ))}
                    </div>
                    {pricePositioning.sweet_spot && (
                      <div className="bg-emerald-50 dark:bg-emerald-950/10 rounded-lg border border-emerald-200 p-3">
                        <p className="text-xs font-semibold text-emerald-700 dark:text-emerald-400">Sweet Spot</p>
                        <p className="text-sm text-emerald-600 dark:text-emerald-300">{pricePositioning.sweet_spot}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
              {ai.product_price_analysis && (
                <div className="mt-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg border p-4">
                  <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">{ai.product_price_analysis}</p>
                </div>
              )}
              <div className="mt-4 border rounded-lg overflow-hidden">
                <div className="max-h-48 overflow-y-auto divide-y divide-gray-100 dark:divide-gray-800">
                  {prices.slice(0, 15).map((p, i) => (
                    <div key={i} className="flex items-center justify-between py-2.5 px-4 gap-3 hover:bg-gray-50 dark:hover:bg-gray-800/50">
                      <span className="text-sm text-gray-700 dark:text-gray-300 truncate min-w-0">{p.product}</span>
                      <span className="text-sm font-bold text-violet-600 dark:text-violet-400 shrink-0">{p.price}</span>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </Section>

        {/* ═══ 12. Market Gap ═══ */}
        <Section id="kesenjangan" title="Analisis Kesenjangan Pasar" icon={faLightbulb}>
          {ai.market_gap_analysis ? (
            <div className="space-y-4">
              <p className="text-sm sm:text-base leading-relaxed text-gray-600 dark:text-gray-300">{ai.market_gap_analysis}</p>
              {ai.market_opportunity && (
                <div className="bg-emerald-50 dark:bg-emerald-950/10 rounded-lg p-4 sm:p-5 border border-emerald-200 dark:border-emerald-900/30">
                  <p className="text-sm font-bold text-emerald-700 dark:text-emerald-400 mb-2 flex items-center gap-1.5"><FontAwesomeIcon icon={faLightbulb} className="text-emerald-500" /> Peluang yang Teridentifikasi</p>
                  <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">{ai.market_opportunity}</p>
                </div>
              )}
            </div>
          ) : (<p className="text-sm text-gray-500 dark:text-gray-400">{ai.opportunity_analysis || 'Belum cukup data.'}</p>)}
        </Section>

        {/* ═══ 6. PERSONA (GABUNGAN: Persona + Pain Points + Product Opportunities) ═══ */}
        <Section id="persona" title="Persona & Peluang" icon={faUsers}>
          <div className="space-y-5">
            {customerPersonas.length > 0 && (
              <div>
                <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Persona Pelanggan</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {(customerPersonas as any[]).slice(0, 4).map((p: any, i: number) => (
                    <div key={i} className={`rounded-lg border p-3 ${p.is_hypothesis ? 'bg-amber-50/50 dark:bg-amber-950/10 border-amber-200/60' : 'bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700'}`}>
                      <div className="flex items-center justify-between mb-1">
                        <p className="text-sm font-bold text-gray-900 dark:text-white">{p.name}</p>
                        {p.is_hypothesis && <Badge color="bg-amber-100 text-amber-700">AI Hypothesis</Badge>}
                      </div>
                      {p.description && <p className="text-xs text-gray-500 dark:text-gray-400 mb-2">{p.description}</p>}
                      {p.potential_need && <p className="text-xs"><span className="font-semibold">Kebutuhan:</span> {p.potential_need}</p>}
                    </div>
                  ))}
                </div>
              </div>
            )}
            {painPointAnalysis.top_complaints?.length > 0 && (
              <div>
                <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Pain Points & Opportunity</p>
                <div className="space-y-2">
                  {(painPointAnalysis as any).top_complaints.slice(0, 3).map((pp: any, i: number) => (
                    <div key={i} className="bg-rose-50 dark:bg-rose-950/20 rounded-lg border border-rose-200 dark:border-rose-900/30 p-3">
                      <div className="flex items-start justify-between gap-2">
                        <p className="text-sm font-semibold text-rose-700 dark:text-rose-400">{pp.complaint}</p>
                        {pp.frequency && <Badge color="bg-rose-100 text-rose-700">{pp.frequency}</Badge>}
                      </div>
                      {pp.opportunity && (
                        <p className="text-xs text-emerald-600 dark:text-emerald-400 mt-2"><FontAwesomeIcon icon={faLightbulb} className="mr-1" />{pp.opportunity}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
            {productOpps.length > 0 && (
              <div>
                <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Peluang Produk Prioritas</p>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-200 dark:border-gray-700">
                        <th className="text-left py-2 px-3 font-semibold text-gray-600 dark:text-gray-400">Produk</th>
                        <th className="text-center py-2 px-3 font-semibold text-gray-600 dark:text-gray-400">Demand</th>
                        <th className="text-center py-2 px-3 font-semibold text-gray-600 dark:text-gray-400">Kompetisi</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(productOpps as any[]).slice(0, 5).map((po: any, i: number) => (
                        <tr key={i} className="border-b border-gray-100 dark:border-gray-800">
                          <td className="py-2.5 px-3 font-medium text-gray-900 dark:text-white">{po.product}</td>
                          <td className="text-center py-2.5 px-3"><Badge color={po.demand === 'tinggi' || po.demand === 'sedang' ? 'bg-emerald-100 text-emerald-700' : 'bg-gray-100 text-gray-600'}>{po.demand}</Badge></td>
                          <td className="text-center py-2.5 px-3"><Badge color={po.competition === 'terdeteksi' ? 'bg-amber-100 text-amber-700' : 'bg-gray-100 text-gray-600'}>{po.competition || 'unknown'}</Badge></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
            {customerPersonas.length === 0 && painPointAnalysis.top_complaints?.length === 0 && productOpps.length === 0 && (
              <p className="text-sm text-gray-500 dark:text-gray-400">Data persona dan peluang belum tersedia.</p>
            )}
          </div>
        </Section>

        {/* ═══ 7. RISIKO (GABUNGAN: Risiko + SWOT) ═══ */}
        <Section id="risiko" title="Risiko & SWOT" icon={faShield}>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-5">
            <SWOTBox title="Strengths" color="emerald" items={dc.swot.strength} icon={faArrowTrendUp} />
            <SWOTBox title="Weaknesses" color="rose" items={dc.swot.weakness} icon={faTimes} />
            <SWOTBox title="Opportunities" color="blue" items={dc.swot.opportunity} icon={faArrowTrendUp} />
            <SWOTBox title="Threats" color="amber" items={dc.swot.threat} icon={faTriangleExclamation} />
          </div>
          {dc.reasons_caution && dc.reasons_caution.length > 0 && (
            <div className="bg-rose-50 dark:bg-rose-950/20 rounded-lg p-4 border border-rose-200 dark:border-rose-900/30">
              <p className="text-sm font-bold text-rose-700 dark:text-rose-400 mb-3 flex items-center gap-2"><FontAwesomeIcon icon={faTriangleExclamation} className="text-rose-500" /> Faktor Risiko Utama</p>
              <ul className="space-y-1.5">{dc.reasons_caution.slice(0, 4).map((r, i) => (<li key={i} className="text-sm text-rose-600 dark:text-rose-300 flex items-start gap-2"><span className="w-1.5 h-1.5 rounded-full bg-rose-400 mt-1.5 shrink-0" />{r.replace(/^[⚠]?\s*/, '')}</li>))}</ul>
            </div>
          )}
        </Section>

        <UnitEconomicsSection price_stats={price_stats} ai_unit_economics_analysis={ai.unit_economics_analysis} />

        {/* ═══ 9. VALIDASI (GABUNGAN: Validasi + Batasan Data) ═══ */}
        <Section id="validasi" title="Validasi & Batasan" icon={faClipboardList}>
          <div className="space-y-5">
            {validationChecklist.must_validate?.length > 0 && (
              <div>
                <p className="text-sm font-bold text-rose-600 dark:text-rose-400 mb-3 flex items-center gap-1.5"><FontAwesomeIcon icon={faExclamationTriangle} className="text-rose-500" /> Wajib Validasi</p>
                <div className="space-y-3">
                  {(validationChecklist as any).must_validate.slice(0, 3).map((v: any, i: number) => (
                    <ValidationCard key={i} {...v} />
                  ))}
                </div>
              </div>
            )}
            {validationChecklist.recommended?.length > 0 && (
              <div>
                <p className="text-sm font-bold text-emerald-600 dark:text-emerald-400 mb-3 flex items-center gap-1.5"><FontAwesomeIcon icon={faCheck} className="text-emerald-500" /> Disarankan</p>
                <div className="space-y-3">
                  {(validationChecklist as any).recommended.slice(0, 3).map((v: any, i: number) => (
                    <ValidationCard key={i} {...v} />
                  ))}
                </div>
              </div>
            )}
            {dataLimitations.length > 0 && (
              <div className="bg-amber-50 dark:bg-amber-950/10 rounded-lg border border-amber-200 p-4">
                <p className="text-sm font-semibold text-amber-700 dark:text-amber-400 mb-2">Batasan Data</p>
                <ul className="space-y-1">
                  {(dataLimitations as any[]).slice(0, 3).map((dl: any, i: number) => (
                    <li key={i} className="text-xs text-amber-600 dark:text-amber-300 flex items-start gap-2"><FontAwesomeIcon icon={faInfoCircle} className="mt-0.5 shrink-0 text-[10px]" />{dl.limitation}</li>
                  ))}
                </ul>
              </div>
            )}
            {validationChecklist.must_validate?.length === 0 && validationChecklist.recommended?.length === 0 && dataLimitations.length === 0 && (
              <p className="text-sm text-gray-500 dark:text-gray-400">{ai.validation_experiments || 'Data validasi belum tersedia.'}</p>
            )}
          </div>
        </Section>

        {/* ═══ 15. REKOMENDASI & RENCANA AKSI (GABUNGAN) ═══ */}
        <Section id="rekomendasi" title="Rekomendasi & Rencana Aksi" icon={faListCheck}>
          <div className="space-y-5">
            {ai.business_recommendation && (
              <div className="bg-violet-50 dark:bg-violet-950/20 rounded-lg border border-violet-200 dark:border-violet-900/30 p-4">
                <p className="text-sm font-bold text-violet-700 dark:text-violet-400 mb-2">Rekomendasi Utama</p>
                <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">{ai.business_recommendation}</p>
              </div>
            )}
            {(ai.recommendation || '').split('\n\n').filter(Boolean).map((block, i) => {
              const fields: Record<string, string> = {}
              for (const line of block.split('\n')) {
                const m = line.match(/^\s*-\s*\*\*([^*]+)\*\*:\s*(.*)/)
                if (m) fields[m[1].trim().toLowerCase().replace(/\s+/g, '_')] = m[2].trim()
              }
              return (
                <div key={i} className="bg-gray-50 dark:bg-gray-800/50 rounded-lg border p-4">
                  {fields.tindakan && <p className="text-base font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2"><span className="w-6 h-6 rounded-full bg-violet-100 dark:bg-violet-900/30 flex items-center justify-center text-violet-600 dark:text-violet-400 text-xs shrink-0"><FontAwesomeIcon icon={faArrowRight} /></span>{fields.tindakan}</p>}
                  <div className="space-y-2">
                    {fields.alasan && <p className="text-sm text-gray-600 dark:text-gray-400"><span className="font-semibold text-gray-700 dark:text-gray-300">Alasan:</span> {fields.alasan}</p>}
                    {fields.data_pendukung && <p className="text-sm text-gray-500 dark:text-gray-400"><span className="font-semibold text-gray-600 dark:text-gray-400">Data:</span> {fields.data_pendukung}</p>}
                    {fields.dampak && <p className="text-sm text-emerald-600 dark:text-emerald-400"><span className="font-semibold">Dampak:</span> {fields.dampak}</p>}
                  </div>
                </div>
              )
            })}
            {ai.final_recommendation && (
              <div className="bg-gradient-to-r from-violet-50 to-indigo-50 dark:from-violet-950/20 dark:to-indigo-950/20 rounded-lg border border-violet-200 dark:border-violet-900/30 p-4">
                <p className="text-sm font-bold text-violet-700 dark:text-violet-400 mb-2 flex items-center gap-1.5"><FontAwesomeIcon icon={faLightbulb} className="text-violet-500" /> Kesimpulan Akhir</p>
                <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">{ai.final_recommendation}</p>
              </div>
            )}
          </div>
        </Section>

        {/* ═══ NEW: Decision Criteria ═══ */}
        <Section id="kriteria" title="Kriteria Keputusan" icon={faArrowUpWideShort}>
          {/* What Would Change the Decision */}
          <div className="space-y-4">
            {ai.what_would_change_decision && (
              <div className="bg-violet-50 dark:bg-violet-950/20 rounded-lg border border-violet-200 dark:border-violet-900/30 p-4">
                <p className="text-sm font-bold text-violet-700 dark:text-violet-400 mb-2">Apa yang Bisa Mengubah Keputusan</p>
                <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">{ai.what_would_change_decision}</p>
              </div>
            )}

            {decisionCriteria.length > 0 && (
              <div className="space-y-3">
                <p className="text-sm font-semibold text-gray-700 dark:text-gray-300">Kriteria Perubahan Keputusan</p>
                {(decisionCriteria as any[]).map((dc: any, i: number) => (
                  <div key={i} className="bg-gray-50 dark:bg-gray-800/50 rounded-lg border p-4">
                    <div className="flex items-center justify-between gap-3">
                      <p className="text-sm text-gray-700 dark:text-gray-300 flex-1">{dc.condition}</p>
                      <div className="flex items-center gap-2 shrink-0">
                        <span className="text-xs px-2 py-0.5 rounded bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400">{dc.current_decision}</span>
                        <FontAwesomeIcon icon={faArrowRight} className="text-xs text-gray-400" />
                        <span className="text-xs px-2 py-0.5 rounded bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400">{dc.new_decision}</span>
                      </div>
                    </div>
                    {dc.rationale && <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">{dc.rationale}</p>}
                  </div>
                ))}
              </div>
            )}

            {ai.decision_criteria_text && (
              <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4 border">
                <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">{ai.decision_criteria_text}</p>
              </div>
            )}

            {/* Insight Confidences */}
            {insightConfidences.length > 0 && (
              <div className="mt-5">
                <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Confidence per Insight</p>
                <div className="space-y-2">
                  {(insightConfidences as any[]).map((ic: any, i: number) => (
                    <div key={i} className="flex items-center gap-3 text-sm bg-gray-50 dark:bg-gray-800/50 rounded-lg px-4 py-3 border">
                      <span className="font-medium text-gray-900 dark:text-white w-40 truncate">{ic.insight}</span>
                      <span className="text-xs text-gray-500 w-24">{ic.value}</span>
                      <div className="flex-1 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <div className={`h-full rounded-full ${(ic.confidence || 0) >= 60 ? 'bg-emerald-500' : (ic.confidence || 0) >= 40 ? 'bg-amber-500' : 'bg-rose-500'}`} style={{ width: `${ic.confidence || 0}%` }} />
                      </div>
                      <span className="text-xs font-semibold text-gray-600 w-12 text-right">{ic.confidence || 0}%</span>
                      {ic.note && <span className="text-xs text-gray-400 hidden lg:inline">{ic.note}</span>}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {dc.recommended_next_step && (
              <div className="mt-5 bg-gradient-to-r from-emerald-50 to-teal-50 dark:from-emerald-950/20 dark:to-teal-950/20 rounded-lg p-4 border border-emerald-200 dark:border-emerald-900/30">
                <p className="text-sm font-bold text-emerald-700 dark:text-emerald-400 mb-1 flex items-center gap-1.5"><FontAwesomeIcon icon={faArrowRight} className="text-emerald-500" /> Langkah Selanjutnya yang Paling Masuk Akal</p>
                <p className="text-sm text-emerald-600 dark:text-emerald-300">{dc.recommended_next_step}</p>
              </div>
            )}
          </div>
        </Section>

      </div>
    </div>
  )
}

// ── Sub-components ──

function StatCard({ label, value, sub, valueColor }: { label: string; value: React.ReactNode; sub?: string | number; valueColor?: string }) {
  return (
    <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg p-4 text-center border">
      <p className="text-xs text-gray-500 dark:text-gray-400">{label}</p>
      <p className={`text-2xl sm:text-3xl font-bold mt-1 ${valueColor || 'text-gray-900 dark:text-white'}`}>{typeof value === 'number' ? value.toLocaleString() : value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  )
}

function DataCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-violet-50 dark:bg-violet-950/20 rounded-lg px-3.5 py-3 border border-violet-200 dark:border-violet-900/30">
      <p className="text-xs text-gray-500 dark:text-gray-400">{label}</p>
      <p className="text-sm font-semibold text-gray-900 dark:text-white mt-0.5">{value}</p>
    </div>
  )
}

function SWOTBox({ title, color, items, icon }: { title: string; color: string; items: string[]; icon: any }) {
  const colorMap: Record<string, { text: string; bg: string; border: string }> = {
    emerald: { text: 'text-emerald-700 dark:text-emerald-400', bg: 'bg-emerald-50 dark:bg-emerald-950/20', border: 'border-emerald-200 dark:border-emerald-900/30' },
    rose: { text: 'text-rose-700 dark:text-rose-400', bg: 'bg-rose-50 dark:bg-rose-950/20', border: 'border-rose-200 dark:border-rose-900/30' },
    blue: { text: 'text-blue-700 dark:text-blue-400', bg: 'bg-blue-50 dark:bg-blue-950/20', border: 'border-blue-200 dark:border-blue-900/30' },
    amber: { text: 'text-amber-700 dark:text-amber-400', bg: 'bg-amber-50 dark:bg-amber-950/20', border: 'border-amber-200 dark:border-amber-900/30' },
  }
  const c = colorMap[color] || colorMap.emerald
  const iconColor = color === 'emerald' ? 'text-emerald-500' : color === 'rose' ? 'text-rose-500' : color === 'blue' ? 'text-blue-500' : 'text-amber-500'
  return (
    <div className={`${c.bg} rounded-lg p-4 sm:p-5 border ${c.border}`}>
      <p className={`text-sm font-bold ${c.text} flex items-center gap-1.5 mb-3`}><FontAwesomeIcon icon={icon} className={iconColor} /> {title}</p>
      {items.length > 0 ? (
        <ul className="space-y-1.5">{items.map((s, i) => (<li key={i} className={`text-sm ${c.text} flex items-start gap-2`}><FontAwesomeIcon icon={faCheck} className={`${iconColor} mt-0.5 shrink-0 text-[10px]`} />{s}</li>))}</ul>
      ) : (<p className={`text-sm ${c.text} italic`}>Tidak ada data.</p>)}
    </div>
  )
}

function ValidationCard({ question, experiment, success_metric, budget }: any) {
  return (
    <div className="bg-white dark:bg-gray-900 rounded-lg border p-4">
      <p className="text-sm font-semibold text-gray-900 dark:text-white flex items-start gap-2">
        <FontAwesomeIcon icon={faClipboardList} className="text-violet-400 mt-0.5 shrink-0" />
        {question}
      </p>
      <div className="flex flex-wrap gap-2 mt-3">
        {experiment && <span className="text-xs bg-violet-50 dark:bg-violet-950/20 text-violet-600 dark:text-violet-400 px-2.5 py-1 rounded">Eksperimen: {experiment}</span>}
        {success_metric && <span className="text-xs bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-400 px-2.5 py-1 rounded">Sukses: {success_metric}</span>}
        {budget && <span className="text-xs bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 px-2.5 py-1 rounded">Budget: {budget}</span>}
      </div>
    </div>
  )
}

function UnitEconomicsSection({ price_stats, ai_unit_economics_analysis }: { price_stats: { total: number; min: string; min_num: number; max: string; max_num: number; avg: string; avg_num: number; median: string; median_num: number; p25: string; p25_num: number; p75: string; p75_num: number; iqr: number; distribution: Record<string, number> }; ai_unit_economics_analysis?: string }) {
  const [ueResult, setUeResult] = useState<{ sell: number; hpp: number; grossProfit: number; grossMargin: number; breakEven: number } | null>(null)

  return (
    <Section id="ekonomi_unit" title="Unit Economics" icon={faMoneyBillWave}>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
        {ai_unit_economics_analysis || 'Data biaya produksi belum tersedia. Gunakan kalkulator di bawah untuk estimasi.'}
      </p>

      {price_stats.total > 0 && (
        <div className="bg-gray-50 dark:bg-gray-800/50 rounded-lg border p-4 mb-4">
          <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Estimasi Pricing Potential</p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="bg-white dark:bg-gray-900 rounded-lg p-3 border text-center">
              <p className="text-xs text-gray-500">Harga Rata-rata Pasar</p>
              <p className="text-lg font-bold text-violet-600">{price_stats.avg}</p>
            </div>
            <div className="bg-white dark:bg-gray-900 rounded-lg p-3 border text-center">
              <p className="text-xs text-gray-500">Harga Median</p>
              <p className="text-lg font-bold text-gray-900 dark:text-white">{price_stats.median}</p>
            </div>
            <div className="bg-white dark:bg-gray-900 rounded-lg p-3 border text-center">
              <p className="text-xs text-gray-500">P25 (Batas Bawah)</p>
              <p className="text-lg font-bold text-amber-600">{price_stats.p25}</p>
            </div>
            <div className="bg-white dark:bg-gray-900 rounded-lg p-3 border text-center">
              <p className="text-xs text-gray-500">P75 (Batas Atas)</p>
              <p className="text-lg font-bold text-emerald-600">{price_stats.p75}</p>
            </div>
          </div>
          <p className="text-xs text-gray-400 mt-3"><FontAwesomeIcon icon={faInfoCircle} className="mr-1" /> Ini adalah potensi pricing, BUKAN profit. Data HPP diperlukan untuk menghitung profit aktual.</p>
        </div>
      )}

      <div className="bg-white dark:bg-gray-900 rounded-lg border p-4">
        <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Kalkulator Unit Economics</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {[
            { id: 'ue-sell', label: 'Harga Jual (Rp)', def: price_stats.median_num || 25000 },
            { id: 'ue-mat', label: 'Biaya Bahan Baku (Rp)', def: Math.round((price_stats.median_num || 25000) * 0.3) },
            { id: 'ue-lab', label: 'Biaya Tenaga Kerja (Rp)', def: 0 },
            { id: 'ue-pack', label: 'Biaya Packaging (Rp)', def: 2000 },
            { id: 'ue-ship', label: 'Biaya Pengiriman (Rp)', def: 0 },
            { id: 'ue-mkt', label: 'Biaya Marketplace / Marketing (Rp)', def: Math.round((price_stats.median_num || 25000) * 0.15) },
            { id: 'ue-other', label: 'Biaya Lainnya (Rp)', def: 0, fullWidth: true },
          ].map(f => (
            <div key={f.id} className={f.fullWidth ? 'md:col-span-2' : ''}>
              <label className="text-xs text-gray-500 block mb-1">{f.label}</label>
              <input type="number" id={f.id} defaultValue={f.def} className="w-full rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm px-3 py-2" />
            </div>
          ))}
        </div>
        <button onClick={() => {
          const sell = parseFloat((document.getElementById('ue-sell') as HTMLInputElement).value) || 0
          const mat = parseFloat((document.getElementById('ue-mat') as HTMLInputElement).value) || 0
          const lab = parseFloat((document.getElementById('ue-lab') as HTMLInputElement).value) || 0
          const pack = parseFloat((document.getElementById('ue-pack') as HTMLInputElement).value) || 0
          const ship = parseFloat((document.getElementById('ue-ship') as HTMLInputElement).value) || 0
          const mkt = parseFloat((document.getElementById('ue-mkt') as HTMLInputElement).value) || 0
          const other = parseFloat((document.getElementById('ue-other') as HTMLInputElement).value) || 0
          const hpp = mat + lab + pack + ship + mkt + other
          const grossProfit = sell - hpp
          const grossMargin = sell > 0 ? (grossProfit / sell * 100) : 0
          const breakEven = grossProfit > 0 ? Math.ceil((mat + lab + pack + ship + other) / grossProfit) : Infinity
          setUeResult({ sell, hpp, grossProfit, grossMargin, breakEven })
        }} className="mt-3 w-full rounded-lg bg-violet-600 hover:bg-violet-700 text-white text-sm font-medium px-4 py-2.5 transition-colors cursor-pointer">
          Hitung Unit Economics
        </button>

        {ueResult && (
          <div className="mt-4 space-y-2">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-center">
              <div className="bg-white dark:bg-gray-900 rounded p-3 border">
                <p className="text-xs text-gray-500">HPP</p>
                <p className="text-lg font-bold text-rose-600">Rp{ueResult.hpp.toLocaleString()}</p>
              </div>
              <div className="bg-white dark:bg-gray-900 rounded p-3 border">
                <p className="text-xs text-gray-500">Gross Profit</p>
                <p className={`text-lg font-bold ${ueResult.grossProfit <= 0 ? 'text-rose-500' : 'text-emerald-600'}`}>Rp{ueResult.grossProfit.toLocaleString()}</p>
              </div>
              <div className="bg-white dark:bg-gray-900 rounded p-3 border">
                <p className="text-xs text-gray-500">Gross Margin</p>
                <p className={`text-lg font-bold ${ueResult.grossMargin >= 35 ? 'text-emerald-600' : ueResult.grossMargin >= 20 ? 'text-amber-600' : 'text-rose-600'}`}>{ueResult.grossMargin.toFixed(1)}%</p>
              </div>
              <div className="bg-white dark:bg-gray-900 rounded p-3 border">
                <p className="text-xs text-gray-500">Break-even (unit)</p>
                <p className="text-lg font-bold text-violet-600">{isFinite(ueResult.breakEven) ? ueResult.breakEven : '∞'}</p>
              </div>
            </div>
            <p className="text-xs text-gray-500 mt-3">
              {ueResult.grossMargin >= 35 ? '✅ Margin cukup baik. Bisnis memiliki ruang untuk biaya operasional dan promosi.' :
               ueResult.grossMargin >= 20 ? '⚠️ Margin moderat. Perlu volume penjualan yang cukup untuk mencapai profit.' :
               ueResult.grossMargin >= 15 ? '⚠️ Margin tipis. Risiko kerugian tinggi.' :
               '❌ Margin sangat rendah atau negatif. Evaluasi ulang harga jual atau struktur biaya.'}
            </p>
            <p className="text-xs text-gray-400 mt-2"><FontAwesomeIcon icon={faInfoCircle} className="mr-1" /> Estimasi ini berdasarkan input Anda. Hasil aktual dapat berbeda.</p>
          </div>
        )}
      </div>
    </Section>
  )
}
