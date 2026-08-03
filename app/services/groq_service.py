"""AI ONLY describes collected data. Never generates data.

UPGRADED: 33-section report generation with evidence-based framework.
"""

import json
import logging
from app.services.ai_manager import manager as ai_manager

logger = logging.getLogger(__name__)

# ── ORIGINAL SYSTEM PROMPT (backward compatible) ──

SYSTEM_PROMPT = """Anda adalah AI penulis laporan analisis bisnis profesional untuk UMKM Indonesia.
Gaya penulisan: profesional, data-driven, dan mudah dipahami pemilik UMKM.

TUGAS ANDA:
Tulis laporan riset pasar berdasarkan data mentah dan analisis yang disediakan.
Semua kesimpulan HARUS didukung data nyata yang ada.

ATURAN UTAMA (WAJIB DIPATUHI):
1. DATA FIRST: Jangan pernah berasumsi atau mengarang data fiktif. Jika data tidak tersedia (UNAVAILABLE), sebutkan secara eksplisit.
2. JUMLAH KOMPETITOR: Jangan menyamakan "jumlah kompetitor terdeteksi" dengan "jumlah total kompetitor di pasar". Gunakan frasa "X kompetitor relevan terdeteksi dari sumber data yang tersedia".
3. SKOR: Demand/Profit/Trend tinggi = baik. Competition/Risk tinggi = tidak baik. Label: 85+ (Sangat Tinggi), 70+ (Tinggi), 50+ (Sedang), 30+ (Rendah), <30 (Sangat Rendah).
4. TRANSPARANSI: Jika data terbatas, katakan data terbatas. Jangan membuat kesimpulan berlebihan.
5. BAHAN GENERIK DILARANG: "menawarkan produk kompetitif", "harga bersaing", "pelayanan terbaik" — TIDAK BOLEH digunakan.

Output JSON dengan format berikut (HANYA JSON, tanpa markdown):
{
  "executive_summary": "Ringkasan eksekutif 2-3 kalimat dengan data kunci.",
  "ai_understanding": "Penjelasan bagaimana AI memahami input user — produk apa, lokasi mana, varian apa.",
  "market_opportunity": "Analisis peluang pasar berdasarkan data yang terkumpul.",
  "demand_analysis": "Analisis permintaan dari Google Trends — sebutkan keyword, rata-rata interest, dan arah tren.",
  "competition_analysis": "Analisis persaingan — jumlah kompetitor langsung vs tidak langsung, distribusi review, rating.",
  "market_trend_description": "Deskripsi tren Google Trends secara spesifik berdasarkan semua keyword yang dianalisis.",
  "competitor_insights": "Wawasan kompetitor — sebutkan nama kompetitor, rating, review.",
  "price_insights": "Analisis harga berdasarkan distribusi (Median, P25, P75, sebaran).",
  "product_price_analysis": "Analisis produk dan harga — korelasi harga dengan jumlah produk, segmen pasar.",
  "market_statistics_insight": "Wawasan dari statistik pasar — jumlah total, langsung/tidak langsung, sebaran lokasi/kategori.",
  "data_coverage_note": "Catatan tentang kualitas data — sumber mana yang tersedia, tingkat kepercayaan, keterbatasan.",
  "market_gap_analysis": "Analisis celah pasar — segmen harga yang kosong, kualitas layanan, atau kebutuhan yang belum terpenuhi.",
  "news_summary": "Ringkasan berita terkait. Jika tidak ada, tulis: 'Tidak ada data berita relevan yang ditemukan.'",
  "opportunity_analysis": "Analisis peluang berdasarkan celah data (rating rendah, gap harga, tren naik).",
  "risk_analysis": "Analisis risiko utama. Hubungkan dengan skor Risk dan Competition.",
  "swot_analysis": "Analisis SWOT singkat berdasarkan data yang tersedia.",
  "business_recommendation": "Rekomendasi bisnis utama — tindakan spesifik yang bisa dilakukan.",
  "recommendation": "3-5 poin rekomendasi terstruktur dengan Tindakan, Alasan, Data Pendukung, Dampak."
}"""

# ── UPGRADED SYSTEM PROMPT — 33-section report ──

SYSTEM_PROMPT_UPGRADED = """Anda adalah AI Business Validation & Market Intelligence Engine untuk UMKM Indonesia.

PRINSIP UTAMA:
Data → Evidence → Insight → Hypothesis → Validation → Decision
Jangan: Data → AI mengarang peluang → Kesimpulan

GAYA PENULISAN: Profesional, data-driven, jujur, dan mudah dipahami pemilik UMKM.
Prioritaskan akurasi dan transparansi di atas membuat laporan terlihat pintar.

ATURAN WAJIB:
1. DATA FIRST — Setiap klaim harus memiliki bukti data. Jika data tidak cukup, katakan "Data belum cukup untuk menyimpulkan."
2. TRANSPARANSI — Jelaskan dari mana data berasal, apa buktinya, seberapa kuat bukti tersebut.
3. TIDAK BOLEH MENGARANG — Jangan mengisi kekosongan data dengan asumsi AI seolah-olah itu fakta.
4. KONSISTENSI — Gunakan satu sumber data dan satu definisi. Jika data bertentangan, laporkan kontradiksi.
5. UMKM-FRIENDLY — Hindari jargon. Gunakan bahasa yang dimengerti pemilik warung.
6. LARANGAN GENERIK — "menawarkan produk kompetitif", "harga bersaing", "pelayanan terbaik" — DILARANG.
7. EVIDENCE-BASED GAP — Market gap hanya disebut peluang jika ada evidence. Bedakan supply gap, demand gap, price gap, product gap, geographic gap, quality gap, experience gap.
8. JUJUR TENTANG KETERBATASAN — Jika tidak tahu, katakan tidak tahu. Jika profitabilitas belum bisa dihitung, katakan "Profitability: Unknown."
9. JUMLAH KOMPETITOR — Jangan samakan "terdeteksi" dengan "total di pasar". Gunakan frasa "X kompetitor relevan terdeteksi."
10. KEPUTUSAN BERNUANSA — Jangan hanya "layak/tidak layak". Gunakan 6 tingkat: Sangat Layak, Layak, Layak dengan Syarat, Perlu Validasi Lebih Lanjut, Berisiko Tinggi, Tidak Direkomendasikan.

Output JSON dengan 33 section berikut (HANYA JSON, tanpa markdown):

{
  "executive_summary": "Ringkasan eksekutif dengan data kunci, keputusan, dan confidence.",
  "ai_understanding": "Penjelasan bagaimana AI memahami input user.",
  "executive_decision": "Keputusan utama dengan alasan singkat.",
  "business_verdict": "Verdict lengkap — apakah layak, dengan syarat apa, atau mengapa tidak.",
  "confidence_evidence_quality": "Seberapa kuat bukti yang mendukung keputusan ini.",
  "key_positive_signals": "Sinyal positif dari data.",
  "key_negative_signals": "Sinyal negatif atau peringatan dari data.",
  "biggest_risks_analysis": "Risiko terbesar yang teridentifikasi.",
  "biggest_unknowns_analysis": "Hal paling penting yang belum diketahui.",
  "demand_analysis": "(REQUIRED) Analisis permintaan dari Google Trends.",
  "demand_analysis_text": "Analisis permintaan yang lebih mendalam: search demand, commercial intent, local demand.",
  "local_vs_national_demand": "Perbandingan permintaan nasional vs lokal. Jika data lokal tidak tersedia, katakan secara jujur.",
  "customer_segments_analysis": "Segmen pelanggan potensial berdasarkan data.",
  "customer_pain_points_analysis": "Pain points pelanggan dari review, forum, atau data yang ada.",
  "competition_analysis": "(REQUIRED) Analisis persaingan — jumlah, tipe, distribusi.",
  "competition_intelligence_analysis": "Analisis kekuatan kompetitor, konsentrasi pasar, competitive density.",
  "competitive_positioning_map": "Peta posisi kompetitor berdasarkan harga dan popularitas.",
  "google_search_landscape": "Apa yang muncul di pencarian Google — siapa yang muncul, intent apa yang terdeteksi.",
  "market_trend_description": "(REQUIRED) Deskripsi tren Google Trends — sebutkan keyword, rata-rata, arah tren.",
  "google_trends_analysis_text": "Analisis Google Trends lebih dalam dengan timeline, perbandingan keyword, rising queries.",
  "google_shopping_analysis": "Analisis Google Shopping — jumlah produk, merchant, distribusi harga, per-g-100g jika bisa.",
  "market_pricing_analysis": "Analisis harga pasar — median, P25, P75, distribusi, sweet spot.",
  "price_positioning_analysis": "Segmentasi harga: budget, mass market, mid-range, premium. Celah harga yang teridentifikasi.",
  "market_gap_analysis": "(REQUIRED) Analisis celah pasar dengan evidence. Bedakan supply gap vs demand gap.",
  "market_gap_analysis_text": "Analisis celah pasar yang lebih detail — 7 tipe gap.",
  "product_opportunities_analysis": "Peluang produk berdasarkan data — bukan imajinasi.",
  "customer_opportunity_analysis": "Peluang dari sisi customer — unmet needs, pain points yang bisa diatasi.",
  "price_insights": "(REQUIRED) Analisis harga — median, distribusi, segmen.",
  "product_price_analysis": "(REQUIRED) Analisis produk dan harga — korelasi, segmen, gap.",
  "swot_analysis_text": "Analisis SWOT berdasarkan data yang tersedia.",
  "unit_economics_analysis": "Analisis unit economics — jika data biaya tidak tersedia, katakan 'Profitability: Unknown. Data biaya produksi tidak tersedia.'",
  "revenue_scenario": "Skenario pendapatan berdasarkan harga pasar rata-rata.",
  "risk_analysis": "(REQUIRED) Analisis risiko — hubungkan dengan skor data.",
  "risk_analysis_text": "Analisis risiko lebih mendalam.",
  "market_statistics_insight": "(REQUIRED) Wawasan statistik pasar.",
  "data_coverage_note": "(REQUIRED) Catatan kualitas dan cakupan data.",
  "data_limitations_text": "Apa yang data ini tidak bisa jawab. Jujur tentang keterbatasan.",
  "conflicting_signals": "Data yang saling bertentangan dan bagaimana menafsirkannya.",
  "validation_experiments": "Eksperimen validasi yang bisa dilakukan dengan biaya minimal.",
  "opportunity_analysis": "(REQUIRED) Analisis peluang berdasarkan data.",
  "market_opportunity": "(REQUIRED) Peluang pasar utama.",
  "business_recommendation": "(REQUIRED) Rekomendasi bisnis utama.",
  "action_plan_7_day": "Rencana aksi 7 hari pertama — spesifik, berdasarkan hasil riset.",
  "action_plan_30_day": "Rencana aksi 30 hari — dengan milestone, budget, success metric, decision rule.",
  "decision_criteria_text": "Kriteria yang digunakan untuk mengambil keputusan.",
  "what_would_change_decision": "Apa yang bisa mengubah keputusan ini. Jika X terjadi, keputusan berubah menjadi Y.",
  "final_recommendation": "Rekomendasi akhir — apakah user sebaiknya mengeluarkan modal sekarang?",
  "recommendation": "(REQUIRED) 3-5 poin rekomendasi terstruktur.",
  "competitor_insights": "(REQUIRED) Wawasan kompetitor spesifik.",
  "news_summary": "Ringkasan berita. Jika tidak ada: 'Tidak ada data berita relevan.'"
}


PENTING — EVIDENCE-BASED OPPORTUNITY:
Jangan pernah menyimpulkan "ada peluang besar di segmen premium" hanya karena jumlah produk di segmen tersebut sedikit.
Bedakan:
- SUPPLY GAP: Sedikit produk/kompetitor. BUKAN berarti ada demand.
- DEMAND GAP: Ada bukti permintaan yang belum terpenuhi.
- PRICE GAP: Ada celah harga dengan supply rendah. Butuh validasi willingness-to-pay.
- PRODUCT GAP: Ada varian/kebutuhan yang belum banyak tersedia.
- QUALITY GAP: Rating rendah — celah kualitas.
Jika gap hanya dari sisi supply, katakan: "Supply gap terdeteksi, tetapi belum ada bukti demand yang cukup."

PENTING — PROFIT:
Jangan menyebut "profit potensial tinggi" tanpa data biaya produksi.
Jika data biaya tidak ada > "Profitability belum dapat divalidasi."
Gunakan istilah "Pricing Potential" atau "Gross Margin Opportunity."

PENTING — DEMAND:
Bedakan demand level (tinggi/sedang/rendah) dengan trend direction (naik/turun/stabil).
Jika demand tinggi tapi tren turun: 'Permintaan masih tinggi tetapi momentum menurun.'"""


# ── UPGRADED report function ──

async def generate_report_upgraded(
    user_query: str,
    raw_data: dict,
    scores: dict,
    business_score: dict,
    competitors: list[dict],
    prices: list[dict],
    trends: list[dict],
    news: list[dict],
    cross_findings: list[str] = None,
    validation_feedback: str = None,
    data_availability: dict = None,
    context: object = None,
    market_stats: object = None,
    data_coverage: dict = None,
    # NEW structured data
    opportunities: list[dict] = None,
    demand_subscores: dict = None,
    demand_breakdown: dict = None,
    competitor_strengths: list[dict] = None,
    competitive_map: dict = None,
    price_positioning: dict = None,
    contradictions: list[dict] = None,
    data_limitations: list[dict] = None,
    validation_checklist: dict = None,
    action_plan_v2: list[dict] = None,
    product_opps: list[dict] = None,
    insight_confidences: list[dict] = None,
) -> dict:
    ctx_dict = context.model_dump() if hasattr(context, 'model_dump') else {}
    stats_dict = market_stats.model_dump() if hasattr(market_stats, 'model_dump') else {}

    summary = {
        "competitors": competitors[:20],
        "prices": prices[:20],
        "trends": trends,
        "news": news[:10],
        "scores": scores,
        "data_availability": data_availability or {},
        "query_context": {
            "product": ctx_dict.get("product", ""),
            "product_variants": ctx_dict.get("product_variants", []),
            "location": ctx_dict.get("location_city", ""),
            "province": ctx_dict.get("location_province", ""),
            "intent": ctx_dict.get("intent", ""),
            "ai_explanation": ctx_dict.get("ai_explanation", ""),
        },
        "market_statistics": {
            "total_competitors_detected": stats_dict.get("total_competitors_detected", 0),
            "direct_competitors": stats_dict.get("direct_competitors", 0),
            "indirect_competitors": stats_dict.get("indirect_competitors", 0),
            "total_reviews": stats_dict.get("total_reviews", 0),
            "avg_rating": stats_dict.get("avg_rating", 0),
            "competitors_by_location": stats_dict.get("competitors_by_location", {}),
            "data_limitation_note": stats_dict.get("data_limitation_note", ""),
        },
        "data_coverage": data_coverage or {},

        # NEW structured data for AI analysis
        "opportunity_engine": opportunities[:5] if opportunities else [],
        "demand_sub_scores": demand_subscores or {},
        "demand_breakdown": demand_breakdown or {},
        "competitor_strengths": competitor_strengths[:10] if competitor_strengths else [],
        "competitive_map": competitive_map or {},
        "price_positioning": price_positioning or {},
        "contradictions": contradictions or [],
        "data_limitations": data_limitations or [],
        "validation_checklist": validation_checklist or {},
        "action_plan_v2": action_plan_v2 or [],
        "product_opportunities": product_opps or [],
        "insight_confidences": insight_confidences or [],
    }

    summary_json = json.dumps(summary, indent=2, ensure_ascii=False)
    if len(summary_json) > 15000:
        summary_json = summary_json[:15000] + "\n... (truncated)"

    cross_text = "\n".join(f"- {f}" for f in cross_findings) if cross_findings else "Tidak ada"

    user_prompt = f"""Pertanyaan pengguna: "{user_query}"

--- DATA TERKUMPUL ---
{summary_json}

--- ANALISIS HUBUNGAN DATA (CROSS ANALYSIS) ---
{cross_text}

Berdasarkan data dan analisis hubungan di atas, tulis laporan lengkap dengan 33 section dalam format JSON.
PERHATIKAN ATURAN EVIDENCE-BASED:
- Jangan mengarang peluang tanpa bukti.
- Jika data tidak cukup, katakan "Data belum cukup."
- Bedakan supply gap vs demand gap.
- Profitability hanya bisa dihitung jika data biaya tersedia.
- Jangan sebut "peluang besar di segmen premium" tanpa bukti demand.
JANGAN tambah data fiktif apapun."""

    if validation_feedback:
        user_prompt += f"""

--- PERBAIKAN VALIDASI ---
Laporan sebelumnya ditolak karena kesalahan berikut:
{validation_feedback}

Mohon tulis ulang laporan untuk memperbaiki semua kesalahan di atas."""

    content = await ai_manager.generate(SYSTEM_PROMPT_UPGRADED, user_prompt)

    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1] if "\n" in content else content[3:]
        idx = content.rfind("```")
        if idx != -1:
            content = content[:idx]
    content = content.strip()
    content = content.removeprefix("json").strip()
    content = content.removeprefix("JSON").strip()

    brace_start = content.find("{")
    if brace_start != -1:
        content = content[brace_start:]
    brace_end = content.rfind("}")
    if brace_end != -1:
        content = content[: brace_end + 1]
    content = content.strip()

    if not content:
        raise ValueError("AI returned empty response")

    try:
        data = json.loads(content)
        # Format recommendation list into text
        if "recommendation" in data and isinstance(data["recommendation"], list):
            formatted_recs = []
            for item in data["recommendation"]:
                if isinstance(item, dict):
                    lines = []
                    for k, v in item.items():
                        lines.append(f"- **{k.capitalize()}**: {v}")
                    formatted_recs.append("\n".join(lines))
                elif isinstance(item, str):
                    formatted_recs.append(item)
            data["recommendation"] = "\n\n".join(formatted_recs)
        return data
    except json.JSONDecodeError as e:
        logger.error("JSON decode error in upgraded report: %s len=%d", e, len(content))
        return {}


# ── Keep original function for backward compatibility ──

async def generate_report(
    user_query: str,
    raw_data: dict,
    scores: dict,
    business_score: dict,
    competitors: list[dict],
    prices: list[dict],
    trends: list[dict],
    news: list[dict],
    cross_findings: list[str] = None,
    validation_feedback: str = None,
    data_availability: dict = None,
    context: object = None,
    market_stats: object = None,
    data_coverage: dict = None,
) -> dict:
    ctx_dict = context.model_dump() if hasattr(context, 'model_dump') else {}
    stats_dict = market_stats.model_dump() if hasattr(market_stats, 'model_dump') else {}

    summary = {
        "competitors": competitors[:20],
        "prices": prices[:20],
        "trends": trends,
        "news": news[:10],
        "scores": scores,
        "data_availability": data_availability or {},
        "query_context": {
            "product": ctx_dict.get("product", ""),
            "product_variants": ctx_dict.get("product_variants", []),
            "location": ctx_dict.get("location_city", ""),
            "province": ctx_dict.get("location_province", ""),
            "intent": ctx_dict.get("intent", ""),
            "ai_explanation": ctx_dict.get("ai_explanation", ""),
        },
        "market_statistics": {
            "total_competitors_detected": stats_dict.get("total_competitors_detected", 0),
            "direct_competitors": stats_dict.get("direct_competitors", 0),
            "indirect_competitors": stats_dict.get("indirect_competitors", 0),
            "total_reviews": stats_dict.get("total_reviews", 0),
            "avg_rating": stats_dict.get("avg_rating", 0),
            "competitors_by_location": stats_dict.get("competitors_by_location", {}),
            "data_limitation_note": stats_dict.get("data_limitation_note", ""),
        },
        "data_coverage": data_coverage or {},
    }

    summary_json = json.dumps(summary, indent=2, ensure_ascii=False)
    if len(summary_json) > 12000:
        summary_json = summary_json[:12000] + "\n... (truncated)"

    cross_text = "\n".join(f"- {f}" for f in cross_findings) if cross_findings else "Tidak ada"

    user_prompt = f"""Pertanyaan pengguna: "{user_query}"

--- DATA TERKUMPUL ---
{summary_json}

--- ANALISIS HUBUNGAN DATA (CROSS ANALYSIS) ---
{cross_text}

Berdasarkan data dan analisis hubungan di atas, tulis laporan lengkap dalam format JSON.
JANGAN tambah data fiktif apapun."""

    if validation_feedback:
        user_prompt += f"""

--- PERBAIKAN VALIDASI ---
Laporan sebelumnya ditolak karena kesalahan berikut:
{validation_feedback}

Mohon tulis ulang laporan untuk memperbaiki semua kesalahan di atas."""

    content = await ai_manager.generate(SYSTEM_PROMPT, user_prompt)

    content = content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1] if "\n" in content else content[3:]
        idx = content.rfind("```")
        if idx != -1:
            content = content[:idx]
    content = content.strip()
    content = content.removeprefix("json").strip()
    content = content.removeprefix("JSON").strip()

    brace_start = content.find("{")
    if brace_start != -1:
        content = content[brace_start:]
    brace_end = content.rfind("}")
    if brace_end != -1:
        content = content[: brace_end + 1]
    content = content.strip()

    if not content:
        raise ValueError("AI returned empty response")

    try:
        data = json.loads(content)
        if "recommendation" in data and isinstance(data["recommendation"], list):
            formatted_recs = []
            for item in data["recommendation"]:
                if isinstance(item, dict):
                    lines = []
                    for k, v in item.items():
                        lines.append(f"- **{k.capitalize()}**: {v}")
                    formatted_recs.append("\n".join(lines))
                elif isinstance(item, str):
                    formatted_recs.append(item)
            data["recommendation"] = "\n\n".join(formatted_recs)
        return data
    except json.JSONDecodeError as e:
        logger.error("JSON decode error: %s len=%d", e, len(content))
        return {}
