import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.routers.research import (
    get_score_label,
    _validate_data_quality,
    _perform_cross_analysis,
    _validate_report_json,
    _build_decision,
    _calculate_scores_detailed,
    _build_score_methodology,
    _parse_review_stats,
)
from app.schemas.research import Competitor, PriceItem, TrendItem, NewsItem, PriceStats, ReviewStats, BusinessScore


def test_score_labeling():
    print("Testing score labeling...")
    assert get_score_label(85) == "Sangat Tinggi"
    assert get_score_label(75) == "Tinggi"
    assert get_score_label(55) == "Sedang"
    assert get_score_label(35) == "Rendah"
    assert get_score_label(20) == "Sangat Rendah"
    assert get_score_label(None) == "Data Tidak Tersedia"
    print("✓ Score labeling tests passed!")


def test_data_validation_and_confidence():
    print("Testing data quality validation and confidence scoring...")
    competitors = [Competitor(name="Toko A", rating=4.5, reviews=10)]
    prices = [PriceItem(price_num=10000) for _ in range(5)]
    trends = [TrendItem(interest_values=[50, 60, 70])]
    news = [NewsItem(title="News 1")]
    avail = {"competitors": "PARTIAL", "prices": "PARTIAL", "trends": "AVAILABLE", "news": "PARTIAL"}

    metrics = _validate_data_quality(competitors, prices, trends, news, "Bandung", avail)
    assert metrics["competitors_count"] == 1
    assert metrics["prices_count"] == 5
    assert metrics["trends_count"] == 3
    assert metrics["news_count"] == 1
    assert metrics["has_specific_location"] is True

    review_stats = _parse_review_stats(competitors)
    scores = _calculate_scores_detailed(competitors, trends, prices, avail, review_stats)
    decision = _build_decision(
        scores, competitors, trends, prices, PriceStats(), review_stats, metrics, "toko roti", avail
    )

    assert 30 <= decision.confidence <= 92
    assert decision.swot.strength
    assert decision.swot.weakness
    assert decision.swot.opportunity
    assert decision.swot.threat

    # Test score methodology
    sm = _build_score_methodology(scores, competitors, trends, prices, review_stats, avail)
    assert sm.demand.value is not None
    assert sm.competition.factors is not None
    assert sm.overall.confidence > 0
    print(f"✓ Data validation & confidence tests passed! Confidence: {decision.confidence}")


def test_cross_analysis():
    print("Testing programmatic cross-analysis...")
    scores = BusinessScore(demand=80, competition=25, profit_potential=60, trend=70, risk=40, overall=60)
    avail = {"competitors": "AVAILABLE", "prices": "AVAILABLE", "trends": "AVAILABLE", "news": "PARTIAL"}

    competitors = [
        Competitor(name="Big Player", rating=4.8, reviews=500),
        Competitor(name="Small", rating=4.0, reviews=20),
    ]
    findings = _perform_cross_analysis(scores, competitors, [], [], PriceStats(), ReviewStats(total_reviews=520), avail)
    assert any("dominan" in f.lower() or "review" in f.lower() for f in findings)

    prices_war = [PriceItem(price_num=20000) for _ in range(6)]
    competitors_war = [Competitor() for _ in range(12)]
    findings_war = _perform_cross_analysis(
        scores, competitors_war, [], prices_war, PriceStats(total=6), ReviewStats(), avail
    )
    assert any("perang harga" in f.lower() or "budget" in f.lower() or "anomali" in f.lower() for f in findings_war)
    print("✓ Cross-analysis tests passed!")


def test_report_validation():
    print("Testing report validation loop...")
    scores = BusinessScore(demand=80, competition=25, profit_potential=60, trend=70, risk=30, overall=75)
    competitors = [Competitor(name="Toko Roti Bandung")]
    prices = [PriceItem(price_num=50000)]
    trends = [TrendItem(interest_values=[10])]
    news = [NewsItem()]
    cross_findings = ["Test finding"]
    avail = {"competitors": "AVAILABLE", "prices": "AVAILABLE", "trends": "AVAILABLE", "news": "PARTIAL"}

    valid_report = {
        "executive_summary": "Pasar roti di Bandung memiliki prospek baik.",
        "ai_understanding": "User ingin membuka toko roti di Bandung.",
        "market_opportunity": "Peluang pasar cukup besar dengan permintaan stabil.",
        "demand_analysis": "Permintaan menunjukkan tren positif.",
        "competition_analysis": "Persaingan masih terkendali dengan 1 kompetitor.",
        "market_trend_description": "Tren Google Trends menunjukkan minat pencarian stabil.",
        "competitor_insights": "Toko Roti Bandung terdeteksi sebagai kompetitor utama.",
        "price_insights": "Harga pasar bervariasi dengan kisaran Rp50.000.",
        "product_price_analysis": "Produk roti memiliki rentang harga yang sehat.",
        "market_statistics_insight": "Data pasar menunjukkan 1 kompetitor terdeteksi.",
        "data_coverage_note": "Data tersedia dari 3 sumber.",
        "market_gap_analysis": "Terdapat celah di segmen harga menengah.",
        "news_summary": "Terdapat berita mengenai pertumbuhan UMKM.",
        "opportunity_analysis": "Peluang di segmen menengah.",
        "risk_analysis": "Risiko utama: Rendah.",
        "business_recommendation": "Fokus pada kualitas produk dan layanan.",
        "recommendation": "- **Tindakan**: Buka outlet fisik.\n- **Alasan**: Persaingan terkendali.",
    }
    errors = _validate_report_json(valid_report, scores, {}, competitors, prices, trends, news, cross_findings, avail)
    assert len(errors) == 0, f"Expected 0 errors, got: {errors}"

    print("✓ Report validation tests passed!")


def test_competition_consistency():
    print("Testing competition score consistency...")
    avail = {"competitors": "AVAILABLE", "prices": "AVAILABLE", "trends": "AVAILABLE", "news": "PARTIAL"}
    few = [Competitor(name=f"T{i}") for i in range(3)]
    many = [Competitor(name=f"T{i}") for i in range(15)]
    rs_few = _parse_review_stats(few)
    rs_many = _parse_review_stats(many)
    scores_few = _calculate_scores_detailed(few, [TrendItem(interest_values=[50, 50])], [PriceItem(price_num=100000)], avail, rs_few)
    scores_many = _calculate_scores_detailed(many, [TrendItem(interest_values=[50, 50])], [PriceItem(price_num=100000)], avail, rs_many)
    assert scores_few.competition is not None and scores_few.competition < 40
    assert scores_many.competition is not None and scores_many.competition >= 50
    print(f"✓ Competition consistency tests passed! few={scores_few.competition} many={scores_many.competition}")


if __name__ == "__main__":
    try:
        test_score_labeling()
        test_data_validation_and_confidence()
        test_cross_analysis()
        test_report_validation()
        test_competition_consistency()
        print("\n=== ALL TESTS PASSED SUCCESSFULLY! ===")
    except AssertionError as e:
        print(f"\n✖ Test failed: {e}", file=sys.stderr)
        sys.exit(1)
