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
  source?: string
  query_used?: string
  relevance_score?: number
  competitor_type?: string
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
  source_data_count?: number
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
  source?: string
}

export interface ReviewStats {
  total_reviews: number
  avg_rating: number
  competitor_count: number
  median_reviews?: number
  rating_distribution?: Record<string, number>
  review_distribution?: Record<string, number>
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

export interface ScoreFactor {
  name: string
  contribution: number
  weight: number
  source: string
  sample_size: number
  data_period: string
  confidence: number
}

export interface ScoreDetail {
  value: number
  label: string
  factors: ScoreFactor[]
  methodology: string
  confidence: number
  data_sources: string[]
}

export interface ScoreMethodology {
  demand: ScoreDetail
  competition: ScoreDetail
  profit_potential: ScoreDetail
  trend: ScoreDetail
  risk: ScoreDetail
  overall: ScoreDetail
}

export interface SourceBreakdown {
  google_maps: number
  google_search: number
  google_shopping: number
  google_trends: number
  tavily_news: number
}

export interface MarketStatistics {
  total_competitors_detected: number
  total_competitors_analyzed: number
  direct_competitors: number
  indirect_competitors: number
  total_reviews: number
  avg_rating: number
  median_rating: number
  rating_distribution: Record<string, number>
  review_distribution: Record<string, number>
  competitors_by_location: Record<string, number>
  competitors_by_category: Record<string, number>
  competitors_by_popularity: Record<string, number>
  avg_reviews_per_competitor: number
  median_reviews: number
  source_breakdown: SourceBreakdown
  data_limitation_note: string
}

// ── Evidence-based Opportunity types ──

export interface EvidenceItem {
  description: string
  source: string
  strength: string
}

export interface MarketOpportunity {
  opportunity: string
  evidence: EvidenceItem[]
  counter_evidence: string[]
  confidence: string
  gap_type: string
  validation_required: string[]
}

// ── Demand sub-scores ──

export interface DemandSubScores {
  search_demand: number
  commercial_intent: number
  local_demand: number
  shopping_demand: number
  content_demand: number
  social_demand: number
  overall_demand: number
}

// ── National / Regional / Local demand ──

export interface DemandBreakdown {
  national: number
  regional: number
  local: number
  local_data_available: boolean
  note: string
}

// ── Competitor Intelligence ──

export interface CompetitorStrength {
  name: string
  rating: number
  reviews: number
  popularity: string
  brand_visibility: number
  search_visibility: number
  product_variety: number
  price_positioning: string
  strength_score: number
}

export interface CompetitivePosition {
  price_tier: string
  quality_tier: string
  popularity_tier: string
}

export interface CompetitiveMap {
  x_axis: string
  y_axis: string
  positions: CompetitivePosition[]
}

// ── Customer Persona ──

export interface CustomerPersona {
  name: string
  description: string
  potential_need: string
  evidence: string
  demand_signal: string
  price_sensitivity: string
  recommended_positioning: string
  is_hypothesis: boolean
}

// ── Customer Pain Points ──

export interface PainPoint {
  complaint: string
  frequency: string
  source: string
  opportunity: string
  confidence: string
}

export interface PainPointAnalysis {
  top_complaints: PainPoint[]
  unmet_needs: string[]
  opportunities: PainPoint[]
}

// ── Product Opportunity Matrix ──

export interface ProductOpportunity {
  product: string
  demand: string
  competition: string
  evidence: string
  difficulty: string
  confidence: string
}

// ── Unit Economics ──

export interface UnitEconomicsInput {
  selling_price: number
  raw_material: number
  labor: number
  packaging: number
  shipping: number
  marketplace_fee: number
  marketing: number
  other_costs: number
}

export interface UnitEconomicsOutput {
  hpp: number
  gross_profit: number
  gross_margin: number
  break_even_units: number
  minimum_sales: number
  estimated_monthly_profit: number
  note: string
}

// ── Price Analysis ──

export interface PriceSegment {
  name: string
  min: number
  max: number
  count: number
  percentage: number
}

export interface PricePerUnit {
  price_per_100g: number
  weight_g: number
}

export interface PricePositioning {
  segments: PriceSegment[]
  sweet_spot: string
  competitive_gap: string[]
  demand_validated_gap: string[]
}

// ── Decision Change Criteria ──

export interface DecisionChange {
  condition: string
  current_decision: string
  new_decision: string
  rationale: string
}

// ── Validation Checklist ──

export interface ValidationItem {
  question: string
  priority: string
  experiment: string
  success_metric: string
  budget: string
}

export interface ValidationChecklist {
  must_validate: ValidationItem[]
  recommended: ValidationItem[]
}

// ── Enhanced Action Plan ──

export interface ActionPlanV2 {
  day_range: string
  goal: string
  actions: string[]
  budget: string
  success_metric: string
  decision_rule: string
}

// ── Contradiction Detection ──

export interface SignalContradiction {
  signal_a: string
  signal_b: string
  explanation: string
  resolution: string
}

// ── Data Limitations ──

export interface DataLimitation {
  limitation: string
  impact: string
  mitigation: string
}

// ── Per-insight confidence ──

export interface InsightConfidence {
  insight: string
  value: string
  confidence: number
  note: string
}

// ── Trends Analysis (UPGRADED) ──

export interface TrendsKeywordResult {
  keyword: string
  has_data: boolean
  status: string
  interest_values: number[]
  avg_interest?: number
  peak_interest?: number
  lowest_interest?: number
  trend_direction?: string
  growth_rate?: number
  data_points?: number
  period?: string
  related_queries: string[]
  rising_queries: string[]
  timeline: Array<{ date: string; value: number; month: string; year: number }>
  period_type: string
}

export interface TrendsAnalysis {
  keywords_analyzed: TrendsKeywordResult[]
  selected_keyword: string
  fallback_used: boolean
  fallback_reason: string
  has_any_data: boolean
  avg_interest_all?: number
  keyword_count_with_data?: number
}

// ── Decision Engine (UPGRADED) ──

export interface DecisionEngine {
  verdict: string
  verdict_label: string
  confidence: number
  reasons_go: string[]
  reasons_caution: string[]
  reasons_why_feasible: string[]
  reasons_why_not_feasible: string[]
  opportunity_score: number
  opportunity_reasons_positive: string[]
  opportunity_reasons_negative: string[]
  saturation_score: number
  saturation_reasons: string[]
  insights: string[]
  demand_benchmark: BenchmarkLabel
  competition_benchmark: BenchmarkLabel
  profit_benchmark: BenchmarkLabel
  trend_benchmark: BenchmarkLabel
  risk_benchmark: BenchmarkLabel
  swot: SwotItem
  market_gaps: MarketGap[]
  action_plan: ActionPlan[]
  score_methodology?: ScoreMethodology
  // UPGRADE fields
  verdict_extended: string
  decision_reasoning: string[]
  strongest_evidence: string[]
  biggest_risk: string[]
  biggest_unknown: string[]
  recommended_next_step: string
  decision_criteria: DecisionChange[]
  validation_checklist: ValidationChecklist
}

// ── AI Analysis (UPGRADED — 33 sections) ──

export interface AiAnalysis {
  executive_summary: string
  market_trend_description: string
  competitor_insights: string
  price_insights: string
  news_summary: string
  opportunity_analysis: string
  risk_analysis: string
  recommendation: string
  ai_understanding?: string
  market_opportunity?: string
  demand_analysis?: string
  competition_analysis?: string
  product_price_analysis?: string
  market_statistics_insight?: string
  data_coverage_note?: string
  market_gap_analysis?: string
  business_recommendation?: string
  // 33-section upgrade fields
  executive_decision: string
  business_verdict: string
  confidence_evidence_quality: string
  key_positive_signals: string
  key_negative_signals: string
  biggest_risks_analysis: string
  biggest_unknowns_analysis: string
  demand_analysis_text: string
  local_vs_national_demand: string
  customer_segments_analysis: string
  customer_pain_points_analysis: string
  competition_intelligence_analysis: string
  competitive_positioning_map: string
  google_search_landscape: string
  google_trends_analysis_text: string
  google_shopping_analysis: string
  market_pricing_analysis: string
  price_positioning_analysis: string
  market_gap_analysis_text: string
  product_opportunities_analysis: string
  customer_opportunity_analysis: string
  swot_analysis_text: string
  unit_economics_analysis: string
  revenue_scenario: string
  risk_analysis_text: string
  data_limitations_text: string
  conflicting_signals: string
  validation_experiments: string
  action_plan_7_day: string
  action_plan_30_day: string
  decision_criteria_text: string
  what_would_change_decision: string
  final_recommendation: string
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
  demand_label?: string
  competition_label?: string
  profit_potential_label?: string
  trend_label?: string
  risk_label?: string
  price_stats?: PriceStats
  review_stats?: ReviewStats
  competitor_count?: number
}

// ── Research Report (UPGRADED) ──

export interface ResearchReport {
  query: string
  business_score: BusinessScore
  decision: DecisionEngine
  competitors: Competitor[]
  total_competitors: number
  total_competitors_detected?: number
  review_stats: ReviewStats
  market_statistics?: MarketStatistics
  prices: PriceItem[]
  price_stats: PriceStats
  trends: TrendItem[]
  news: NewsItem[]
  ai: AiAnalysis
  trends_analysis?: TrendsAnalysis
  score_methodology?: ScoreMethodology
  data_coverage?: Record<string, number | string>
  query_context?: any
  queries_used?: any
  // UPGRADE fields
  demand_sub_scores: DemandSubScores
  demand_breakdown: DemandBreakdown
  competitor_strengths: CompetitorStrength[]
  competitive_map: CompetitiveMap
  customer_personas: CustomerPersona[]
  pain_point_analysis: PainPointAnalysis
  product_opportunities: ProductOpportunity[]
  unit_economics_input: UnitEconomicsInput | null
  unit_economics_output: UnitEconomicsOutput | null
  price_positioning: PricePositioning
  validation_checklist: ValidationChecklist
  action_plan_v2: ActionPlanV2[]
  contradictions: SignalContradiction[]
  data_limitations: DataLimitation[]
  insight_confidences: InsightConfidence[]
  market_opportunities: MarketOpportunity[]
}
