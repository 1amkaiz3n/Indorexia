import asyncio
import logging
import re
from statistics import median
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.schemas.research import (
    ResearchRequest, ResearchResponse, HistoryQuery, ReportAction,
    Competitor, PriceItem, PriceStats, TrendItem, NewsItem, ReviewStats, MarketGap, BusinessScore,
    DecisionEngine, BenchmarkLabel, SwotItem, ActionPlan, DecisionItem, AiAnalysis,
    TrendsKeywordResult, TrendsAnalysis, ScoreDetail, ScoreFactor, ScoreMethodology,
    MarketStatistics, SourceBreakdown,
    # NEW types
    EvidenceItem, MarketOpportunity,
    DemandSubScores, DemandBreakdown,
    CompetitorStrength, CompetitivePosition, CompetitiveMap,
    CustomerPersona, PainPoint, PainPointAnalysis,
    ProductOpportunity,
    UnitEconomicsInput, UnitEconomicsOutput,
    PriceSegment, PricePerUnit, PricePositioning,
    DecisionChange, ValidationItem, ValidationChecklist,
    ActionPlanV2, SignalContradiction, DataLimitation, InsightConfidence,
)
from app.schemas.query import ResearchContext, ResearchQueries
from app.services import serpapi_service, tavily_service, groq_service, json_storage_service
from app.services.query_understanding import understand_query, generate_queries, _fallback_parse, _fallback_queries
from app.services.dedup_engine import deduplicate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["research"])

# ── Helper: score label ──

def get_score_label(score: int | None) -> str:
    if score is None:
        return "Data Tidak Tersedia"
    if score >= 85: return "Sangat Tinggi"
    if score >= 70: return "Tinggi"
    if score >= 50: return "Sedang"
    if score >= 30: return "Rendah"
    return "Sangat Rendah"


# ── Main Research Endpoint (UPGRADED PIPELINE) ──

@router.post("/research")
async def research(req: ResearchRequest):
    query = req.query
    location = req.location
    visitor_id = req.visitor_id or "anon"
    try:
        # ── Phase 1: AI Query Understanding ──
        try:
            context = await understand_query(query)
        except Exception as e:
            logger.warning("AI query understanding failed, using fallback: %s", e)
            context = _fallback_parse(query)

        if location:
            context.location_raw = location
            if not context.location_city:
                context.location_city = location

        logger.info("Research context: intent=%s product=%s location=%s",
                     context.intent, context.product, context.location_city)

        # ── Phase 2: AI Query Generation ──
        try:
            queries = await generate_queries(context)
        except Exception as e:
            logger.warning("AI query generation failed, using fallback: %s", e)
            queries = _fallback_queries(context)

        if not queries.maps_queries:
            queries.maps_queries = [f"{context.product} {context.location_city}".strip()]
        if not queries.search_queries:
            queries.search_queries = [f"{context.product} {context.location_city} bisnis".strip()]
        if not queries.shopping_queries:
            queries.shopping_queries = [f"{context.product}"]
        if not queries.trends_queries:
            queries.trends_queries = [f"{context.product}"]
        if not queries.tavily_queries:
            queries.tavily_queries = [f"{context.product} {context.location_city} UMKM".strip()]

        logger.info("Generated queries: maps=%d search=%d shopping=%d trends=%d tavily=%d",
                     len(queries.maps_queries), len(queries.search_queries),
                     len(queries.shopping_queries), len(queries.trends_queries),
                     len(queries.tavily_queries))

        # ── Phase 3: Data Collection ──
        raw = await _gather_data_all_sources(context, queries)

        # ── Phase 4: Parse & Deduplicate Competitors ──
        all_competitors = _parse_all_competitors(raw)
        logger.info("Raw competitors before dedup: %d", len(all_competitors))
        competitors = deduplicate(all_competitors)
        total_competitors_detected = len(all_competitors)
        logger.info("Competitors after dedup: %d", len(competitors))

        competitors = _classify_competitors(competitors, context.product)

        # ── Parse Other Data ──
        review_stats = _parse_review_stats(competitors)
        prices = _parse_all_prices(raw)
        prices = _filter_relevant_prices(prices, context.product)
        price_stats = _calc_price_stats(prices)
        trends = _parse_all_trends(raw)
        trends_analysis = _build_trends_analysis(trends, raw)
        news = _filter_relevant_news(_parse_all_news(raw), context.product)

        # ── Phase 5: Market Statistics ──
        market_stats = _build_market_statistics(competitors, review_stats, raw)

        # ── Phase 6: Data Quality ──
        data_availability = _assess_data_availability(raw, competitors, prices, trends, news)
        data_coverage = _calculate_data_coverage(raw, competitors, prices, trends, news, queries)
        metrics = _validate_data_quality(competitors, prices, trends, news, context.location_city, data_availability)

        # ── Phase 7: Transparent Scoring ──
        scores = _calculate_scores_detailed(competitors, trends, prices, data_availability, review_stats)
        cross_findings = _perform_cross_analysis(scores, competitors, trends, prices, price_stats, review_stats, data_availability)

        # ═══════════════════════════════════════════════
        # PHASE 7b: NEW UPGRADED ENGINE
        # ═══════════════════════════════════════════════

        # 7b.1 Evidence-based Opportunity Engine
        opportunities = _build_opportunity_engine(scores, competitors, trends, prices, price_stats, review_stats, data_availability, context)

        # 7b.2 Demand Sub-scores
        demand_subscores = _build_demand_sub_scores(trends, prices, news, data_availability)

        # 7b.3 Demand Breakdown (national vs regional vs local)
        demand_breakdown = _build_demand_breakdown(trends, raw, context)

        # 7b.4 Competitor Strength + Competitive Map
        competitor_strengths = _analyze_competitor_strength(competitors)
        competitive_map = _build_competitive_map(competitors, prices)

        # 7b.5 Price Positioning
        price_positioning = _build_price_positioning(prices, price_stats)

        # 7b.6 Data Limitations
        data_limitations = _build_data_limitations(raw, competitors, prices, trends, news, context)

        # 7b.7 Contradiction Detection
        contradictions = _detect_contradictions(scores, competitors, trends, prices, price_stats, review_stats, data_availability)

        # 7b.8 Validation Checklist
        validation_checklist = _build_validation_checklist(scores, price_stats, context)

        # 7b.9 Insight Confidences
        insight_confidences = _build_insight_confidences(scores, competitors, prices, trends, review_stats, data_availability)

        # 7b.10 Action Plan V2 (enhanced)
        action_plan_v2 = _build_action_plan_v2(scores, price_stats, competitors, review_stats, context)

        # 7b.11 Product Opportunities
        product_opps = _build_product_opportunities(scores, competitors, trends, prices, data_availability, context)

        # ── Phase 7c: Decision Engine ──
        decision = _build_decision_upgraded(
            scores, competitors, trends, prices, price_stats, review_stats, metrics,
            context.product, data_availability,
            trends_analysis=trends_analysis,
            opportunities=opportunities,
            contradictions=contradictions,
            validation_checklist=validation_checklist,
            data_limitations=data_limitations,
            demand_breakdown=demand_breakdown,
        )

        scores_dict = scores.model_dump()
        scores_dict["demand_label"] = get_score_label(scores.demand)
        scores_dict["competition_label"] = get_score_label(scores.competition)
        scores_dict["profit_potential_label"] = get_score_label(scores.profit_potential)
        scores_dict["trend_label"] = get_score_label(scores.trend)
        scores_dict["risk_label"] = get_score_label(scores.risk)
        scores_dict["data_availability"] = data_availability
        scores_dict["price_stats"] = price_stats.model_dump()
        scores_dict["review_stats"] = review_stats.model_dump()
        scores_dict["competitor_count"] = len(competitors)

        # ── Phase 8: AI Report Generation ──
        ai_report = {}
        validation_errors = []
        feedback = None

        for attempt in range(3):
            ai_report = await groq_service.generate_report_upgraded(
                query, raw, scores_dict, scores_dict,
                [c.model_dump() for c in competitors],
                [p.model_dump() for p in prices],
                [t.model_dump() for t in trends],
                [n.model_dump() for n in news],
                cross_findings=cross_findings,
                validation_feedback=feedback,
                data_availability=data_availability,
                context=context,
                market_stats=market_stats,
                data_coverage=data_coverage,
                # NEW: structured data
                opportunities=[o.model_dump() for o in opportunities],
                demand_subscores=demand_subscores.model_dump(),
                demand_breakdown=demand_breakdown.model_dump(),
                competitor_strengths=[c.model_dump() for c in competitor_strengths],
                competitive_map=competitive_map.model_dump(),
                price_positioning=price_positioning.model_dump(),
                contradictions=[c.model_dump() for c in contradictions],
                data_limitations=[d.model_dump() for d in data_limitations],
                validation_checklist=validation_checklist.model_dump(),
                action_plan_v2=[a.model_dump() for a in action_plan_v2],
                product_opps=[p.model_dump() for p in product_opps],
                insight_confidences=[ic.model_dump() for ic in insight_confidences],
            )

            validation_errors = _validate_report_json_upgraded(
                ai_report, scores, raw, competitors, prices, trends, news, cross_findings, data_availability
            )

            if not validation_errors:
                logger.info(f"AI report validated on attempt {attempt + 1}")
                break
            else:
                logger.warning(f"AI report validation failed attempt {attempt + 1}: {validation_errors}")
                feedback = "Validasi laporan sebelumnya gagal dengan error berikut:\\n" + "\\n".join(f"- {err}" for err in validation_errors) + "\\n\\nHarap perbaiki."

        ai = AiAnalysis(
            executive_summary=ai_report.get("executive_summary", ""),
            market_trend_description=ai_report.get("market_trend_description", ""),
            competitor_insights=ai_report.get("competitor_insights", ""),
            price_insights=ai_report.get("price_insights", ""),
            news_summary=ai_report.get("news_summary", ""),
            opportunity_analysis=ai_report.get("opportunity_analysis", ""),
            risk_analysis=ai_report.get("risk_analysis", ""),
            recommendation=ai_report.get("recommendation", ""),
            ai_understanding=ai_report.get("ai_understanding", ""),
            market_opportunity=ai_report.get("market_opportunity", ""),
            demand_analysis=ai_report.get("demand_analysis", ""),
            competition_analysis=ai_report.get("competition_analysis", ""),
            product_price_analysis=ai_report.get("product_price_analysis", ""),
            market_statistics_insight=ai_report.get("market_statistics_insight", ""),
            data_coverage_note=ai_report.get("data_coverage_note", ""),
            market_gap_analysis=ai_report.get("market_gap_analysis", ""),
            business_recommendation=ai_report.get("business_recommendation", ""),
            # 33-section fields
            executive_decision=ai_report.get("executive_decision", ""),
            business_verdict=ai_report.get("business_verdict", ""),
            confidence_evidence_quality=ai_report.get("confidence_evidence_quality", ""),
            key_positive_signals=ai_report.get("key_positive_signals", ""),
            key_negative_signals=ai_report.get("key_negative_signals", ""),
            biggest_risks_analysis=ai_report.get("biggest_risks_analysis", ""),
            biggest_unknowns_analysis=ai_report.get("biggest_unknowns_analysis", ""),
            demand_analysis_text=ai_report.get("demand_analysis_text", ""),
            local_vs_national_demand=ai_report.get("local_vs_national_demand", ""),
            customer_segments_analysis=ai_report.get("customer_segments_analysis", ""),
            customer_pain_points_analysis=ai_report.get("customer_pain_points_analysis", ""),
            competition_intelligence_analysis=ai_report.get("competition_intelligence_analysis", ""),
            competitive_positioning_map=ai_report.get("competitive_positioning_map", ""),
            google_search_landscape=ai_report.get("google_search_landscape", ""),
            google_trends_analysis_text=ai_report.get("google_trends_analysis_text", ""),
            google_shopping_analysis=ai_report.get("google_shopping_analysis", ""),
            market_pricing_analysis=ai_report.get("market_pricing_analysis", ""),
            price_positioning_analysis=ai_report.get("price_positioning_analysis", ""),
            market_gap_analysis_text=ai_report.get("market_gap_analysis_text", ""),
            product_opportunities_analysis=ai_report.get("product_opportunities_analysis", ""),
            customer_opportunity_analysis=ai_report.get("customer_opportunity_analysis", ""),
            swot_analysis_text=ai_report.get("swot_analysis_text", ""),
            unit_economics_analysis=ai_report.get("unit_economics_analysis", ""),
            revenue_scenario=ai_report.get("revenue_scenario", ""),
            risk_analysis_text=ai_report.get("risk_analysis_text", ""),
            data_limitations_text=ai_report.get("data_limitations_text", ""),
            conflicting_signals=ai_report.get("conflicting_signals", ""),
            validation_experiments=ai_report.get("validation_experiments", ""),
            action_plan_7_day=ai_report.get("action_plan_7_day", ""),
            action_plan_30_day=ai_report.get("action_plan_30_day", ""),
            decision_criteria_text=ai_report.get("decision_criteria_text", ""),
            what_would_change_decision=ai_report.get("what_would_change_decision", ""),
            final_recommendation=ai_report.get("final_recommendation", ""),
        )

        score_methodology = _build_score_methodology(scores, competitors, trends, prices, review_stats, data_availability)

        report = ResearchResponse(
            query=query,
            business_score=scores,
            decision=decision,
            competitors=competitors,
            total_competitors=len(competitors),
            total_competitors_detected=total_competitors_detected,
            review_stats=review_stats,
            market_statistics=market_stats,
            prices=prices,
            price_stats=price_stats,
            trends=trends,
            news=news,
            ai=ai,
            trends_analysis=trends_analysis,
            score_methodology=score_methodology,
            data_coverage=data_coverage,
            # NEW fields
            demand_sub_scores=demand_subscores,
            demand_breakdown=demand_breakdown,
            competitor_strengths=competitor_strengths,
            competitive_map=competitive_map,
            price_positioning=price_positioning,
            validation_checklist=validation_checklist,
            action_plan_v2=action_plan_v2,
            contradictions=contradictions,
            data_limitations=data_limitations,
            insight_confidences=insight_confidences,
            market_opportunities=opportunities,
            product_opportunities=product_opps,
        )

        resp_data = report.model_dump()
        resp_data["trends_analysis"] = trends_analysis.model_dump() if trends_analysis else {}
        resp_data["query_context"] = context.model_dump()
        resp_data["queries_used"] = queries.model_dump()

        saved = await json_storage_service.save_research(
            visitor_id=visitor_id,
            query=query,
            location=context.location_city or location or "Indonesia",
            verdict=decision.verdict_label,
            score=scores.overall,
            raw_data=raw,
            report=resp_data,
        )

        return {
            "id": str(saved.get("id", "")) if saved else "",
            "report": resp_data,
        }
    except Exception as e:
        logger.exception("Research failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/research/history")
async def get_history(body: HistoryQuery):
    try:
        items = await json_storage_service.get_history(
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
        data = await json_storage_service.get_report(report_id, visitor_id)
        if not data:
            raise HTTPException(status_code=404, detail="Not found")
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/research/{report_id}")
async def delete_report(report_id: str, visitor_id: str = ""):
    ok = await json_storage_service.delete_report(report_id, visitor_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Not found")
    return {"ok": True}


@router.delete("/research")
async def delete_all(visitor_id: str = ""):
    ok = await json_storage_service.delete_all_reports(visitor_id)
    return {"ok": ok}


@router.patch("/research/{report_id}")
async def update_report(report_id: str, body: ReportAction):
    data = await json_storage_service.update_report(
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
    data = await json_storage_service.duplicate_report(report_id, visitor_id)
    if not data:
        raise HTTPException(status_code=404, detail="Not found")
    return data


@router.post("/api/research/unit-economics")
async def calculate_unit_economics(body: UnitEconomicsInput):
    """Calculate unit economics from user-provided costs."""
    output = _simulate_unit_economics(body)
    return output.model_dump()


# ═══════════════════════════════════════════════
#  DATA GATHERING  (upgraded with timeline)
# ═══════════════════════════════════════════════

async def _gather_data_all_sources(context: ResearchContext, queries: ResearchQueries) -> dict:
    results = {
        "search_results": [],
        "trends_results": [],
        "shopping_results": [],
        "tavily_results": [],
        "trends_keywords_raw": [],
        "trends_analysis": None,
    }

    loc = context.location_city or "Indonesia"

    # Google Search (multi-query)
    for q in queries.search_queries:
        resp = await serpapi_service.search_google(q, loc, num=20)
        results["search_results"].append({"query": q, "data": resp})
        await asyncio.sleep(0.3)

    # Google Maps (multi-query)
    for q in queries.maps_queries:
        resp = await serpapi_service.search_google(q, loc, num=20)
        results["search_results"].append({"query": q, "data": resp, "source": "maps"})
        await asyncio.sleep(0.3)

    # Google Trends (multi-keyword) — UPGRADED: extract full timeline
    trends_keywords_results = []
    for q in queries.trends_queries:
        await asyncio.sleep(0.5)
        resp = await serpapi_service.google_trends(q, loc)
        has_data = isinstance(resp, dict) and "error" not in resp
        vals = []
        rq, rising_q = [], []
        timeline_data = []

        if has_data:
            for entry in ((resp.get("interest_over_time") or {}).get("timeline_data") or []):
                entry_val = 0
                for v in (entry.get("values") or []):
                    try:
                        entry_val = int(v.get("extracted_value", v.get("value", 0)))
                    except:
                        pass
                vals.append(entry_val)

                # Extract date info
                date_str = entry.get("date", "")
                timestamp = entry.get("timestamp", "")
                month = ""
                year = ""
                if date_str:
                    try:
                        # Parse "Jul 27 – Aug 2, 2025" -> month=Jul, year=2025
                        parts = date_str.split()
                        if len(parts) >= 2:
                            month = parts[0]
                        if len(parts) >= 4:
                            year = parts[-1].strip(",")
                    except:
                        pass

                timeline_data.append({
                    "date": date_str,
                    "value": entry_val,
                    "month": month,
                    "year": int(year) if year else 0,
                    "timestamp": timestamp,
                })

            rq_data = resp.get("related_queries") or {}
            for r in (rq_data.get("top") or []):
                if isinstance(r, dict) and r.get("query"): rq.append(r["query"])
            for r in (rq_data.get("rising") or []):
                if isinstance(r, dict) and r.get("query"): rising_q.append(r["query"])

        kw_res = TrendsKeywordResult(
            keyword=q,
            has_data=bool(vals),
            status="AVAILABLE" if vals else ("ERROR" if not has_data else "NO_DATA"),
            interest_values=vals,
            avg_interest=sum(vals) / len(vals) if vals else 0,
            peak_interest=max(vals) if vals else 0,
            lowest_interest=min(vals) if vals else 0,
            data_points=len(vals),
            timeline=timeline_data,
            period_type="weekly",
            related_queries=rq[:10],
            rising_queries=rising_q[:10],
        )
        if len(vals) >= 2:
            half = len(vals) // 2
            first_half = sum(vals[:half]) / half
            second_half = sum(vals[half:]) / (len(vals) - half)
            growth = ((second_half - first_half) / first_half * 100) if first_half > 0 else 0
            kw_res.growth_rate = round(growth, 1)
            kw_res.trend_direction = "rising" if growth > 5 else ("declining" if growth < -5 else "stable")

        trends_keywords_results.append(kw_res)
        if vals:
            results["trends_results"].append({"query": q, "data": resp})

    # Google Shopping (multi-query)
    for q in queries.shopping_queries:
        resp = await serpapi_service.google_shopping(q, loc)
        if isinstance(resp, dict) and ("error" not in resp) and resp.get("shopping_results"):
            results["shopping_results"].append({"query": q, "data": resp})
        await asyncio.sleep(0.3)

    # Tavily (multi-query)
    for q in queries.tavily_queries:
        resp = await tavily_service.search_general(q, max_results=10)
        if isinstance(resp, dict) and "error" not in resp:
            results["tavily_results"].append({"query": q, "data": resp})
        await asyncio.sleep(0.3)

    # Build TrendsAnalysis
    has_any = any(kw.has_data for kw in trends_keywords_results)
    keywords_with_data = [kw for kw in trends_keywords_results if kw.has_data]
    avg_interest_all = 0
    if keywords_with_data:
        avg_interest_all = round(sum(kw.avg_interest for kw in keywords_with_data) / len(keywords_with_data), 1)

    selected_kw = ""
    fallback_used = False
    fallback_reason = ""
    best_raw = {}
    if keywords_with_data:
        keywords_with_data.sort(key=lambda x: len(x.interest_values), reverse=True)
        selected_kw = keywords_with_data[0].keyword
        best_data = None
        for tr in results["trends_results"]:
            if tr["query"] == selected_kw:
                best_data = tr["data"]
                break
        if best_data:
            best_raw = best_data
        if selected_kw != queries.trends_queries[0]:
            fallback_used = True
            fallback_reason = f"Keyword spesifik '{queries.trends_queries[0]}' tidak memiliki data. Sistem menggunakan keyword '{selected_kw}' sebagai indikator tren."

    results["trends"] = _trim(best_raw)
    results["trends_keywords_raw"] = [kw.model_dump() for kw in trends_keywords_results]
    results["trends_analysis"] = TrendsAnalysis(
        keywords_analyzed=trends_keywords_results,
        selected_keyword=selected_kw,
        fallback_used=fallback_used,
        fallback_reason=fallback_reason,
        has_any_data=has_any,
        avg_interest_all=avg_interest_all,
        keyword_count_with_data=len(keywords_with_data),
    ).model_dump()

    logger.info("Gathered data: search=%d queries, trends=%d kw, shopping=%d, tavily=%d",
                 len(queries.search_queries) + len(queries.maps_queries),
                 len(trends_keywords_results),
                 len(results["shopping_results"]),
                 len(results["tavily_results"]))
    return results


def _trim(d: dict) -> dict:
    if isinstance(d, dict):
        return {k: _trim(v) for k, v in list(d.items())[:50]}
    if isinstance(d, list):
        return [_trim(v) for v in d[:20]]
    if isinstance(d, str):
        return d[:500]
    return d


# ═══════════════════════════════════════════════
#  PARSERS
# ═══════════════════════════════════════════════

def _parse_all_competitors(raw: dict) -> list[Competitor]:
    out = []
    search_results = raw.get("search_results", [])

    for result in search_results:
        data = result.get("data", {})
        query_used = result.get("query", "")
        source = result.get("source", "google_search")

        if not isinstance(data, dict) or "error" in data:
            continue

        try:
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
                    source=source,
                    query_used=query_used,
                    relevance_score=1.0,
                    competitor_type="direct",
                ))

        except Exception as e:
            logger.warning("Parse competitors error (query=%s): %s", query_used, e)

    return out


def _classify_competitors(competitors: list[Competitor], product: str) -> list[Competitor]:
    if not product:
        return competitors
    product_words = set(product.lower().split())
    for comp in competitors:
        name_lower = comp.name.lower()
        if any(w in name_lower for w in product_words if len(w) > 2):
            comp.competitor_type = "direct"
        else:
            comp.competitor_type = "indirect"
    return competitors


def _parse_review_stats(competitors: list[Competitor]) -> ReviewStats:
    total = sum(c.reviews or 0 for c in competitors)
    rated = [c.rating for c in competitors if c.rating]
    avg = sum(rated) / len(rated) if rated else 0
    med_rating = median(rated) if len(rated) >= 3 else avg
    all_reviews = [c.reviews or 0 for c in competitors if c.reviews is not None]
    med_reviews = median(all_reviews) if all_reviews else 0

    rating_dist = {}
    for r in rated:
        key = int(r)
        rating_dist[f"{key} Bintang"] = rating_dist.get(f"{key} Bintang", 0) + 1

    review_dist = {}
    for rv in all_reviews:
        if rv == 0:
            key = "0"
        elif rv <= 10:
            key = "1-10"
        elif rv <= 50:
            key = "11-50"
        elif rv <= 100:
            key = "51-100"
        elif rv <= 500:
            key = "101-500"
        else:
            key = "500+"
        review_dist[key] = review_dist.get(key, 0) + 1

    return ReviewStats(
        total_reviews=total,
        avg_rating=round(avg, 1),
        competitor_count=len(competitors),
        median_reviews=med_reviews,
        rating_distribution=rating_dist,
        review_distribution=review_dist,
    )


def _build_market_statistics(competitors: list[Competitor], review_stats: ReviewStats, raw: dict) -> MarketStatistics:
    direct = sum(1 for c in competitors if c.competitor_type == "direct")
    indirect = sum(1 for c in competitors if c.competitor_type == "indirect")

    loc_dist = {}
    for c in competitors:
        if c.address:
            from app.services.dedup_engine import extract_city
            city = extract_city(c.address)
            if city:
                loc_dist[city.capitalize()] = loc_dist.get(city.capitalize(), 0) + 1

    cat_dist = {}
    for c in competitors:
        cat = c.type or "Tidak diketahui"
        cat_dist[cat] = cat_dist.get(cat, 0) + 1

    pop_dist = {"Rendah (0-10 review)": 0, "Sedang (11-100 review)": 0, "Tinggi (100+ review)": 0}
    for c in competitors:
        r = c.reviews or 0
        if r <= 10:
            pop_dist["Rendah (0-10 review)"] += 1
        elif r <= 100:
            pop_dist["Sedang (11-100 review)"] += 1
        else:
            pop_dist["Tinggi (100+ review)"] += 1

    source_breakdown = SourceBreakdown()
    for result in raw.get("search_results", []):
        source = result.get("source", "google_search")
        data = result.get("data", {})
        if isinstance(data, dict) and "error" not in data:
            if source == "maps":
                source_breakdown.google_maps += 1
            else:
                source_breakdown.google_search += 1

    tavily_results = raw.get("tavily_results", [])
    for tr in tavily_results:
        data = tr.get("data", {})
        if isinstance(data, dict) and "error" not in data:
            n = len(data.get("results", []))
            source_breakdown.tavily_news += n

    source_breakdown.google_trends = len([kw for kw in (raw.get("trends_keywords_raw") or []) if kw.get("has_data")])
    source_breakdown.google_shopping = len(raw.get("shopping_results", []))

    all_reviews_list = [c.reviews or 0 for c in competitors if c.reviews is not None]
    med_reviews = median(all_reviews_list) if all_reviews_list else 0
    avg_reviews = sum(all_reviews_list) / len(all_reviews_list) if all_reviews_list else 0

    rated = [c.rating for c in competitors if c.rating]
    med_rating = median(rated) if len(rated) >= 3 else (sum(rated) / len(rated) if rated else 0)

    data_limit_note = ""
    if len(competitors) < 5:
        data_limit_note = f"Hanya {len(competitors)} kompetitor relevan terdeteksi dari sumber data yang tersedia. Data ini belum cukup untuk menyimpulkan tingkat persaingan pasar secara keseluruhan."
    elif len(competitors) < 15:
        data_limit_note = f"{len(competitors)} kompetitor relevan terdeteksi. Data ini memberikan gambaran awal namun mungkin belum merepresentasikan seluruh kondisi pasar."

    return MarketStatistics(
        total_competitors_detected=len(competitors),
        total_competitors_analyzed=len(competitors),
        direct_competitors=direct,
        indirect_competitors=indirect,
        total_reviews=review_stats.total_reviews,
        avg_rating=review_stats.avg_rating,
        median_rating=round(med_rating, 1),
        rating_distribution=review_stats.rating_distribution,
        review_distribution=review_stats.review_distribution,
        competitors_by_location=loc_dist,
        competitors_by_category=cat_dist,
        competitors_by_popularity=pop_dist,
        avg_reviews_per_competitor=round(avg_reviews, 1),
        median_reviews=med_reviews,
        source_breakdown=source_breakdown,
        data_limitation_note=data_limit_note,
    )


# ── Price Parsers ──

def _parse_all_prices(raw: dict) -> list[PriceItem]:
    out = []
    shopping_results = raw.get("shopping_results", [])
    for result in shopping_results:
        data = result.get("data", {})
        query_used = result.get("query", "")
        if not isinstance(data, dict) or "error" in data:
            continue
        try:
            for item in (data.get("shopping_results") or []) or []:
                raw_price = item.get("extracted_price") or item.get("price", "")
                price_num = 0
                if isinstance(raw_price, (int, float)):
                    price_num = float(raw_price)
                elif isinstance(raw_price, str):
                    nums = re.findall(r'[\\d.]+', raw_price.replace('Rp', '').replace('.', '').strip())
                    if nums:
                        price_num = float(nums[0])
                out.append(PriceItem(
                    product=item.get("title", "") or "",
                    price=item.get("price", "") or str(raw_price),
                    price_num=price_num,
                    source=query_used,
                    merchant=item.get("merchant_name", "") or "",
                ))
        except Exception as e:
            logger.warning("Parse prices error: %s", e)
    return out


def _filter_relevant_prices(prices: list[PriceItem], business_type: str) -> list[PriceItem]:
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

    food_keywords = {"keripik", "singkong", "makanan", "snack", "camilan", "kue", "roti", "kripik",
                     "pisang", "ubi", "kentang", "tempe", "tahu", "bakso", "soto", "nasi",
                     "mie", "ayam", "ikan", "sapi", "kambing", "seafood", "sambal", "saus",
                     "manis", "asin", "pedas", "gurih", "renyah", "kering", "basah"}

    detection_keywords = keywords | fashion_keywords | food_keywords

    filtered = []
    for p in prices:
        title_lower = p.product.lower()
        if not any(kw in title_lower for kw in detection_keywords):
            continue
        filtered.append(p)

    if not filtered:
        return prices

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
    # Adaptive distribution based on actual data spread
    max_price = nums[-1]
    if max_price <= 50000:
        ranges = [(0, 10000, "0-10rb"), (10000, 25000, "10-25rb"), (25000, 50000, "25-50rb")]
    elif max_price <= 100000:
        ranges = [(0, 25000, "0-25rb"), (25000, 50000, "25-50rb"), (50000, 100000, "50-100rb")]
    elif max_price <= 300000:
        ranges = [(0, 50000, "0-50rb"), (50000, 100000, "50-100rb"), (100000, 300000, "100-300rb")]
    else:
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
        source_data_count=len(prices),
    )


# ── Trends Parsers ──

def _parse_all_trends(raw: dict) -> list[TrendItem]:
    out = []
    for tr in raw.get("trends_results", []):
        data = tr.get("data", {})
        query_used = tr.get("query", "")
        if not isinstance(data, dict) or "error" in data:
            continue
        try:
            vals = []
            for entry in ((data.get("interest_over_time") or {}).get("timeline_data") or []):
                for v in (entry.get("values") or []):
                    try: vals.append(int(v.get("extracted_value", v.get("value", 0))))
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
                keyword=query_used, interest_values=vals,
                related_queries=related_q[:10], rising_queries=rising_q[:10],
                related_topics=related_t[:10], rising_topics=rising_t[:10],
            ))
        except Exception as e:
            logger.warning("Parse trends error for %s: %s", query_used, e)
    return out


def _build_trends_analysis(trends: list[TrendItem], raw: dict) -> TrendsAnalysis | None:
    ta_data = raw.get("trends_analysis")
    if ta_data and isinstance(ta_data, dict):
        return TrendsAnalysis(**ta_data)
    return None


# ── News Parsers ──

def _parse_all_news(raw: dict) -> list[NewsItem]:
    out = []
    for tr in raw.get("tavily_results", []):
        data = tr.get("data", {})
        query_used = tr.get("query", "")
        if not isinstance(data, dict) or "error" in data:
            continue
        try:
            for r in (data.get("results") or []) or []:
                if isinstance(r, dict):
                    out.append(NewsItem(
                        title=r.get("title", "") or "",
                        content=(r.get("content") or "")[:500],
                        url=r.get("url", "") or "",
                        source=query_used,
                    ))
        except Exception as e:
            logger.warning("Parse news error for %s: %s", query_used, e)
    return out


def _filter_relevant_news(news: list[NewsItem], business_type: str) -> list[NewsItem]:
    words = business_type.lower().split()
    keywords = set(w for w in words if w not in ("toko", "usaha", "bisnis", "jualan", "buka", "online", "shop", "store", "di", "dan", "atau"))
    keywords.update({"bisnis", "usaha", "pasar", "industri", "tren", "fashion", "retail", "kuliner", "makanan", "minuman"})

    blocked_domains = {"wikipedia", "wiktionary", "wikibooks", "wikiversity", "wikidata", "mediawiki"}

    filtered = []
    for n in news:
        title_lower = n.title.lower()
        url_lower = n.url.lower()
        if any(d in url_lower for d in blocked_domains):
            continue
        content_lower = n.content.lower()
        relevant = any(kw in title_lower or kw in content_lower for kw in keywords)
        if relevant:
            filtered.append(n)

    if not filtered:
        return []
    return filtered


# ═══════════════════════════════════════════════
#  DATA QUALITY
# ═══════════════════════════════════════════════

def _assess_data_availability(raw: dict, competitors: list, prices: list, trends: list, news: list) -> dict:
    def source_status(data_list: list, key_check: str | None = None) -> str:
        if not data_list:
            return "UNAVAILABLE"
        valid = sum(1 for d in data_list if isinstance(d.get("data"), dict) and "error" not in d.get("data", {}))
        if valid >= 2:
            return "AVAILABLE"
        if valid >= 1:
            return "PARTIAL"
        return "UNAVAILABLE"

    if len(competitors) >= 10:
        comp_status = "AVAILABLE"
    elif len(competitors) > 0:
        comp_status = "PARTIAL"
    else:
        comp_status = "UNAVAILABLE"

    if len(prices) >= 15:
        price_status = "AVAILABLE"
    elif len(prices) > 0:
        price_status = "PARTIAL"
    else:
        price_status = "UNAVAILABLE"

    ta = raw.get("trends_analysis", {})
    if ta.get("has_any_data"):
        total_vals = sum(len(kw.get("interest_values", [])) for kw in ta.get("keywords_analyzed", []))
        trend_status = "AVAILABLE" if total_vals >= 15 else "PARTIAL"
    else:
        trend_vals = sum(len(t.interest_values) for t in trends)
        trend_status = "AVAILABLE" if trend_vals >= 15 else ("PARTIAL" if trend_vals > 0 else "UNAVAILABLE")

    if len(news) >= 5:
        news_status = "AVAILABLE"
    elif len(news) > 0:
        news_status = "PARTIAL"
    else:
        tavily_results = raw.get("tavily_results", [])
        if tavily_results:
            news_status = "PARTIAL"
        else:
            news_status = "UNAVAILABLE"

    return {
        "competitors": comp_status,
        "prices": price_status,
        "trends": trend_status,
        "news": news_status,
    }


def _calculate_data_coverage(raw: dict, competitors: list, prices: list, trends: list, news: list, queries: ResearchQueries) -> dict:
    coverage = {}

    ta = raw.get("trends_analysis", {})
    kw_with_data = ta.get("keyword_count_with_data", 0)
    total_kw = len(queries.trends_queries) if queries.trends_queries else 1
    coverage["google_trends"] = round(kw_with_data / total_kw * 100) if total_kw > 0 else 0

    maps_queries_count = len(queries.maps_queries)
    maps_with_data = 0
    for result in raw.get("search_results", []):
        if result.get("source") == "maps":
            data = result.get("data", {})
            if isinstance(data, dict) and "error" not in data and data.get("local_results", {}).get("places"):
                maps_with_data += 1
    coverage["google_maps"] = round(maps_with_data / maps_queries_count * 100) if maps_queries_count > 0 else 0

    shop_queries = len(queries.shopping_queries)
    shop_with_data = len(raw.get("shopping_results", []))
    coverage["google_shopping"] = round(shop_with_data / shop_queries * 100) if shop_queries > 0 else 0

    search_queries = len(queries.search_queries)
    search_with_data = 0
    for result in raw.get("search_results", []):
        if result.get("source") != "maps":
            data = result.get("data", {})
            if isinstance(data, dict) and "error" not in data:
                search_with_data += 1
    coverage["google_search"] = round(search_with_data / search_queries * 100) if search_queries > 0 else 0

    tavily_queries = len(queries.tavily_queries)
    tavily_with_data = len(raw.get("tavily_results", []))
    coverage["tavily_news"] = round(tavily_with_data / tavily_queries * 100) if tavily_queries > 0 else 0

    all_pcts = [v for v in coverage.values() if v > 0]
    overall = round(sum(all_pcts) / len(all_pcts)) if all_pcts else 0
    coverage["overall"] = overall
    coverage["level"] = "High" if overall >= 70 else ("Medium" if overall >= 40 else "Low")

    return coverage


def _validate_data_quality(competitors: list, prices: list, trends: list, news: list, location: str, data_availability: dict | None = None) -> dict:
    trend_vals_count = sum(len(t.interest_values) for t in trends)
    return {
        "competitors_count": len(competitors),
        "prices_count": len(prices),
        "trends_count": trend_vals_count,
        "news_count": len(news),
        "has_specific_location": location.lower() not in ("indonesia", ""),
        "availability": data_availability or {}
    }


# ═══════════════════════════════════════════════
#  NEW: EVIDENCE-BASED OPPORTUNITY ENGINE
# ═══════════════════════════════════════════════

def _build_opportunity_engine(
    scores: BusinessScore, competitors: list[Competitor], trends: list[TrendItem],
    prices: list[PriceItem], price_stats: PriceStats, review_stats: ReviewStats,
    availability: dict, context: ResearchContext
) -> list[MarketOpportunity]:
    """Identify market opportunities with evidence tracking."""
    opportunities = []

    # 1. Supply Gap: Few competitors in a segment
    if availability["competitors"] != "UNAVAILABLE" and len(competitors) < 5:
        opp = MarketOpportunity(
            opportunity=f"Supply Gap — Hanya {len(competitors)} kompetitor terdeteksi di area {context.location_city or 'ini'}.",
            evidence=[
                EvidenceItem(description=f"{len(competitors)} kompetitor relevan terdeteksi.", source="Google Maps", strength="sedang"),
            ],
            counter_evidence=[
                "Jumlah kompetitor rendah bisa berarti pasar belum terbentuk, bukan peluang.",
                "Bisnis informal/rumahan tidak terdeteksi di Google Maps.",
            ],
            confidence="rendah",
            gap_type="supply",
            validation_required=["Konfirmasi apakah benar hanya ada sedikit pesaing di lapangan."],
        )
        opportunities.append(opp)

    # 2. Price Gap: Price segments with low supply
    if price_stats.total > 0 and price_stats.distribution:
        sorted_dist = sorted(price_stats.distribution.items(), key=lambda x: x[1])
        low_supply_segments = [seg for seg, pct in sorted_dist if pct < 15]
        if low_supply_segments:
            opp = MarketOpportunity(
                opportunity=f"Price Gap — Segmen harga {', '.join(low_supply_segments[:2])} memiliki sedikit produk terdeteksi (masing-masing <15% dari total {price_stats.total} produk).",
                evidence=[
                    EvidenceItem(description=f"Distribusi produk per segmen: {dict(sorted_dist[-3:])}", source="Google Shopping", strength="sedang"),
                ],
                counter_evidence=[
                    "Jumlah produk sedikit bukan berarti permintaan tinggi — bisa jadi pasar yang tidak matang.",
                    "Segmen premium sering overestimated oleh AI tanpa bukti willingness-to-pay.",
                ],
                confidence="sedang",
                gap_type="price",
                validation_required=["Validasi apakah konsumen bersedia membayar di segmen tersebut."],
            )
            opportunities.append(opp)

    # 3. Quality Gap: Low average ratings
    if review_stats.avg_rating > 0 and review_stats.avg_rating < 4.0 and review_stats.competitor_count >= 3:
        opp = MarketOpportunity(
            opportunity=f"Quality Gap — Rata-rata rating kompetitor {review_stats.avg_rating:.1f}/5.0 menunjukkan adanya celah kualitas yang dapat dimanfaatkan.",
            evidence=[
                EvidenceItem(description=f"Rata-rata rating: {review_stats.avg_rating:.1f} dari {review_stats.competitor_count} kompetitor.", source="Google Maps", strength="kuat"),
                EvidenceItem(description=f"Jumlah total review: {review_stats.total_reviews:,}", source="Google Maps", strength="sedang"),
            ],
            counter_evidence=[
                "Rating rendah mungkin mencerminkan basis pelanggan yang sudah ada, bukan potensi pasar baru.",
                "Rating di Google Maps tidak selalu mencerminkan kualitas produk secara keseluruhan.",
            ],
            confidence="sedang",
            gap_type="quality",
            validation_required=["Pelajari keluhan spesifik dari review rendah untuk mengidentifikasi celah kualitas."],
        )
        opportunities.append(opp)

    # 4. Geographic Gap: Product sold but local supply limited
    if context.location_city and len(competitors) <= 3 and availability["trends"] != "UNAVAILABLE":
        opp = MarketOpportunity(
            opportunity=f"Geographic Gap — Minat pencarian terdeteksi secara nasional namun kompetitor lokal di {context.location_city} terbatas ({len(competitors)} terdeteksi).",
            evidence=[
                EvidenceItem(description=f"{len(competitors)} kompetitor di {context.location_city}.", source="Google Maps", strength="sedang"),
            ],
            counter_evidence=[
                "Minat pencarian nasional belum menjamin permintaan lokal yang setara.",
                "Google Maps tidak mendeteksi semua bisnis informal.",
            ],
            confidence="sedang",
            gap_type="geographic",
            validation_required=["Validasi permintaan lokal melalui survey atau pre-order."],
        )
        opportunities.append(opp)

    # 5. Demand Gap: High search volume but low supply
    if scores.demand is not None and scores.demand >= 70 and scores.competition is not None and scores.competition <= 40:
        opp = MarketOpportunity(
            opportunity="Demand-Supply Mismatch — Permintaan pencarian tinggi tetapi persaingan terdeteksi rendah.",
            evidence=[
                EvidenceItem(description=f"Demand skor: {scores.demand}/100 (tinggi)", source="Google Trends + Google Shopping", strength="kuat"),
                EvidenceItem(description=f"Competition skor: {scores.competition}/100 (rendah)", source="Google Maps", strength="sedang"),
            ],
            counter_evidence=[
                "Permintaan pencarian tinggi belum tentu berarti permintaan pembelian.",
                "Persaingan mungkin lebih tinggi di saluran lain (marketplace, offline).",
            ],
            confidence="sedang",
            gap_type="demand",
            validation_required=["Validasi commercial intent (keyword seperti 'beli', 'harga', 'grosir')."],
        )
        opportunities.append(opp)

    if not opportunities:
        opportunities.append(MarketOpportunity(
            opportunity="Belum ditemukan celah pasar yang jelas dari data yang tersedia.",
            evidence=[],
            counter_evidence=["Data mungkin tidak cukup untuk mengidentifikasi peluang spesifik."],
            confidence="rendah",
            gap_type="supply",
            validation_required=["Kumpulkan data primer melalui survey atau wawancara."],
        ))

    return opportunities


# ═══════════════════════════════════════════════
#  NEW: DEMAND SUB-SCORES
# ═══════════════════════════════════════════════

def _build_demand_sub_scores(trends: list[TrendItem], prices: list[PriceItem], news: list[NewsItem], availability: dict) -> DemandSubScores:
    # Search Demand (Google Trends avg interest)
    search_demand = 0
    all_vals = []
    for t in trends:
        all_vals.extend(t.interest_values)
    if all_vals:
        avg = sum(all_vals) / len(all_vals)
        if avg > 70: search_demand = min(95, 70 + int((avg - 70) * 0.8))
        elif avg > 40: search_demand = 50 + int((avg - 40) * 0.8)
        elif avg > 20: search_demand = 30 + int((avg - 20) * 1.0)
        else: search_demand = max(10, int(avg * 0.8))

    # Commercial Intent (from related_queries)
    commercial_intent = 0
    commercial_keywords = {"beli", "harga", "jual", "grosir", "supplier", "terdekat", "toko", "pesan", "delivery", "shop", "store", "online", "murah"}
    for t in trends:
        all_q = t.related_queries + t.rising_queries
        commercial_hits = sum(1 for q in all_q if any(kw in q.lower() for kw in commercial_keywords))
        if len(all_q) > 0:
            ratio = commercial_hits / len(all_q)
            commercial_intent = min(95, int(ratio * 100))

    # Local Demand (from location-specific queries)
    local_demand = 50 if availability.get("competitors") != "UNAVAILABLE" else 0

    # Shopping Demand (from price data volume)
    shopping_demand = min(95, len(prices) * 3) if prices else 0

    # Content Demand (from news/articles)
    content_demand = min(95, len(news) * 10) if news else 0

    # Social Demand (placeholder — not available via current APIs)
    social_demand = 0

    weights = {"search": 0.30, "commercial": 0.25, "local": 0.20, "shopping": 0.15, "content": 0.05, "social": 0.05}
    overall = int(
        search_demand * weights["search"] +
        commercial_intent * weights["commercial"] +
        local_demand * weights["local"] +
        shopping_demand * weights["shopping"] +
        content_demand * weights["content"] +
        social_demand * weights["social"]
    )

    return DemandSubScores(
        search_demand=search_demand,
        commercial_intent=commercial_intent,
        local_demand=local_demand,
        shopping_demand=shopping_demand,
        content_demand=content_demand,
        social_demand=social_demand,
        overall_demand=overall,
    )


# ═══════════════════════════════════════════════
#  NEW: DEMAND BREAKDOWN
# ═══════════════════════════════════════════════

def _build_demand_breakdown(trends: list[TrendItem], raw: dict, context: ResearchContext) -> DemandBreakdown:
    """
    Estimate national, regional, and local demand.
    Uses different keywords for different geographies.
    """
    all_vals = []
    for t in trends:
        all_vals.extend(t.interest_values)

    national = 0
    regional = 0
    local = 0

    if all_vals:
        avg = sum(all_vals) / len(all_vals)
        national = int(avg)

    # Regional adjustment: if province/city known, estimate regional
    if context.location_province:
        regional = max(0, national - 10)  # regional typically lower than national
    else:
        regional = national

    # Local adjustment
    if context.location_city:
        # With specific location, local signal exists
        kw_results = raw.get("trends_keywords_raw", [])
        local_keywords_found = 0
        for kw in kw_results:
            if isinstance(kw, dict):
                kw_name = kw.get("keyword", "").lower()
                city = context.location_city.lower()
                if city in kw_name and kw.get("has_data"):
                    local_keywords_found += 1
                    local = kw.get("avg_interest", 0)
                    break
        # If no local keyword data found, estimate
        if local == 0 and regional > 0:
            local = max(0, regional - 15)
    else:
        local = 0

    note = ""
    if context.location_city and local == 0:
        note = f"Data permintaan spesifik untuk {context.location_city} tidak tersedia dari Google Trends. Permintaan lokal belum dapat dipastikan."
    elif context.location_city:
        note = f"Data permintaan lokal untuk {context.location_city} terdeteksi."
    else:
        note = "Tidak ada lokasi spesifik. Analisis didasarkan pada data nasional."

    return DemandBreakdown(
        national=int(national),
        regional=int(regional),
        local=int(local),
        local_data_available=local > 0,
        note=note,
    )


# ═══════════════════════════════════════════════
#  NEW: COMPETITOR INTELLIGENCE
# ═══════════════════════════════════════════════

def _analyze_competitor_strength(competitors: list[Competitor]) -> list[CompetitorStrength]:
    """Analyze each competitor's strength based on available data."""
    strengths = []
    for c in competitors:
        if not c.name:
            continue

        # Calculate popularity
        rev = c.reviews or 0
        if rev > 100:
            pop = "tinggi"
        elif rev > 10:
            pop = "sedang"
        else:
            pop = "rendah"

        # Estimate brand visibility from name length + reviews
        brand_vis = min(80, max(10, len(c.name) * 2 + rev // 2))
        search_vis = min(80, max(10, rev))
        product_variety = min(50, max(1, rev // 10))

        # Price positioning from name hints
        price_pos = "menengah"
        name_low = c.name.lower()
        if any(kw in name_low for kw in ["murah", "ekonomis", "hemat"]):
            price_pos = "ekonomis"
        elif any(kw in name_low for kw in ["premium", "mewah", "eksklusif", "luxury"]):
            price_pos = "premium"

        # Rating contribution
        rating_score = (c.rating or 3.0) / 5.0 * 30
        strength_score = round((rating_score + min(rev, 200) / 200 * 40 + brand_vis / 80 * 30) / 100 * 100, 1)

        strengths.append(CompetitorStrength(
            name=c.name,
            rating=c.rating or 0,
            reviews=rev,
            popularity=pop,
            brand_visibility=brand_vis,
            search_visibility=search_vis,
            product_variety=product_variety,
            price_positioning=price_pos,
            strength_score=strength_score,
        ))

    strengths.sort(key=lambda x: x.strength_score, reverse=True)
    return strengths[:15]


def _build_competitive_map(competitors: list[Competitor], prices: list[PriceItem]) -> CompetitiveMap:
    """Build competitive positioning map (price vs popularity)."""
    positions = []
    for c in competitors[:20]:
        if not c.name:
            continue

        rev = c.reviews or 0
        if rev > 100:
            pop_tier = "tinggi"
        elif rev > 10:
            pop_tier = "sedang"
        else:
            pop_tier = "rendah"

        rating_val = c.rating or 0
        if rating_val >= 4.5:
            qual_tier = "tinggi"
        elif rating_val >= 4.0:
            qual_tier = "sedang"
        else:
            qual_tier = "rendah"

        price_tier = "menengah"
        name_low = c.name.lower()
        if any(kw in name_low for kw in ["murah", "ekonomis", "hemat"]):
            price_tier = "ekonomis"
        elif any(kw in name_low for kw in ["premium", "mewah", "eksklusif"]):
            price_tier = "premium"

        positions.append(CompetitivePosition(
            price_tier=price_tier,
            quality_tier=qual_tier,
            popularity_tier=pop_tier,
        ))

    return CompetitiveMap(
        x_axis="price",
        y_axis="popularity",
        positions=positions,
    )


# ═══════════════════════════════════════════════
#  NEW: PRICE POSITIONING
# ═══════════════════════════════════════════════

def _build_price_positioning(prices: list[PriceItem], price_stats: PriceStats) -> PricePositioning:
    """Analyze price segments, sweet spot, and gaps."""
    nums = sorted([p.price_num for p in prices if p.price_num > 0])
    if not nums:
        return PricePositioning()

    n = len(nums)
    max_price = nums[-1]

    # Adaptive segments
    if max_price <= 50000:
        segments_def = [
            ("Budget", 0, 10000),
            ("Mass Market", 10000, 25000),
            ("Mid-range", 25000, 50000),
        ]
    elif max_price <= 100000:
        segments_def = [
            ("Budget", 0, 15000),
            ("Mass Market", 15000, 35000),
            ("Mid-range", 35000, 70000),
            ("Premium", 70000, max_price + 1),
        ]
    elif max_price <= 300000:
        segments_def = [
            ("Budget", 0, 25000),
            ("Mass Market", 25000, 75000),
            ("Mid-range", 75000, 150000),
            ("Premium", 150000, max_price + 1),
        ]
    else:
        segments_def = [
            ("Budget", 0, 50000),
            ("Mass Market", 50000, 100000),
            ("Mid-range", 100000, 300000),
            ("Premium", 300000, max_price + 1),
        ]

    segments = []
    for name, lo, hi in segments_def:
        cnt = sum(1 for x in nums if lo <= x < hi)
        segments.append(PriceSegment(
            name=name,
            min=lo,
            max=hi,
            count=cnt,
            percentage=round(cnt / n * 100, 1),
        ))

    # Sweet spot: segment with most products
    sweet = max(segments, key=lambda s: s.count)
    sweet_spot = f"{sweet.name} ({int(sweet.min)}-{int(sweet.max)}) dengan {sweet.percentage}% produk"

    # Competitive gaps: segments with low supply
    comp_gaps = [s.name for s in segments if s.percentage < 15]
    demand_validated_gaps = []
    for s in segments:
        if s.percentage < 15:
            demand_validated_gaps.append(
                f"{s.name} ({int(s.min)}-{int(s.max)}): supply rendah ({s.percentage}%), perlu validasi demand."
            )

    return PricePositioning(
        segments=segments,
        sweet_spot=sweet_spot,
        competitive_gap=comp_gaps,
        demand_validated_gap=demand_validated_gaps,
    )


# ═══════════════════════════════════════════════
#  NEW: DATA LIMITATIONS
# ═══════════════════════════════════════════════

def _build_data_limitations(raw: dict, competitors: list, prices: list, trends: list, news: list, context: ResearchContext) -> list[DataLimitation]:
    limitations = [
        DataLimitation(
            limitation="Google Trends bukan volume pencarian absolut — hanya indeks relatif (0-100).",
            impact="Angka 76 tidak berarti 76.000 pencarian, melainkan 76% dari puncak popularitas keyword.",
            mitigation="Gunakan sebagai indikator arah, bukan volume absolut.",
        ),
        DataLimitation(
            limitation="Google Maps bukan database seluruh bisnis.",
            impact=f"{len(competitors)} kompetitor terdeteksi belum tentu mewakili total pasar.",
            mitigation="Jadikan data ini sebagai sampling, bukan sensus.",
        ),
        DataLimitation(
            limitation="Google Shopping tidak representatif untuk seluruh saluran penjualan.",
            impact=f"{len(prices)} produk terdeteksi dari Google Shopping. Marketplace seperti Tokopedia/Shopee tidak tercakup.",
            mitigation="Lengkapi dengan riset harga di marketplace utama.",
        ),
    ]
    if context.location_city:
        limitations.append(DataLimitation(
            limitation=f"Data spesifik {context.location_city} terbatas.",
            impact="Analisis lokal sangat bergantung pada output Google Trends untuk keyword + lokasi.",
            mitigation="Validasi permintaan lokal melalui survey atau pre-order.",
        ))
    limitations.append(DataLimitation(
        limitation="Penjualan aktual kompetitor tidak diketahui.",
        impact="Peringkat/review di Google Maps tidak mencerminkan volume penjualan atau profitabilitas.",
        mitigation="Gunakan data ini sebagai proksi, bukan indikator langsung.",
    ))
    return limitations


# ═══════════════════════════════════════════════
#  NEW: CONTRADICTION DETECTION
# ═══════════════════════════════════════════════

def _detect_contradictions(
    scores: BusinessScore, competitors: list[Competitor], trends: list[TrendItem],
    prices: list[PriceItem], price_stats: PriceStats, review_stats: ReviewStats,
    availability: dict
) -> list[SignalContradiction]:
    """Detect when signals from different data sources contradict each other."""
    contradictions = []

    # 1. High demand but low competition
    if scores.demand is not None and scores.competition is not None:
        if scores.demand >= 65 and scores.competition <= 30:
            contradictions.append(SignalContradiction(
                signal_a=f"Demand tinggi ({scores.demand}) dari Google Trends",
                signal_b=f"Kompetisi rendah ({scores.competition}) dari Google Maps",
                explanation="Demand sinyal positif tetapi supply terdeteksi sedikit. Ini bisa berupa early market opportunity, atau bisa juga berarti pasar tidak terbentuk karena alasan struktural.",
                resolution="Validasi dengan data penjualan aktual dan commercial intent keywords.",
            ))

    # 2. High trend but declining momentum
    if scores.demand is not None and scores.trend is not None:
        if scores.demand >= 60 and scores.trend < 45:
            contradictions.append(SignalContradiction(
                signal_a=f"Demand saat ini baik ({scores.demand})",
                signal_b=f"Tren pencarian menurun ({scores.trend})",
                explanation="Minat pencarian saat ini masih ada tetapi momentum menunjukkan penurunan. Pasar mungkin telah melewati puncaknya.",
                resolution="Fokus pada retensi daripada akuisisi agresif.",
            ))

    # 3. Low competition but many products
    if availability.get("prices") != "UNAVAILABLE" and availability.get("competitors") != "UNAVAILABLE":
        if len(prices) >= 20 and len(competitors) <= 5:
            contradictions.append(SignalContradiction(
                signal_a=f"Banyak produk ({len(prices)}) di Google Shopping",
                signal_b=f"Sedikit kompetitor ({len(competitors)}) di Google Maps",
                explanation="Banyak produk terdeteksi tetapi sedikit bisnis. Ini bisa berarti beberapa penjual menjual banyak varian, atau kompetitor online tidak terdaftar di Google Maps.",
                resolution="Periksa marketplace (Tokopedia/Shopee) untuk penjual yang mungkin tidak memiliki Google Business Profile.",
            ))

    # 4. Low ratings but good demand
    if review_stats.avg_rating and review_stats.avg_rating < 4.0 and scores.demand is not None and scores.demand >= 60:
        contradictions.append(SignalContradiction(
            signal_a=f"Rating rendah ({review_stats.avg_rating:.1f}/5.0)",
            signal_b=f"Demand tinggi ({scores.demand}/100)",
            explanation="Konsumen terus mencari meskipun rating kompetitor rendah — ada unmet need yang belum dipenuhi dengan baik.",
            resolution="Kualitas layanan bisa menjadi diferensiasi utama. Identifikasi keluhan spesifik dari review.",
        ))

    return contradictions


# ═══════════════════════════════════════════════
#  NEW: VALIDATION CHECKLIST
# ═══════════════════════════════════════════════

def _build_validation_checklist(scores: BusinessScore, price_stats: PriceStats, context: ResearchContext) -> ValidationChecklist:
    must = []
    recommended = []

    must.append(ValidationItem(
        question="Apakah pelanggan lokal bersedia membeli produk ini?",
        priority="wajib",
        experiment="Tawarkan 3 varian harga kepada 20-30 calon pelanggan.",
        success_metric="Minimal 20% menunjukkan minat beli.",
        budget="Rp50.000-Rp200.000",
    ))

    must.append(ValidationItem(
        question="Berapa harga yang bersedia dibayar oleh pelanggan?",
        priority="wajib",
        experiment=f"Uji 3 titik harga: Rp{int(price_stats.median_num * 0.7)}, Rp{price_stats.median_num}, Rp{int(price_stats.median_num * 1.3)}",
        success_metric="Konversi tertinggi pada harga target.",
        budget="Rp100.000",
    ))

    if context.location_city:
        must.append(ValidationItem(
            question=f"Apakah ada cukup pelanggan di {context.location_city}?",
            priority="wajib",
            experiment=f"Buat pre-order campaign terbatas untuk 50 unit di {context.location_city}.",
            success_metric="Minimal 20 pre-order dalam 7 hari.",
            budget="Rp0 (pre-order)",
        ))

    recommended.append(ValidationItem(
        question="Apakah margin setelah semua biaya masih cukup?",
        priority="disarankan",
        experiment="Hitung HPP aktual dengan 3 supplier berbeda.",
        success_metric="Gross margin minimal 35%.",
        budget="Rp100.000-Rp300.000",
    ))

    recommended.append(ValidationItem(
        question="Apakah produk dapat dikirim tanpa rusak?",
        priority="disarankan",
        experiment="Kirim 5 sampel produk ke alamat berbeda via ekspedisi.",
        success_metric="Tingkat kerusakan < 10%.",
        budget="Rp50.000-Rp100.000",
    ))

    return ValidationChecklist(must_validate=must, recommended=recommended)


# ═══════════════════════════════════════════════
#  SWOT BUILDER
# ═══════════════════════════════════════════════

def _build_swot(scores: BusinessScore, competitors: list[Competitor], prices: list[PriceItem], price_stats: PriceStats, review_stats: ReviewStats, demand_breakdown: DemandBreakdown | None = None) -> SwotItem:
    d = scores.demand; c = scores.competition; p = scores.profit_potential; t = scores.trend; r = scores.risk
    sw_s, sw_w, sw_o, sw_t = [], [], [], []

    if d is not None and d >= 55: sw_s.append(f"Permintaan pasar {get_score_label(d).lower()} (skor {d})")
    if p is not None and p >= 55: sw_s.append(f"Potensi pricing {get_score_label(p).lower()} (skor {p})")
    if c is not None and c <= 40: sw_s.append(f"Persaingan masih terkendali ({len(competitors)} kompetitor terdeteksi)")
    if demand_breakdown and demand_breakdown.local_data_available:
        sw_s.append(f"Data permintaan lokal tersedia ({demand_breakdown.local})")
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
        if cheap >= 3: sw_t.append(f"Ancaman perang harga ({cheap} produk < Rp50rb)")
    if not sw_t: sw_t.append("Munculnya pemain baru dengan modal iklan lebih besar")

    return SwotItem(strength=sw_s[:3], weakness=sw_w[:3], opportunity=sw_o[:3], threat=sw_t[:3])


# ═══════════════════════════════════════════════
#  NEW: INSIGHT CONFIDENCES
# ═══════════════════════════════════════════════

def _build_insight_confidences(scores: BusinessScore, competitors: list, prices: list, trends: list, review_stats: ReviewStats, availability: dict) -> list[InsightConfidence]:
    confs = []

    n_prices = len(prices)
    n_comp = len(competitors)
    n_reviews = review_stats.total_reviews or 0
    n_trend = sum(len(t.interest_values) for t in trends)

    # Market Demand confidence
    demand_conf = min(85, 30 + n_trend * 2)
    confs.append(InsightConfidence(
        insight="Market Demand",
        value=f"{scores.demand}/100" if scores.demand is not None else "N/A",
        confidence=demand_conf,
        note=f"Berdasarkan {n_trend} data point dari Google Trends.",
    ))

    # Competition confidence
    comp_conf = min(80, 20 + n_comp * 4)
    confs.append(InsightConfidence(
        insight="Competition",
        value=f"{scores.competition}/100" if scores.competition is not None else "N/A",
        confidence=comp_conf,
        note=f"Berdasarkan {n_comp} kompetitor dari Google Maps.",
    ))

    # Price Analysis confidence
    price_conf = min(85, 25 + n_prices * 3)
    confs.append(InsightConfidence(
        insight="Price Analysis",
        value=f"{n_prices} produk dianalisis",
        confidence=price_conf,
        note=f"Berdasarkan {n_prices} produk dari Google Shopping.",
    ))

    # Premium Opportunity — low confidence by default
    confs.append(InsightConfidence(
        insight="Premium Opportunity",
        value="Perlu validasi",
        confidence=35,
        note="Willingness-to-pay belum tervalidasi.",
    ))

    # Profitability — low confidence
    confs.append(InsightConfidence(
        insight="Profitability",
        value="Tidak diketahui",
        confidence=20,
        note="Data biaya produksi aktual tidak tersedia.",
    ))

    return confs


# ═══════════════════════════════════════════════
#  NEW: ACTION PLAN V2
# ═══════════════════════════════════════════════

def _build_action_plan_v2(scores: BusinessScore, price_stats: PriceStats, competitors: list, review_stats: ReviewStats, context: ResearchContext) -> list[ActionPlanV2]:
    plans = []

    # Week 1: Validation
    plans.append(ActionPlanV2(
        day_range="Hari 1-7",
        goal="Validasi 3 segmen harga dan minat beli",
        actions=[
            f"Tawarkan 3 paket harga (Rp{int(price_stats.median_num * 0.7)}/{price_stats.median_num}/{int(price_stats.median_num * 1.3)}) kepada 20-30 calon pelanggan.",
            "Lakukan 10 wawancara singkat dengan target pelanggan.",
            "Catat tingkat minat dan harga yang dipilih.",
        ],
        budget="Rp50.000 - Rp200.000",
        success_metric="Minimal 20% menunjukkan minat beli pada harga target.",
        decision_rule="Jika < 10% minat, reposition harga atau evaluasi produk.",
    ))

    # Week 2: Product testing
    mid_price = int(price_stats.median_num) if price_stats.total > 0 else 25000
    plans.append(ActionPlanV2(
        day_range="Hari 8-14",
        goal="Uji coba produk dengan 3 varian",
        actions=[
            f"Buat 3 varian produk (rasa/ukuran/kemasan).",
            "Jual 10-15 unit per varian melalui pre-order atau grup WA.",
            "Kumpulkan feedback tentang rasa, kemasan, dan harga.",
        ],
        budget="Rp300.000 - Rp500.000",
        success_metric="Minimal 30 unit terjual dalam 7 hari.",
        decision_rule="Jika < 15 unit terjual, evaluasi product-market fit.",
    ))

    # Week 3: Operations
    plans.append(ActionPlanV2(
        day_range="Hari 15-21",
        goal="Tes packaging, pengiriman, dan operasional",
        actions=[
            "Kirim 5-10 sampel produk via ekspedisi (JNE/SiCepat/Shopee Express).",
            "Evaluasi kerusakan dan biaya pengiriman.",
            "Hitung HPP aktual (bahan baku + tenaga kerja + packaging + gas/listrik).",
        ],
        budget="Rp100.000 - Rp250.000",
        success_metric="Tingkat kerusakan < 10%, HPP < 50% dari harga jual.",
        decision_rule="Jika HPP > 60% dari harga jual, cari supplier alternatif atau naikkan harga.",
    ))

    # Week 4: Mini launch
    plans.append(ActionPlanV2(
        day_range="Hari 22-30",
        goal="Tes penjualan skala kecil",
        actions=[
            "Daftar di 1 marketplace (Shopee/Tokopedia/GrabFood).",
            "Upload 3-5 produk dengan foto menarik.",
            "Jalankan campaign penjualan dengan target 50 unit.",
        ],
        budget="Rp500.000 - Rp1.000.000",
        success_metric="Conversion rate > 3%, repeat purchase > 10%.",
        decision_rule="Jika conversion rate < 3%, revisi strategi pricing atau positioning.",
    ))

    return plans


# ═══════════════════════════════════════════════
#  NEW: PRODUCT OPPORTUNITIES
# ═══════════════════════════════════════════════

def _build_product_opportunities(scores: BusinessScore, competitors: list[Competitor], trends: list[TrendItem], prices: list[PriceItem], availability: dict, context: ResearchContext) -> list[ProductOpportunity]:
    """Build product opportunity matrix from available data."""
    opps = []

    # Analyze related queries for product cravings
    rising_q = set()
    for t in trends:
        rising_q.update(t.rising_queries)
        rising_q.update(t.related_queries[:5])

    # Common product variants from search queries
    variant_keywords = {
        "pedas": "Varian Pedas",
        "manis": "Varian Manis",
        "original": "Original",
        "balado": "Varian Balado",
        "barbeku": "Varian Barbeque",
        "keju": "Varian Keju",
        "asli": "Original",
        "mini": "Kemasan Mini",
        "besar": "Kemasan Besar",
        "ekonomis": "Kemasan Ekonomis",
        "lauk": "Keripik sebagai Lauk",
        "camilan": "Camilan Sehari-hari",
        "oleh": "Oleh-oleh / Gift",
        "hampers": "Hampers",
        "kado": "Kado / Hadiah",
        "premium": "Produk Premium",
        "100gr": "Kemasan 100gr",
        "250gr": "Kemasan 250gr",
        "500gr": "Kemasan 500gr",
        "1kg": "Kemasan 1kg",
    }

    found_variants = set()
    for q in rising_q:
        for kw, variant in variant_keywords.items():
            if kw in q.lower():
                found_variants.add(variant)

    # Determine evidence from data
    for variant in sorted(found_variants)[:8]:
        confidence = "rendah"
        demand = "unknown"
        competition = "unknown"

        if any(trend_val > 50 for trend in trends for trend_val in trend.interest_values):
            demand = "sedang"

        # Check if any competitor mentions match
        comp_hints = sum(1 for c in competitors if variant.lower()[:4] in c.name.lower())
        if comp_hints > 0:
            competition = "terdeteksi"

        opps.append(ProductOpportunity(
            product=variant,
            demand=demand,
            competition=competition,
            evidence=f"Muncul dalam pencarian terkait ({len([q for q in rising_q if any(kw in q.lower() for kw, v in variant_keywords.items() if v == variant)])} mentions).",
            difficulty="rendah" if "Kemasan" in variant else "sedang",
            confidence=confidence,
        ))

    if not opps:
        opps.append(ProductOpportunity(
            product=context.product or "Produk Dasar",
            demand="unknown",
            competition="unknown",
            evidence="Data produk spesifik belum tersedia dari Google Trends.",
            difficulty="sedang",
            confidence="rendah",
        ))

    return opps


# ═══════════════════════════════════════════════
#  NEW: UNIT ECONOMICS SIMULATION
# ═══════════════════════════════════════════════

def _simulate_unit_economics(inp: UnitEconomicsInput) -> UnitEconomicsOutput:
    """Calculate unit economics from user-provided inputs."""
    if inp.selling_price <= 0:
        return UnitEconomicsOutput(
            note="Harga jual harus diisi untuk menghitung unit economics.",
        )

    hpp = inp.raw_material + inp.labor + inp.packaging + inp.shipping + inp.marketplace_fee + inp.marketing + inp.other_costs
    gross_profit = inp.selling_price - hpp
    gross_margin = (gross_profit / inp.selling_price * 100) if inp.selling_price > 0 else 0

    # Break-even: if margin positive
    total_fixed = inp.marketing  # treat marketing as fixed for simplicity
    break_even = 0
    if gross_profit > 0:
        break_even = max(1, int(total_fixed / gross_profit))

    note = ""
    if gross_margin >= 40:
        note = "Margin cukup baik. Bisnis memiliki ruang untuk biaya operasional dan promosi."
    elif gross_margin >= 25:
        note = "Margin moderat. Perlu volume penjualan yang cukup untuk mencapai profit."
    elif gross_margin >= 15:
        note = "Margin tipis. Risiko kerugian tinggi jika volume tidak tercapai."
    else:
        note = "Margin sangat rendah atau negatif. Evaluasi ulang harga jual atau struktur biaya."

    return UnitEconomicsOutput(
        hpp=round(hpp),
        gross_profit=round(gross_profit),
        gross_margin=round(gross_margin, 1),
        break_even_units=break_even,
        minimum_sales=break_even,
        estimated_monthly_profit=round(gross_profit * 100),  # rough estimate: 100 units
        note=note,
    )



# ═══════════════════════════════════════════════
#  TRANSPARENT SCORING ENGINE
# ═══════════════════════════════════════════════

def _calculate_scores_detailed(competitors: list[Competitor], trends: list[TrendItem], prices: list[PriceItem], availability: dict, review_stats: ReviewStats) -> BusinessScore:
    demand = None; competition = None; profit = None; trend_score = None; risk = None

    # 1. Demand — based on ALL trend keywords
    if availability["trends"] != "UNAVAILABLE":
        all_vals = []
        for t in trends:
            all_vals.extend(t.interest_values)
        if all_vals:
            avg = sum(all_vals) / len(all_vals)
            if avg > 70: demand = min(95, 70 + int((avg - 70) * 0.8))
            elif avg > 40: demand = 50 + int((avg - 40) * 0.8)
            elif avg > 20: demand = 30 + int((avg - 20) * 1.0)
            else: demand = max(10, int(avg * 0.8))
        else:
            demand = 50

        # Trend score
        trend_score = 50
        if all_vals and len(all_vals) >= 4:
            half = len(all_vals)//2
            first = sum(all_vals[:half])/half
            second = sum(all_vals[half:])/(len(all_vals)-half)
            if second - first > 10: trend_score = 80
            elif second - first > 5: trend_score = 65
            elif second - first > -5: trend_score = 50
            else: trend_score = 30
        elif all_vals and len(all_vals) >= 2:
            half = len(all_vals)//2
            first = sum(all_vals[:half])/half if half > 0 else all_vals[0]
            second = sum(all_vals[half:])/(len(all_vals)-half) if (len(all_vals)-half) > 0 else all_vals[-1]
            if second - first > 5: trend_score = 65
            elif second - first > -5: trend_score = 50
            else: trend_score = 35
    else:
        demand = None
        trend_score = None

    # 2. Competition — based on ALL competitors
    if availability["competitors"] != "UNAVAILABLE":
        n = len(competitors)
        if n == 0: competition = 5
        elif n <= 3: competition = 15
        elif n <= 5: competition = 25
        elif n <= 10: competition = 35
        elif n <= 20: competition = 50
        elif n <= 35: competition = 65
        elif n <= 50: competition = 80
        else: competition = 95

        if review_stats and review_stats.total_reviews > 0 and n > 0:
            avg_reviews = review_stats.total_reviews / n
            if avg_reviews > 100 and competition:
                competition = min(95, competition + 10)
    else:
        competition = None

    # 3. Profit Potential — UPGRADED: more conservative, renamed conceptually
    if availability["prices"] != "UNAVAILABLE":
        n_p = len(prices)
        if n_p == 0:
            profit = 40
        elif n_p <= 5:
            profit = 45
        elif n_p <= 15:
            profit = 55
        elif n_p <= 30:
            profit = 65
        elif n_p <= 50:
            profit = 75
        else:
            profit = 85

        # Adjust down: profit is about margin, not just product count
        if profit and profit >= 70:
            profit = min(85, profit - 10)  # Cap at 85, not 95
    else:
        profit = None

    # 4. Risk
    factors = []
    if trend_score is not None: factors.append(100 - trend_score)
    if competition is not None: factors.append(competition)
    if factors:
        risk = round(sum(factors) / len(factors))
    else:
        risk = None

    # 5. Overall
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


# ═══════════════════════════════════════════════
#  UPGRADED DECISION ENGINE (6 tiers)
# ═══════════════════════════════════════════════

def _build_decision_upgraded(
    scores: BusinessScore, competitors: list[Competitor], trends: list[TrendItem],
    prices: list[PriceItem], price_stats: PriceStats, review_stats: ReviewStats,
    metrics: dict, business_type: str, availability: dict,
    trends_analysis: TrendsAnalysis | None = None,
    opportunities: list[MarketOpportunity] = None,
    contradictions: list[SignalContradiction] = None,
    validation_checklist: ValidationChecklist = None,
    data_limitations: list[DataLimitation] = None,
    demand_breakdown: DemandBreakdown = None,
) -> DecisionEngine:
    d = scores.demand; c = scores.competition; p = scores.profit_potential; t = scores.trend; r = scores.risk
    ov = scores.overall
    ta = trends_analysis

    def bl(score):
        lbl = get_score_label(score)
        return BenchmarkLabel(label=lbl, level=lbl)

    sat = c if c is not None else 0
    sat_reasons = []
    if availability["competitors"] == "UNAVAILABLE":
        sat_reasons.append("Data lokasi tidak tersedia")
    else:
        if c is not None:
            if c >= 70: sat_reasons.append("Persaingan digital sangat ketat")
            elif c >= 40: sat_reasons.append("Tingkat persaingan moderat")
            else: sat_reasons.append("Kompetitor digital masih minim")
        if len(competitors) > 5:
            max_rev = max([comp.reviews or 0 for comp in competitors])
            if max_rev > 200: sat_reasons.append("Ada pemain dengan dominasi review besar")

    comp_inv = (100 - c) if c is not None else 50
    opp_factors = [v for v in [d, p, t, comp_inv] if v is not None]
    opp = round(sum(opp_factors) / len(opp_factors)) if opp_factors else 0

    opp_pos, opp_neg = [], []
    if d is not None and d >= 60: opp_pos.append("Permintaan pasar tinggi")
    if p is not None and p >= 60: opp_pos.append("Potensi profit margin sehat")
    if c is not None and c <= 40: opp_pos.append("Akses pasar masih terbuka")
    if d is not None and d < 40: opp_neg.append("Minat pasar rendah")
    if c is not None and c >= 70: opp_neg.append("Hambatan masuk tinggi (padat)")

    # ── UPGRADED VERDICT (6-tier) ──
    key_data_missing = (d is None or p is None or t is None)
    uncertainty_high = bool(contradictions and len(contradictions) >= 2)
    high_risk = r is not None and r >= 70
    strong_demand = d is not None and d >= 70
    low_competition = c is not None and c <= 30
    decent_profit = p is not None and p >= 55
    positive_trend = t is not None and t >= 55

    # Count positive and negative signals
    positive_count = sum([strong_demand, low_competition, decent_profit, positive_trend])
    negative_signals = sum([
        high_risk,
        uncertainty_high,
        key_data_missing,
        c is not None and c >= 70,
        d is not None and d < 40,
        t is not None and t < 40,
    ])

    if ov is not None and ov >= 80 and positive_count >= 3 and not high_risk:
        verdict = "SANGAT_LAYAK"
        verdict_label = "Sangat Layak Dijalankan"
    elif ov is not None and ov >= 65 and positive_count >= 2 and not high_risk:
        verdict = "LAYAK"
        verdict_label = "Layak Dijalankan"
    elif ov is not None and ov >= 50 and positive_count >= 1:
        verdict = "LAYAK_DENGAN_SYARAT"
        verdict_label = "Layak dengan Syarat"
    elif high_risk and ov is not None and ov < 50:
        verdict = "BERISIKO_TINGGI"
        verdict_label = "Berisiko Tinggi"
    elif key_data_missing or uncertainty_high:
        verdict = "PERLU_VALIDASI"
        verdict_label = "Perlu Validasi Lebih Lanjut"
    else:
        verdict = "TIDAK_DIREKOMENDASIKAN"
        verdict_label = "Tidak Direkomendasikan"

    # ── Confidence Score ──
    avail_count = sum(1 for v in availability.values() if v == "AVAILABLE")
    partial_count = sum(1 for v in availability.values() if v == "PARTIAL")
    unavailable_count = sum(1 for v in availability.values() if v == "UNAVAILABLE")

    conf_base = 40
    conf_score = conf_base + (avail_count * 12) + (partial_count * 6) - (unavailable_count * 4)
    if metrics.get("has_specific_location"): conf_score += 5
    if price_stats.total >= 10: conf_score += 5
    if price_stats.total >= 20: conf_score += 3
    if len(competitors) >= 10: conf_score += 5
    if len(competitors) >= 20: conf_score += 3
    if t is None: conf_score -= 8
    if d is None: conf_score -= 8
    if uncertainty_high: conf_score -= 5
    confidence = max(30, min(92, conf_score))

    # ── Insights ──
    insights = []
    if price_stats.total > 0:
        insights.append(f"Pasar didominasi harga {price_stats.median} (Median). Celah profit ada di rentang {price_stats.p25} - {price_stats.p75}.")
    if len(competitors) >= 3:
        top_comp = sorted(competitors, key=lambda x: x.reviews or 0, reverse=True)[0]
        insights.append(f"Kompetitor '{top_comp.name}' memiliki ulasan terbanyak, menandakan loyalitas pelanggan di titik tersebut kuat.")
    if t is not None and t < 45:
        insights.append("Tren pencarian menurun — fokus retensi pelanggan lebih realistis daripada akuisisi agresif.")

    # ── Reasons ──
    reasons_go = []
    if d is not None and d >= 60: reasons_go.append("Permintaan pasar cukup kuat")
    if p is not None and p >= 60: reasons_go.append("Potensi profit menarik")
    if c is not None and c <= 40: reasons_go.append("Persaingan digital masih terkendali")
    if t is not None and t >= 55: reasons_go.append("Tren pencarian positif")
    if not reasons_go: reasons_go.append("Data dasar tersedia untuk evaluasi")

    reasons_caution = []
    if c is not None and c >= 70: reasons_caution.append("Persaingan tinggi — butuh diferensiasi")
    if r is not None and r >= 70: reasons_caution.append("Risiko pasar tinggi")
    if d is not None and d < 40: reasons_caution.append("Permintaan masih lemah")
    if t is not None and t < 40: reasons_caution.append("Tren pencarian menurun")
    for k, v in availability.items():
        if v == "UNAVAILABLE":
            reasons_caution.append(f"Data {k} tidak tersedia")
    if not reasons_caution: reasons_caution.append("Validasi lapangan tetap diperlukan")

    reasons_why_feasible = []
    if d is not None and d >= 60:
        reasons_why_feasible.append("Permintaan pasar cukup kuat berdasarkan data tren")
    if p is not None and p >= 55:
        reasons_why_feasible.append("Potensi pricing cukup baik berdasarkan data Google Shopping")
    if c is not None and c <= 40:
        reasons_why_feasible.append("Persaingan digital relatif rendah")
    if len(competitors) > 0 and len(competitors) <= 5:
        reasons_why_feasible.append("Jumlah kompetitor utama masih terbatas")
    if price_stats.distribution:
        low_segs = [k for k, v in price_stats.distribution.items() if v < 15]
        if low_segs:
            reasons_why_feasible.append(f"Terdapat celah pasar di segmen: {', '.join(low_segs[:2])}")
    if t is not None and t >= 55:
        reasons_why_feasible.append("Tren pencarian positif mendukung prospek bisnis")
    if review_stats.avg_rating > 0 and review_stats.avg_rating < 4.0:
        reasons_why_feasible.append("Celah kualitas layanan terbuka lebar")
    if c is not None and c <= 30:
        reasons_why_feasible.append("Hambatan masuk pasar digital sangat rendah")
    if demand_breakdown and demand_breakdown.local_data_available:
        reasons_why_feasible.append(f"Data permintaan lokal ({demand_breakdown.local}) menunjukkan sinyal positif")
    if not reasons_why_feasible:
        reasons_why_feasible.append("Data dasar tersedia untuk evaluasi lebih lanjut")

    reasons_why_not_feasible = []
    if availability.get("trends") == "UNAVAILABLE":
        reasons_why_not_feasible.append("Data permintaan spesifik daerah belum cukup")
    if ta and not ta.has_any_data:
        reasons_why_not_feasible.append("Google Trends lokal tidak tersedia")
    elif ta and ta.fallback_used:
        reasons_why_not_feasible.append("Google Trends keyword spesifik tidak tersedia")
    if d is None:
        reasons_why_not_feasible.append("Permintaan aktual konsumen belum tervalidasi")
    if t is None:
        reasons_why_not_feasible.append("Tren pasar belum dapat dianalisis")
    if price_stats.total > 3 and price_stats.min_num and price_stats.min_num < 30000:
        reasons_why_not_feasible.append("Potensi perang harga di segmen ekonomis")
    if c is not None and c >= 60:
        reasons_why_not_feasible.append("Persaingan pasar cukup ketat")
    if r is not None and r >= 60:
        reasons_why_not_feasible.append("Risiko operasional pasar perlu diperhitungkan")
    if len(competitors) <= 2:
        reasons_why_not_feasible.append("Data kompetitor terbatas untuk analisis yang lebih akurat")
    if price_stats.total == 0:
        reasons_why_not_feasible.append("Data harga pasar belum tersedia")
    if review_stats.total_reviews == 0:
        reasons_why_not_feasible.append("Data review konsumen belum cukup")
    if metrics.get("has_specific_location") == False:
        reasons_why_not_feasible.append("Analisis belum menggunakan lokasi spesifik")
    reasons_why_not_feasible.append("Tingkat conversion rate belum diketahui")
    reasons_why_not_feasible.append("Data profit belum berdasarkan biaya produksi aktual")

    # ── 33-section decision fields ──
    decision_reasoning = [
        f"Skor keseluruhan: {ov}/100 — {verdict_label}",
        f"Demand: {d or 0}/100, Competition: {c or 0}/100, Risk: {r or 0}/100",
    ]
    if contradictions:
        decision_reasoning.append(f"Terdeteksi {len(contradictions)} kontradiksi data yang perlu diperhatikan.")

    # Strongest evidence
    strongest_evidence = []
    if d is not None and d >= 60:
        strongest_evidence.append(f"Demand terdeteksi dari Google Trends dengan skor {d}/100")
    if price_stats.total > 0:
        strongest_evidence.append(f"{price_stats.total} produk dianalisis dengan median harga {price_stats.median}")
    if len(competitors) > 0:
        strongest_evidence.append(f"{len(competitors)} kompetitor terdeteksi melalui Google Maps/Search")

    # Biggest risk
    biggest_risk = []
    if r is not None and r >= 60:
        biggest_risk.append(f"Risk score {r}/100 — faktor risiko signifikan")
    if c is not None and c >= 60:
        biggest_risk.append(f"Persaingan tinggi — butuh diferensiasi kuat")
    if price_stats.total > 0 and price_stats.min_num and price_stats.min_num < 30000:
        biggest_risk.append("Ancaman perang harga di segmen bawah")
    if not biggest_risk:
        biggest_risk.append("Validasi pasar diperlukan sebelum modal besar dikeluarkan")

    # Biggest unknown
    biggest_unknown = [
        "Willingness-to-pay pelanggan sebenarnya belum diketahui",
        "Data biaya produksi aktual (HPP) tidak tersedia",
        "Conversion rate dan repeat purchase belum tervalidasi",
    ]

    # Decision criteria
    decision_criteria = []
    if verdict in ("PERLU_VALIDASI", "LAYAK_DENGAN_SYARAT"):
        decision_criteria.append(DecisionChange(
            condition="Demand lokal tervalidasi dengan minat beli > 20%",
            current_decision=verdict_label,
            new_decision="Layak Dijalankan",
            rationale="Jika permintaan lokal terbukti, risiko utama berkurang.",
        ))
        decision_criteria.append(DecisionChange(
            condition="Gross margin terbukti > 35% setelah HPP aktual dihitung",
            current_decision=verdict_label,
            new_decision="Layak Dijalankan",
            rationale="Unit economics yang sehat memungkinkan skalabilitas.",
        ))

    return DecisionEngine(
        verdict=verdict,
        verdict_label=verdict_label,
        verdict_extended=verdict,
        confidence=confidence,
        reasons_go=reasons_go[:4],
        reasons_caution=reasons_caution[:4],
        reasons_why_feasible=reasons_why_feasible[:6],
        reasons_why_not_feasible=reasons_why_not_feasible[:8],
        opportunity_score=opp,
        opportunity_reasons_positive=opp_pos,
        opportunity_reasons_negative=opp_neg,
        saturation_score=sat,
        saturation_reasons=sat_reasons[:3],
        insights=insights[:4],
        demand_benchmark=bl(d),
        competition_benchmark=bl(c),
        profit_benchmark=bl(p),
        trend_benchmark=bl(t),
        risk_benchmark=bl(r),
        swot=_build_swot(scores, competitors, prices, price_stats, review_stats, demand_breakdown),
        market_gaps=[],
        action_plan=[],
        score_methodology=ScoreMethodology(),
        # 33-section fields
        decision_reasoning=decision_reasoning[:5],
        strongest_evidence=strongest_evidence[:3],
        biggest_risk=biggest_risk[:3],
        biggest_unknown=biggest_unknown[:3],
        recommended_next_step="Lakukan validasi willingness-to-pay dengan pre-order terbatas 30-50 unit" if verdict in ("PERLU_VALIDASI", "LAYAK_DENGAN_SYARAT", "BERISIKO_TINGGI") else "Mulai dengan produksi skala kecil dan uji pasar selama 30 hari",
        decision_criteria=decision_criteria,
        validation_checklist=validation_checklist or ValidationChecklist(),
    )


# ── Keep backward-compatible decision builder ──
def _build_decision(scores: BusinessScore, competitors: list[Competitor], trends: list[TrendItem],
    prices: list[PriceItem], price_stats: PriceStats, review_stats: ReviewStats,
    metrics: dict, business_type: str, availability: dict,
    trends_analysis: TrendsAnalysis | None = None) -> DecisionEngine:
    """Backward-compatible wrapper."""
    return _build_decision_upgraded(
        scores, competitors, trends, prices, price_stats, review_stats,
        metrics, business_type, availability,
        trends_analysis=trends_analysis,
    )


# ═══════════════════════════════════════════════
#  SCORE METHODOLOGY BUILDER
# ═══════════════════════════════════════════════

def _build_score_methodology(scores: BusinessScore, competitors: list, trends: list, prices: list, review_stats: ReviewStats, availability: dict) -> ScoreMethodology:
    n_competitors = len(competitors)
    n_prices = len(prices)
    all_trend_vals = sum(len(t.interest_values) for t in trends)

    demand_factors = []
    if scores.demand is not None:
        demand_factors.append(ScoreFactor(
            name="Search Interest (Google Trends)", contribution=40,
            weight=0.40, source="Google Trends", sample_size=all_trend_vals,
            data_period=f"{all_trend_vals} data points",
            confidence=min(90, all_trend_vals * 5),
        ))
        demand_factors.append(ScoreFactor(
            name="Commercial Intent", contribution=25,
            weight=0.25, source="Google Trends Related Queries",
            sample_size=all_trend_vals, data_period="Last 12 months",
            confidence=70,
        ))
        demand_factors.append(ScoreFactor(
            name="Local Demand", contribution=20,
            weight=0.20, source="Google Maps & Search",
            sample_size=n_competitors, data_period="Current",
            confidence=min(80, n_competitors * 8),
        ))
        demand_factors.append(ScoreFactor(
            name="Shopping Demand", contribution=15,
            weight=0.15, source="Google Shopping",
            sample_size=n_prices, data_period="Current",
            confidence=min(80, n_prices * 3),
        ))

    competition_factors = []
    if scores.competition is not None:
        competition_factors.append(ScoreFactor(
            name="Jumlah Kompetitor", contribution=50,
            weight=0.50, source="Google Maps",
            sample_size=n_competitors, data_period="Current",
            confidence=min(90, n_competitors * 5),
        ))
        competition_factors.append(ScoreFactor(
            name="Konsentrasi Review", contribution=30,
            weight=0.30, source="Google Maps Reviews",
            sample_size=review_stats.total_reviews if review_stats else 0,
            data_period="Current",
            confidence=min(80, (review_stats.total_reviews or 0) // 10),
        ))
        competition_factors.append(ScoreFactor(
            name="Rata-rata Rating", contribution=20,
            weight=0.20, source="Google Maps Ratings",
            sample_size=review_stats.competitor_count if review_stats else 0,
            data_period="Current",
            confidence=min(80, (review_stats.competitor_count or 0) * 10),
        ))

    profit_factors = []
    if scores.profit_potential is not None:
        profit_factors.append(ScoreFactor(
            name="Jumlah Produk Terdeteksi", contribution=40,
            weight=0.40, source="Google Shopping",
            sample_size=n_prices, data_period="Current",
            confidence=min(85, n_prices * 5),
        ))
        profit_factors.append(ScoreFactor(
            name="Distribusi Harga", contribution=35,
            weight=0.35, source="Google Shopping",
            sample_size=n_prices, data_period="Current",
            confidence=70,
        ))
        profit_factors.append(ScoreFactor(
            name="Ketersediaan Varian", contribution=25,
            weight=0.25, source="Google Shopping",
            sample_size=n_prices, data_period="Current",
            confidence=65,
        ))

    trend_factors = []
    if scores.trend is not None:
        trend_factors.append(ScoreFactor(
            name="Arah Tren Pencarian", contribution=45,
            weight=0.45, source="Google Trends",
            sample_size=all_trend_vals, data_period=f"{all_trend_vals} periode",
            confidence=min(85, all_trend_vals * 5),
        ))
        trend_factors.append(ScoreFactor(
            name="Growth Rate", contribution=30,
            weight=0.30, source="Google Trends",
            sample_size=all_trend_vals, data_period="First half vs second half",
            confidence=70,
        ))
        trend_factors.append(ScoreFactor(
            name="Konsistensi Data", contribution=25,
            weight=0.25, source="Google Trends",
            sample_size=all_trend_vals, data_period="All time",
            confidence=min(80, all_trend_vals * 3),
        ))

    risk_factors = []
    if scores.risk is not None:
        risk_factors.append(ScoreFactor(
            name="Tingkat Persaingan", contribution=40,
            weight=0.40, source="Google Maps",
            sample_size=n_competitors, data_period="Current",
            confidence=min(85, n_competitors * 5),
        ))
        risk_factors.append(ScoreFactor(
            name="Volatilitas Tren", contribution=35,
            weight=0.35, source="Google Trends",
            sample_size=all_trend_vals, data_period=f"{all_trend_vals} periode",
            confidence=min(75, all_trend_vals * 3),
        ))
        risk_factors.append(ScoreFactor(
            name="Kesenjangan Data", contribution=25,
            weight=0.25, source="All Sources",
            sample_size=4, data_period="Current",
            confidence=sum(1 for v in availability.values() if v != "UNAVAILABLE") * 20,
        ))

    overall_factors = [
        ScoreFactor(name="Demand", contribution=scores.demand or 0,
                     weight=0.30, source="Google Trends", sample_size=all_trend_vals,
                     data_period="Last 12 months", confidence=min(85, all_trend_vals * 3)),
        ScoreFactor(name="Competition (inverted)", contribution=100 - (scores.competition or 0),
                     weight=0.20, source="Google Maps", sample_size=n_competitors,
                     data_period="Current", confidence=min(85, n_competitors * 5)),
        ScoreFactor(name="Profit Potential", contribution=scores.profit_potential or 0,
                     weight=0.15, source="Google Shopping", sample_size=n_prices,
                     data_period="Current", confidence=min(80, n_prices * 3)),
        ScoreFactor(name="Trend", contribution=scores.trend or 0,
                     weight=0.20, source="Google Trends", sample_size=all_trend_vals,
                     data_period="All time", confidence=min(80, all_trend_vals * 3)),
        ScoreFactor(name="Risk (inverted)", contribution=100 - (scores.risk or 0),
                     weight=0.15, source="Composite", sample_size=4,
                     data_period="Current", confidence=70),
    ]

    def calc_confidence(factors: list[ScoreFactor]) -> float:
        if not factors:
            return 0
        return round(sum(f.confidence * f.weight for f in factors) / sum(f.weight for f in factors), 1)

    return ScoreMethodology(
        demand=ScoreDetail(
            value=scores.demand or 0,
            label=get_score_label(scores.demand),
            factors=demand_factors,
            methodology="Demand dihitung dari rata-rata Google Trends interest, dikalibrasi ke skala 0-100, dengan penyesuaian dari volume shopping dan data lokal.",
            confidence=calc_confidence(demand_factors),
            data_sources=["Google Trends", "Google Shopping", "Google Maps"],
        ),
        competition=ScoreDetail(
            value=scores.competition or 0,
            label=get_score_label(scores.competition),
            factors=competition_factors,
            methodology="Competition dihitung dari jumlah kompetitor terdeteksi, konsentrasi review, dan rata-rata rating.",
            confidence=calc_confidence(competition_factors),
            data_sources=["Google Maps"],
        ),
        profit_potential=ScoreDetail(
            value=scores.profit_potential or 0,
            label=get_score_label(scores.profit_potential),
            factors=profit_factors,
            methodology="Profit Potential dihitung dari jumlah produk terdeteksi, distribusi harga, dan variasi produk.",
            confidence=calc_confidence(profit_factors),
            data_sources=["Google Shopping"],
        ),
        trend=ScoreDetail(
            value=scores.trend or 0,
            label=get_score_label(scores.trend),
            factors=trend_factors,
            methodology="Trend dihitung dari perbandingan interest paruh pertama vs paruh kedua data Google Trends.",
            confidence=calc_confidence(trend_factors),
            data_sources=["Google Trends"],
        ),
        risk=ScoreDetail(
            value=scores.risk or 0,
            label=get_score_label(scores.risk),
            factors=risk_factors,
            methodology="Risk dihitung dari kombinasi competition score, volatilitas tren, dan ketersediaan data.",
            confidence=calc_confidence(risk_factors),
            data_sources=["Google Maps", "Google Trends", "All Sources"],
        ),
        overall=ScoreDetail(
            value=scores.overall,
            label=get_score_label(scores.overall),
            factors=overall_factors,
            methodology="Overall = Demand(30%) + inverted Competition(20%) + Profit(15%) + Trend(20%) + inverted Risk(15%).",
            confidence=calc_confidence(overall_factors),
            data_sources=["Google Trends", "Google Maps", "Google Shopping"],
        ),
    )


# ═══════════════════════════════════════════════
#  CROSS ANALYSIS
# ═══════════════════════════════════════════════

def _perform_cross_analysis(scores: BusinessScore, competitors: list[Competitor], trends: list[TrendItem], prices: list[PriceItem], price_stats: PriceStats, review_stats: ReviewStats, availability: dict) -> list[str]:
    findings = []

    if availability["competitors"] != "UNAVAILABLE" and len(competitors) > 0:
        reviews_list = [c.reviews or 0 for c in competitors]
        if len(reviews_list) >= 2:
            max_rev = max(reviews_list)
            others_avg = (sum(reviews_list) - max_rev) / (len(reviews_list) - 1) if len(reviews_list) > 1 else 0
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

    if availability["prices"] != "UNAVAILABLE" and price_stats.total > 0 and price_stats.distribution:
        sorted_dist = sorted(price_stats.distribution.items(), key=lambda x: x[1], reverse=True)
        dominant_seg = sorted_dist[0]
        if dominant_seg[1] >= 50:
            findings.append(
                f"Pasar didominasi produk di rentang harga {dominant_seg[0]} ({dominant_seg[1]}%). "
                "Memasuki segmen ini butuh efisiensi biaya tinggi atau diferensiasi kuat."
            )
        missing = [s for s in ["0-50rb", "50-100rb", "100-300rb", "300rb+", "0-25rb", "25-50rb", "0-10rb", "10-25rb", "25-50rb", "50-100rb"] if s not in price_stats.distribution or price_stats.distribution.get(s, 0) < 10]
        if missing:
            findings.append(
                f"Sedikit/tidak ada produk di segmen {', '.join(missing[:2])}. "
                "Ini bisa jadi peluang, namun perlu validasi tambahan."
            )

    if scores.trend is not None and scores.demand is not None:
        if scores.trend >= 50 and scores.demand >= 50:
            findings.append("Permintaan pasar kuat didukung tren pencarian yang stabil/meningkat.")
        elif scores.trend < 40 and scores.demand >= 50:
            findings.append("Demand saat ini baik, namun tren pencarian mulai menurun — waspadai potensi kejenuhan pasar.")

    if len(competitors) >= 3 and review_stats.avg_rating > 0 and review_stats.avg_rating < 4.1:
        findings.append(
            f"Rating rata-rata kompetitor rendah ({review_stats.avg_rating:.1f}/5.0). "
            "Kualitas layanan yang lebih baik adalah peluang besar untuk merebut pasar."
        )

    if availability["prices"] != "UNAVAILABLE" and price_stats.total > 5:
        cheap_products = sum(1 for p in prices if p.price_num > 0 and p.price_num < 50000)
        if cheap_products >= 5 and len(competitors) > 8:
            findings.append("Risiko perang harga tinggi di segmen budget (produk < Rp50rb) dengan kompetisi padat.")

    if not findings:
        findings.append("Belum cukup anomali data untuk menarik kesimpulan hubungan antar sumber.")

    return findings


# ═══════════════════════════════════════════════
#  REPORT VALIDATION (UPGRADED)
# ═══════════════════════════════════════════════

def _validate_report_json_upgraded(ai_report: dict, scores: BusinessScore, raw_data: dict, competitors: list[Competitor], prices: list[PriceItem], trends: list[TrendItem], news: list[NewsItem], cross_findings: list[str], data_availability: dict) -> list[str]:
    errors = []

    required_fields = [
        "executive_summary", "market_trend_description", "competitor_insights",
        "price_insights", "news_summary", "opportunity_analysis", "risk_analysis",
        "recommendation", "ai_understanding", "market_opportunity", "demand_analysis",
        "competition_analysis", "market_statistics_insight", "data_coverage_note",
        "market_gap_analysis", "business_recommendation",
    ]
    for field in required_fields:
        if not ai_report.get(field):
            errors.append(f"Field '{field}' kosong atau tidak ditemukan.")

    for key, status in data_availability.items():
        if status == "UNAVAILABLE":
            pass  # Allow empty fields for unavailable data

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

# Also keep the old name for backward compat
_validate_report_json = _validate_report_json_upgraded
