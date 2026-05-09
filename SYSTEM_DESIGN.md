# System Design Document
## TelcoAI — Enterprise GenAI Customer Support Portal

---

## Overview

This document explains the design decisions behind the TelcoAI support portal. The goal was to build something that works end-to-end, handles real telecom support scenarios, and is structured in a way that could actually scale — not just a demo that falls apart under any real load.

The system takes a customer support message, detects and masks any sensitive information, retrieves relevant context from a dataset, sends everything to an AI model, and returns a structured analysis back to the agent. The agent can then edit the draft reply and submit it.

---

## 1. Tech Stack and Why

### Backend — FastAPI

I chose FastAPI over Flask or Django for one specific reason: it is async by default. When you call an LLM API, you are waiting anywhere from 2 to 5 seconds for a response. With a synchronous framework, your entire server is frozen during that wait — nobody else can get a response. FastAPI uses Python's asyncio under the hood, so while one request is waiting for the AI, the server is still processing other requests.

The other practical benefit is that FastAPI generates Swagger documentation automatically from the code. You don't write a separate API spec — the Pydantic models you define for validation are the same models that appear in the docs at `/docs`. That's one less thing to maintain.

### AI — Groq + LLaMA 3.3 70B

The project uses Groq as the inference provider running Meta's LLaMA 3.3 70B model. The main reason for choosing Groq is that it offers a free tier with no credit card required, which matters for a prototype. LLaMA 3.3 70B is a capable model that handles structured output tasks well.

Groq's API is OpenAI-compatible, so if we need to switch to a different provider later — Azure OpenAI, a self-hosted model, or any other compatible endpoint — it is a one-line change in the config file. The API key variable is named `GROQ_API_KEY` in the settings for this reason, so the swap is even simpler.

### Structured Output — Pydantic + Forced Tool-Use

Getting consistent, parseable output from an LLM is harder than it sounds. Asking the model to "respond in JSON" is unreliable — it might add explanation text, use a slightly different field name, or forget a required field. 

The solution here is forced tool-use (function calling). We define a tool schema that describes every field we need, and we set `tool_choice` to force the model to call that specific tool on every request. The model has no choice but to fill in the schema exactly. Then we validate the output with Pydantic as a second layer.

On top of that, Pydantic validates every incoming request as well. If the frontend sends malformed data, FastAPI rejects it before any business logic runs.

### RAG — scikit-learn TF-IDF

For the retrieval layer, I used TF-IDF vectorization and cosine similarity from scikit-learn rather than a vector database. The dataset has 1000 records. For that size, TF-IDF runs in memory in a few milliseconds and produces good results.

The alternative would be something like Pinecone or Weaviate with dense embeddings, which would be better at understanding synonyms and semantic similarity. But that adds an external dependency, API costs, and setup complexity. For a prototype with 1000 records, TF-IDF is the right call. The architecture makes it easy to swap later — the RAG service is isolated in its own module.

### Data Layer — pandas + openpyxl

The dataset comes as an Excel file. pandas reads it in one line and converts it to a list of Python strings. The data is loaded once at startup and cached in memory for the rest of the server's lifetime. There is no database — the dataset is small enough that in-memory storage is both simpler and faster than any DB query.

### Frontend — Flutter Web

Flutter was chosen because it produces a fully decoupled frontend that talks to the backend only through the REST API. This satisfies the architecture requirement directly — there is no tight coupling between the UI and the server logic.

A single Flutter codebase also compiles to web, Android, iOS, and desktop. For a telecom support tool that might need to run on agent workstations and mobile devices, that flexibility is useful without having to maintain multiple codebases.

The alternative of using Streamlit or Gradio was explicitly ruled out in the brief, and rightly so — those tools run the UI server-side as Python, which means they are not separable from the backend. That is not a real enterprise architecture.

---

## 2. Prompt Engineering Strategy

The entire prompting strategy is built around one rule: never trust free-text AI output in production code. Every technique below enforces structure.

### Forced Tool-Use

As mentioned above, we define a JSON Schema for the output we want and force the model to call a specific tool with that schema. This gives us two guarantees:

1. The Groq API enforces the schema at the API level before the response reaches our code
2. Pydantic validates the parsed JSON at the application level before it reaches the router

If either check fails, the server returns a 502 error to the frontend with a clear message. The agent sees an error rather than garbage data.

### Enum Constraints on Categorical Fields

Fields like `category` and `risk_level` use JSON Schema enum constraints. The model can only return one of the explicitly listed values:

```json
"category": {
  "type": "string",
  "enum": ["Technical", "Billing", "Network", "Account", "Service", "General"]
}
```

Without this, the model might return "tech issue" or "billing problem" or "NETWORK" — all different strings that mean the same thing but would break frontend logic that checks the value.

### Nullable Fields

The `escalation_reason` field is typed as `["string", "null"]` rather than just `"string"`. This is important — when there is no escalation, the correct value is `null`, not an empty string or a fabricated explanation. Without this, the model either invents a reason when there is none, or the API returns a validation error.

### System Prompt Design

The system prompt is kept short and specific. It establishes the AI's role as an Iraqi telecom support assistant, sets the currency context (IQD only, no dollars), and lists hard rules:

- Never fabricate account details, balances, or plan specifics
- Escalate billing disputes over 10,000 IQD
- Escalate for legal threats, safety concerns, or repeated complaints
- Follow CMC (Communications and Media Commission of Iraq) compliance requirements

Keeping the rules explicit and numbered means the model applies them consistently. Vague instructions like "be careful with money" produce inconsistent behavior.

### RAG Context Injection

The user message includes a labelled section of relevant records retrieved from the dataset:

```
Relevant knowledge base articles for context:

[retrieved text 1]

[retrieved text 2]
```

This gives the AI reference material specific to the query rather than relying entirely on its training data. The label matters — without it, the model might confuse the context with part of the customer's message.

---

## 3. PII Handling in Production

### What We Do Now

Before any customer message reaches the Groq API, it goes through `pii_service.mask_pii()`. This function scans the message with compiled regular expressions and replaces matches with placeholder text:

| PII Type | Replaced With |
|---|---|
| Iraqi phone numbers (all formats) | `[PHONE_REDACTED]` |
| Email addresses | `[EMAIL_REDACTED]` |
| Credit card numbers | `[CREDIT_CARD_REDACTED]` |

The masking happens server-side. The original message never leaves the server. The Groq API only ever sees the sanitized version.

### What Would Need to Change for Production

**NER-based detection on top of regex.** Regex catches structured PII well — phone numbers, emails, card numbers. It misses unstructured PII like a person's name embedded in a sentence ("I spoke to Ahmed yesterday about my account"). Microsoft's Presidio library adds Named Entity Recognition on top of regex and would catch these cases. It is not in the prototype because it requires downloading a 750MB spaCy language model, which is too heavy for a prototype setup.

**Output scanning.** The current pipeline masks the input but does not scan the AI's output. An LLM can echo PII back in the draft reply, or it can hallucinate a plausible-looking phone number. Before the draft reply is shown to the agent, it should go through the same masking pipeline.

**Audit logging.** Log that PII was detected and what types were found — but never log the actual content. Something like: `"timestamp": "...", "pii_types_detected": ["phone"], "masked": true`. This creates a compliance trail without creating a new PII data store.

**Encryption for anything stored.** If messages are stored for audit purposes, they need AES-256 encryption with keys managed separately (AWS KMS, HashiCorp Vault). The application should never retain plaintext beyond the request lifecycle.

**CMC compliance.** The Iraqi Communications and Media Commission has regulations around customer data handling for telecom providers. Any production deployment would need a legal review to confirm that using a third-party LLM API (even with PII masking) satisfies those requirements. If it does not, the alternative is running a self-hosted model so customer data never leaves the company's infrastructure.

---

## 4. Reducing Latency and Costs at Scale

The bottleneck in this system is the LLM API call. Everything else — PII masking, TF-IDF retrieval, Pydantic validation — runs in under 10ms. The AI call takes 2–5 seconds. So every optimization below targets that one bottleneck.

### Semantic Caching (Biggest Win)

Telecom support tickets are highly repetitive. The same five or six issue types come up over and over — "my internet is slow", "I was charged incorrectly", "no signal in my area". For any two messages that are semantically similar, the AI response will be nearly identical.

The fix is to cache responses in Redis, keyed by the TF-IDF vector of the message. On each new request, compute cosine similarity between the incoming query vector and all cached query vectors. If the best match scores above 0.92, return the cached response directly — no API call at all.

This would likely handle 60–70% of tickets without touching the AI, which reduces both latency (cached response in under 10ms) and cost (zero tokens billed for cache hits).

### Model Tiering

Not every ticket needs a 70B parameter model. A customer asking "how do I check my balance?" does not need the same model as a customer writing a complex complaint about service disruption affecting their business.

Route simple, high-confidence queries to a smaller model (LLaMA 3.1 8B runs about 10x faster and costs roughly 10x less per token). Use the 70B model for complex or ambiguous tickets. A lightweight keyword classifier can handle the routing decision.

### Streaming

Right now the agent waits for the entire response before seeing anything. With response streaming, the draft reply appears word by word as the model generates it. The total time is the same, but the perceived latency drops from "3-5 seconds of blank screen" to "words appearing within half a second". This is a significant UX improvement with no infrastructure cost.

### Pre-warming the RAG Index

The TF-IDF index is currently built on the first request after server startup (lazy loading). For a production server that restarts after deploys, the first request after each deploy takes an extra second. Fix this by loading the index during FastAPI's startup event so it is ready before the first request arrives.

### Horizontal Scaling

FastAPI is stateless — no session data is stored in the server process. Multiple instances can run behind a load balancer (nginx, AWS ALB) without any coordination. The TF-IDF index is read-only and small enough to load per-instance. Scaling from 1 to 10 instances multiplies throughput by 10 with no code changes.

### CDN for the Frontend

The Flutter web build is static HTML, JavaScript, and assets. It does not change between requests. Serving it from a CDN (CloudFront, Cloudflare) means every agent's browser loads the frontend from a server geographically close to them, and it is never a load on the FastAPI server at all.

---

## Final Notes

The current prototype covers the full end-to-end flow and all five required AI outputs. The architecture is structured so that each component — RAG, PII, AI service, routing — can be improved or replaced independently without touching the rest of the system. That separation of concerns is what makes the latency and cost improvements above practical to implement one at a time rather than requiring a full rewrite.

---

*Prepared for the Enterprise GenAI Customer Support Portal assessment submission.*
