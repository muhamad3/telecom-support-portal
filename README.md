# TelcoAI Customer Support Portal

Enterprise GenAI-powered customer support portal for telecommunications. Features AI-driven ticket analysis with structured outputs, RAG-enhanced context retrieval, PII detection, and human-in-the-loop editing.

**Live demo:** [https://telecom-support-portal.netlify.app](https://telecom-support-portal.netlify.app)

---

## Project Structure

```
telecom-support-portal/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── main.py             # FastAPI application entry point
│   │   ├── config.py           # Configuration & environment variables
│   │   ├── models/
│   │   │   └── schemas.py      # Pydantic data models
│   │   ├── routers/
│   │   │   ├── support.py      # AI analysis & submit endpoints
│   │   │   └── dataset.py      # Dataset browsing endpoints
│   │   ├── services/
│   │   │   ├── ai_service.py   # Groq API orchestration
│   │   │   ├── rag_service.py  # TF-IDF retrieval
│   │   │   ├── pii_service.py  # PII detection & masking
│   │   │   └── data_service.py # Dataset loading & filtering
│   │   └── prompts/
│   │       └── templates.py    # System prompts & tool schemas
│   ├── Dataset.xlsx            # 1000-record telecom support dataset
│   ├── requirements.txt
│   └── .env.example
├── frontend_flutter/           # Flutter Web frontend (decoupled SPA)
│   ├── lib/
│   │   ├── main.dart
│   │   ├── models/models.dart
│   │   ├── services/api_service.dart
│   │   ├── screens/
│   │   │   ├── home_screen.dart
│   │   │   ├── analyze_screen.dart
│   │   │   ├── dataset_screen.dart
│   │   │   └── failure_cases_screen.dart
│   │   └── widgets/
│   │       ├── analysis_panel.dart
│   │       └── rag_context_widget.dart
│   └── web/
│       ├── index.html
│       └── netlify.toml
├── docs/
│   ├── system_design.md        # Architecture & design decisions
│   ├── system_design.pdf       # System design (PDF version)
│   └── api_overview.md         # API endpoint documentation
└── README.md
```

---

## Deployment

| Layer | Platform | URL |
|-------|----------|-----|
| Frontend | Netlify | [telecom-support-portal.netlify.app](https://telecom-support-portal.netlify.app) |
| Backend | Railway | [telecom-support-portal-production.up.railway.app](https://telecom-support-portal-production.up.railway.app) |

---

## Local Setup

### Prerequisites

- Python 3.11+
- Flutter 3.22+
- A Groq API key ([console.groq.com](https://console.groq.com))

### 1. Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate    # Linux / Mac
venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set GROQ_API_KEY

# Start the server
uvicorn app.main:app --reload --port 8000
```

API available at `http://localhost:8000`.  
Swagger docs at `http://localhost:8000/docs` (set `ENABLE_DOCS=True` in `.env`).

### 2. Frontend

```bash
cd frontend_flutter

# Install dependencies
flutter pub get

# Run in browser (development — connects to localhost:8000 by default)
flutter run -d chrome

# Build for production (point at deployed backend)
flutter build web --dart-define=API_URL=https://your-backend.railway.app
```

---

## Features

### AI Analysis Pipeline
Every customer support ticket goes through a full pipeline and returns:
1. **Issue Category** — Technical, Billing, Network, Account, Service, or General
2. **Draft Reply** — Professional, context-aware response editable by the agent
3. **Recommended Next Step** — Specific, actionable guidance
4. **Escalation Decision** — Yes/No with written justification
5. **Risk Level** — Low / Medium / High with reasoning

### RAG (Retrieval-Augmented Generation)
- 1,000-record telecom support dataset used as the knowledge base
- TF-IDF vectorisation with cosine similarity — top-3 records retrieved per query
- Retrieved context injected into the AI prompt before each analysis call

### PII Protection
- Regex-based detection: Iraqi phone numbers (all formats), email addresses, credit card numbers
- Masking applied before the message reaches the AI model
- Sanitised message returned alongside the analysis so agents can verify what the model received

### Human-in-the-Loop
- AI-generated draft replies rendered in an editable text area
- Agents modify the response before submission — AI output never goes directly to customers
- Agents can override escalation decisions and add internal notes

### Dataset Browser
- 1,000 historical telecom support records loaded from Dataset.xlsx
- Filterable by issue type, searchable by message content
- One-click loading of any record directly into the analysis form

### Prompt Injection Defence
- System prompt explicitly instructs the model to treat customer input as untrusted data
- Customer messages wrapped in `<customer_input>` XML tags to separate data from instructions
- Off-topic requests (jailbreaks, role-play, unrelated tasks) are handled gracefully without crashing

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/support/analyze` | Analyse a customer ticket with AI |
| POST | `/api/support/submit` | Submit agent-edited response |
| GET | `/api/dataset/records` | List dataset records (paginated, filterable) |
| GET | `/api/dataset/records/{id}` | Get a single dataset record |

Full details in [docs/api_overview.md](docs/api_overview.md).

---

## Documentation

- [System Design](docs/system_design.md) — Architecture, tech stack rationale, prompt engineering, PII strategy, scaling plan
- [System Design PDF](docs/system_design.pdf) — Formatted version of the above
- [API Overview](docs/api_overview.md) — Complete endpoint documentation with request/response examples

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **FastAPI** | Async-native for non-blocking LLM calls, automatic OpenAPI docs, first-class Pydantic support |
| **Forced tool-use** | Guarantees schema compliance — the model cannot return malformed output |
| **TF-IDF over vector DB** | Demonstrates the RAG pattern without requiring external infrastructure |
| **Flutter Web** | Fully decoupled SPA that talks to the backend via REST only; reflects real enterprise frontend/backend team separation |
| **PII masking before AI call** | Customer data is sanitised server-side before it reaches any third-party API |
