from pydantic import BaseModel
from typing import Any


class ResearchRequest(BaseModel):
    query: str
    location: str | None = None
    visitor_id: str = ""


class HistoryQuery(BaseModel):
    visitor_id: str = ""
    search: str = ""
    verdict: str = ""
    sort: str = "newest"


class ReportAction(BaseModel):
    visitor_id: str = ""
    title: str | None = None
    pinned: bool | None = None


# ── Raw parsed data ──

class Competitor(BaseModel):
    name: str = ""
    rating: float | None = None
    reviews: int | None = None
    address: str | None = None
    hours: str | None = None
    website: str | None = None
    phone: str | None = None
    type: str | None = None
    maps_link: str = ""
    source: str = "google_maps"
    query_used: str = ""
    relevance_score: float = 0.0
    competitor_type: str = "direct"


class PriceItem(BaseModel):
    product: str = ""
    price: str = ""
    price_num: float = 0
    source: str = ""
    merchant: str = ""


class PriceStats(BaseModel):
    total: int = 0
    min: str = ""
    min_num: float = 0
    max: str = ""
    max_num: float = 0
    avg: str = ""
    avg_num: float = 0
    median: str = ""
    median_num: float = 0
    p25: str = ""
    p25_num: float = 0
    p75: str = ""
    p75_num: float = 0
    iqr: float = 0
    distribution: dict = {}
    source_data_count: int = 0


class TrendItem(BaseModel):
    keyword: str = ""
    interest_values: list[int] = []
    related_queries: list[str] = []
    rising_queries: list[str] = []
    related_topics: list[str] = []
    rising_topics: list[str] = []


class NewsItem(BaseModel):
    title: str = ""
    content: str = ""
    url: str = ""
    source: str = ""


class ReviewStats(BaseModel):
    total_reviews: int = 0
    avg_rating: float = 0
    competitor_count: int = 0
    median_reviews: int = 0
    rating_distribution: dict = {}
    review_distribution: dict = {}


class MarketGap(BaseModel):
    product: str = ""
    reason: str = ""


# ── Market Statistics ──

class SourceBreakdown(BaseModel):
    google_maps: int = 0
    google_search: int = 0
    google_shopping: int = 0
    google_trends: int = 0
    tavily_news: int = 0


class MarketStatistics(BaseModel):
    total_competitors_detected: int = 0
    total_competitors_analyzed: int = 0
    direct_competitors: int = 0
    indirect_competitors: int = 0
    total_reviews: int = 0
    avg_rating: float = 0
    median_rating: float = 0
    rating_distribution: dict = {}
    review_distribution: dict = {}
    competitors_by_location: dict = {}
    competitors_by_category: dict = {}
    competitors_by_popularity: dict = {}
    avg_reviews_per_competitor: float = 0
    median_reviews: int = 0
    source_breakdown: SourceBreakdown = SourceBreakdown()
    data_limitation_note: str = ""


# ── Evidence-based Opportunity types (NEW) ──

class EvidenceItem(BaseModel):
    description: str = ""
    source: str = ""
    strength: str = ""  # kuat / sedang / lemah


class MarketOpportunity(BaseModel):
    opportunity: str = ""
    evidence: list[EvidenceItem] = []
    counter_evidence: list[str] = []
    confidence: str = ""  # rendah / sedang / tinggi
    gap_type: str = ""  # supply / demand / price / product / geographic / quality / experience
    validation_required: list[str] = []


# ── Demand sub-scores (NEW) ──

class DemandSubScores(BaseModel):
    search_demand: int = 0
    commercial_intent: int = 0
    local_demand: int = 0
    shopping_demand: int = 0
    content_demand: int = 0
    social_demand: int = 0
    overall_demand: int = 0


# ── National / Regional / Local demand (NEW) ──

class DemandBreakdown(BaseModel):
    national: int = 0
    regional: int = 0
    local: int = 0
    local_data_available: bool = False
    note: str = ""


# ── Competitor Intelligence (NEW) ──

class CompetitorStrength(BaseModel):
    name: str = ""
    rating: float = 0.0
    reviews: int = 0
    popularity: str = ""
    brand_visibility: int = 0
    search_visibility: int = 0
    product_variety: int = 0
    price_positioning: str = ""
    strength_score: float = 0.0


class CompetitivePosition(BaseModel):
    price_tier: str = ""
    quality_tier: str = ""
    popularity_tier: str = ""


class CompetitiveMap(BaseModel):
    x_axis: str = "price"
    y_axis: str = "popularity"
    positions: list[CompetitivePosition] = []


# ── Customer Persona (NEW) ──

class CustomerPersona(BaseModel):
    name: str = ""
    description: str = ""
    potential_need: str = ""
    evidence: str = ""
    demand_signal: str = ""
    price_sensitivity: str = ""
    recommended_positioning: str = ""
    is_hypothesis: bool = True


# ── Customer Pain Points (NEW) ──

class PainPoint(BaseModel):
    complaint: str = ""
    frequency: str = ""
    source: str = ""
    opportunity: str = ""
    confidence: str = ""


class PainPointAnalysis(BaseModel):
    top_complaints: list[PainPoint] = []
    unmet_needs: list[str] = []
    opportunities: list[PainPoint] = []


# ── Product Opportunity Matrix (NEW) ──

class ProductOpportunity(BaseModel):
    product: str = ""
    demand: str = ""
    competition: str = ""
    evidence: str = ""
    difficulty: str = ""
    confidence: str = ""


# ── Unit Economics (NEW) ──

class UnitEconomicsInput(BaseModel):
    selling_price: float = 0.0
    raw_material: float = 0.0
    labor: float = 0.0
    packaging: float = 0.0
    shipping: float = 0.0
    marketplace_fee: float = 0.0
    marketing: float = 0.0
    other_costs: float = 0.0


class UnitEconomicsOutput(BaseModel):
    hpp: float = 0.0
    gross_profit: float = 0.0
    gross_margin: float = 0.0
    break_even_units: int = 0
    minimum_sales: int = 0
    estimated_monthly_profit: float = 0.0
    note: str = ""


# ── Price Analysis upgrades (NEW) ──

class PriceSegment(BaseModel):
    name: str = ""
    min: float = 0.0
    max: float = 0.0
    count: int = 0
    percentage: float = 0.0


class PricePerUnit(BaseModel):
    price_per_100g: float = 0.0
    weight_g: float = 0.0


class PricePositioning(BaseModel):
    segments: list[PriceSegment] = []
    sweet_spot: str = ""
    competitive_gap: list[str] = []
    demand_validated_gap: list[str] = []


# ── Decision Change Criteria (NEW) ──

class DecisionChange(BaseModel):
    condition: str = ""
    current_decision: str = ""
    new_decision: str = ""
    rationale: str = ""


# ── Validation Checklist (NEW) ──

class ValidationItem(BaseModel):
    question: str = ""
    priority: str = ""  # wajib / disarankan
    experiment: str = ""
    success_metric: str = ""
    budget: str = ""


class ValidationChecklist(BaseModel):
    must_validate: list[ValidationItem] = []
    recommended: list[ValidationItem] = []


# ── Enhanced Action Plan item (NEW) ──

class ActionPlanV2(BaseModel):
    day_range: str = ""
    goal: str = ""
    actions: list[str] = []
    budget: str = ""
    success_metric: str = ""
    decision_rule: str = ""


# ── Contradiction Detection (NEW) ──

class SignalContradiction(BaseModel):
    signal_a: str = ""
    signal_b: str = ""
    explanation: str = ""
    resolution: str = ""


# ── Data Limitations (NEW) ──

class DataLimitation(BaseModel):
    limitation: str = ""
    impact: str = ""
    mitigation: str = ""


# ── Per-insight confidence (NEW) ──

class InsightConfidence(BaseModel):
    insight: str = ""
    value: str = ""
    confidence: int = 0
    note: str = ""


# ── Enhanced Trends Analysis ──

class TrendsKeywordResult(BaseModel):
    keyword: str = ""
    has_data: bool = False
    status: str = ""
    interest_values: list[int] = []
    avg_interest: float = 0
    peak_interest: int = 0
    lowest_interest: int = 0
    trend_direction: str = ""
    growth_rate: float = 0.0
    data_points: int = 0
    period: str = ""
    related_queries: list[str] = []
    rising_queries: list[str] = []
    # UPGRADE: timeline data
    timeline: list[dict] = []  # [{date, value, month, year}, ...]
    period_type: str = ""  # monthly / yearly


class TrendsAnalysis(BaseModel):
    keywords_analyzed: list[TrendsKeywordResult] = []
    selected_keyword: str = ""
    fallback_used: bool = False
    fallback_reason: str = ""
    has_any_data: bool = False
    avg_interest_all: float = 0
    keyword_count_with_data: int = 0


# ── Decision Engine ──

class DecisionItem(BaseModel):
    label: str = ""
    status: str = ""
    reason: str = ""


class BenchmarkLabel(BaseModel):
    label: str = ""
    level: str = ""


class SwotItem(BaseModel):
    strength: list[str] = []
    weakness: list[str] = []
    opportunity: list[str] = []
    threat: list[str] = []


class ActionPlan(BaseModel):
    phase: str = ""
    tasks: list[str] = []


# ── Score Transparency ──

class ScoreFactor(BaseModel):
    name: str = ""
    contribution: float = 0.0
    weight: float = 0.0
    source: str = ""
    sample_size: int = 0
    data_period: str = ""
    confidence: float = 0.0


class ScoreDetail(BaseModel):
    value: int = 0
    label: str = ""
    factors: list[ScoreFactor] = []
    methodology: str = ""
    confidence: float = 0.0
    data_sources: list[str] = []


class ScoreMethodology(BaseModel):
    demand: ScoreDetail = ScoreDetail()
    competition: ScoreDetail = ScoreDetail()
    profit_potential: ScoreDetail = ScoreDetail()
    trend: ScoreDetail = ScoreDetail()
    risk: ScoreDetail = ScoreDetail()
    overall: ScoreDetail = ScoreDetail()


# ── UPGRADED DecisionEngine ──

class DecisionEngine(BaseModel):
    verdict: str = ""  # SANGAT_LAYAK / LAYAK / LAYAK_DENGAN_SYARAT / PERLU_VALIDASI / BERISIKO_TINGGI / TIDAK_DIREKOMENDASIKAN
    verdict_label: str = ""
    confidence: int = 0
    reasons_go: list[str] = []
    reasons_caution: list[str] = []
    reasons_why_feasible: list[str] = []
    reasons_why_not_feasible: list[str] = []

    opportunity_score: int = 0
    opportunity_reasons_positive: list[str] = []
    opportunity_reasons_negative: list[str] = []
    saturation_score: int = 0
    saturation_reasons: list[str] = []

    demand_benchmark: BenchmarkLabel = BenchmarkLabel()
    competition_benchmark: BenchmarkLabel = BenchmarkLabel()
    profit_benchmark: BenchmarkLabel = BenchmarkLabel()
    trend_benchmark: BenchmarkLabel = BenchmarkLabel()
    risk_benchmark: BenchmarkLabel = BenchmarkLabel()

    insights: list[str] = []
    swot: SwotItem = SwotItem()
    market_gaps: list[MarketGap] = []
    action_plan: list[ActionPlan] = []

    # Score methodology (NEW)
    score_methodology: ScoreMethodology = ScoreMethodology()

    # UPGRADE fields for 33-section report
    verdict_extended: str = ""  # SANGAT_LAYAK / LAYAK / LAYAK_DENGAN_SYARAT / PERLU_VALIDASI / BERISIKO_TINGGI / TIDAK_DIREKOMENDASIKAN
    decision_reasoning: list[str] = []
    strongest_evidence: list[str] = []
    biggest_risk: list[str] = []
    biggest_unknown: list[str] = []
    recommended_next_step: str = ""
    decision_criteria: list[DecisionChange] = []
    validation_checklist: ValidationChecklist = ValidationChecklist()


# ── UPGRADED AiAnalysis (33 sections) ──

class AiAnalysis(BaseModel):
    # Original fields (preserved)
    executive_summary: str = ""
    market_trend_description: str = ""
    competitor_insights: str = ""
    price_insights: str = ""
    news_summary: str = ""
    opportunity_analysis: str = ""
    risk_analysis: str = ""
    recommendation: str = ""
    ai_understanding: str = ""
    market_opportunity: str = ""
    demand_analysis: str = ""
    competition_analysis: str = ""
    product_price_analysis: str = ""
    market_statistics_insight: str = ""
    data_coverage_note: str = ""
    market_gap_analysis: str = ""
    business_recommendation: str = ""

    # UPGRADE: all 33 sections for the final report

    # Section 1-2: Executive & Verdict
    executive_decision: str = ""
    business_verdict: str = ""

    # Section 3: Evidence quality
    confidence_evidence_quality: str = ""

    # Section 4-5: Key signals
    key_positive_signals: str = ""
    key_negative_signals: str = ""

    # Section 6-7: Risks & unknowns
    biggest_risks_analysis: str = ""
    biggest_unknowns_analysis: str = ""

    # Section 8-9: Demand analysis
    demand_analysis_text: str = ""
    local_vs_national_demand: str = ""

    # Section 10: Customer segments
    customer_segments_analysis: str = ""

    # Section 11: Pain points
    customer_pain_points_analysis: str = ""

    # Section 12-13: Competition
    competition_intelligence_analysis: str = ""
    competitive_positioning_map: str = ""

    # Section 14: Google Search landscape
    google_search_landscape: str = ""

    # Section 15: Google Trends
    google_trends_analysis_text: str = ""

    # Section 16: Google Shopping
    google_shopping_analysis: str = ""

    # Section 17-18: Pricing
    market_pricing_analysis: str = ""
    price_positioning_analysis: str = ""

    # Section 19: Market gap
    market_gap_analysis_text: str = ""

    # Section 20-21: Product & customer opportunities
    product_opportunities_analysis: str = ""
    customer_opportunity_analysis: str = ""

    # Section 22: SWOT
    swot_analysis_text: str = ""

    # Section 23-24: Unit economics
    unit_economics_analysis: str = ""
    revenue_scenario: str = ""

    # Section 25: Risk
    risk_analysis_text: str = ""

    # Section 26: Data limitations
    data_limitations_text: str = ""

    # Section 27: Conflicting signals
    conflicting_signals: str = ""

    # Section 28: Validation experiments
    validation_experiments: str = ""

    # Section 29-30: Action plans
    action_plan_7_day: str = ""
    action_plan_30_day: str = ""

    # Section 31-32: Decision criteria
    decision_criteria_text: str = ""
    what_would_change_decision: str = ""

    # Section 33: Final recommendation
    final_recommendation: str = ""


class BusinessScore(BaseModel):
    demand: int | None = None
    competition: int | None = None
    profit_potential: int | None = None
    trend: int | None = None
    risk: int | None = None
    overall: int = 0
    formula_note: str = ""
    data_availability: dict = {}
    demand_label: str = ""
    competition_label: str = ""
    profit_potential_label: str = ""
    trend_label: str = ""
    risk_label: str = ""


class ResearchResponse(BaseModel):
    query: str = ""
    business_score: BusinessScore = BusinessScore()
    decision: DecisionEngine = DecisionEngine()

    competitors: list[Competitor] = []
    total_competitors: int = 0
    total_competitors_detected: int = 0
    review_stats: ReviewStats = ReviewStats()
    market_statistics: MarketStatistics = MarketStatistics()
    prices: list[PriceItem] = []
    price_stats: PriceStats = PriceStats()
    trends: list[TrendItem] = []
    news: list[NewsItem] = []

    ai: AiAnalysis = AiAnalysis()
    trends_analysis: TrendsAnalysis = TrendsAnalysis()
    score_methodology: ScoreMethodology = ScoreMethodology()
    data_coverage: dict = {}

    # NEW top-level fields for upgraded research response
    demand_sub_scores: DemandSubScores = DemandSubScores()
    demand_breakdown: DemandBreakdown = DemandBreakdown()
    competitor_strengths: list[CompetitorStrength] = []
    competitive_map: CompetitiveMap = CompetitiveMap()
    customer_personas: list[CustomerPersona] = []
    pain_point_analysis: PainPointAnalysis = PainPointAnalysis()
    product_opportunities: list[ProductOpportunity] = []
    unit_economics_input: UnitEconomicsInput | None = None
    unit_economics_output: UnitEconomicsOutput | None = None
    price_positioning: PricePositioning = PricePositioning()
    validation_checklist: ValidationChecklist = ValidationChecklist()
    action_plan_v2: list[ActionPlanV2] = []
    contradictions: list[SignalContradiction] = []
    data_limitations: list[DataLimitation] = []
    insight_confidences: list[InsightConfidence] = []
    market_opportunities: list[MarketOpportunity] = []
