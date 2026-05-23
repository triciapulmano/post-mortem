# Post-Mortem Analyzer

> Why did that post *really* perform?

Most social media analytics tools tell you *what* happened — views, likes, reach. They rarely tell you *why*. Post-Mortem Analyzer is an ETL + AI pipeline that takes any public Instagram URL and returns a scored breakdown of what drove (or killed) its performance, grounded in three layers of data: the post itself, the account's own history, and platform-wide benchmarks for that niche.

Built as a portfolio project to demonstrate a full data engineering stack with an AI layer that's genuinely load-bearing — not decorative.

---

## What it does

A marketer pastes an Instagram URL. The pipeline:

1. Fetches the post and the account's last 50 posts via Apify
2. Normalizes engagement metrics into a consistent schema
3. Computes account-level averages (best days, best hours, top content type, recurring themes)
4. Pulls platform benchmarks for that niche from the database
5. Sends all three layers to Gemini Flash, which scores the post across 5 dimensions and writes a plain-English brief
6. Stores everything in PostgreSQL and returns the result to a React dashboard

The key insight: a post with 1.5% engagement rate means nothing in isolation. Against an account that averages 4%, it underperformed. Against a platform median of 1.1%, it's above average. The three-layer approach is what makes the score meaningful.

---

## Architecture

```
Instagram / Apify
       │
       ▼
┌─────────────────────────────────────┐
│         On-demand pipeline          │
│  Extract → Transform → Load → Score │
└─────────────────────────────────────┘
       │                    ▲
       │                    │
       ▼                    │
  PostgreSQL ◄──── Benchmark pipeline
       │           (runs weekly)
       ▼
   FastAPI
       │
       ▼
 React dashboard
```

Two separate ETL pipelines feed one database:

- **On-demand pipeline** — triggered when a user pastes a URL. Fetches the post, checks the cache for account history, runs AI scoring, and returns results.
- **Benchmark pipeline** — runs on a schedule (weekly). Fetches top posts across 10 niches and 2 platforms, computes median and p75 engagement rates by content type, and writes reference rows to the database. This is what gives the AI a real baseline to score against.

---

## Tech stack

| Layer | Technology | Why |
|---|---|---|
| Data extraction | Apify (Instagram + TikTok scrapers) | Handles aggressive rate limiting better than direct scraping |
| ETL orchestration | Python + custom pipeline modules | Simple, readable, easy to extend |
| Database | PostgreSQL | Relational data with JSONB for platform-specific raw fields |
| AI scoring | Google Gemini Flash | Free tier, fast, reliable JSON output |
| Backend API | FastAPI | Lightweight, async, auto-generates docs |
| Frontend | React + TypeScript | Component-based, type-safe |

---

## Database schema

Five tables, cleanly separated by concern:

- **`accounts`** — one row per tracked Instagram/X account
- **`posts`** — normalized post data with a `raw_data` JSONB column for platform-specific fields
- **`account_snapshots`** — periodic follower count captures for growth tracking
- **`benchmarks`** — niche-level engagement averages, refreshed weekly
- **`analyses`** — AI scores and explanations, cached so repeat analyses don't re-run the AI call

---

## AI scoring

The scoring prompt sends three layers of context to Gemini:

```
Target post → raw metrics + caption + content type + timing
Account history → avg engagement rate, best days/hours, top content type, recurring themes
Platform benchmark → median + p75 engagement rate for that niche + content type
```

Gemini scores the post 0–100 across five dimensions:

| Dimension | What it measures |
|---|---|
| Timing | Did this post go out at a high-engagement window for this account? |
| Format | Does the content type match what performs best for this account? |
| Hook | How strong is the opening line or visual hook? |
| Topic | Does this topic match what this audience responds to? Flags fatigue if themes repeat. |
| Velocity | How fast did it pick up engagement relative to this account's average? |

The prompt explicitly instructs the model to avoid clustering scores around 70–75 and to use the account history and benchmarks as reference points — not generic best practices. This matters: a post at 2am might score 90 on timing if that account's data shows 2am works for them specifically.

---

## Project structure

```
post-mortem/
├── etl/
│   ├── extractors/
│   │   └── instagram.py      # Apify-based Instagram fetcher
│   │   └── tiktok.py         # Apify-based TikTok fetcher
│   ├── transformers/
│   │   └── normalize.py      # Normalization + account average computation
│   ├── loaders/
│   │   └── db.py             # PostgreSQL read/write
│   └── pipelines/
│       ├── on_demand.py      # URL → scores, orchestrates the full flow
│       └── benchmark.py      # Weekly niche benchmark runner
├── ai/
│   └── analyzer.py           # Gemini prompt + scoring logic
├── api/
│   └── routes.py             # FastAPI endpoints
├── db/
│   └── schema.sql            # Table definitions
├── dashboard/                # React + TypeScript frontend
└── .env                      # API keys (not committed)
```

---

## Running locally

**Prerequisites:** Python 3.12+, Node 18+, PostgreSQL, accounts on Apify and Google AI Studio.

**1. Clone and install**

```bash
git clone https://github.com/yourusername/post-mortem.git
cd post-mortem
pip install -r requirements.txt
```

**2. Set up environment variables**

```bash
cp .env.example .env
```

Fill in:

```
DATABASE_URL=postgresql://postmortem:postmortem@localhost:5432/postmortem
APIFY_API_TOKEN=your_token
GEMINI_API_KEY=your_key
```

**3. Set up the database**

```bash
psql postgresql://postmortem:postmortem@localhost:5432/postmortem -f db/schema.sql
```

**4. Start the backend**

```bash
uvicorn api.routes:app --reload --port 8000 --host 0.0.0.0
```

**5. Start the frontend**

```bash
cd dashboard
npm install
npm start
```

Open `http://localhost:3000`, paste an Instagram URL, and run an analysis.

---

## Design decisions worth noting

**Why Apify over direct scraping?** Instagram aggressively blocks unauthenticated requests from cloud server IPs — Codespaces, EC2, Railway, all flagged immediately. Apify handles session rotation and proxy management, which makes it reliable enough for a real product.

**Why cache account history?** The first analysis for any account takes ~60 seconds because it fetches 50 posts from Apify. Every subsequent analysis for that same account skips the fetch entirely — it just reads from the database. This is the most important performance optimization in the pipeline.

**Why store raw_data as JSONB?** Instagram and X return very different metadata. Rather than adding 15 nullable columns to the posts table, `raw_data` stores the original API response. You can mine it later for new fields without a schema migration.

**Why separate the benchmark pipeline?** Decoupling benchmark collection from on-demand analysis means the scoring step never blocks on slow API calls. The benchmark runner is a weekly batch job; the on-demand pipeline just reads from what's already in the database.

---

## Roadmap

- [ ] X (Twitter) extractor — architecture supports it, needs a paid API tier
- [ ] TikTok support via Apify
- [ ] Scheduled re-analysis to track how scores change as engagement accumulates
- [ ] Multi-post comparison — analyze a batch of posts side by side
- [ ] Email digest — weekly summary of best and worst performing posts

---

## License

MIT