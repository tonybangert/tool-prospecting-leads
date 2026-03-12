# AI-Powered Subscription Ecosystem Dashboard + ICP Research Tool

Sales demo dashboard for **PerformanceLabs** featuring an **ICP (Ideal Customer Profile) research tool** that uses Claude to extract structured customer profiles from conversation, searches Apollo for matching prospects, and scores account fit.

## Tech Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy (async), PostgreSQL, Redis
- **Frontend:** Vanilla JS (ES modules), Chart.js 4, Vite, custom CSS
- **AI:** Anthropic Claude API via agent framework
- **External APIs:** Apollo.io (prospect search)
- **Infra:** Docker Compose (PostgreSQL + Redis), Alembic migrations

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Apollo.io API key (free tier works)
- Anthropic API key (for Claude ICP extraction)

### Setup

```bash
# 1. Start PostgreSQL + Redis
docker compose up -d

# 2. Backend
cd backend
python -m venv venv && source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env  # add your API keys
alembic upgrade head

# 3. Frontend
cd ../frontend
npm install

# 4. Run
cd ../backend && uvicorn app.main:app --reload --port 8000
cd ../frontend && npm run dev   # in a separate terminal
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `ANTHROPIC_API_KEY` | Claude API key |
| `APOLLO_API_KEY` | Apollo.io API key |

## Features

### Dashboard (Phase 0)
Live demo dashboard with sample data — no external APIs required:
- KPI bar (MRR, subscribers, active rate, ARPU, engagement, churn)
- Subscriber overview with status/tier distributions
- Churn prediction scatter plot + high-risk list
- AI behavioral segments with radar charts
- Upsell/retention recommendations with revenue impact
- Revenue forecast (baseline vs AI-enhanced)
- AI agent retention action timeline

### ICP Research (Phase 1)
- **Claude conversation:** Describe your ideal customer in plain English; Claude extracts structured criteria
- **CRUD:** Create, list, update, activate ICP models
- **Scoring engine:** Weighted multi-factor fit scoring (firmographic, tech, persona, timing, data confidence)

### Prospect Search (Phase 2)
- **Apollo integration:** Search contacts matching ICP criteria via Apollo.io free-tier API
- **ICP-to-filter mapping:** Automatic translation of ICP criteria to Apollo search filters
- **Fit scoring:** Each prospect scored against the ICP model with sub-score breakdown
- **Deduplication:** Same Apollo contact won't be stored twice per ICP
- **Results UI:** Prospect table with color-coded ICP fit badges (green/yellow/red)

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/dashboard/kpis` | GET | Top-line KPI metrics |
| `/api/subscribers` | GET | Subscriber profiles + distributions |
| `/api/churn` | GET | Churn predictions + risk distribution |
| `/api/segments` | GET | AI behavioral segments |
| `/api/recommendations` | GET | Upsell/retention recommendations |
| `/api/revenue-forecast` | GET | Historical + projected MRR |
| `/api/retention-actions` | GET | AI agent action log |
| `/api/icp/` | GET/POST | List or create ICP models |
| `/api/icp/{id}` | GET/PATCH | Get or update ICP model |
| `/api/icp/{id}/activate` | POST | Activate ICP model |
| `/api/icp/conversation` | POST | Claude-powered ICP extraction |
| `/api/prospects/search/{model_id}` | POST | Search Apollo + score + persist |
| `/api/prospects/{model_id}` | GET | List stored prospects (sorted by score) |

## Testing

```bash
cd backend
python -m pytest tests/ -v
```

Tests use in-memory SQLite — no database setup required. Apollo calls are mocked in prospect tests.

## Project Structure

```
backend/
  app/
    main.py              # FastAPI app + dashboard routes
    config.py            # Settings (env-based)
    database.py          # Async SQLAlchemy engine + session
    models/              # SQLAlchemy models (ICPModel, Prospect)
    schemas/             # Pydantic request/response schemas
    routes/              # ICP CRUD, prospect search
    services/            # Apollo client, scoring, ICP filter mapper
    sample_data.py       # Hardcoded demo data
    data_generators.py   # Dashboard aggregation helpers
  agents/                # Claude agent framework (ICP extraction)
  alembic/               # Database migrations
  tests/                 # Pytest async tests

frontend/
  index.html             # Single-page dashboard
  src/
    main.js              # App initialization
    components/          # Render functions (KPIs, charts, prospects)
    utils/api.js         # API client functions
    styles/main.css      # Dashboard + prospect styles
```
