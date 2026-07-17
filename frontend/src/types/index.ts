export interface Competitor {
  name: string
  rating: number | null
  reviews: number | null
  address: string | null
  hours: string | null
  website: string | null
  phone: string | null
  type: string | null
  maps_link: string
}

export interface PriceItem {
  product: string
  price: string
  price_num: number
  source: string
  merchant: string
}

export interface PriceStats {
  total: number
  min: string
  min_num: number
  max: string
  max_num: number
  avg: string
  avg_num: number
  median: string
  median_num: number
  p25: string
  p25_num: number
  p75: string
  p75_num: number
  iqr: number
  distribution: Record<string, number>
}

export interface TrendItem {
  keyword: string
  interest_values: number[]
  related_queries: string[]
  rising_queries: string[]
  related_topics: string[]
  rising_topics: string[]
}

export interface NewsItem {
  title: string
  content: string
  url: string
}

export interface ReviewStats {
  total_reviews: number
  avg_rating: number
  competitor_count: number
}

export interface MarketGap {
  product: string
  reason: string
}

export interface BenchmarkLabel {
  label: string
  level: string
}

export interface SwotItem {
  strength: string[]
  weakness: string[]
  opportunity: string[]
  threat: string[]
}

export interface ActionPlan {
  phase: string
  tasks: string[]
}

export interface DecisionEngine {
  verdict: string
  verdict_label: string
  confidence: number
  reasons_go: string[]
  reasons_caution: string[]
  opportunity_score: number
  opportunity_reasons_positive: string[]
  opportunity_reasons_negative: string[]
  saturation_score: number
  saturation_reasons: string[]
  demand_benchmark: BenchmarkLabel
  competition_benchmark: BenchmarkLabel
  profit_benchmark: BenchmarkLabel
  trend_benchmark: BenchmarkLabel
  risk_benchmark: BenchmarkLabel
  swot: SwotItem
  market_gaps: MarketGap[]
  action_plan: ActionPlan[]
}

export interface AiAnalysis {
  executive_summary: string
  market_trend_description: string
  competitor_insights: string
  price_insights: string
  news_summary: string
  opportunity_analysis: string
  risk_analysis: string
  recommendation: string
}

export interface BusinessScore {
  demand: number | null
  competition: number | null
  profit_potential: number | null
  trend: number | null
  risk: number | null
  overall: number
  formula_note: string
  data_availability?: Record<string, string>
}

export interface ResearchReport {
  query: string
  business_score: BusinessScore
  decision: DecisionEngine
  competitors: Competitor[]
  review_stats: ReviewStats
  prices: PriceItem[]
  price_stats: PriceStats
  trends: TrendItem[]
  news: NewsItem[]
  ai: AiAnalysis
  total_competitors: number
}
