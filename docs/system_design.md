# System Design Document

## TelcoAI Customer Support Portal

---

## 1. Tech Stack Selection

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Backend** | FastAPI (Python 3.11+) | Async-native, automatic OpenAPI/Swagger docs, tight Pydantic integration. Right balance between development speed and production-readiness. |
| **AI Provider** | Groq — LLaMA 3.3 70B | Forced tool-use guarantees structured JSON output — the model cannot return malformed data. No regex fallbacks or output parsing heuristics are needed. |
| **RAG** | scikit-learn TF-IDF + cosine similarity | Lightweight retrieval with no external vector database dependency. Demonstrates the RAG pattern clearly. A production system would use FAISS or a dedicated vector store. |
| **Frontend** | Flutter Web | Decoupled SPA communicating over REST. Compiles to static files, enabling independent deployment and clear separation between frontend and backend teams. |
| **Validation** | Pydantic v2 | Enforces AI output structure, auto-generates JSON Schema for the OpenAPI docs, and provides a second validation layer on top of the model's tool-use guarantee. |

### Why not Streamlit or Gradio?

Both tools are genuinely useful for rapid prototyping, but they tightly couple UI rendering and application logic inside a single Python process. That does not reflect how enterprise telecom systems are built — frontend and backend teams deploy independently, scale independently, and own separate codebases. A decoupled SPA makes all of that possible and is a more accurate demonstration of production architecture.

---

## 2. Architecture Overview

```
  Flutter Web (SPA)                     FastAPI Backend
  +----------------------+   REST      +--------------------------------+
  |  Analyse Screen      | <-------->  |  Router Layer                  |
  |  Dataset Browser     |             |    /api/support/analyse         |
  |  Failure Cases       |             |    /api/dataset/records         |
  |  Analytics Dashboard |             |                                 |
  +----------------------+             |  +------------+ +------------+  |
                                       |  | AI Service | | PII Service|  |
                                       |  | (Groq API) | |(regex mask)|  |
                                       |  +------------+ +------------+  |
                                       |  +------------+ +------------+  |
                                       |  | RAG Service| | Data Svc   |  |
                                       |  | (TF-IDF)   | | (xlsx)     |  |
                                       |  +------------+ +------------+  |
                                       +--------------------------------+
```

### Service responsibilities

- **Router layer** — HTTP endpoint definitions, request validation via Pydantic, response serialisation. Intentionally thin — no business logic.
- **AI Service** — LLM orchestration. Builds the prompt, calls Groq with forced tool-use, and extracts the structured response.
- **RAG Service** — Indexes the knowledge base on startup using TF-IDF, then retrieves the top-k most relevant articles per ticket before the AI call.
- **PII Service** — Regex-based detection and masking of Iraqi phone numbers, email addresses, and credit card numbers before any data reaches the LLM.
- **Data Service** — Loads the historical dataset from the Excel file, supports filtering, sorting, and pagination for the dataset browser.

---

## 3. Prompt Engineering Strategy

### Forced tool-use for guaranteed structured output

The most important prompt engineering decision in this project was choosing forced tool-use over asking the model to produce JSON in free text. With free-text JSON prompting the model occasionally adds explanation text before the JSON block, uses slightly different key names, or omits optional fields — all of which break downstream parsing. With forced tool-use the model has no choice but to populate exactly the schema defined. Pydantic validation on the output provides a second safety layer.

**Implementation:** `tool_choice = {"type": "function", "function": {"name": "analyze_support_ticket"}}` — the model cannot respond in free text.

### System prompt structure

The system prompt establishes five things, in order of priority:

1. **Role framing** — telecom customer support specialist with knowledge of Iraqi telecom regulations and CMC guidelines.
2. **Hard behavioural constraints** — never fabricate account details, always acknowledge when information is missing.
3. **Escalation thresholds** — billing disputes over 10,000 IQD, multi-user outages, legal threats, or repeated unresolved complaints trigger human escalation.
4. **Regulatory awareness** — CMC (Communications and Media Commission of Iraq) compliance for data handling and customer communication.
5. **Tone guidance** — professional, empathetic, solution-oriented; no corporate jargon.

### Prompt injection defence

Customer messages are untrusted external input. Two layers of protection are in place:

- **System prompt security section** — explicitly instructs the model to ignore any instructions embedded in customer input (jailbreak patterns, persona swaps, off-topic requests). If detected, the model returns a polite redirection rather than complying.
- **XML tag framing** — the customer message is wrapped in `<customer_input>` tags in the user message, clearly separating untrusted data from system instructions.

### RAG context injection

Before each AI call, the RAG service retrieves the three most relevant knowledge base articles using TF-IDF cosine similarity and injects them into the user message. This gives the model access to current fee tables, troubleshooting workflows, and escalation policies without bloating the system prompt with static content. The knowledge base can be updated independently of the model or the prompt.

---

## 4. PII Handling

### Two-stage masking

| Stage | What happens |
|-------|-------------|
| **1 — Input masking** | The customer message passes through the PII service before reaching the AI model. Iraqi phone numbers (all formats), email addresses, and credit card numbers are replaced with labelled placeholders: `[PHONE_REDACTED]`, `[EMAIL_REDACTED]`, `[CREDIT_CARD_REDACTED]`. |
| **2 — Sanitised message in response** | The API response includes the `sanitized_message` field alongside the AI analysis so support agents can verify exactly what the model received and confirm sensitive data was handled correctly. |

### Production recommendations

| Measure | Description |
|---------|-------------|
| **NER-based detection** | Supplement regex with a Named Entity Recognition model (Presidio, spaCy NER, or AWS Comprehend) to catch names, addresses, and other context-dependent PII that regex cannot reliably identify. |
| **Output scanning** | Run PII detection on the AI-generated draft reply before it reaches the agent — the model may inadvertently reconstruct PII from context. |
| **Encryption at rest** | All stored tickets and AI outputs should be encrypted using AES-256. Customer messages must not persist in plaintext anywhere in the pipeline. |
| **Audit logging** | Log every PII access event with agent ID, timestamp, and business justification. Required for CMC regulatory compliance. |
| **Data retention policy** | Auto-purge customer messages after case resolution. Retention period to be defined by the legal team based on CMC requirements. |
| **Anonymisation pipeline** | Before using historical tickets for model fine-tuning or analytics, run the full dataset through an anonymisation pipeline. |

> **CMC note:** Iraqi Communications and Media Commission regulations govern how telecom providers handle customer data. Using a third-party LLM API with customer messages requires explicit legal review and possibly customer consent. The masking layer reduces — but does not eliminate — this risk.

---

## 5. Latency & Cost Optimisation at Scale

The single-instance architecture is appropriate for this stage. Below are the changes that would be prioritised as usage grows.

### Latency reduction

| Strategy | Expected impact | Effort |
|----------|----------------|--------|
| **Semantic response caching** | Cache AI responses in Redis keyed by a hash of the TF-IDF vector. Near-identical tickets return instantly, eliminating 30–40% of LLM calls. | Medium |
| **Streaming responses** | Stream the AI reply to the frontend via SSE so agents see the draft building in real time. Perceived latency drops significantly even if total generation time is unchanged. | Medium |
| **RAG with FAISS** | Pre-compute embeddings for the knowledge base and use FAISS approximate nearest-neighbour search instead of recomputing TF-IDF on every request. | Medium |
| **Edge CDN for frontend** | Serve the static frontend from a CDN and co-locate the API server in the same region as the LLM provider to minimise round-trip latency. | Low |

### Cost reduction

| Strategy | Expected impact | Effort |
|----------|----------------|--------|
| **Model tiering** | Route straightforward tickets to a smaller model. Reserve the 70B model for complex or ambiguous tickets. Could reduce token costs by 50–60%. | Medium |
| **Prompt compression** | The current system prompt and RAG context can be made more concise without losing instruction quality. Low effort with immediate impact on cost per call. | Low |
| **Batch processing** | For non-urgent tickets received via email or web form, batch them and process during off-peak hours to reduce peak load. | Medium |
| **Token budgeting** | Set `max_tokens` per request type. Add monitoring and alerting on token usage anomalies to catch runaway prompts early. | Low |

### Scaling architecture (high volume)

```
                    +---------------+
                    |  Load Balancer |
                    +-------+-------+
                            |
           +----------------+-----------------+
           |                |                 |
    +------+------+  +------+------+  +-------+-----+
    |  API Pod 1  |  |  API Pod 2  |  |  API Pod 3  |
    +------+------+  +------+------+  +-------+-----+
           |                |                 |
    +------+-----------------+-----------------+------+
    |              Message Queue (Redis)              |
    +-------------------------+------------------------+
                              |
          +-------------------+------------------+
          |                   |                  |
   +------+------+   +--------+------+   +-------+-----+
   |  AI Worker 1|   |  AI Worker 2  |   |  AI Worker 3|
   +-------------+   +---------------+   +-------------+
```

- API pods handle intake and PII masking — CPU-light and horizontally scalable.
- The message queue decouples request intake from LLM calls, preventing thundering-herd overload.
- AI workers scale based on queue depth using auto-scale rules.
- Circuit breaker pattern: if the LLM provider is unavailable, queue requests and serve cached responses rather than returning errors.

---

## 6. Security

| Control | Current status | Production requirement |
|---------|---------------|----------------------|
| **HTTPS** | Enforced on both Netlify (frontend) and Railway (backend) | Same — already correct. |
| **CORS** | Locked to `https://telecom-support-portal.netlify.app` | Same, with a review process as new frontend domains are added. |
| **Input validation** | All inputs validated via Pydantic before processing. | Same — already production-grade. |
| **Prompt injection defence** | Implemented — system prompt hardening and XML tag message framing. | Same, with ongoing red-team testing as the model is updated. |
| **API docs** | Intentionally enabled on the demo deployment so reviewers can inspect the API at `/docs` and `/redoc`. Will be disabled before any production release. | Leave `ENABLE_DOCS` unset — `/docs`, `/redoc`, and `/openapi.json` return 404. |
| **Error messages** | Sanitised — internal details and raw LLM output never returned to the frontend. | Same — already correct. |
| **Rate limiting** | Not implemented. | Add via slowapi middleware with per-IP and per-agent-role limits. |
| **Authentication** | Not implemented — open API for demonstration purposes. | JWT tokens with role-based access control: agent, supervisor, admin. |
| **Audit trail** | Not implemented. | All AI analyses and agent edits logged immutably with timestamp and user ID. |
| **Secrets management** | Environment variables via Railway and `.env` locally. | Secrets vault with restricted access and rotation policy. |
| **Human-in-the-loop** | Implemented — agents review and edit every response before submission. | Same — this is a hard architectural requirement, not optional. |

> **Human-in-the-loop is a hard architectural requirement.** AI-generated draft responses never reach the customer directly. Every response goes through a support agent review step before submission. This is the primary safeguard against hallucinated account details, incorrect fee information, or inappropriate tone reaching customers.
