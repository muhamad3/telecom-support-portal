# System Design Document

## TelcoAI Customer Support Portal — Enterprise GenAI Prototype

---

## 1. Tech Stack Selection

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Backend Framework** | FastAPI (Python 3.11+) | Async-native, automatic OpenAPI/Swagger docs, Pydantic integration for structured data validation, high performance with uvicorn |
| **AI Provider** | Groq (LLaMA 3.3 70B) | Tool-use capability guarantees structured JSON output, strong instruction following, free tier with no credit card required |
| **RAG Retrieval** | scikit-learn TF-IDF + cosine similarity | Lightweight, no external vector DB dependency for prototype, demonstrates the RAG pattern clearly. Production would use a dedicated vector store |
| **Frontend** | Vanilla HTML/CSS/JavaScript | Zero build step, fully decoupled from backend via REST API, demonstrates clean architecture without framework overhead |
| **Data Validation** | Pydantic v2 | Enforces structured AI outputs, provides serialization/deserialization, auto-generates JSON Schema for OpenAPI docs |

### Why Not Streamlit/Gradio?

The architecture requirement explicitly calls for a decoupled frontend/backend reflecting enterprise environments. Streamlit and Gradio tightly couple UI and logic in a single Python process, which:

- Prevents independent scaling of frontend and backend
- Makes it impossible to swap the frontend framework
- Doesn't reflect real-world telecom enterprise architectures where frontend teams and backend teams operate independently

---

## 2. Architecture Overview

```
┌-----------------┐     REST API      ┌----------------------------------┐
│                  │  ◄--------------► │          FastAPI Backend         │
│  Frontend (SPA)  │                   │                                  │
│  HTML/CSS/JS     │                   │  ┌--------┐  ┌---------------┐  │
│                  │                   │  │ Router  │--│ PII Service   │  │
└-----------------┘                   │  │ Layer   │  └---------------┘  │
                                       │  │         │  ┌---------------┐  │
                                       │  │         │--│ RAG Service   │  │
                                       │  │         │  │ (TF-IDF)      │  │
                                       │  │         │  └---------------┘  │
                                       │  │         │  ┌---------------┐  │
                                       │  │         │--│ AI Service    │  │
                                       │  │         │  │ (Groq API)    │  │
                                       │  │         │  └---------------┘  │
                                       │  │         │  ┌---------------┐  │
                                       │  │         │--│ Data Service  │  │
                                       │  └--------┘  └---------------┘  │
                                       └----------------------------------┘
```

### Separation of Concerns

The backend follows a layered architecture with four distinct service modules:

1. **Router Layer** (`routers/`) — HTTP endpoint definitions, request validation, response formatting
2. **AI Service** (`services/ai_service.py`) — LLM orchestration, prompt management, structured output extraction
3. **RAG Service** (`services/rag_service.py`) — Knowledge base indexing and retrieval
4. **PII Service** (`services/pii_service.py`) — Personal data detection and masking
5. **Data Service** (`services/data_service.py`) — Dataset loading, filtering, pagination

Each service is independently testable and replaceable without affecting others.

---

## 3. Prompt Engineering Strategy

### Approach: Tool-Use Forced Structured Output

Rather than asking the model to output JSON in free-text (unreliable), we use **forced tool-use** with `tool_choice: {"type": "function", "function": {"name": "analyze_support_ticket"}}`. This forces the model to return a structured response matching our exact schema.

**Advantages:**
- 100% schema compliance — the model cannot return malformed output
- No regex/JSON parsing heuristics needed
- Pydantic validation on the output provides a second safety layer
- The tool schema serves as both the output format AND the model's instruction

### System Prompt Design

The system prompt establishes:
1. **Role**: Telecom customer support expert
2. **Behavioral constraints**: Never fabricate account details, acknowledge missing information
3. **Escalation criteria**: Specific thresholds (billing disputes over 10,000 IQD, multi-user outages, legal threats, repeated complaints)
4. **Regulatory awareness**: CMC (Communications and Media Commission of Iraq) compliance considerations
5. **Tone guidelines**: Professional, empathetic, solution-oriented

### RAG Integration

Before the AI analysis call, relevant knowledge base articles are retrieved using TF-IDF cosine similarity and injected into the user message as additional context. This gives the model access to:
- Standard operating procedures
- Fee explanations
- Troubleshooting workflows
- Escalation policies

---

## 4. PII Handling Strategy

### Current Implementation (Prototype)

The PII service operates at two stages:

1. **Input Masking**: Before the customer message reaches the AI model, PII is detected and masked:
   - Iraqi phone numbers (all formats) → `[PHONE_REDACTED]`
   - Email addresses → `[EMAIL_REDACTED]`
   - Credit card numbers → `[CREDIT_CARD_REDACTED]`

2. **Sanitized Message**: The response returns the `sanitized_message` (post-masking) alongside the AI analysis so agents can see what the model actually received.

### Production PII Recommendations

For a production deployment:

| Measure | Description |
|---------|-------------|
| **NER-based detection** | Supplement regex with a Named Entity Recognition model (e.g., Presidio, AWS Comprehend) for unstructured PII like names-in-context |
| **Output scanning** | Run PII detection on the AI-generated draft reply before displaying to agents |
| **Encryption at rest** | Encrypt all stored tickets and AI outputs using AES-256 |
| **Audit logging** | Log all PII access with agent ID, timestamp, and justification |
| **Data retention** | Auto-purge customer messages after case resolution (configurable retention period) |
| **CMC compliance** | Iraqi Communications and Media Commission regulations govern telecom customer data handling; legal review required before using third-party LLM APIs with customer data |
| **Anonymization pipeline** | Before using tickets for model fine-tuning or analytics, run through a full anonymization pipeline |

---

## 5. Latency and Cost Optimization at Scale

### Latency Reduction

| Strategy | Impact | Complexity |
|----------|--------|------------|
| **Semantic caching** | Cache AI responses in Redis keyed by TF-IDF vector; return cached result for similar queries above cosine similarity threshold, avoiding the API call entirely | Low |
| **Streaming responses** | Stream the AI response to the frontend via SSE so agents see the draft building in real-time | Medium |
| **RAG pre-computation** | Pre-compute embeddings for the knowledge base; use approximate nearest neighbors (FAISS/Annoy) instead of exact cosine similarity | Medium |
| **Response caching** | Cache AI responses for identical/near-identical tickets using semantic hashing | Medium |
| **Edge deployment** | Deploy the frontend via CDN; keep API servers in the same region as the AI provider | Low |

### Cost Reduction

| Strategy | Impact | Complexity |
|----------|--------|------------|
| **Model tiering** | Route simple tickets to a smaller model (LLaMA 3.1 8B); reserve the 70B model for complex or ambiguous tickets | Medium |
| **Prompt optimization** | Minimize token count in system prompts and RAG context; use concise knowledge base summaries | Low |
| **Batch processing** | For non-urgent tickets (email channel), batch process during off-peak hours to reduce peak load and cost | Medium |
| **Caching layer** | Implement semantic similarity caching — if a very similar ticket was recently analyzed, reuse the analysis | High |
| **Token budgeting** | Set max_tokens appropriately per request type; monitor and alert on token usage anomalies | Low |

### Scaling Architecture

For production at scale (10,000+ tickets/day):

```
                    ┌--------------┐
                    │  Load        │
                    │  Balancer    │
                    └------┬-------┘
                           │
              ┌------------┼------------┐
              │            │            │
        ┌-----┴-----┐ ┌---┴-----┐ ┌---┴-----┐
        │  API Pod 1 │ │ API Pod 2│ │ API Pod 3│
        └-----┬-----┘ └---┬-----┘ └---┬-----┘
              │            │            │
        ┌-----┴------------┴------------┴-----┐
        │          Message Queue (Redis)       │
        └-----------------┬-------------------┘
                          │
              ┌-----------┼-----------┐
              │           │           │
        ┌-----┴-----┐ ┌--┴------┐ ┌--┴------┐
        │ AI Worker 1│ │AI Worker2│ │AI Worker3│
        └-----------┘ └---------┘ └---------┘
```

- **Horizontal scaling**: Separate API servers from AI workers
- **Queue-based processing**: Decouple request intake from LLM calls
- **Auto-scaling**: Scale AI workers based on queue depth
- **Circuit breaker**: If the AI provider is down, queue requests and serve cached responses

---

## 6. Security Considerations

- **CORS**: Configured to allow only specific frontend origins
- **Input validation**: All inputs validated via Pydantic before processing
- **Rate limiting**: Should be added via middleware (e.g., slowapi) for production
- **API authentication**: Production should use JWT tokens with role-based access
- **Audit trail**: All AI analyses and agent submissions should be logged immutably
- **Content security**: AI outputs are treated as untrusted — the human-in-the-loop step prevents direct AI-to-customer communication
