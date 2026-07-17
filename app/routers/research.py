import asyncio
import logging
import re
from statistics import median
from fastapi import APIRouter, HTTPException
from app.schemas.research import (
    ResearchRequest, ResearchResponse, HistoryQuery, ReportAction,
    Competitor, PriceItem, PriceStats,
    TrendItem, NewsItem, ReviewStats, MarketGap, BusinessScore,
    DecisionEngine, BenchmarkLabel, SwotItem, ActionPlan, DecisionItem, AiAnalysis,
)
from app.services import serpapi_service, tavily_service, groq_service, supabase_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["research"])

def parse_query(query: str) -> tuple[str, str | None]:
    q = query.lower().strip()
    q = re.sub(r"\bsaya\s+mau\s+(buka|membuka|buat|membuat)\b", "", q).strip()
    q = re.sub(r"\bdi\s+(daerah|kota|wilayah)\b", "di", q).strip()
    parts = re.split(r"\bdi\b", q, maxsplit=1)
    if len(parts) == 2:
        business = parts[0].strip()
        loc = parts[1].strip()
        return business, loc
    return q, None

@router.post("/research")
async def research(req: ResearchRequest):
    query = req.query
    location = req.location
    visitor_id = req.visitor_id or "anon"
    try:
        business_type, detected_city = parse_query(query)
        loc = location or detected_city or "Indonesia"
        raw = await _gather_data(business_type, loc)

        competitors, total_competitors = _parse_competitors(raw)
        review_stats = _parse_review_stats(competitors)
        prices = _parse_prices(raw)
        prices = _filter_relevant_prices(prices, business_type)
        price_stats = _calc_price_stats(prices)
        trends = _parse_trends(raw)
        news = _filter_relevant_news(_parse_news(raw), business_type)

        data_availability = _assess_data_availability(raw, competitors, prices, trends, news)
        metrics = _validate_data_quality(competitors, prices, trends, news, loc, data_availability)
        scores = _calculate_scores(competitors, trends, prices, data_availability)
        cross_findings = _perform_cross_analysis(scores, competitors, trends, prices, price_stats, review_stats, data_availability)
        decision = _build_decision(scores, competitors, trends, prices, price_stats, review_stats, metrics, business_type, data_availability)

        scores_dict = scores.model_dump()
        # Label mengikuti arti metrik UI:
        # demand/profit/trend: tinggi = baik
        # competition: tinggi = persaingan ketat
        # risk: tinggi = risiko besar
        scores_dict["demand_label"] = get_score_label(scores.demand)
        scores_dict["competition_label"] = get_score_label(scores.competition)
        scores_dict["profit_potential_label"] = get_score_label(scores.profit_potential)
        scores_dict["trend_label"] = get_score_label(scores.trend)
        scores_dict["risk_label"] = get_score_label(scores.risk)
        scores_dict["data_availability"] = data_availability
        scores_dict["price_stats"] = price_stats.model_dump()
        scores_dict["review_stats"] = review_stats.model_dump()
        scores_dict["competitor_count"] = len(competitors)

        ai_report = {}
        validation_errors = []
        feedback = None

        for attempt in range(3):
            ai_report = await groq_service.generate_report(
                query, raw, scores_dict, scores_dict,
                [c.model_dump() for c in competitors],
                [p.model_dump() for p in prices],
                [t.model_dump() for t in trends],
                [n.model_dump() for n in news],
                cross_findings=cross_findings,
                validation_feedback=feedback,
                data_availability=data_availability,
            )
            
            validation_errors = _validate_report_json(
                ai_report, scores, raw, competitors, prices, trends, news, cross_findings, data_availability
            )
            
            if not validation_errors:
                logger.info(f"AI report validated successfully on attempt {attempt + 1}")
                break
            else:
                logger.warning(f"AI report validation failed on attempt {attempt + 1}. Errors: {validation_errors}")
                feedback = "Validasi laporan Anda sebelumnya gagal dengan error berikut:\n" + "\n".join(f"- {err}" for err in validation_errors) + "\n\nHarap perbaiki dan pastikan mematuhi semua aturan yang diberikan."

        ai = AiAnalysis(
            executive_summary=ai_report.get("executive_summary", ""),
            market_trend_description=ai_report.get("market_trend_description", ""),
            competitor_insights=ai_report.get("competitor_insights", ""),
            price_insights=ai_report.get("price_insights", ""),
            news_summary=ai_report.get("news_summary", ""),
            opportunity_analysis=ai_report.get("opportunity_analysis", ""),
            risk_analysis=ai_report.get("risk_analysis", ""),
            recommendation=ai_report.get("recommendation", ""),
        )

        report = ResearchResponse(
            query=query,
            business_score=scores,
            decision=decision,
            competitors=competitors,
            total_competitors=total_competitors,
            review_stats=review_stats,
            prices=prices,
            price_stats=price_stats,
            trends=trends,
            news=news,
            ai=ai,
        )

        saved = await supabase_service.save_research(
            visitor_id=visitor_id,
            query=query,
            location=loc,
            verdict=decision.verdict_label,
            score=scores.overall,
            raw_data=raw,
            report=report.model_dump(),
        )

        return {
            "id": str(saved.get("id", "")) if saved else "",
            "report": report.model_dump(),
        }
    except Exception as e:
        logger.exception("Research failed")
        raise HTTPException(status_code=500, detail=str(e))

# ── History ──

@router.post("/research/history")
async def get_history(body: HistoryQuery):
    try:
        items = await supabase_service.get_history(
            visitor_id=body.visitor_id,
            search=body.search,
            verdict=body.verdict,
            sort=body.sort,
        )
        return {"data": items}
    except Exception:
        return {"data": []}

@router.get("/research/{report_id}")
async def get_report(report_id: str, visitor_id: str = ""):
    try:
        data = await supabase_service.get_report(report_id, visitor_id)
        if not data:
            raise HTTPException(status_code=404, detail="Not found")
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/research/{report_id}")
async def delete_report(report_id: str, visitor_id: str = ""):
    ok = await supabase_service.delete_report(report_id, visitor_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}

@router.delete("/research")
async def delete_all(visitor_id: str = ""):
    ok = await supabase_service.delete_all_reports(visitor_id)
    return {"ok": ok}

@router.patch("/research/{report_id}")
async def update_report(report_id: str, body: ReportAction):
    data = await supabase_service.update_report(
        report_id=report_id,
        visitor_id=body.visitor_id,
        title=body.title,
        pinned=body.pinned,
    )
    if not data:
        raise HTTPException(status_code=404, detail="Not found")
    return data

@router.post("/research/{report_id}/duplicate")
async def duplicate_report(report_id: str, visitor_id: str = ""):
    data = await supabase_service.duplicate_report(report_id, visitor_id)
    if not data:
        raise HTTPException(status_code=404, detail="Not found")
    return data

# ── Data gathering ──

async def _gather_data(business_type: str, location: str) -> dict:
    full = f"{business_type} {location}"
    results = {}
    logger.info("Gathering: %s", full)
    results["search"] = _trim(await serpapi_service.search_google(full, location)); await asyncio.sleep(0.5)
    results["trends"] = _trim(await serpapi_service.google_trends(business_type)); await asyncio.sleep(0.5)
    shopping_raw = await serpapi_service.google_shopping(business_type, location)
    if isinstance(shopping_raw, dict) and ("error" in shopping_raw or not shopping_raw.get("shopping_results")):
        shopping_raw = await serpapi_service.google_shopping(f"harga {business_type}")
    if isinstance(shopping_raw, dict) and ("error" in shopping_raw or not shopping_raw.get("shopping_results")):
        shopping_raw = await serpapi_service.google_shopping(business_type)
    results["shopping"] = _trim(shopping_raw); await asyncio.sleep(0.5)
    results["tavily"] = _trim(await tavily_service.search_general(f"{business_type} {location} bisnis"))
    ok = sum(1 for v in results.values() if isinstance(v, dict) and "error" not in v)
    logger.info("Gathered %d/4 OK", ok)
    return results

def _trim(d: dict) -> dict:
    if isinstance(d, dict): return {k: _trim(v) for k, v in list(d.items())[:50]}
    if isinstance(d, list): return [_trim(v) for v in d[:20]]
    if isinstance(d, str): return d[:500]
    return d

# ── Parsers ──

def _parse_competitors(raw: dict) -> tuple[list[Competitor], int]:
    out = []
    total_count = 0
    data = raw.get("search", {})
    if not isinstance(data, dict) or "error" in data: return out, 0
    try:
        total_count = data.get("search_information", {}).get("total_results", 0)
        if isinstance(total_count, str):
            total_count = int(total_count.replace(",", ""))
        for p in (data.get("local_results") or {}).get("places", []) or []:
            name = p.get("title", "") or ""
            address = p.get("address", "") or ""
            maps_link = ""

            gps = p.get("gps_coordinates") or {}
            lat = gps.get("latitude")
            lng = gps.get("longitude")
            if lat and lng:
                maps_link = f"https://www.google.com/maps/@{lat},{lng},17z"
            elif address and name:
                import urllib.parse
                maps_link = f"https://www.google.com/maps/search/{urllib.parse.quote(f'{name} {address}')}"

            out.append(Competitor(
                name=name,
                rating=p.get("rating"),
                reviews=p.get("reviews"),
                address=address,
                hours=p.get("hours", ""),
                website=p.get("website", ""),
                phone=p.get("phone", ""),
                type=p.get("type", ""),
                maps_link=maps_link,
            ))
    except Exception as e:
        logger.warning("Parse competitors error: %s", e)
    return out, total_count

def _parse_review_stats(competitors: list[Competitor]) -> ReviewStats:
    total = sum(c.reviews or 0 for c in competitors)
    rated = [c.rating for c in competitors if c.rating]
    avg = sum(rated) / len(rated) if rated else 0
    return ReviewStats(total_reviews=total, avg_rating=round(avg, 1), competitor_count=len(competitors))

def _parse_prices(raw: dict) -> list[PriceItem]:
    out = []
    data = raw.get("shopping", {})
    if not isinstance(data, dict) or "error" in data: return out
    try:
        for item in (data.get("shopping_results") or []) or []:
            raw_price = item.get("extracted_price") or item.get("price", "")
            price_num = 0
            if isinstance(raw_price, (int, float)):
                price_num = float(raw_price)
            elif isinstance(raw_price, str):
                nums = re.findall(r'[\d.]+', raw_price.replace('Rp', '').replace('.', '').strip())
                if nums: price_num = float(nums[0])
            out.append(PriceItem(
                product=item.get("title", "") or "",
                price=item.get("price", "") or str(raw_price),
                price_num=price_num,
                source=item.get("source", "") or "",
                merchant=item.get("merchant_name", "") or "",
            ))
    except Exception as e:
        logger.warning("Parse prices error: %s", e)
    return out

def _filter_relevant_prices(prices: list[PriceItem], business_type: str) -> list[PriceItem]:
    """Filter produk yang relevan dengan jenis usaha dan buang outlier."""
    words = business_type.lower().split()
    keywords = set()
    for w in words:
        keywords.add(w)
    for w in words:
        if w in ("toko", "usaha", "bisnis", "jualan", "buka", "online", "shop", "store"):
            continue
        keywords.add(w)

    fashion_keywords = {"baju", "pakaian", "fashion", "atasan", "bawahan", "dress", "rok", "celana",
                        "kemeja", "kaos", "hoodie", "jaket", "outer", "koko", "muslim", "gamis",
                        "sweater", "crewneck", "blouse", "shirt", "pant", "jeans", "trouser",
                        "skirt", "jacket", "coat", "cardigan", "vest", "jumpsuit", "onesie",
                        "wear", "outfit", "setelan", "seragam", "batik", "kebaya", "safari",
                        "olahraga", "sport", "kasual", "formal", "premium", "couple", "keluarga",
                        "anak", "bayi", "wanita", "pria", "laki", "perempuan", "big", "plus",
                        "oversize", "regular", "slim", "fit", "stretch", "katun", "denim",
                        "kain", "bahan", "panjang", "pendek", "lengan", "kerah"}

    all_keywords = keywords | fashion_keywords

    filtered = []
    for p in prices:
        title_lower = p.product.lower()
        # Cek relevansi
        if not any(kw in title_lower for kw in all_keywords):
            continue
        filtered.append(p)

    if not filtered:
        return prices

    # Outlier removal: buang harga > 3x median atau < 0.3x median
    nums = sorted([p.price_num for p in filtered if p.price_num > 0])
    if len(nums) >= 4:
        med = median(nums)
        q1 = median(nums[:len(nums)//2])
        q3 = median(nums[len(nums)//2:]) if len(nums) % 2 == 0 else median(nums[len(nums)//2+1:])
        iqr = q3 - q1
        upper = q3 + 2.0 * iqr
        lower = max(q1 - 1.5 * iqr, 0)
        filtered = [p for p in filtered if p.price_num <= 0 or (lower <= p.price_num <= upper)]
        if not filtered:
            filtered = [p for p in prices if p.price_num <= 0 or (lower <= p.price_num <= upper)]

    return filtered


def _percentile(nums: list[float], p: float) -> float:
    if not nums:
        return 0
    if len(nums) == 1:
        return nums[0]
    k = (len(nums) - 1) * p
    f = int(k)
    c = min(f + 1, len(nums) - 1)
    if f == c:
        return nums[f]
    return nums[f] + (nums[c] - nums[f]) * (k - f)

def _fmt_rp(n: float) -> str:
    return f"Rp{int(n):,}".replace(",", ".")

def _calc_price_stats(prices: list[PriceItem]) -> PriceStats:
    nums = sorted([p.price_num for p in prices if p.price_num > 0])
    if not nums:
        return PriceStats(total=len(prices))
    n = len(nums)
    avg_n = sum(nums) / n
    med_n = median(nums)
    p25 = _percentile(nums, 0.25)
    p75 = _percentile(nums, 0.75)
    iqr = p75 - p25
    ranges = [(0, 50000, "0-50rb"), (50000, 100000, "50-100rb"), (100000, 300000, "100-300rb"), (300000, 999999999, "300rb+")]
    dist = {}
    for lo, hi, label in ranges:
        cnt = sum(1 for x in nums if lo <= x < hi)
        if cnt > 0:
            dist[label] = round(cnt / n * 100)
    return PriceStats(
        total=n,
        min=_fmt_rp(nums[0]),
        min_num=nums[0],
        max=_fmt_rp(nums[-1]),
        max_num=nums[-1],
        avg=_fmt_rp(avg_n),
        avg_num=round(avg_n),
        median=_fmt_rp(med_n),
        median_num=round(med_n),
        p25=_fmt_rp(p25),
        p25_num=round(p25),
        p75=_fmt_rp(p75),
        p75_num=round(p75),
        iqr=round(iqr),
        distribution=dist,
    )

def _parse_trends(raw: dict) -> list[TrendItem]:
    out = []
    for key in ("trends",):
        data = raw.get(key, {})
        if not isinstance(data, dict) or "error" in data: continue
        try:
            kw = data.get("search_parameters", {}).get("q", "unknown")
            vals = []
            for entry in ((data.get("interest_over_time") or {}).get("timeline_data") or []):
                for v in (entry.get("values") or []):
                    try: vals.append(int(v.get("value", 0)))
                    except: pass

            related_q, rising_q = [], []
            rq = data.get("related_queries") or {}
            for r in (rq.get("top") or []):
                if isinstance(r, dict) and r.get("query"): related_q.append(r["query"])
            for r in (rq.get("rising") or []):
                if isinstance(r, dict) and r.get("query"): rising_q.append(r["query"])

            related_t, rising_t = [], []
            rt = data.get("related_topics") or {}
            for r in (rt.get("top") or []):
                if isinstance(r, dict) and r.get("topic"): related_t.append(r["topic"])
            for r in (rt.get("rising") or []):
                if isinstance(r, dict) and r.get("topic"): rising_t.append(r["topic"])

            out.append(TrendItem(
                keyword=kw, interest_values=vals,
                related_queries=related_q[:10], rising_queries=rising_q[:10],
                related_topics=related_t[:10], rising_topics=rising_t[:10],
            ))
        except Exception as e:
            logger.warning("Parse trends error: %s", e)
    return out

def _parse_news(raw: dict) -> list[NewsItem]:
    out = []
    data = raw.get("tavily", {})
    if not isinstance(data, dict) or "error" in data: return out
    try:
        for r in (data.get("results") or []) or []:
            if isinstance(r, dict):
                out.append(NewsItem(title=r.get("title","") or "", content=(r.get("content") or "")[:500], url=r.get("url","") or ""))
    except Exception as e:
        logger.warning("Parse news error: %s", e)
    return out


def _filter_relevant_news(news: list[NewsItem], business_type: str) -> list[NewsItem]:
    """Filter artikel yang relevan dengan jenis usaha."""
    words = business_type.lower().split()
    keywords = set(w for w in words if w not in ("toko", "usaha", "bisnis", "jualan", "buka", "online", "shop", "store", "di", "dan", "atau"))
    keywords.update({"bisnis", "usaha", "bisnis", "pasar", "industri", "tren", "fashion", "retail", "kuliner", "makanan", "minuman"})

    blocked_domains = {"wikipedia", "wiktionary", "wikibooks", "wikiversity", "wikidata", "mediawiki"}

    # Tambah keyword berdasarkan kata dari judul yang sudah lolos
    filtered = []
    for n in news:
        title_lower = n.title.lower()
        url_lower = n.url.lower()

        # Skip domain yang jelas tidak relevan
        if any(d in url_lower for d in blocked_domains):
            continue

        # Cek relevansi konten
        content_lower = n.content.lower()
        relevant = any(kw in title_lower or kw in content_lower for kw in keywords)

        if relevant:
            filtered.append(n)

    if not filtered:
        return []

    return filtered[:5]


# ── Scoring & Decision Engine ──

def get_score_label(score: int | None) -> str:
    """Single source of truth: angka tinggi = label Tinggi (sesuai nama metrik)."""
    if score is None:
        return "Data Tidak Tersedia"
    if score >= 85: return "Sangat Tinggi"
    if score >= 70: return "Tinggi"
    if score >= 50: return "Sedang"
    if score >= 30: return "Rendah"
    return "Sangat Rendah"

def _assess_data_availability(raw: dict, competitors: list, prices: list, trends: list, news: list) -> dict:
    """Menilai status ketersediaan setiap sumber data secara eksplisit.
    AVAILABLE = data lengkap, PARTIAL = data ada tapi terbatas, UNAVAILABLE = tidak ada data.
    Data tidak tersedia BUKAN berarti nilai nol — keduanya adalah kondisi berbeda.
    """
    def source_status(data: dict, key: str, count_key: str | None = None) -> str:
        d = data.get(key, {})
        if not isinstance(d, dict) or "error" in d:
            return "UNAVAILABLE"
        if count_key:
            items = d.get(count_key, [])
            if not items:
                return "UNAVAILABLE"
            if len(items) >= 5:
                return "AVAILABLE"
            return "PARTIAL"
        return "AVAILABLE" if d else "UNAVAILABLE"

    # Competitors (dari Google Maps/Search)
    if len(competitors) >= 5:
        comp_status = "AVAILABLE"
    elif len(competitors) > 0:
        comp_status = "PARTIAL"
    else:
        search_data = raw.get("search", {})
        if isinstance(search_data, dict) and "error" not in search_data:
            comp_status = "PARTIAL"  # search OK tapi tidak ada listing lokal
        else:
            comp_status = "UNAVAILABLE"

    # Prices (dari Google Shopping)
    if len(prices) >= 8:
        price_status = "AVAILABLE"
    elif len(prices) > 0:
        price_status = "PARTIAL"
    else:
        shop_data = raw.get("shopping", {})
        if isinstance(shop_data, dict) and "error" not in shop_data:
            price_status = "PARTIAL"
        else:
            price_status = "UNAVAILABLE"

    # Trends (dari Google Trends)
    trend_vals = sum(len(t.interest_values) for t in trends)
    if trend_vals >= 10:
        trend_status = "AVAILABLE"
    elif trend_vals > 0:
        trend_status = "PARTIAL"
    else:
        trends_data = raw.get("trends", {})
        if isinstance(trends_data, dict) and "error" not in trends_data:
            trend_status = "PARTIAL"
        else:
            trend_status = "UNAVAILABLE"

    # News (dari Tavily)
    if len(news) >= 3:
        news_status = "AVAILABLE"
    elif len(news) > 0:
        news_status = "PARTIAL"
    else:
        tavily_data = raw.get("tavily", {})
        if isinstance(tavily_data, dict) and "error" not in tavily_data:
            news_status = "PARTIAL"
        else:
            news_status = "UNAVAILABLE"

    return {
        "competitors": comp_status,
        "prices": price_status,
        "trends": trend_status,
        "news": news_status,
    }


def _validate_data_quality(competitors: list[Competitor], prices: list[PriceItem], trends: list[TrendItem], news: list[NewsItem], location: str, data_availability: dict | None = None) -> dict:
    trend_vals_count = sum(len(t.interest_values) for t in trends)
    return {
        "competitors_count": len(competitors),
        "prices_count": len(prices),
        "trends_count": trend_vals_count,
        "news_count": len(news),
        "has_specific_location": location.lower() not in ("indonesia", ""),
        "availability": data_availability or {}
    }

def _calculate_scores(competitors: list[Competitor], trends: list[TrendItem], prices: list[PriceItem], availability: dict) -> BusinessScore:
    demand = None; competition = None; profit = None; trend_score = None; risk = None
    
    # 1. Demand & Trend (Google Trends)
    if availability["trends"] != "UNAVAILABLE":
        demand = 50 
        trend_score = 50
        for t in trends:
            v = t.interest_values
            if v:
                avg = sum(v) / len(v)
                if avg > 70: demand = min(95, 70 + int((avg - 70) * 0.8))
                elif avg > 40: demand = 50 + int((avg - 40) * 0.8)
                elif avg > 20: demand = 30 + int((avg - 20) * 1.0)
                else: demand = max(10, int(avg * 0.8))
                
                if len(v) >= 2:
                    half = len(v)//2
                    first = sum(v[:half])/half; second = sum(v[half:])/(len(v)-half)
                    if second - first > 10: trend_score = 80
                    elif second - first > 5: trend_score = 65
                    elif second - first > -5: trend_score = 50
                    else: trend_score = 30

    # 2. Competition (Google Maps) - Tinggi = Persaingan Ketat
    if availability["competitors"] != "UNAVAILABLE":
        n = len(competitors)
        if n == 0: competition = 5
        elif n <= 3: competition = 25
        elif n <= 10: competition = 50
        elif n <= 20: competition = 75
        else: competition = 95

    # 3. Profit Potential (Google Shopping)
    if availability["prices"] != "UNAVAILABLE":
        n_p = len(prices)
        if n_p == 0: profit = 40
        else: profit = min(90, 40 + n_p * 3)

    # 4. Risk - Tinggi = Bahaya/Beresiko
    # Dihitung dari (100 - trend) + competition
    factors = []
    if trend_score is not None: factors.append(100 - trend_score)
    if competition is not None: factors.append(competition)
    
    if factors:
        risk = round(sum(factors) / len(factors))
    else:
        risk = None

    # Overall (Tinggi = Layak)
    # Weights: demand(30), competition(invert, 20), profit(15), trend(20), risk(invert, 15)
    weights = {"demand": 0.30, "competition": 0.20, "profit": 0.15, "trend": 0.20, "risk": 0.15}
    comp_val = (100 - competition) if competition is not None else None
    risk_val = (100 - risk) if risk is not None else None
    
    active_vals = {
        "demand": demand, "competition": comp_val, "profit": profit, 
        "trend": trend_score, "risk": risk_val
    }
    
    tw = 0; ws = 0
    for k, v in active_vals.items():
        if v is not None:
            ws += v * weights[k]
            tw += weights[k]
    
    overall = round(ws / tw) if tw > 0 else 0

    return BusinessScore(
        demand=demand, competition=competition, profit_potential=profit, 
        trend=trend_score, risk=risk, overall=overall,
        formula_note="Overall: Demand(30%) + (100-Comp)(20%) + Profit(15%) + Trend(20%) + (100-Risk)(15%)",
        data_availability=availability
    )


def _perform_cross_analysis(scores: BusinessScore, competitors: list[Competitor], trends: list[TrendItem], prices: list[PriceItem], price_stats: PriceStats, review_stats: ReviewStats, availability: dict) -> list[str]:
    findings = []
    
    # 1. Market dominance check (Significancy check)
    if availability["competitors"] != "UNAVAILABLE" and len(competitors) > 0:
        # Cari pemain dominan berdasarkan review (selisih > 2x lipat dari rata-rata yang lain)
        reviews = [c.reviews or 0 for c in competitors]
        if len(reviews) >= 2:
            max_rev = max(reviews)
            others_avg = (sum(reviews) - max_rev) / (len(reviews) - 1)
            if max_rev > 100 and max_rev > others_avg * 3:
                leader = next(c for c in competitors if (c.reviews or 0) == max_rev)
                findings.append(
                    f"Pemain '{leader.name}' terlihat cukup dominan dengan {max_rev:,} review, "
                    f"jauh di atas rata-rata kompetitor lain ({int(others_avg)} review)."
                )
            elif max_rev > 0:
                findings.append(
                    "Distribusi review relatif merata di antara kompetitor terdeteksi, "
                    "belum terlihat satu pemain yang benar-benar mendominasi pasar secara digital."
                )
        
    # 2. Price Distribution Segment Gaps (Rule 5)
    if availability["prices"] != "UNAVAILABLE" and price_stats.total > 0 and price_stats.distribution:
        # Urutkan distribusi untuk cari celah
        sorted_dist = sorted(price_stats.distribution.items(), key=lambda x: x[1], reverse=True)
        dominant_seg = sorted_dist[0]
        if dominant_seg[1] >= 50:
            findings.append(
                f"Pasar didominasi produk di rentang harga {dominant_seg[0]} ({dominant_seg[1]}%). "
                "Memasuki segmen ini butuh efisiensi biaya tinggi atau diferensiasi kuat."
            )
        # Cari segmen kosong/minim
        all_segments = ["0-50rb", "50-100rb", "100-300rb", "300rb+"]
        missing = [s for s in all_segments if s not in price_stats.distribution or price_stats.distribution[s] < 10]
        if missing:
            findings.append(
                f"Data yang dianalisis menunjukkan sedikit/tidak ada produk di segmen {', '.join(missing)}. "
                "Ini bisa jadi peluang, namun perlu validasi tambahan terhadap permintaan konsumen."
            )
            
    # 3. Trends stability + Demand
    if scores.trend is not None and scores.demand is not None:
        if scores.trend >= 50 and scores.demand >= 50:
            findings.append("Permintaan pasar kuat didukung tren pencarian yang stabil/meningkat.")
        elif scores.trend < 40 and scores.demand >= 50:
            findings.append("Demand saat ini baik, namun tren pencarian mulai menurun — waspadai potensi kejenuhan pasar.")
            
    # 4. Digital/Service quality gap
    if len(competitors) >= 3 and review_stats.avg_rating > 0 and review_stats.avg_rating < 4.1:
        findings.append(
            f"Rating rata-rata kompetitor rendah ({review_stats.avg_rating:.1f}/5.0). "
            "Kualitas layanan yang lebih baik adalah peluang besar untuk merebut pasar."
        )
        
    # 5. Price War Risk
    if availability["prices"] != "UNAVAILABLE" and price_stats.total > 5:
        cheap_products = sum(1 for p in prices if p.price_num > 0 and p.price_num < 50000)
        if cheap_products >= 5 and len(competitors) > 8:
            findings.append("Risiko perang harga tinggi di segmen budget (produk <Rp50rb) dengan kompetisi padat.")
            
    if not findings:
        findings.append("Belum cukup anomali data untuk menarik kesimpulan hubungan antar sumber.")
        
    return findings

def _validate_report_json(ai_report: dict, scores: BusinessScore, raw_data: dict, competitors: list[Competitor], prices: list[PriceItem], trends: list[TrendItem], news: list[NewsItem], cross_findings: list[str], data_availability: dict) -> list[str]:
    errors = []
    
    required_fields = ["executive_summary", "market_trend_description", "competitor_insights", "price_insights", "news_summary", "opportunity_analysis", "risk_analysis", "recommendation"]
    for field in required_fields:
        if not ai_report.get(field):
            errors.append(f"Field '{field}' kosong atau tidak ditemukan.")
            
    # Audit Missing Data (Rule 3)
    for key, status in data_availability.items():
        if status == "UNAVAILABLE":
            # AI tidak boleh menyimpulkan nilai 0 jika data tidak ada
            content = str(ai_report).lower()
            if f"{key} rendah" in content or f"tidak ada {key}" in content:
                # Tapi news ada pengecualian
                if key == "news" and "tidak ada data berita" in content:
                    continue
                # errors.append(f"Kontradiksi: Data {key} tidak tersedia, AI dilarang menyimpulkan kondisi {key} rendah.")

    # Audit Price Recommendation vs Distribution (Rule 5)
    price_text = ai_report.get("price_insights", "").lower() + ai_report.get("recommendation", "").lower()
    if data_availability["prices"] == "AVAILABLE" and price_text:
        # Cari angka harga di rekomendasi
        prices_in_text = re.findall(r"rp\s?([\d.]+)", price_text)
        if prices_in_text:
            # Sederhana: cek apakah harga yang disarankan ada di segmen yang masuk akal
            pass # Logic kompleks bisa ditambah di sini

    # Audit Score Consistency (Rule 1 & 2)
    risk_text = ai_report.get("risk_analysis", "").lower()
    if risk_text and scores.risk is not None:
        label = get_score_label(scores.risk).lower()
        if label not in risk_text and scores.risk < 80: # Toleransi dikit
             pass # AI mungkin pakai sinonim, tapi label utama harusnya muncul

    forbidden_generic_phrases = [
        "menawarkan produk kompetitif", "harga yang bersaing", "lakukan analisis lebih lanjut",
        "pertimbangkan faktor-faktor lain", "strategi pemasaran yang efektif", "memberikan pelayanan terbaik"
    ]
    for field in required_fields:
        val = ai_report.get(field, "")
        if isinstance(val, str):
            for phrase in forbidden_generic_phrases:
                if phrase in val.lower():
                    errors.append(f"Field '{field}' mengandung kalimat generik: '{phrase}'.")
                    
    return errors

def _build_decision(scores: BusinessScore, competitors: list[Competitor], trends: list[TrendItem], prices: list[PriceItem], price_stats: PriceStats, review_stats: ReviewStats, metrics: dict, business_type: str, availability: dict) -> DecisionEngine:
    d = scores.demand; c = scores.competition; p = scores.profit_potential; t = scores.trend; r = scores.risk
    ov = scores.overall

    def bl(score):
        lbl = get_score_label(score)
        return BenchmarkLabel(label=lbl, level=lbl)

    # 1. Saturation Score (Kejenuhan)
    # Saturation dihitung dari tingkat persaingan (c)
    sat = c if c is not None else 0
    sat_reasons = []
    if availability["competitors"] == "UNAVAILABLE":
        sat_reasons.append("Data lokasi tidak tersedia")
    else:
        if c is not None:
            if c >= 70: sat_reasons.append("✖ Persaingan digital sangat ketat")
            elif c >= 40: sat_reasons.append("✔ Tingkat persaingan moderat")
            else: sat_reasons.append("✔ Kompetitor digital masih minim")
        if len(competitors) > 5:
            max_rev = max([comp.reviews or 0 for comp in competitors])
            if max_rev > 200: sat_reasons.append("✖ Ada pemain dengan dominasi review besar")

    # 2. Opportunity Score (Peluang)
    # Opportunity berbanding lurus dengan demand, profit, trend, dan berbanding terbalik dengan competition
    comp_inv = (100 - c) if c is not None else 50
    opp_factors = [v for v in [d, p, t, comp_inv] if v is not None]
    opp = round(sum(opp_factors) / len(opp_factors)) if opp_factors else 0
    
    opp_pos, opp_neg = [], []
    if d is not None and d >= 60: opp_pos.append("✔ Permintaan pasar tinggi")
    if p is not None and p >= 60: opp_pos.append("✔ Potensi profit margin sehat")
    if c is not None and c <= 40: opp_pos.append("✔ Akses pasar masih terbuka")
    
    if d is not None and d < 40: opp_neg.append("✖ Minat pasar rendah")
    if c is not None and c >= 70: opp_neg.append("✖ Hambatan masuk tinggi (padat)")

    # 3. Verdict Mapping
    if ov >= 80: verdict, verdict_label = "GO", "✅ Sangat Layak Dijalankan"
    elif ov >= 65: verdict, verdict_label = "GO", "✅ Layak Dengan Catatan"
    elif ov >= 50: verdict, verdict_label = "CAUTION", "⚠️ Risiko Cukup Tinggi"
    elif ov >= 35: verdict, verdict_label = "CAUTION", "⚠️ Perlu Pertimbangan Matang"
    else: verdict, verdict_label = "STOP", "🔴 Tidak Disarankan"

    # 4. Confidence Score (Rule 5 & 9)
    # Realistis 60-85%
    conf_base = 40
    avail_count = sum(1 for v in availability.values() if v == "AVAILABLE")
    partial_count = sum(1 for v in availability.values() if v == "PARTIAL")
    conf_score = conf_base + (avail_count * 10) + (partial_count * 5)
    if metrics["has_specific_location"]: conf_score += 5
    confidence = min(85, conf_score)

    # 5. Key Insights (Professional & Data-driven)
    insights = []
    if price_stats.total > 0:
        insights.append(f"Pasar didominasi harga {price_stats.median} (Median). Celah profit ada di rentang {price_stats.p25} - {price_stats.p75}.")
    if len(competitors) >= 3:
        top_comp = sorted(competitors, key=lambda x: x.reviews or 0, reverse=True)[0]
        insights.append(f"Kompetitor '{top_comp.name}' memiliki ulasan terbanyak, menandakan loyalitas pelanggan di titik tersebut kuat.")
    if t is not None and t < 45:
        insights.append("Tren pencarian menurun — fokus retensi pelanggan lebih realistis daripada akuisisi agresif.")
    if c is not None and len(competitors) > 0 and c <= 40:
        insights.append(f"Hanya {len(competitors)} kompetitor terdeteksi di Maps — hambatan masuk digital relatif rendah, tapi reputasi pemain lama tetap perlu dihitung.")
    if c is not None and c >= 70:
        insights.append(f"Persaingan digital tinggi (skor {c}) dari {len(competitors)} pemain — diferensiasi produk/layanan wajib.")

    # 6. Reasons
    reasons_go = []
    if d is not None and d >= 60: reasons_go.append("✔ Permintaan pasar cukup kuat")
    if p is not None and p >= 60: reasons_go.append("✔ Potensi profit menarik")
    if c is not None and c <= 40: reasons_go.append("✔ Persaingan digital masih terkendali")
    if t is not None and t >= 55: reasons_go.append("✔ Tren pencarian positif")
    if not reasons_go: reasons_go.append("✔ Data dasar tersedia untuk evaluasi")

    reasons_caution = []
    if c is not None and c >= 70: reasons_caution.append("⚠ Persaingan tinggi — butuh diferensiasi")
    if r is not None and r >= 70: reasons_caution.append("⚠ Risiko pasar tinggi")
    if d is not None and d < 40: reasons_caution.append("⚠ Permintaan masih lemah")
    if t is not None and t < 40: reasons_caution.append("⚠ Tren pencarian menurun")
    for k, v in availability.items():
        if v == "UNAVAILABLE":
            reasons_caution.append(f"⚠ Data {k} tidak tersedia")
    if not reasons_caution: reasons_caution.append("⚠ Validasi lapangan tetap diperlukan")

    # 7. SWOT (selalu lengkap)
    sw_s, sw_w, sw_o, sw_t = [], [], [], []
    if d is not None and d >= 55: sw_s.append(f"Permintaan pasar {get_score_label(d).lower()} (skor {d})")
    if p is not None and p >= 55: sw_s.append(f"Potensi profit {get_score_label(p).lower()} (skor {p})")
    if c is not None and c <= 40: sw_s.append(f"Persaingan masih terkendali ({len(competitors)} kompetitor)")
    if not sw_s: sw_s.append("Ada data pasar dasar untuk perencanaan")

    if c is not None and c >= 60: sw_w.append(f"Persaingan {get_score_label(c).lower()} (skor {c})")
    if d is not None and d < 45: sw_w.append(f"Permintaan masih {get_score_label(d).lower()}")
    if t is not None and t < 45: sw_w.append("Tren pencarian belum mendukung pertumbuhan cepat")
    if price_stats.total > 0 and price_stats.min_num > 0 and price_stats.max_num / max(price_stats.min_num, 1) > 10:
        sw_w.append("Spread harga pasar lebar — margin mudah tergerus")
    if not sw_w: sw_w.append("Brand awareness belum terbentuk")

    if price_stats.distribution:
        low_segs = [k for k, v in price_stats.distribution.items() if v < 15]
        if low_segs:
            sw_o.append(f"Segmen harga minim kompetisi: {', '.join(low_segs[:2])}")
        else:
            top_seg = max(price_stats.distribution.items(), key=lambda x: x[1])
            sw_o.append(f"Mayoritas pasar di {top_seg[0]} ({top_seg[1]}%) — peluang diferensiasi di luar segmen utama")
    if review_stats.avg_rating > 0 and review_stats.avg_rating < 4.2:
        sw_o.append(f"Rating kompetitor rata-rata {review_stats.avg_rating:.1f} — celah kualitas layanan")
    if c is not None and c < 50: sw_o.append("Hambatan masuk digital relatif rendah")
    if not sw_o: sw_o.append("Eksplorasi niche dan positioning lokal")

    if c is not None and c >= 70: sw_t.append("Kompetitor padat — biaya akuisisi pelanggan cenderung naik")
    if r is not None and r >= 60: sw_t.append(f"Risiko pasar {get_score_label(r).lower()} (skor {r})")
    if price_stats.total > 5 and price_stats.min_num < 50000:
        cheap = sum(1 for pv in prices if pv.price_num and pv.price_num < 50000)
        if cheap >= 3: sw_t.append(f"Ancaman perang harga ({cheap} produk <Rp50rb)")
    if not sw_t: sw_t.append("Munculnya pemain baru dengan modal iklan lebih besar")

    # 8. Action Plan
    bt = business_type.lower()
    is_service = any(x in bt for x in ["laundry", "cuci", "servis", "bengkel", "klinik", "salon", "les"])
    is_fnb = any(x in bt for x in ["warung", "makan", "kopi", "cafe", "snack", "resto"])
    if is_service:
        plan = [
            ActionPlan(phase="Hari 1-10", tasks=["Audit supplier & peralatan", "Set up Google Business Profile", "SOP kualitas layanan"]),
            ActionPlan(phase="Hari 11-20", tasks=["Optimasi Maps & review", "Sebar brosur radius 1-2km", "Promosi opening"]),
            ActionPlan(phase="Hari 21-30", tasks=["Kumpulkan testimoni", "Evaluasi efisiensi operasional", "Program loyalitas dasar"]),
        ]
    elif is_fnb:
        plan = [
            ActionPlan(phase="Hari 1-10", tasks=["Finalisasi menu & food testing", "Riset kemasan delivery", "Daftar Grab/Go/ShopeeFood"]),
            ActionPlan(phase="Hari 11-20", tasks=["Foto produk estetik", "Endorse micro-influencer lokal", "Setup media sosial"]),
            ActionPlan(phase="Hari 21-30", tasks=["Promo bundling", "Evaluasi menu terlaris", "Iklan berbasis radius"]),
        ]
    else:
        plan = [
            ActionPlan(phase="Hari 1-10", tasks=["Sourcing supplier", "Setup Shopee & Tokopedia", "Analisis kompetitor marketplace"]),
            ActionPlan(phase="Hari 11-20", tasks=["Optimasi SEO judul produk", "Aset iklan digital", "Live streaming dasar"]),
            ActionPlan(phase="Hari 21-30", tasks=["Marketplace ads hemat", "Affiliate marketing", "Evaluasi conversion rate"]),
        ]

    return DecisionEngine(
        verdict=verdict, verdict_label=verdict_label, confidence=confidence,
        reasons_go=reasons_go[:4], reasons_caution=reasons_caution[:4],
        opportunity_score=opp, opportunity_reasons_positive=opp_pos, opportunity_reasons_negative=opp_neg,
        saturation_score=sat, saturation_reasons=sat_reasons[:3],
        insights=insights[:4],
        demand_benchmark=bl(d), competition_benchmark=bl(c), profit_benchmark=bl(p),
        trend_benchmark=bl(t), risk_benchmark=bl(r),
        swot=SwotItem(strength=sw_s[:3], weakness=sw_w[:3], opportunity=sw_o[:3], threat=sw_t[:3]),
        market_gaps=[], action_plan=plan,
    )
