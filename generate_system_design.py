"""
Generates: TelcoAI System Design Document.pdf
Run from the project root: venv/Scripts/python generate_system_design.py
"""

from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether,
)

OUTPUT = "TelcoAI System Design Document.pdf"

# ── Colours ───────────────────────────────────────────────────────────────────
BLUE        = colors.HexColor("#0066CC")
BLUE_LIGHT  = colors.HexColor("#E6F0FF")
BLUE_DARK   = colors.HexColor("#004D99")
GREY_BG     = colors.HexColor("#F3F4F6")
GREY_TEXT   = colors.HexColor("#64748B")
GREEN       = colors.HexColor("#0D9668")
GREEN_LIGHT = colors.HexColor("#ECFDF5")
ORANGE      = colors.HexColor("#D97706")
ORANGE_LT   = colors.HexColor("#FFFBEB")
RED         = colors.HexColor("#DC2626")
RED_LIGHT   = colors.HexColor("#FEF2F2")
BLACK       = colors.HexColor("#1E293B")
WHITE       = colors.white
BORDER      = colors.HexColor("#E2E8F0")

W, H = A4


def sty(name, **kw):
    return ParagraphStyle(name, **kw)


S = {
    "cover_title": sty("ct", fontName="Helvetica-Bold", fontSize=30,
        textColor=WHITE, leading=36, spaceAfter=6, alignment=TA_CENTER),
    "cover_sub": sty("cs", fontName="Helvetica", fontSize=13,
        textColor=colors.HexColor("#B3D4FF"), leading=18, alignment=TA_CENTER),
    "cover_meta": sty("cm", fontName="Helvetica", fontSize=10,
        textColor=colors.HexColor("#7CB8FF"), leading=14, alignment=TA_CENTER),
    "h1": sty("h1", fontName="Helvetica-Bold", fontSize=18, textColor=BLUE,
        spaceBefore=18, spaceAfter=8, leading=22),
    "h2": sty("h2", fontName="Helvetica-Bold", fontSize=13, textColor=BLACK,
        spaceBefore=14, spaceAfter=5, leading=17),
    "h3": sty("h3", fontName="Helvetica-Bold", fontSize=11, textColor=BLUE_DARK,
        spaceBefore=10, spaceAfter=4, leading=14),
    "body": sty("body", fontName="Helvetica", fontSize=10, textColor=BLACK,
        leading=15, spaceAfter=6, alignment=TA_JUSTIFY),
    "bullet": sty("bullet", fontName="Helvetica", fontSize=10, textColor=BLACK,
        leading=14, spaceAfter=3, leftIndent=16),
    "note": sty("note", fontName="Helvetica-Oblique", fontSize=9,
        textColor=GREY_TEXT, leading=13, spaceAfter=4, leftIndent=8),
    "toc": sty("toc", fontName="Helvetica", fontSize=11, textColor=BLACK,
        leading=18, leftIndent=0),
    "code_inline": sty("ci", fontName="Courier", fontSize=9,
        textColor=BLUE_DARK, leading=13),
}


def P(text, s="body"):
    return Paragraph(text, S[s])


def SP(n=6):
    return Spacer(1, n)


def HR():
    return HRFlowable(width="100%", thickness=1, color=BORDER,
                      spaceAfter=8, spaceBefore=4)


def info_box(title, lines, bg=BLUE_LIGHT, border=BLUE):
    title_sty = ParagraphStyle("ibt", fontName="Helvetica-Bold",
                               fontSize=10, textColor=border, leading=14)
    body_sty = ParagraphStyle("ibb", fontName="Helvetica",
                              fontSize=9.5, textColor=BLACK, leading=14)
    data = [[Paragraph(title, title_sty)]]
    for line in lines:
        data.append([Paragraph(line, body_sty)])
    t = Table(data, colWidths=[W - 4 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), bg),
        ("BACKGROUND",    (0, 1), (-1, -1), colors.HexColor("#F8FAFC")),
        ("BOX",           (0, 0), (-1, -1), 1.5, border),
        ("LINEBELOW",     (0, 0), (-1, 0), 1, border),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
    ]))
    return t


def two_col(rows, header=None):
    lbl = ParagraphStyle("tl", fontName="Helvetica-Bold",
                         fontSize=9, textColor=BLACK, leading=13)
    val = ParagraphStyle("tv", fontName="Helvetica",
                         fontSize=9, textColor=BLACK, leading=13)
    hdr = ParagraphStyle("th", fontName="Helvetica-Bold",
                         fontSize=9, textColor=WHITE, leading=13)
    data = []
    if header:
        data.append([Paragraph(header[0], hdr), Paragraph(header[1], hdr)])
    for left, right in rows:
        data.append([Paragraph(left, lbl), Paragraph(right, val)])
    col_w = W - 4 * cm
    t = Table(data, colWidths=[col_w * 0.28, col_w * 0.72])
    cmds = [
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [GREY_BG, WHITE]),
        ("BOX",   (0, 0), (-1, -1), 0.8, BORDER),
        ("GRID",  (0, 0), (-1, -1), 0.5, BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]
    if header:
        cmds += [
            ("BACKGROUND",     (0, 0), (-1, 0), BLUE),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [GREY_BG, WHITE]),
        ]
    t.setStyle(TableStyle(cmds))
    return t


def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BLUE)
    canvas.rect(0, H - 1.1 * cm, W, 1.1 * cm, fill=1, stroke=0)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(WHITE)
    canvas.drawString(2 * cm, H - 0.72 * cm, "TelcoAI Support Portal")
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(W - 2 * cm, H - 0.72 * cm, "System Design Document")
    canvas.setFillColor(GREY_BG)
    canvas.rect(0, 0, W, 0.9 * cm, fill=1, stroke=0)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY_TEXT)
    canvas.drawString(2 * cm, 0.32 * cm, f"Confidential  ·  {date.today().year}")
    canvas.drawRightString(W - 2 * cm, 0.32 * cm, f"Page {doc.page}")
    canvas.restoreState()


def on_cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(BLUE_DARK)
    canvas.rect(0, 0, W, H, fill=1, stroke=0)
    canvas.setFillColor(BLUE)
    canvas.rect(0, H * 0.38, W, H * 0.62, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#FFFFFF18"))
    canvas.circle(W - 3 * cm, H - 3 * cm, 5 * cm, fill=1, stroke=0)
    canvas.circle(3 * cm, 4 * cm, 3.5 * cm, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#FFFFFF10"))
    canvas.circle(W * 0.5, H * 0.45, 8 * cm, fill=1, stroke=0)
    canvas.restoreState()


doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4,
    leftMargin=2 * cm, rightMargin=2 * cm,
    topMargin=1.8 * cm, bottomMargin=1.5 * cm,
    title="TelcoAI System Design Document",
    author="TelcoAI",
)
story = []

# ════════════════════════════════════════════════════════════════════════════
# COVER
# ════════════════════════════════════════════════════════════════════════════
story += [
    SP(5 * cm),
    P("TelcoAI Support Portal", "cover_title"),
    SP(4),
    P("System Design Document", "cover_sub"),
    SP(3),
    P("Enterprise GenAI Customer Support Portal<br/>"
      "for Telecommunications", "cover_sub"),
    SP(3.5 * cm),
    P(f"Version 1.0  ·  {date.today().strftime('%B %Y')}", "cover_meta"),
    SP(2),
    P("FastAPI  ·  Groq AI  ·  Pydantic  ·  scikit-learn  ·  Flutter Web",
      "cover_meta"),
    PageBreak(),
]

# ════════════════════════════════════════════════════════════════════════════
# TABLE OF CONTENTS
# ════════════════════════════════════════════════════════════════════════════
story += [P("Contents", "h1"), HR()]
for entry in [
    "1.  Tech Stack &amp; Why It Was Selected",
    "2.  Prompt Engineering Strategy",
    "3.  PII Handling in a Production Environment",
    "4.  Reducing Latency and Costs at Scale",
]:
    story.append(P(f"<b>{entry}</b>", "toc"))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# 1. TECH STACK
# ════════════════════════════════════════════════════════════════════════════
story += [P("1. Tech Stack &amp; Why It Was Selected", "h1"), HR()]
story.append(P(
    "Every technology in this stack was chosen for a specific reason. The guiding "
    "principle was: <b>use the simplest tool that correctly solves the problem</b>. "
    "Complexity was added only where the requirement demanded it.",
    "body"))
story.append(SP(8))

story.append(P("Backend", "h2"))
story.append(two_col([
    ("FastAPI",
     "Chosen as the API framework because it is async-native — meaning it can handle "
     "multiple concurrent LLM requests without blocking. A synchronous framework "
     "(Flask, Django) would stall the entire server for 2–5 seconds on every AI call. "
     "FastAPI also generates Swagger documentation at /docs automatically from the "
     "Pydantic models, with zero additional code."),
    ("Groq + LLaMA 3.3 70B",
     "Groq provides free-tier LLM inference with sub-second token generation. "
     "LLaMA 3.3 70B is a large open-weight model that performs at GPT-4 class on "
     "reasoning and structured output tasks. The Groq client is OpenAI-compatible, "
     "meaning the project can switch to any OpenAI-compatible provider (Azure OpenAI, "
     "self-hosted Ollama, or any other compatible endpoint) by changing one line in config.py."),
    ("Pydantic v2",
     "Used for two purposes simultaneously: (1) request validation — invalid inputs "
     "are rejected before any business logic runs, and (2) response serialisation — "
     "Python objects are converted to JSON automatically. The AIAnalysis model also "
     "acts as a second validation layer on top of the tool-use schema, ensuring the "
     "AI output is structurally correct before it reaches the frontend."),
    ("scikit-learn\n(TF-IDF + cosine)",
     "Provides the RAG retrieval layer. TF-IDF vectorisation and cosine similarity "
     "are fast, deterministic, and require no external service. The alternative — "
     "dense vector embeddings with a vector database (Pinecone, Weaviate) — would "
     "require network calls, API keys, and cost money per query. For a 1000-record "
     "dataset, TF-IDF runs in under 5ms in-memory and produces high-quality results."),
    ("pandas + openpyxl",
     "pandas reads the Dataset.xlsx file in a single line and converts it to a "
     "Python list. openpyxl is the Excel engine pandas uses internally. These are "
     "the industry standard for Excel ingestion in Python. The data is loaded once "
     "at startup and cached in memory — no repeated file I/O on requests."),
], header=["Technology", "Why it was chosen"]))
story.append(SP(10))

story.append(P("Frontend", "h2"))
story.append(two_col([
    ("Flutter Web",
     "Flutter produces a fully decoupled frontend that communicates with the backend "
     "exclusively through REST API calls. This satisfies the assessment requirement "
     "for a 'decoupled architecture that reflects a real-world enterprise environment'. "
     "A single Flutter codebase also produces iOS, Android, and desktop builds without "
     "code changes — relevant for a telecom company deploying support tools across "
     "agent devices."),
    ("Why NOT Streamlit\nor Gradio",
     "The assessment explicitly states these tools are not recommended. Both are "
     "monolithic: the Python UI code runs server-side and is tightly coupled to "
     "the backend. They cannot be independently deployed, scaled, or maintained. "
     "Enterprise software requires a separate, independently deployable frontend "
     "that communicates with the backend over a defined API contract."),
], header=["Technology", "Why it was chosen"]))
story.append(SP(10))

story.append(info_box("Architecture Decision: Why a decoupled architecture matters", [
    "In a production telecom environment, the frontend and backend have different "
    "scaling requirements. During peak hours, hundreds of agents may use the UI "
    "simultaneously while the AI backend is the bottleneck.",
    "",
    "With a decoupled architecture: the Flutter web app is served from a CDN globally, "
    "while the FastAPI backend scales horizontally with multiple instances behind a "
    "load balancer. Each can be updated, redeployed, or scaled independently.",
    "",
    "With Streamlit/Gradio: every UI interaction is a server-side Python call. "
    "Scaling the UI means scaling the entire Python process — including all the "
    "ML models and business logic — which is wasteful and expensive.",
], bg=BLUE_LIGHT, border=BLUE))

story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# 2. PROMPT ENGINEERING
# ════════════════════════════════════════════════════════════════════════════
story += [P("2. Prompt Engineering Strategy", "h1"), HR()]
story.append(P(
    "The prompt engineering in this system is built around one core principle: "
    "<b>never trust free-text AI output in a production system</b>. Every technique "
    "below serves the goal of making the AI output deterministic and machine-parseable.",
    "body"))
story.append(SP(8))

story.append(P("Strategy 1 — Forced Tool-Use for Guaranteed Structured Output", "h2"))
story.append(P(
    "The standard approach of asking the AI to 'respond in JSON' is unreliable. "
    "The model may add explanation text before the JSON, use a slightly different "
    "field name, or include a trailing comment that breaks parsing.",
    "body"))
story.append(P(
    "Instead, this system uses <b>forced tool-use (function calling)</b>. A tool "
    "schema is defined with every required field, its type, and allowed values. "
    "The <b>tool_choice parameter is set to forced</b>, meaning the model has no "
    "choice but to call the tool and fill in every required field of the schema exactly.",
    "body"))
story.append(SP(6))
story.append(info_box("How forced tool-use works", [
    "1. We define ANALYSIS_TOOL with a JSON Schema describing 9 fields (category, "
    "draft_reply, recommended_next_step, escalation_decision, escalation_reason, "
    "risk_level, risk_justification, sentiment, confidence_score).",
    "",
    "2. We set tool_choice = {type: function, function: {name: analyze_support_ticket}}.",
    "",
    "3. The Groq API enforces schema compliance at the API level — it rejects responses "
    "that do not match the schema before they reach our code.",
    "",
    "4. We parse the tool call arguments with json.loads() and validate with Pydantic. "
    "Two layers of validation: API-level and application-level.",
], bg=GREEN_LIGHT, border=GREEN))
story.append(SP(10))

story.append(P("Strategy 2 — Enum Constraints on Categorical Fields", "h2"))
story.append(P(
    "Fields like category and risk_level are defined with an <b>enum constraint</b> "
    "in the tool schema. The model can only return one of the explicitly listed values. "
    "This eliminates variation like 'tech issue' vs 'Technical' vs 'technical support' "
    "— the output is always exactly one of the six defined categories.",
    "body"))
story.append(SP(10))

story.append(P("Strategy 3 — Nullable Fields with Type Union", "h2"))
story.append(P(
    "The <b>escalation_reason</b> field is defined as <b>type: [\"string\", \"null\"]</b> "
    "rather than just type: string. This tells the model it is valid to return null when "
    "no escalation is needed. Without this, the model either fabricates a reason or the "
    "API rejects the response with a validation error.",
    "body"))
story.append(SP(10))

story.append(P("Strategy 4 — System Prompt with Hard Constraints", "h2"))
story.append(P(
    "The system prompt establishes the AI's role and sets non-negotiable rules that "
    "are enforced on every request:",
    "body"))
story.append(two_col([
    ("Never fabricate",
     "Explicitly instructs the model not to invent account balances, plan details, "
     "or technical specifics not present in the ticket. This is the primary guardrail "
     "against hallucination."),
    ("Escalation triggers",
     "Lists specific conditions that must trigger escalation: billing disputes over "
     "10,000 IQD, legal threats, safety concerns, repeated complaints, or VIP customers. "
     "This makes escalation decisions consistent and auditable."),
    ("Regulatory awareness",
     "Instructs the model to consider CMC (Communications and Media Commission of Iraq) "
     "compliance in its recommendations. This is telecom-specific and prevents the AI "
     "from suggesting actions that would violate Iraqi telecommunications regulations."),
    ("RAG context injection",
     "The user message includes a clearly labelled section of relevant dataset "
     "records retrieved by TF-IDF. The model is instructed to use this context, "
     "grounding responses in actual reference material."),
]))
story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# 3. PII HANDLING
# ════════════════════════════════════════════════════════════════════════════
story += [P("3. PII Handling in a Production Environment", "h1"), HR()]
story.append(P(
    "PII (Personally Identifiable Information) in telecom is governed by the CMC "
    "(Communications and Media Commission of Iraq). "
    "Sending raw customer data to a third-party AI API without appropriate controls "
    "is a regulatory risk. The system implements a multi-stage PII pipeline.",
    "body"))
story.append(SP(8))

story.append(P("Current Implementation (Prototype)", "h2"))
story.append(two_col([
    ("Stage 1 — Input\nMasking",
     "Before the customer message reaches the Groq API, pii_service.mask_pii() "
     "scans it with compiled regex patterns and replaces matches with placeholders: "
     "[PHONE_REDACTED], [EMAIL_REDACTED], [CREDIT_CARD_REDACTED]. "
     "The original message is never sent outside the server."),
    ("Patterns covered",
     "Iraqi mobile phone numbers (all formats: +964, 0, and bare 07xx, with or "
     "without separators), email addresses, and 16-digit credit card numbers."),
    ("Stage 2 — RAG\nData Quality",
     "The RAG knowledge base (Dataset.xlsx) contains only synthetic/anonymised "
     "support text — no real customer data. This prevents PII cross-contamination "
     "where one customer's data appears in another customer's AI context."),
]))
story.append(SP(10))

story.append(P("Production Enhancements Required", "h2"))
story.append(two_col([
    ("NER-based Detection\n(Presidio)",
     "Microsoft Presidio adds Named Entity Recognition on top of regex. It detects "
     "unstructured PII that regex cannot — person names embedded in sentences, "
     "street addresses, dates of birth, and IP addresses. Deploy as a sidecar "
     "service to avoid adding heavyweight NLP dependencies to the main API."),
    ("Output Scanning",
     "Scan the AI-generated draft_reply for any PII before displaying it to the "
     "agent. LLMs can echo PII from the input or hallucinate plausible-looking "
     "data. A post-processing scan with the same PII pipeline catches this."),
    ("Audit Logging",
     "Log that PII was detected and what types were masked — but never log the "
     "actual PII content. This creates a compliance audit trail without creating "
     "a new PII data store. Logs should include: timestamp, session ID, PII types "
     "detected, and masking applied."),
    ("Encryption at Rest",
     "Any message stored (for audit purposes) must be encrypted with AES-256. "
     "The encryption key must be managed separately from the data (AWS KMS, "
     "Azure Key Vault, HashiCorp Vault). The application should never store the "
     "plaintext of customer messages longer than the request lifecycle."),
    ("Data Retention Policy",
     "CMC regulations require a defined data retention policy for telecom customer data. "
     "Raw messages should be auto-deleted after processing unless explicitly "
     "required for audit. Retained data must be accessible for deletion on "
     "customer request in accordance with Iraqi data protection requirements."),
    ("Zero-Trust API Access",
     "The Groq/LLM API key must be stored in a secrets manager (not in .env "
     "files in production). Rotate keys quarterly. Use API key scoping to "
     "restrict what the key can access. Monitor API call volumes for anomalies."),
], header=["Enhancement", "Why and How"]))
story.append(SP(10))

story.append(info_box("CMC Compliance Note for Iraqi Telecom", [
    "The Communications and Media Commission of Iraq (CMC) regulates customer data "
    "handling for all telecom providers operating in Iraq. Customer support data, "
    "including message content and service usage details, is considered sensitive "
    "personal information under Iraqi telecommunications law.",
    "",
    "Sending raw support tickets to a third-party LLM API without PII masking "
    "creates regulatory exposure. The pre-masking pipeline in this system addresses "
    "this by ensuring no identifiable customer data leaves the server.",
    "",
    "In production: consult legal counsel on whether the LLM provider's data "
    "processing agreement satisfies CMC requirements, or deploy a self-hosted "
    "model to eliminate third-party data sharing entirely.",
], bg=ORANGE_LT, border=ORANGE))

story.append(PageBreak())

# ════════════════════════════════════════════════════════════════════════════
# 4. LATENCY AND COSTS
# ════════════════════════════════════════════════════════════════════════════
story += [P("4. Reducing Latency and Costs at Scale", "h1"), HR()]
story.append(P(
    "The primary cost driver is LLM API calls. The primary latency driver is also "
    "LLM API calls (2–5 seconds each). Every strategy below targets one or both. "
    "Strategies are ordered from highest to lowest impact.",
    "body"))
story.append(SP(8))

story.append(P("Latency Reductions", "h2"))
story.append(two_col([
    ("Semantic Response\nCaching",
     "Cache the AI response for queries that are semantically similar to previously "
     "answered ones. Use Redis to store responses, keyed by the TF-IDF vector of "
     "the query. On each new request, compute cosine similarity against cached "
     "query vectors. If similarity > 0.92, return the cached response immediately. "
     "Expected latency reduction: 90%+ for common issue types (billing, outage "
     "queries are highly repetitive in telecom). Zero LLM cost for cache hits."),
    ("Response Streaming",
     "Instead of waiting for the complete AI response before sending anything to "
     "the frontend, stream tokens as they are generated. The agent sees the draft "
     "reply appearing word-by-word, reducing perceived latency from 3–5 seconds "
     "to under 1 second for the first visible content."),
    ("RAG Index\nPre-warming",
     "The current implementation loads the TF-IDF index on the first request "
     "(lazy loading). In production, pre-warm the index at server startup using "
     "FastAPI's lifespan event. The first request after deploy then has the same "
     "latency as all subsequent requests."),
    ("Model Tiering",
     "Route simple, high-confidence queries (clear billing issues, standard outage "
     "reports) to a smaller, faster model (LLaMA 3.1 8B — ~10x faster). Reserve "
     "the 70B model for complex or ambiguous tickets. Use a lightweight classifier "
     "to route between tiers based on message length, keyword signals, and "
     "historical patterns."),
    ("Async Parallel\nProcessing",
     "The current pipeline runs sequentially: PII masking → RAG → AI. PII masking "
     "is synchronous (regex, fast). RAG retrieval could run concurrently with the "
     "AI call start: begin the Groq call with the masked message first, then "
     "inject RAG context in a follow-up. This saves ~50ms of RAG processing time "
     "that currently blocks the AI call."),
], header=["Strategy", "Implementation and Expected Impact"]))
story.append(SP(10))

story.append(P("Cost Reductions", "h2"))
story.append(two_col([
    ("Semantic Caching",
     "The system prompt (SYSTEM_PROMPT in templates.py) is identical on every "
     "single request. Caching AI responses in Redis keyed by the TF-IDF vector "
     "of the query eliminates redundant API calls for similar tickets, which is "
     "the biggest single win for both latency and cost at scale."),
    ("Smaller Context\nWindows",
     "The current RAG retrieves up to 3 context documents. At scale, audit whether "
     "3 documents actually improve output quality vs. 1. Each additional context "
     "document adds tokens to every request. A/B test with 1 vs. 3 RAG results "
     "and measure quality vs. cost tradeoff."),
    ("Batch Processing\nfor Non-Urgent Tickets",
     "Low-priority tickets submitted outside business hours do not need real-time "
     "responses. Batch these using a job queue (Celery + Redis) and process them "
     "during off-peak hours when API rate limits are lower and compute costs may "
     "be cheaper. Only real-time agent sessions need the live API."),
    ("Upgrade RAG to\nDense Embeddings",
     "TF-IDF cannot understand synonyms. An agent typing 'invoice problem' does "
     "not match dataset records containing 'billing dispute' well. Upgrading to "
     "Sentence Transformers (all-MiniLM-L6-v2) with FAISS indexing produces much "
     "better RAG matches, which means the AI needs less clarification and produces "
     "higher-quality first drafts — reducing agent edit time and re-analysis costs."),
    ("Horizontal Scaling\nwith Load Balancing",
     "FastAPI is stateless — no session data is stored in the server process. "
     "Run multiple instances behind a load balancer (nginx, AWS ALB). The RAG "
     "index and dataset cache are loaded per-process (acceptable for read-only "
     "data). This scales throughput linearly with instance count, keeping "
     "per-instance load (and therefore per-instance LLM call rate) manageable."),
    ("CDN for Flutter\nWeb Assets",
     "The Flutter web build (HTML, JS, assets) is static and does not change "
     "between requests. Serve it from a CDN (CloudFront, Cloudflare). This "
     "eliminates all frontend traffic from the FastAPI server, reducing server "
     "load and bandwidth costs by the number of page loads."),
], header=["Strategy", "Implementation and Expected Impact"]))

story.append(SP(10))
story.append(HR())
story.append(SP(6))
story.append(Paragraph(
    "This document covers the four required areas of the system design submission. "
    "For full API documentation, run the backend and open "
    "<b>http://localhost:8000/docs</b>. "
    "For code-level explanations, refer to the accompanying Backend Code Reference PDF.",
    ParagraphStyle("end", fontName="Helvetica-Oblique", fontSize=10,
                   textColor=GREY_TEXT, alignment=TA_CENTER)))

doc.build(story, onFirstPage=on_cover, onLaterPages=on_page)
print(f"Created: {OUTPUT}")
