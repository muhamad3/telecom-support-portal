# TelcoAI Customer Support Portal

Enterprise GenAI-powered customer support portal for telecommunications. Features AI-driven ticket analysis with structured outputs, RAG-enhanced context retrieval, PII detection, and human-in-the-loop editing.

## Project Structure

```
telecom-support-portal/
├-- backend/                    # FastAPI backend
│   ├-- app/
│   │   ├-- main.py            # FastAPI application entry point
│   │   ├-- config.py          # Configuration management
│   │   ├-- models/
│   │   │   └-- schemas.py     # Pydantic data models
│   │   ├-- routers/
│   │   │   ├-- support.py     # AI analysis & submit endpoints
│   │   │   └-- dataset.py     # Dataset browsing endpoints
│   │   ├-- services/
│   │   │   ├-- ai_service.py  # Groq API orchestration
│   │   │   ├-- rag_service.py # TF-IDF retrieval
│   │   │   ├-- pii_service.py # PII detection & masking
│   │   │   └-- data_service.py# Dataset loading & filtering
│   │   └-- prompts/
│   │       └-- templates.py   # System prompts & tool schemas
│   ├-- Dataset.xlsx           # 1000-record telecom support dataset
│   ├-- requirements.txt
│   └-- .env.example
├-- frontend_flutter/           # Decoupled Flutter Web frontend
│   ├-- lib/
│   │   ├-- main.dart
│   │   ├-- models/models.dart
│   │   ├-- services/api_service.dart
│   │   ├-- screens/
│   │   │   ├-- home_screen.dart
│   │   │   ├-- analyze_screen.dart
│   │   │   ├-- dataset_screen.dart
│   │   │   └-- failure_cases_screen.dart
│   │   └-- widgets/
│   │       ├-- analysis_panel.dart
│   │       └-- rag_context_widget.dart
│   └-- web/index.html
├-- docs/
│   ├-- system_design.md       # Architecture & design decisions
│   └-- api_overview.md        # API endpoint documentation
├-- SYSTEM_DESIGN.md           # Full system design document
└-- README.md
```

## Quick Start

### Prerequisites

- Python 3.11+
- A Groq API key ([console.groq.com](https://console.groq.com))

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate    # Linux/Mac
venv\Scripts\activate       # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# Start the server
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000` with:
- Swagger docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 2. Frontend Setup

```bash
cd frontend_flutter

# Install Flutter dependencies
flutter pub get

# Run in Chrome (development)
flutter run -d chrome --web-renderer html

# Or build for production
flutter build web
```

Open `http://localhost:PORT` shown in the terminal (Flutter assigns a random port in dev mode).

## Features

### AI Analysis Pipeline
For every customer support ticket, the system returns:
1. **Issue Category** — Technical, Billing, Network, Account, Service, or General
2. **Draft Reply** — Professional, context-aware response (editable by agent)
3. **Recommended Next Step** — Actionable guidance for the agent
4. **Escalation Decision** — Yes/No with justification
5. **Risk Level** — Low/Medium/High with reasoning

### RAG (Retrieval-Augmented Generation)
- 1000-record telecom support dataset (Dataset.xlsx) used as the knowledge base
- TF-IDF vectorization with cosine similarity retrieval (top-3 records per query)
- Relevant records are injected into the AI prompt for context-aware responses

### PII Protection
- Regex-based detection: Iraqi phone numbers (all formats), email addresses, credit card numbers
- Automatic masking before AI processing — original message never leaves the server
- Sanitized message shown alongside AI analysis for agent awareness

### Human-in-the-Loop
- AI-generated draft replies are displayed in an editable text area
- Agents can modify the response before submission
- Agents can override escalation decisions
- Agent notes field for internal documentation

### Dataset Integration
- 1000 telecom support records loaded from Dataset.xlsx
- Filterable by issue type (Technical, Billing, Network, Account, Service, General)
- Searchable by message content
- One-click loading from dataset into the analysis form

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/support/analyze` | Analyze a customer ticket with AI |
| POST | `/api/support/submit` | Submit agent-edited response |
| GET | `/api/dataset/records` | List dataset records (paginated, filterable) |
| GET | `/api/dataset/records/{id}` | Get single dataset record |

See [docs/api_overview.md](docs/api_overview.md) for full details.

## Documentation

- [System Design Document](docs/system_design.md) — Architecture, tech stack rationale, prompt engineering strategy, PII handling, scaling plan
- [Failure Cases](docs/failure_cases.md) — 5 GenAI failure scenarios with root causes, business risks, and guardrails
- [API Overview](docs/api_overview.md) — Complete endpoint documentation with request/response examples

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **FastAPI over Flask/Django** | Async-native for non-blocking LLM calls, automatic OpenAPI docs, first-class Pydantic support |
| **Forced tool-use for structured output** | Guarantees schema compliance vs. fragile JSON parsing from free-text |
| **TF-IDF over vector DB** | Appropriate for prototype scale; demonstrates RAG pattern without heavy infrastructure |
| **Flutter Web over Streamlit/Gradio** | Fully decoupled frontend that talks to the backend only via REST API; single codebase compiles to web, Android, iOS, and desktop |
| **Three-stage PII pipeline** | Defense in depth: input masking, clean RAG data, output scanning |
