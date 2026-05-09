# API Documentation Overview

## Base URL

```
http://localhost:8000
```

Interactive API docs are available at:
- **Swagger UI**: `http://localhost:8000/docs`

---

## Endpoints

### System

#### `GET /health`
Health check endpoint.

**Response** `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

### Support (AI Analysis)

#### `POST /api/support/analyze`
Analyze a customer support ticket using AI. The endpoint performs PII detection, RAG retrieval, and structured AI analysis.

**Request Body**
```json
{
  "customer_message": "My internet has been dropping every 30 minutes for the past week and I am losing work because of it."
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `customer_message` | string | Yes | The customer's support message |

**Response** `200 OK`
```json
{
  "analysis": {
    "category": "Technical",
    "draft_reply": "Thank you for contacting us. I understand how frustrating...",
    "recommended_next_step": "Run a remote line diagnostic and escalate to NOC if packet loss exceeds 5%.",
    "escalation_decision": false,
    "escalation_reason": null,
    "risk_level": "Medium",
    "risk_justification": "Customer reports ongoing service disruption affecting their work. Churn risk is elevated.",
    "sentiment": null,
    "confidence_score": null
  },
  "sanitized_message": "My internet has been dropping every 30 minutes for the past week and I am losing work because of it.",
  "rag_context": [
    "Internet connection dropping intermittently — check for line noise and run a remote diagnostic..."
  ]
}
```

**Error Response** `502 Bad Gateway`
```json
{
  "detail": "AI service error: Connection timeout"
}
```

---

#### `POST /api/support/submit`
Submit an agent-edited response after reviewing and modifying the AI-generated draft.

**Request Body**
```json
{
  "edited_reply": "Thank you for contacting us. I sincerely apologize for the intermittent connectivity...",
  "agent_notes": "Customer is a remote worker — prioritize resolution",
  "approved_escalation": false
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `edited_reply` | string | Yes | The agent's final edited reply |
| `agent_notes` | string | No | Internal agent notes (not sent to customer) |
| `approved_escalation` | boolean | No | Override the AI escalation decision (null = keep AI decision) |

**Response** `200 OK`
```json
{
  "status": "submitted",
  "submitted_at": "2025-01-15T10:35:00Z",
  "edited_reply": "Thank you for contacting us. I sincerely apologize for the intermittent connectivity..."
}
```

---

### Dataset

#### `GET /api/dataset/records`
List customer support records from the dataset with filtering and pagination.

**Query Parameters**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 1 | Page number (1-indexed) |
| `page_size` | int | 10 | Records per page (1–100) |
| `issue_type` | string | null | Filter by type: Technical, Billing, Network, Account, Service, General |
| `search` | string | null | Free-text search in message content |

**Response** `200 OK`
```json
{
  "records": [
    {
      "id": 1,
      "issue_type": "Billing",
      "message": "I have been charged twice for my monthly plan this month...",
      "priority": "High"
    }
  ],
  "total": 1000,
  "page": 1,
  "page_size": 10
}
```


---

## Data Models

### AIAnalysis

| Field | Type | Description |
|-------|------|-------------|
| `category` | enum | Technical, Billing, Network, Account, Service, General |
| `draft_reply` | string | AI-generated professional reply |
| `recommended_next_step` | string | Actionable next step for the agent |
| `escalation_decision` | boolean | Whether to escalate the ticket |
| `escalation_reason` | string \| null | Reason for escalation, or null if no escalation |
| `risk_level` | enum | Low, Medium, High |
| `risk_justification` | string | Explanation of the risk assessment |
| `sentiment` | string \| null | Detected customer sentiment (optional) |
| `confidence_score` | float \| null | Model confidence 0.0–1.0 (optional) |

### Request/Response Flow

```
Customer Message
       │
       ▼
  PII Detection ──► Mask sensitive data (phone, email, credit card)
       │
       ▼
  RAG Retrieval ──► Fetch top-3 relevant records from Dataset.xlsx
       │
       ▼
  AI Analysis   ──► Groq API (forced tool-use for structured output)
       │
       ▼
  Response      ──► Structured JSON to frontend
       │
       ▼
  Agent Review  ──► Human-in-the-loop editing
       │
       ▼
  Submission    ──► Final approved response
```
