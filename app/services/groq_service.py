"""AI ONLY describes collected data. Never generates data."""

import json
import logging
from app.services.ai_manager import manager as ai_manager

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """Anda adalah AI penulis laporan analisis bisnis profesional untuk UMKM Indonesia.

TUGAS ANDA:
Tulis deskripsi laporan bisnis berdasarkan data mentah dan analisis hubungan data (cross analysis) yang disediakan. Semua kesimpulan harus didukung data nyata yang ada.

ATURAN UTAMA (WAJIB DIPATUHI):
1. DATA FIRST & EVIDENCE BASED: Jangan pernah berasumsi atau mengarang data fiktif. Jika data tidak tersedia (UNAVAILABLE), sebutkan secara eksplisit "Data tidak tersedia" dan tulis "Belum cukup data untuk menyimpulkan" pada bagian terkait.
2. KONSISTENSI SKOR & LABEL:
   - Demand, Profit Potential, Trend Score: Tinggi (70-100) = BAIK/TINGGI.
   - Competition Score: Tinggi (70-100) = PERSAINGAN KETAT/PADAT (Sulit).
   - Risk Score: Tinggi (70-100) = RISIKO TINGGI (Bahaya).
   Gunakan label: 85+ (Sangat Tinggi), 70+ (Tinggi), 50+ (Sedang), 30+ (Rendah), <30 (Sangat Rendah).
3. DYNAMIC NARRATIVE: Hindari kata "mendominasi" atau "market leader" kecuali ada selisih review/pangsa yang sangat signifikan (>3x lipat dari rata-rata). Gunakan "distribusi relatif merata" jika data kompetitor serupa.
4. PRICE DISTRIBUTION BASED RECOMMENDATION: Rekomendasi harga WAJIB mengikuti distribusi pasar (Median, P25, P75). Jangan menyarankan harga di luar jangkauan data kecuali ada alasan diferensiasi kuat.
5. NO GENERIC COPY: Dilarang keras menggunakan template "menawarkan produk kompetitif", "harga bersaing", "pelayanan terbaik". Sebutkan angka, nama kompetitor, atau tren spesifik.

Output JSON wajib menggunakan format berikut:
{
  "executive_summary": "Analisis profesional (2-3 kalimat). Sebutkan data kunci (jumlah kompetitor, tren, harga).",
  "market_trend_description": "Deskripsi tren Google Trends secara spesifik (angka/minat).",
  "competitor_insights": "Analisis peta persaingan Google Maps. Sebutkan nama kompetitor utama, rating, dan volume review.",
  "price_insights": "Analisis harga Google Shopping sesuai distribusi (Median, P25, P75, Sebaran).",
  "news_summary": "Ringkasan berita Tavily. Jika tidak ada, tulis: 'Data tidak tersedia'.",
  "opportunity_analysis": "Analisis peluang berdasarkan celah data (misal: rating rendah, gap harga, tren naik).",
  "risk_analysis": "Analisis risiko utama. Hubungkan dengan skor Risk dan Competition.",
  "recommendation": "3-4 poin terstruktur (Tindakan, Alasan, Data Pendukung, Dampak)."
}"""




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
) -> dict:
    summary = {
        "competitors": competitors[:10],
        "prices": prices[:15],
        "trends": trends,
        "news": news,
        "scores": scores,
        "data_availability": data_availability or {},
    }
    summary_json = json.dumps(summary, indent=2, ensure_ascii=False)
    if len(summary_json) > 10000:
        summary_json = summary_json[:10000] + "\n... (truncated)"

    cross_text = "\n".join(f"- {f}" for f in cross_findings) if cross_findings else "Tidak ada"

    user_prompt = f"""Pertanyaan pengguna: "{user_query}"

--- DATA TERKUMPUL ---
{summary_json}

--- ANALISIS HUBUNGAN DATA (CROSS ANALYSIS) ---
{cross_text}

Berdasarkan data dan analisis hubungan di atas, tulis laporan dalam format JSON.
JANGAN tambah data fiktif apapun."""

    if validation_feedback:
        user_prompt += f"""

--- PERBAIKAN VALIDASI ---
Laporan sebelumnya ditolak karena kesalahan berikut:
{validation_feedback}

Mohon tulis ulang laporan untuk memperbaiki semua kesalahan di atas dengan tetap mematuhi aturan JSON."""

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

