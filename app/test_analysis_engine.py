import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.routers.research import (
    get_score_label,
    _validate_data_quality,
    _calculate_scores,
    _perform_cross_analysis,
    _validate_report_json,
    _build_decision,
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

    scores = _calculate_scores(competitors, trends, prices, avail)
    decision = _build_decision(
        scores, competitors, trends, prices, PriceStats(), ReviewStats(), metrics, "toko roti", avail
    )

    assert 40 <= decision.confidence <= 85
    assert decision.swot.strength
    assert decision.swot.weakness
    assert decision.swot.opportunity
    assert decision.swot.threat
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
        "executive_summary": "Pasar roti di Bandung memiliki prospek baik dengan 1 kompetitor utama terdeteksi.",
        "market_trend_description": "Tren Google Trends menunjukkan minat pencarian stabil.",
        "competitor_insights": "Toko Roti Bandung terdeteksi sebagai kompetitor utama.",
        "price_insights": "Harga pasar bervariasi dengan kisaran Rp50.000.",
        "news_summary": "Terdapat berita mengenai pertumbuhan UMKM kuliner.",
        "opportunity_analysis": "Peluang di segmen menengah dengan margin memadai.",
        "risk_analysis": "Risiko utama: Rendah — hambatan masuk minimal.",
        "recommendation": "- **Tindakan**: Buka outlet fisik.\n- **Alasan**: Persaingan terkendali.\n- **Data Pendukung**: 1 kompetitor utama.\n- **Dampak**: Penjualan meningkat.",
    }
    errors = _validate_report_json(valid_report, scores, {}, competitors, prices, trends, news, cross_findings, avail)
    assert len(errors) == 0, f"Expected 0 errors, got: {errors}"

    invalid_generic = valid_report.copy()
    invalid_generic["executive_summary"] = "Kami akan menawarkan produk kompetitif dengan harga yang bersaing."
    errors_gen = _validate_report_json(
        invalid_generic, scores, {}, competitors, prices, trends, news, cross_findings, avail
    )
    assert any("generik" in err for err in errors_gen)
    print("✓ Report validation tests passed!")


def test_competition_consistency():
    print("Testing competition score consistency...")
    avail = {"competitors": "AVAILABLE", "prices": "AVAILABLE", "trends": "AVAILABLE", "news": "PARTIAL"}
    few = [Competitor(name=f"T{i}") for i in range(3)]
    many = [Competitor(name=f"T{i}") for i in range(15)]
    scores_few = _calculate_scores(few, [TrendItem(interest_values=[50, 50])], [PriceItem(price_num=100000)], avail)
    scores_many = _calculate_scores(many, [TrendItem(interest_values=[50, 50])], [PriceItem(price_num=100000)], avail)
    assert scores_few.competition is not None and scores_few.competition < 40
    assert scores_many.competition is not None and scores_many.competition >= 70
    assert get_score_label(scores_few.competition) in ("Rendah", "Sangat Rendah")
    assert get_score_label(scores_many.competition) in ("Tinggi", "Sangat Tinggi")
    print("✓ Competition consistency tests passed!")


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
