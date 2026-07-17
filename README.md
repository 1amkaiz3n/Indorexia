# Indorexia — UMKM Business Research Intelligence

<p align="center">
  <img src="https://img.shields.io/badge/Status-Production_Ready-7C3AED?style=for-the-badge">
  <img src="https://img.shields.io/badge/Python-3.12+-7C3AED?style=for-the-badge&logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/FastAPI-0.139-7C3AED?style=for-the-badge&logo=fastapi&logoColor=white">
  <img src="https://img.shields.io/badge/React-19-7C3AED?style=for-the-badge&logo=react&logoColor=white">
</p>

---

## 📋 Table of Contents

- [1. Project Overview](#1-project-overview)
- [2. Features](#2-features)
- [3. How It Works](#3-how-it-works)
- [4. Installation Guide](#4-installation-guide)
- [5. Configuration](#5-configuration)
- [6. Usage Guide](#6-usage-guide)
- [7. Project Structure](#7-project-structure)
- [8. Technology Stack](#8-technology-stack)
- [9. Security Notes](#9-security-notes)
- [10. Future Development](#10-future-development)
- [11. License](#11-license)

---

## 1. Project Overview

### Tujuan

Indorexia adalah platform riset pasar otomatis yang dirancang khusus untuk UMKM dan calon pengusaha di Indonesia. Platform ini mengumpulkan data dari berbagai sumber publik (Google Trends, Google Maps, Google Shopping, dan Tavily), menganalisisnya secara deterministik, dan menghasilkan laporan kelayakan bisnis yang komprehensif — tanpa memerlukan akun, tanpa biaya, dan tanpa kemampuan teknis dari pengguna.

### Masalah yang Diselesaikan

| Masalah | Dampak | Solusi Indorexia |
|---------|--------|------------------|
| Riset pasar manual memakan waktu berhari-hari | Keputusan bisnis tertunda | Riset otomatis selesai dalam 30-60 detik |
| Biaya konsultan bisnis mahal (Rp500k-Rp5jt) | UMKM tidak mampu | Gratis, tanpa biaya per report |
| Data tersebar di banyak platform | Analisis tidak komprehensif | Satu dashboard, 4 sumber data terintegrasi |
| AI sering membuat data palsu (hallucination) | Keputusan berdasarkan fiksi | Semua data dari API nyata, AI hanya mendeskripsikan |
| Tidak tahu cara membaca data pasar | Kebingungan mengambil keputusan | Decision Engine + rekomendasi jelas |

### Keunggulan Utama

- **Deterministic Scoring** — Skor bisnis dihitung dengan rumus tetap, bukan tebakan AI. Setiap skor bisa dijelaskan dan di-reproduksi.
- **No Hallucination** — AI tidak pernah membuat data. AI hanya menulis deskripsi dari data yang sudah terkumpul. Semua fakta (harga, kompetitor, tren) berasal dari API nyata.
- **Anonymous & Gratis** — Tidak perlu akun. Tidak perlu login. Langsung pakai.
- **Decision Engine** — Bukan sekadar menampilkan data, tapi memberikan keputusan: Layak Dijalankan / Perlu Dipertimbangkan / Tidak Disarankan.
- **Action Plan** — Langsung dapat rencana tindakan 30 hari berdasarkan hasil riset.

---

## 2. Features

### 🔬 Research Engine

| Fitur | Detail |
|-------|--------|
| **Google Trends Analysis** | Mengambil data minat pencarian, query terkait, topik terkait, dan query yang sedang naik daun. Menampilkan sparkline chart dan statistik deskriptif. |
| **Google Maps Competitor Scan** | Mendeteksi kompetitor di area tertentu dengan nama, rating, jumlah review, alamat, jam operasional, website, dan link Google Maps langsung. |
| **Google Shopping Price Intelligence** | Mengumpulkan harga produk dari Google Shopping. Menampilkan daftar harga lengkap, statistik (min, max, rata-rata, median), dan distribusi harga. |
| **Tavily News Aggregation** | Mengumpulkan berita terkait industri dan lokasi untuk analisis sentimen dan konteks pasar. |

### 🧠 Decision Engine

| Fitur | Detail |
|-------|--------|
| **Business Verdict** | Output: ✅ Layak Dijalankan / ⚠️ Perlu Dipertimbangkan / 🔴 Tidak Disarankan. Dilengkapi confidence score. |
| **Benchmark Scoring** | 5 dimensi skor (Permintaan, Persaingan, Profit, Tren, Risiko) dengan label: Sangat Tinggi / Tinggi / Sedang / Rendah / Sangat Rendah. |
| **Opportunity & Saturation Score** | Mengukur potensi peluang dan tingkat kejenuhan pasar. |
| **SWOT Analysis** | Strength, Weakness, Opportunity, Threat — dihasilkan dari analisis data, bukan tebakan. |
| **Risk Assessment** | Identifikasi risiko kompetisi, pasar, dan operasional. |
| **Action Plan** | Rencana tindakan 30 hari dalam 4 fase: Minggu 1–4. |

### 📊 Report & Visualization

| Fitur | Detail |
|-------|--------|
| **Executive Summary** | Ringkasan komprehensif dari AI berdasarkan data terkumpul. |
| **Trend Sparkline Chart** | Visualisasi data Google Trends dengan bar chart interaktif (hover untuk lihat nilai). |
| **Price Distribution Bar** | Distribusi harga produk dalam rentang (0-50rb, 50-100rb, 100-300rb, 300rb+). |
| **Market Statistics** | Total kompetitor, total review, rata-rata rating, jumlah produk ditemukan. |
| **Sources Transparency** | Menampilkan status setiap sumber data (✓ Sukses / ✗ Tidak Ada Data). |

### 👤 User Experience

| Fitur | Detail |
|-------|--------|
| **Anonymous Session** | Visitor ID disimpan di localStorage, tidak perlu akun. |
| **Refresh-Safe** | Report terakhir tetap muncul setelah refresh halaman. |
| **Research History** | Halaman history dengan card modern, search, filter berdasarkan status, sort by tanggal/skor. |
| **Bookmark / Pin** | Sematkan report penting ke urutan teratas. |
| **Rename & Duplicate** | Ubah judul report atau buat salinan untuk riset ulang. |
| **Bulk Delete** | Hapus beberapa report sekaligus atau hapus semua history. |
| **Dark Mode** | Otomatis mengikuti preferensi sistem. |
| **Full Responsive** | Desktop, tablet, dan mobile. |

---

## 3. How It Works

### System Architecture

```
User Input (Query)
      │
      ▼
┌──────────────────────────────────────────────────────────┐
│                   Research Router                         │
│  Parse query → ekstrak jenis usaha & lokasi              │
└──────────────────────────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────────────────────────┐
│               Data Collection Layer                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ SerpAPI  │  │ SerpAPI  │  │ SerpAPI  │  │ Tavily   │ │
│  │ Google   │  │ Google   │  │ Google   │  │ Web      │ │
│  │ Search   │  │ Trends   │  │ Shopping │  │ Search   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
└──────────────────────────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────────────────────────┐
│                   Parser Layer                            │
│  Parse API responses → Competitor, PriceItem, TrendItem, │
│  NewsItem structs. Calculate PriceStats, ReviewStats.     │
└──────────────────────────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────────────────────────┐
│                   Scoring Engine                          │
│  Calculate: Demand, Competition, Profit, Trend, Risk     │
│  → Overall Score (deterministic, no AI)                  │
└──────────────────────────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────────────────────────┐
│                   Decision Engine                         │
│  → Verdict (GO/CAUTION/STOP)                             │
│  → Opportunity Score, Saturation Score                   │
│  → SWOT Analysis, Action Plan, Market Gaps               │
│  → Benchmark Labels (Sangat Tinggi/Tinggi/Sedang/dll)    │
└────────────────////////////////////////////////////////──┘
      │
      ▼
┌──────────────────────────────────────────────────────────┐
│                   AI Writer Layer                         │
│  AI hanya menulis teks deskripsi (bukan data):           │
│  Executive Summary, Market Trend Description,            │
│  Competitor Insights, Price Insights,                    │
│  News Summary, Opportunity/Risk Analysis, Recommendation │
└──────────────────────────────────────────────────────────┘
      │
      ▼
┌──────────────────────────────────────────────────────────┐
│                   Response + Storage                      │
│  → Return report to frontend                             │
│  → Save to Supabase (async) with visitor_id              │
│  → Frontend caches to localStorage for refresh safety    │
└──────────────────────────────────────────────────────────┘
```

### User Flow

```
1. Buka website → Visitor ID dibuat otomatis (localStorage)
2. Masukkan query → "saya mau buka toko baju di bandung"
3. Sistem parse → business_type="toko baju", location="bandung"
4. Data collection → 4 API calls (sequential, with retry)
5. Parsing → extract competitors, prices, trends, news
6. Scoring → demand, competition, profit, trend, risk
7. Decision → verdict, SWOT, action plan, opportunity score
8. AI writes → executive summary, insights, recommendation
9. Report returned → ditampilkan di frontend + simpan ke Supabase
10. User dapat:
    - Refresh halaman → report tetap muncul (dari localStorage)
    - Buka /history → lihat semua report
    - Pin, rename, duplicate, delete report
    - Buka report lama → langsung tampil (tanpa API ulang)
```

### AI Provider Fallback

```
Mencoba Gemini...
Gemini gagal (Rate limited 429)
Mencoba Groq...
Groq gagal (Timeout)
Mencoba OpenRouter...
Sukses menggunakan: OpenRouter
```

Jika semua provider gagal → error message user-friendly, aplikasi tidak crash.

---

## 4. Installation Guide

### Prerequisites

| Software | Minimum Version | Catatan |
|----------|----------------|---------|
| Python | 3.12+ | `python3 --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |
| Supabase Project | - | Akun gratis sudah cukup |

### Langkah Instalasi

#### 1. Clone Repository

```bash
git clone https://github.com/yourusername/Indorexia.git
cd Indorexia
```

#### 2. Backend Setup

```bash
# Buat virtual environment (opsional tapi disarankan)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# atau venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

#### 3. Frontend Setup

```bash
cd frontend
npm install
cd ..
```

#### 4. Konfigurasi Environment

```bash
cp .env.example .env
# atau edit langsung file .env
```

Isi semua API key yang diperlukan (lihat bagian Configuration).

#### 5. Database Setup

Buka Supabase Dashboard → SQL Editor → paste isi `supabase-schema.sql` → Run.

#### 6. Build Frontend

```bash
cd frontend
npm run build
cd ..
```

#### 7. Jalankan Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Buka `http://localhost:8000` di browser.

---

## 5. Configuration

### Environment Variables (`Indorexia/.env`)

| Variable | Required | Description |
|----------|----------|-------------|
| `SERPAPI_API_KEY` | ✅ Yes | API key dari [serpapi.com](https://serpapi.com) — untuk Google Search, Trends, Shopping |
| `TAVILY_API_KEY` | ✅ Yes | API key dari [tavily.com](https://tavily.com) — untuk web & news search |
| `GROQ_API_KEY` | ✅ Yes (min 1) | API key dari [groq.com](https://groq.com) — AI provider (Llama 3.3) |
| `GEMINI_API_KEY` | ✅ Yes (min 1) | API key dari [Google AI Studio](https://aistudio.google.com) — AI provider fallback |
| `OPENROUTER_API_KEY` | ✅ Yes (min 1) | API key dari [openrouter.ai](https://openrouter.ai) — AI provider fallback |
| `SUPABASE_URL` | Optional | URL Supabase project untuk menyimpan history |
| `SUPABASE_KEY` | Optional | Anon/public key Supabase |

**Catatan**: Minimal satu AI provider harus aktif. Urutan fallback: Gemini → Groq → OpenRouter.

### Contoh `.env`

```env
SERPAPI_API_KEY=your_serpapi_key
TAVILY_API_KEY=your_tavily_key
GROQ_API_KEY=your_groq_key
GEMINI_API_KEY=your_gemini_key
OPENROUTER_API_KEY=your_openrouter_key

SUPABASE_URL=https://your-project.supabase.co/rest/v1/
SUPABASE_KEY=your_supabase_anon_key
```

---

## 6. Usage Guide

### Basic Usage

1. Buka `http://localhost:8000`
2. Masukkan query seperti:
   - `"saya mau buka toko baju di bandung"`
   - `"ide bisnis kuliner di jogja"`
   - `"jualan online skincare untuk remaja"`
   - `"buka kafe di jakarta selatan"`
3. Klik **Riset Sekarang**
4. Tunggu 30-60 detik
5. Baca hasil laporan

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/research` | Melakukan riset baru (body: `{query, location?, visitor_id?}`) |
| `POST` | `/api/research/history` | Mendapatkan daftar history (body: `{visitor_id, search?, verdict?, sort?}`) |
| `GET` | `/api/research/{id}` | Mendapatkan satu report (`?visitor_id=xxx`) |
| `DELETE` | `/api/research/{id}` | Hapus satu report (`?visitor_id=xxx`) |
| `DELETE` | `/api/research` | Hapus semua history (`?visitor_id=xxx`) |
| `PATCH` | `/api/research/{id}` | Update report (body: `{visitor_id, title?, pinned?}`) |
| `POST` | `/api/research/{id}/duplicate` | Duplikat report (`?visitor_id=xxx`) |
| `GET` | `/api/health` | Health check |

### Navigation

| Menu | Deskripsi |
|------|-----------|
| **Research** | Halaman utama untuk melakukan riset baru |
| **History** | Daftar semua report yang pernah dibuat |
| **Pin 📌** | Sematkan report penting di urutan teratas |
| **Rename ✏️** | Ubah judul report |
| **Duplicate 📋** | Buat salinan report |
| **Delete 🗑️** | Hapus report |
| **Bulk Delete** | Hapus beberapa report sekaligus |

---

## 7. Project Structure

```
Indorexia/
├── .env                          # Environment variables (API keys)
├── requirements.txt              # Python dependencies
├── supabase-schema.sql           # Database schema untuk Supabase
│
├── app/                          # Backend (FastAPI)
│   ├── main.py                   # Entry point, middleware, static file serving
│   ├── config.py                 # Pydantic Settings (.env loader)
│   │
│   ├── schemas/
│   │   └── research.py           # Pydantic models (request/response)
│   │
│   ├── routers/
│   │   └── research.py           # API endpoints, parsers, scoring, decision engine
│   │
│   └── services/
│       ├── serpapi_service.py    # Google Search, Trends, Shopping (with retry)
│       ├── tavily_service.py     # Web & news search (with retry)
│       ├── groq_service.py       # AI report generation (prompts + response parsing)
│       ├── ai_manager.py         # AI Provider Manager (fallback: Gemini→Groq→OpenRouter)
│       ├── supabase_service.py   # Database CRUD (visitor-based ownership)
│       │
│       └── providers/            # AI provider implementations
│           ├── base.py           # Abstract AIProvider class + AIProviderError
│           ├── gemini.py         # Google Gemini provider
│           ├── groq.py           # Groq (Llama) provider
│           └── openrouter.py     # OpenRouter (GPT-4o-mini) provider
│
└── frontend/                     # Frontend (React + Vite + Tailwind)
    ├── index.html
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── main.tsx              # React entry point
        ├── App.tsx               # Main app (routing, state, refresh recovery)
        ├── index.css             # Global styles + dark mode
        ├── types/
        │   └── index.ts          # TypeScript interfaces
        ├── lib/
        │   ├── api.ts            # API client (all endpoints)
        │   ├── visitor.ts        # Anonymous visitor ID generation
        │   └── storage.ts        # localStorage cache (refresh-safe)
        └── components/
            ├── Navbar.tsx        # Top navigation (Research / History)
            ├── ResearchForm.tsx  # Search input + example buttons
            ├── ReportView.tsx    # Full report display (all sections)
            └── HistoryPage.tsx   # History dashboard (cards, search, filter, sort)
```

---

## 8. Technology Stack

| Teknologi | Kegunaan |
|-----------|----------|
| **FastAPI** (Python 3.12+) | Backend API framework — async, type-safe, auto-docs |
| **Uvicorn** | ASGI server untuk menjalankan FastAPI |
| **httpx** | HTTP client async untuk panggilan API eksternal |
| **Pydantic** | Validasi data, schema request/response, settings management |
| **SerpAPI** | Google Search, Google Trends, Google Shopping API |
| **Tavily** | Web & news search API |
| **Groq** | AI LLM inference (Llama 3.3 70B) |
| **Google Gemini** | AI LLM fallback (Gemini 2.0 Flash) |
| **OpenRouter** | AI LLM fallback (GPT-4o-mini) |
| **Supabase** | Database (PostgreSQL) untuk history & ownership |
| **React 19** | Frontend UI library |
| **TypeScript** | Type-safe frontend code |
| **Vite** | Frontend build tool & dev server |
| **Tailwind CSS 4** | Utility-first CSS framework |
| **localStorage** | Anonymous session & report cache |

---

## 9. Security Notes

### Ownership & Privacy

- Setiap visitor memiliki `visitor_id` unik yang disimpan di localStorage browser.
- Semua API endpoint history/delete/update memvalidasi `visitor_id` — pengguna hanya bisa mengakses report miliknya sendiri.
- Tidak ada data pribadi yang dikumpulkan. Tidak ada akun. Tidak ada login.
- Report yang dihapus tidak bisa dikembalikan.

### API Key Security

- API key disimpan di file `.env` (tidak di-commit ke repository).
- Jangan pernah mengekspos API key di frontend atau public repository.
- Gunakan environment variables di production.
- SerpAPI, Tavily, Groq, Gemini, dan OpenRouter memiliki rate limits — aplikasi sudah handle retry dan fallback.

### Data Storage

- Report disimpan di Supabase dengan anon key (RLS enabled).
- Jika Supabase tidak dikonfigurasi, aplikasi tetap berfungsi penuh tanpa penyimpanan.
- localStorage di browser hanya menyimpan 1 report terakhir untuk refresh safety.

---

## 10. Future Development

### Tier 1 — Wajib

- [ ] **Decision Engine Enhancement** — Porter Five Forces, Revenue Estimator, BEP Calculator
- [ ] **Market Gap Analysis** — Deteksi otomatis niche berdasarkan rising queries & competitor gaps
- [ ] **Review Sentiment** — Analisis kata kunci dari review kompetitor

### Tier 2 — Sangat Menarik

- [ ] **Google Business Profile** — Atribut bisnis, jam buka, layanan, foto, Q&A
- [ ] **People Also Ask (PAA)** — Pertanyaan calon pelanggan dari Google Search
- [ ] **YouTube Search** — Konten yang sedang ramai terkait niche
- [ ] **Keyword Opportunity Matrix** — Volume vs competition untuk ide produk

### Tier 3 — Level Consultant

- [ ] **Seasonality Prediction** — Prediksi tren 3-6 bulan berdasarkan data historis
- [ ] **Revenue Estimation** — Estimasi omzet berdasarkan rata-rata transaksi
- [ ] **Location Heatmap** — Area terbaik berdasarkan traffic Google Maps
- [ ] **Export Report** — PDF, CSV, atau sharing link
- [ ] **Multi-language** — Inggris, Mandarin, dll

---

## 11. License

## 🛡️ License

<p align="center">
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-All%20Rights%20Reserved-7C3AED?style=for-the-badge&logo=bookstack&logoColor=white">
  </a>
</p>
