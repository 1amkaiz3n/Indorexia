"""AI Query Understanding & Query Generation Pipeline.

Takes raw user input → AI analysis → structured ResearchContext → source-specific queries.
"""

import json
import re
import logging
from app.schemas.query import ResearchContext, ResearchQueries
from app.services.ai_manager import manager as ai_manager

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_UNDERSTAND = """Anda adalah AI Query Understanding untuk platform riset pasar UMKM Indonesia.

TUGAS ANDA:
Analisis input user dan ekstrak informasi terstruktur untuk riset pasar.
Anda HARUS memperbaiki typo, memahami bahasa informal, dan menormalisasi lokasi.

Output JSON WAJIB menggunakan format berikut (HANYA JSON, tanpa markdown):
{
  "intent": "Jenis intent user — pilih salah satu: product_opportunity_research, competition_analysis, demand_analysis, feasibility_study, general_exploration, pricing_research, trend_analysis",
  "business_category": "Kategori bisnis utama — pilih salah satu: food_beverage, fashion, beauty_care, electronics, home_living, health, education, sports, automotive, service, agriculture, other",
  "product": "Produk utama yang disebutkan (paling spesifik)",
  "product_variants": ["Semua varian produk yang disebutkan atau tersirat"],
  "location_city": "Kota, kosongkan jika tidak disebut",
  "location_district": "Kecamatan/kelurahan, kosongkan jika tidak disebut",
  "location_province": "Provinsi, isi dengan provinsi yang benar dari kota yang disebut",
  "location_raw": "Lokasi asli dari input user (seperti ditulis user)",
  "target_market": "Target pasar yang disebut atau tersirat",
  "customer_segment": "Segmen pelanggan: umum, remaja, dewasa, anak-anak, wanita, pria, keluarga, profesional, semua",
  "budget": "Modal yang disebutkan (dalam teks asli), kosongkan jika tidak disebut",
  "business_goal": "Tujuan bisnis: cari_peluang, analisis_persaingan, cari_produk, validasi_ide, riset_harga, analisis_tren",
  "explicit_keywords": ["Keyword eksplisit yang disebut user"],
  "implicit_keywords": ["Keyword implisit yang relevan tapi tidak disebut langsung"],
  "research_type": "Jenis riset: comprehensive, quick_scan, deep_dive",
  "ai_explanation": "Penjelasan singkat bagaimana Anda memahami input user ini, termasuk koreksi typo jika ada, dan asumsi yang dibuat"
}

ATURAN PENTING:
1. PERBAIKI TYPO: "kripik" → "keripik", "pisang" → "pisang", "ciamis" → "Ciamis", dll.
2. NORMALISASI LOKASI: Jika user menyebut "bandung", isi province = "Jawa Barat". Jika "ciamis", province = "Jawa Barat". Jika "jogja", isi city = "Yogyakarta", province = "DI Yogyakarta".
3. EKSTRAK VARIAN: Jika user menyebut beberapa produk (keripik singkong, pisang, ubi), masukkan semua ke product_variants.
4. TANPA LOKASI: Jika hanya ada produk tanpa lokasi, location fields boleh kosong.
5. BAHASA INFORMAL: "jualan" → intent bisnis, "buka toko" → feasibility_study, "bagus nggak" → general_exploration
6. JANGAN BUAT keyword jika tidak ada indikasi dalam input user.
"""


SYSTEM_PROMPT_QUERIES = """Anda adalah AI Query Generator untuk platform riset pasar UMKM Indonesia.

TUGAS ANDA:
Buat daftar query yang optimal untuk setiap sumber data berdasarkan ResearchContext yang diberikan.
Setiap query harus ditulis dalam Bahasa Indonesia.

Output JSON WAJIB menggunakan format berikut (HANYA JSON, tanpa markdown):
{
  "maps_queries": ["Query 1 untuk Google Maps", "Query 2", ...],
  "search_queries": ["Query 1 untuk Google Search", ...],
  "shopping_queries": ["Query 1 untuk Google Shopping", ...],
  "trends_queries": ["Query 1 untuk Google Trends", ...],
  "tavily_queries": ["Query 1 untuk Tavily News", ...]
}

ATURAN PEMBUATAN QUERY:

1. Google Maps (mencari bisnis lokal):
   - Produk + lokasi: "keripik singkong Ciamis"
   - Kategori + lokasi: "makanan ringan Ciamis", "oleh-oleh Ciamis"
   - Variasi produk + lokasi
   - Variasi nama bisnis: "produsen keripik Ciamis", "toko keripik Ciamis"
   - Maksimal 8 query, minimal 3

2. Google Search (mencari informasi pasar luas):
   - Produk + lokasi + konteks bisnis
   - "bisnis keripik Ciamis", "harga keripik singkong Ciamis"
   - Maksimal 5 query, minimal 2

3. Google Shopping (mencari data harga produk):
   - Nama produk (tanpa lokasi untuk hasil lebih luas)
   - Produk + spesifikasi: "keripik singkong 250 gram", "keripik singkong 500 gram"
   - Produk + varian: "keripik pisang", "keripik ubi"
   - Maksimal 6 query, minimal 2

4. Google Trends (mencari minat pencarian):
   - GUNAKAN keyword yang benar-benar merepresentasikan produk dan intent.
   - JANGAN gunakan kata terpisah dari kalimat secara acak.
   - Keyword harus memiliki hubungan semantik jelas dengan produk.
   - Produk utama, varian produk, kombinasi produk + lokasi
   - Maksimal 8 query, minimal 2

5. Tavily/News (mencari berita terkini):
   - Produk + lokasi + konteks
   - Maksimal 3 query, minimal 1

PENTING:
- GUNAKAN lokasi dari context. Jika location_city ada, gunakan kombinasi produk+kota.
- Jika ada product_variants, buat query untuk setiap varian yang relevan.
- Query harus spesifik dan relevan — jangan buat query yang terlalu umum.
- Prioritaskan keyword dengan intent komersial tinggi.
"""


async def understand_query(user_input: str) -> ResearchContext:
    """AI-powered query understanding — parse user input into structured context."""
    user_prompt = f"""Analisis input user berikut dan ekstrak informasi terstruktur untuk riset pasar:

Input user: "{user_input}"

Keluarkan JSON sesuai format yang ditentukan. Pastikan semua field terisi dengan benar."""

    content = await ai_manager.generate(SYSTEM_PROMPT_UNDERSTAND, user_prompt)
    data = _extract_json(content)

    ctx = ResearchContext(
        intent=data.get("intent", "general_exploration"),
        business_category=data.get("business_category", ""),
        product=data.get("product", ""),
        product_variants=data.get("product_variants", []),
        location_city=data.get("location_city", ""),
        location_district=data.get("location_district", ""),
        location_province=data.get("location_province", ""),
        location_country="Indonesia",
        location_raw=data.get("location_raw", ""),
        target_market=data.get("target_market", ""),
        customer_segment=data.get("customer_segment", ""),
        budget=data.get("budget", ""),
        business_goal=data.get("business_goal", ""),
        explicit_keywords=data.get("explicit_keywords", []),
        implicit_keywords=data.get("implicit_keywords", []),
        research_type=data.get("research_type", "comprehensive"),
        ai_explanation=data.get("ai_explanation", ""),
    )
    return ctx


async def generate_queries(context: ResearchContext) -> ResearchQueries:
    """Generate source-specific queries from ResearchContext."""
    context_json = context.model_dump_json(indent=2)

    user_prompt = f"""Buat query riset untuk setiap sumber data berdasarkan ResearchContext berikut:

{context_json}

Buat query yang optimal dan variatif untuk setiap sumber. Keluarkan JSON sesuai format yang ditentukan."""

    content = await ai_manager.generate(SYSTEM_PROMPT_QUERIES, user_prompt)
    data = _extract_json(content)

    queries = ResearchQueries(
        maps_queries=data.get("maps_queries", []),
        search_queries=data.get("search_queries", []),
        shopping_queries=data.get("shopping_queries", []),
        trends_queries=data.get("trends_queries", []),
        tavily_queries=data.get("tavily_queries", []),
    )
    return queries


def _extract_json(content: str) -> dict:
    """Extract JSON from AI response, handling markdown code blocks."""
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
        logger.error("Empty content after JSON extraction")
        return {}

    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        logger.error("JSON decode error in query understanding: %s", e)
        return {}


def _fallback_parse(user_input: str) -> ResearchContext:
    """Fallback if AI fails — simple rule-based parsing."""
    q = user_input.lower().strip()
    q = re.sub(r"\bsaya\s+mau\s+(buka|membuka|buat|membuat|jual|jualan)\b", "", q).strip()
    q = re.sub(r"\bdi\s+(daerah|kota|wilayah)\b", "di", q).strip()
    parts = re.split(r"\bdi\b", q, maxsplit=1)

    product = parts[0].strip() if parts else q
    location_raw = parts[1].strip() if len(parts) == 2 else ""

    location_city = location_raw
    location_province = ""
    known_cities = {
        "bandung": "Jawa Barat", "ciamis": "Jawa Barat", "bogor": "Jawa Barat",
        "bekasi": "Jawa Barat", "depok": "Jawa Barat", "tasikmalaya": "Jawa Barat",
        "garut": "Jawa Barat", "sukabumi": "Jawa Barat", "cirebon": "Jawa Barat",
        "jakarta": "DKI Jakarta", "tangerang": "Banten", "semarang": "Jawa Tengah",
        "surabaya": "Jawa Timur", "malang": "Jawa Timur", "yogyakarta": "DI Yogyakarta",
        "medan": "Sumatera Utara", "makassar": "Sulawesi Selatan", "palembang": "Sumatera Selatan",
    }
    loc_lower = location_raw.lower()
    for city, province in known_cities.items():
        if city in loc_lower:
            location_city = city.capitalize()
            location_province = province
            break

    intent = "general_exploration"
    if any(w in q for w in ["jual", "jualan", "dagang"]):
        intent = "product_opportunity_research"
    elif any(w in q for w in ["modal", "biaya", "mahal", "murah"]):
        intent = "feasibility_study"
    elif any(w in q for w in ["saing", "kompetitor", "pesaing"]):
        intent = "competition_analysis"

    return ResearchContext(
        intent=intent,
        business_category="",
        product=product,
        product_variants=[product] if product else [],
        location_city=location_city,
        location_province=location_province,
        location_raw=location_raw,
        research_type="comprehensive",
        ai_explanation=f"Fallback parse: extracted product '{product}' and location '{location_raw}'",
    )


def _fallback_queries(context: ResearchContext) -> ResearchQueries:
    """Fallback query generation if AI fails."""
    product = context.product or "produk"
    city = context.location_city or ""
    loc = f" {city}" if city else ""

    queries = ResearchQueries()
    queries.maps_queries = [f"{product}{loc}"]
    queries.search_queries = [f"{product}{loc} bisnis", f"{product}{loc} harga"]
    queries.shopping_queries = [f"{product}"]
    queries.trends_queries = [f"{product}"]
    queries.tavily_queries = [f"{product} {city} UMKM" if city else f"{product} bisnis Indonesia"]

    for variant in context.product_variants:
        if variant.lower() != product.lower():
            queries.maps_queries.append(f"{variant}{loc}")
            queries.shopping_queries.append(f"{variant}")
            queries.trends_queries.append(f"{variant}")

    queries.shopping_queries.append(f"{product} 250 gram")
    queries.shopping_queries.append(f"{product} 500 gram")

    cat_queries = []
    if context.business_category == "food_beverage":
        cat_queries = [f"makanan ringan{loc}", f"oleh-oleh{loc}", f"snack{loc}"]
    elif context.business_category == "fashion":
        cat_queries = [f"toko baju{loc}", f"fashion{loc}", f"busana{loc}"]

    for cq in cat_queries:
        queries.maps_queries.append(cq)

    return queries
