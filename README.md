# Clinic Lead Generation AI Agent

An autonomous AI agent built with **LangChain + LangGraph** that collects, validates, and organises clinic leads across the UK, UAE, Pakistan, and Australia.

---

## Team Responsibilities

| Module | Owner | Files |
|--------|-------|-------|
| **Agent & Workflow** | @Aman Emøni | `app/agent/`, `app/graph/`, `main.py` |
| **Data Collection** | @~Saddia | `app/tools/google_maps.py`, `app/tools/web_search.py`, `app/tools/scraper.py` |
| **Data Processing** | @~Print On Demand | `app/tools/validator.py`, `app/services/extraction_service.py` |
| **Database & Output** | @~Abdullah Suleman | MongoDB integration, CSV/Excel/JSON export |

---

## Architecture

```
User Input (ClinicSearchRequest)
        │
        ▼
┌─────────────────────────────────────────────────────────────┐
│                    LangGraph Workflow                        │
│                                                             │
│  parse_request → plan_search → search_google_maps          │
│       → search_web → extract_leads → deduplicate           │
│       → validate_leads → check_quota ──(loop)──┐           │
│                               └──(done)──→ summarise       │
└─────────────────────────────────────────────────────────────┘
        │
        ▼
AgentResponse (leads + summary + errors)
```

---

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env .env.local
# Edit .env and fill in your API keys
```

Required keys:
- `OPENAI_API_KEY` — from [platform.openai.com](https://platform.openai.com)
- `GOOGLE_MAPS_API_KEY` — from [Google Cloud Console](https://console.cloud.google.com) (enable Places API)
- `TAVILY_API_KEY` — free tier at [tavily.com](https://tavily.com)

### 3. Run
```bash
# Default: 100 leads across all target cities
python main.py

# Specific locations and types
python main.py --locations London Dubai --types "Dental Clinic" "Skin Clinic" --max 50

# Filter by rating and automation status
python main.py --locations London --min-rating 4.0 --automation Manual

# Save results to JSON
python main.py --output outputs/leads.json

# Interactive chat mode
python main.py --interactive
```

---

## Target Locations

| Market | Cities |
|--------|--------|
| 🇬🇧 UK (Primary) | London, Manchester, Birmingham, Leeds, Bristol |
| 🇦🇪 UAE (Premium) | Dubai, Abu Dhabi, Sharjah |
| 🇵🇰 Pakistan | Islamabad, Rawalpindi, Lahore, Karachi |
| 🇦🇺 Australia | Sydney, Melbourne, Brisbane |

## Target Clinic Types

Dental · Aesthetic · Skin · Cosmetic · Physiotherapy · Hair Transplant · Eye · Private Medical · Wellness

---

## Lead Priority Logic

| Status | Description | Priority |
|--------|-------------|----------|
| **Manual** (rating ≥ 4.0) | No automation, high reviews | 🔴 High |
| **Manual** (any rating) | No automation | 🟡 Medium |
| **Semi Automated** (rating ≥ 4.0) | Has form, no full system | 🟡 Medium |
| **Automated** | Already has full system | 🟢 Low |

High-priority = best target for selling an AI appointment booking system.

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Google Sheet Columns (Final Output)

`Lead ID` · `Clinic Name` · `Clinic Type` · `Country` · `City` · `Address` · `Phone Number` · `Email` · `Website Available` · `Website URL` · `Doctor/Owner Name` · `Social Media Links` · `Appointment Method` · `Automation Status` · `Google Rating` · `Reviews Count` · `Lead Priority` · `Notes` · `Call Status` · `Follow-up Date`
