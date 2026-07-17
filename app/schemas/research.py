from pydantic import BaseModel


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


class ReviewStats(BaseModel):
    total_reviews: int = 0
    avg_rating: float = 0
    competitor_count: int = 0


class MarketGap(BaseModel):
    product: str = ""
    reason: str = ""


# ── Decision Engine ──

class DecisionItem(BaseModel):
    label: str = ""
    status: str = ""  # go / caution / stop
    reason: str = ""


class BenchmarkLabel(BaseModel):
    label: str = ""
    level: str = ""  # Sangat Tinggi / Tinggi / Sedang / Rendah / Sangat Rendah


class SwotItem(BaseModel):
    strength: list[str] = []
    weakness: list[str] = []
    opportunity: list[str] = []
    threat: list[str] = []


class ActionPlan(BaseModel):
    phase: str = ""
    tasks: list[str] = []


class DecisionEngine(BaseModel):
    verdict: str = ""
    verdict_label: str = ""  # GO / GO WITH CAUTION / DON'T START
    confidence: int = 0
    reasons_go: list[str] = []
    reasons_caution: list[str] = []

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


# ── AI description ──

class AiAnalysis(BaseModel):
    executive_summary: str = ""
    market_trend_description: str = ""
    competitor_insights: str = ""
    price_insights: str = ""
    news_summary: str = ""
    opportunity_analysis: str = ""
    risk_analysis: str = ""
    recommendation: str = ""


class BusinessScore(BaseModel):
    demand: int | None = None
    competition: int | None = None
    profit_potential: int | None = None
    trend: int | None = None
    risk: int | None = None
    overall: int = 0
    formula_note: str = ""
    data_availability: dict = {}


class ResearchResponse(BaseModel):
    query: str = ""
    business_score: BusinessScore = BusinessScore()
    decision: DecisionEngine = DecisionEngine()

    competitors: list[Competitor] = []
    total_competitors: int = 0
    review_stats: ReviewStats = ReviewStats()
    prices: list[PriceItem] = []
    price_stats: PriceStats = PriceStats()
    trends: list[TrendItem] = []
    news: list[NewsItem] = []

    ai: AiAnalysis = AiAnalysis()
    total_competitors: int = 0
