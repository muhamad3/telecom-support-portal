"""
Generate system_design.pdf
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    NextPageTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak,
)
from reportlab.platypus.flowables import Flowable
import os

# ── palette ───────────────────────────────────────────────────────────────────
NAVY     = HexColor("#1a2e4a")
BLUE     = HexColor("#2563eb")
LIGHT_BG = HexColor("#f1f5f9")
BORDER   = HexColor("#cbd5e1")
ACCENT   = HexColor("#0ea5e9")
MUTED    = HexColor("#64748b")
GREEN_BG = HexColor("#f0fdf4")
GREEN_BD = HexColor("#86efac")
WARN_BG  = HexColor("#fffbeb")
WARN_BD  = HexColor("#fcd34d")
CODE_BG  = HexColor("#0f172a")
CODE_FG  = HexColor("#e2e8f0")

PAGE_W, PAGE_H = A4
ML = 2.2 * cm   # left margin
MR = 2.0 * cm   # right margin
MT = 2.0 * cm   # top margin
MB = 2.0 * cm   # bottom margin
TW = PAGE_W - ML - MR   # text width


# ── paragraph helpers ─────────────────────────────────────────────────────────

CELL_STYLE = ParagraphStyle(
    "cell", fontName="Helvetica", fontSize=8.5, leading=13,
    textColor=HexColor("#1e293b"), spaceBefore=0, spaceAfter=0,
)
CELL_BOLD = ParagraphStyle(
    "cellb", fontName="Helvetica-Bold", fontSize=8.5, leading=13,
    textColor=NAVY, spaceBefore=0, spaceAfter=0,
)
HDR_CELL = ParagraphStyle(
    "hdrcell", fontName="Helvetica-Bold", fontSize=8.5, leading=13,
    textColor=white, spaceBefore=0, spaceAfter=0,
)

def C(text):
    """Normal table cell paragraph."""
    return Paragraph(text, CELL_STYLE)

def CB(text):
    """Bold first-column cell paragraph."""
    return Paragraph(text, CELL_BOLD)

def H(text):
    """Header cell paragraph."""
    return Paragraph(text, HDR_CELL)


# ── custom flowables ──────────────────────────────────────────────────────────

class SectionHeader(Flowable):
    def __init__(self, number, title):
        super().__init__()
        self.number = number
        self.title  = title
        self.height = 1.1 * cm

    def wrap(self, avW, avH):
        self.width = avW
        return avW, self.height

    def draw(self):
        c = self.canv
        c.setFillColor(BLUE)
        c.rect(0, 0, 0.35 * cm, self.height, fill=1, stroke=0)
        bx = 0.55 * cm
        c.setFillColor(BLUE)
        c.roundRect(bx, 0.15 * cm, 0.7 * cm, 0.7 * cm, 4, fill=1, stroke=0)
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(bx + 0.35 * cm, 0.28 * cm, str(self.number))
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(1.45 * cm, 0.28 * cm, self.title)


class CodeBlock(Flowable):
    def __init__(self, lines):
        super().__init__()
        self.lines = lines
        self.pad   = 0.35 * cm
        self.lh    = 0.41 * cm
        self.height = 2 * self.pad + 0.3 * cm + len(lines) * self.lh

    def wrap(self, avW, avH):
        self.width = avW
        return avW, self.height

    def draw(self):
        c = self.canv
        c.setFillColor(CODE_BG)
        c.roundRect(0, 0, self.width, self.height, 5, fill=1, stroke=0)
        c.setFillColor(ACCENT)
        c.setFont("Courier-Bold", 7)
        c.drawString(self.pad, self.height - 0.55 * cm, "ARCHITECTURE DIAGRAM")
        c.setFillColor(CODE_FG)
        c.setFont("Courier", 7.2)
        y = self.height - self.pad - self.lh - 0.28 * cm
        for line in self.lines:
            c.drawString(self.pad, y, line)
            y -= self.lh


class CalloutBox(Flowable):
    def __init__(self, text, kind="info"):
        super().__init__()
        self.text = text
        self.kind = kind
        self.pad  = 0.3 * cm

    def wrap(self, avW, avH):
        self.width = avW
        inner_w = avW - 1.1 * cm - 2 * self.pad
        sty = ParagraphStyle("tmp", fontName="Helvetica", fontSize=9, leading=14)
        _, th = Paragraph(self.text, sty).wrap(inner_w, 9999)
        self.height = th + 2 * self.pad + 0.05 * cm
        return avW, self.height

    def draw(self):
        c = self.canv
        bg = WARN_BG if self.kind == "warn" else GREEN_BG
        bd = WARN_BD if self.kind == "warn" else GREEN_BD
        icon = "!" if self.kind == "warn" else "i"
        c.setFillColor(bg)
        c.setStrokeColor(bd)
        c.setLineWidth(1)
        c.roundRect(0, 0, self.width, self.height, 4, fill=1, stroke=1)
        c.setFillColor(MUTED)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(self.pad, self.height - self.pad - 0.2 * cm, icon)
        sty = ParagraphStyle("tmp", fontName="Helvetica", fontSize=9,
                             leading=14, textColor=NAVY)
        p = Paragraph(self.text, sty)
        inner_w = self.width - 1.1 * cm - 2 * self.pad
        p.wrap(inner_w, 9999)
        p.drawOn(c, 1.0 * cm, self.pad)


class CoverPage(Flowable):
    """Minimal cover — title only."""
    def wrap(self, avW, avH):
        return avW, avH

    def split(self, *args):
        return []

    def draw(self):
        c  = self.canv
        W  = PAGE_W
        H  = PAGE_H

        # solid dark background
        c.setFillColor(NAVY)
        c.rect(0, 0, W, H, fill=1, stroke=0)

        # subtle accent band at top
        c.setFillColor(ACCENT)
        c.rect(0, H - 0.55 * cm, W, 0.55 * cm, fill=1, stroke=0)

        # thin horizontal rule centred vertically
        mid = H / 2
        c.setStrokeColor(ACCENT)
        c.setLineWidth(1)
        c.line(W * 0.22, mid + 1.8 * cm, W * 0.78, mid + 1.8 * cm)
        c.line(W * 0.22, mid - 2.6 * cm, W * 0.78, mid - 2.6 * cm)

        # main title
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(W / 2, mid + 0.8 * cm, "TelcoAI Customer Support Portal")

        # subtitle
        c.setFillColor(HexColor("#bfdbfe"))
        c.setFont("Helvetica", 14)
        c.drawCentredString(W / 2, mid + 0.05 * cm, "System Design Document")


# ── page header / footer ──────────────────────────────────────────────────────

def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(BORDER)
    canvas.setLineWidth(0.5)
    canvas.line(ML, PAGE_H - 1.4 * cm, PAGE_W - MR, PAGE_H - 1.4 * cm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(ML, PAGE_H - 1.1 * cm,
                      "TelcoAI Customer Support Portal  —  System Design")
    canvas.drawRightString(PAGE_W - MR, PAGE_H - 1.1 * cm, "INTERNAL / TECHNICAL")
    canvas.line(ML, 1.2 * cm, PAGE_W - MR, 1.2 * cm)
    canvas.drawString(ML, 0.8 * cm, "Confidential — Not for external distribution")
    canvas.drawRightString(PAGE_W - MR, 0.8 * cm, f"Page {doc.page}")
    canvas.restoreState()


# ── table builder ─────────────────────────────────────────────────────────────

BASE_TS = TableStyle([
    ("BACKGROUND",    (0, 0), (-1, 0), NAVY),
    ("TOPPADDING",    (0, 0), (-1, 0), 7),
    ("BOTTOMPADDING", (0, 0), (-1, 0), 7),
    ("ROWBACKGROUNDS",(0, 1), (-1, -1), [white, LIGHT_BG]),
    ("TOPPADDING",    (0, 1), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
    ("LEFTPADDING",   (0, 0), (-1, -1), 7),
    ("RIGHTPADDING",  (0, 0), (-1, -1), 7),
    ("GRID",          (0, 0), (-1, -1), 0.4, BORDER),
    ("VALIGN",        (0, 0), (-1, -1), "TOP"),
])

def make_table(rows, widths):
    t = Table(rows, colWidths=widths, repeatRows=1)
    t.setStyle(BASE_TS)
    return t


# ── paragraph styles ──────────────────────────────────────────────────────────

def styles():
    return dict(
        body=ParagraphStyle(
            "body", fontName="Helvetica", fontSize=9.5, leading=15,
            textColor=HexColor("#1e293b"), alignment=TA_JUSTIFY,
            spaceBefore=0, spaceAfter=6,
        ),
        h3=ParagraphStyle(
            "h3", fontName="Helvetica-Bold", fontSize=9.5, leading=14,
            textColor=BLUE, spaceBefore=10, spaceAfter=3,
        ),
        bullet=ParagraphStyle(
            "bullet", fontName="Helvetica", fontSize=9.5, leading=15,
            textColor=HexColor("#1e293b"), leftIndent=16, spaceBefore=0, spaceAfter=3,
        ),
        toc_head=ParagraphStyle(
            "toc_head", fontName="Helvetica-Bold", fontSize=16,
            textColor=NAVY, spaceAfter=14,
        ),
    )


# ── story builder ─────────────────────────────────────────────────────────────

def build_story(S):
    story = []

    # cover
    story.append(NextPageTemplate("Normal"))
    story.append(CoverPage())
    story.append(PageBreak())

    # table of contents
    story.append(Paragraph("Table of Contents", S["toc_head"]))
    toc_rows = [
        [H("#"), H("Section"), H("Page")],
        [C("1"), C("Tech Stack Selection"),                  C("3")],
        [C("2"), C("Architecture Overview"),                 C("3")],
        [C("3"), C("Prompt Engineering Strategy"),           C("4")],
        [C("4"), C("PII Handling"),                          C("5")],
        [C("5"), C("Latency & Cost Optimisation at Scale"),  C("6")],
        [C("6"), C("Security Considerations"),               C("7")],
    ]
    story.append(make_table(toc_rows, [1.0*cm, TW - 2.5*cm, 1.5*cm]))
    story.append(PageBreak())

    # ── 1. Tech Stack ─────────────────────────────────────────────────────────
    story.append(SectionHeader(1, "Tech Stack Selection"))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "The stack was chosen to reflect the service-oriented patterns found in "
        "production telecom environments, while keeping every component independently "
        "deployable and replaceable. Here is the reasoning behind each choice.",
        S["body"]))
    story.append(Spacer(1, 0.2*cm))

    stack_rows = [
        [H("Layer"), H("Technology"), H("Rationale")],
        [CB("Backend"),
         C("FastAPI (Python 3.11+)"),
         C("Async-native with automatic OpenAPI/Swagger docs and tight Pydantic "
           "integration. The right balance between development speed and "
           "production-readiness.")],
        [CB("AI Provider"),
         C("Groq — LLaMA 3.3 70B"),
         C("Forced tool-use guarantees structured JSON output — the model cannot "
           "return malformed data. No regex fallbacks or output parsing heuristics "
           "are needed.")],
        [CB("RAG"),
         C("scikit-learn TF-IDF + cosine similarity"),
         C("Lightweight retrieval with no external vector database dependency. "
           "Demonstrates the RAG pattern clearly. A production system would use "
           "FAISS or a dedicated vector store.")],
        [CB("Frontend"),
         C("Flutter Web"),
         C("Decoupled SPA communicating over REST. Compiles to static files, "
           "enabling independent deployment and clear separation between "
           "frontend and backend teams.")],
        [CB("Validation"),
         C("Pydantic v2"),
         C("Enforces AI output structure, auto-generates JSON Schema for the "
           "OpenAPI docs, and provides a second validation layer on top of the "
           "model's tool-use guarantee.")],
    ]
    story.append(make_table(stack_rows, [2.4*cm, 3.8*cm, TW - 6.2*cm]))
    story.append(Spacer(1, 0.3*cm))

    # ── 2. Architecture ───────────────────────────────────────────────────────
    story.append(Spacer(1, 0.4*cm))
    story.append(SectionHeader(2, "Architecture Overview"))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "The system follows a layered architecture. The Flutter frontend is a fully "
        "static SPA that communicates with the backend exclusively over a REST API. "
        "There is no shared state, no server-side rendering, and no direct database "
        "access from the UI layer.",
        S["body"]))
    story.append(Spacer(1, 0.25*cm))

    arch = [
        "  Flutter Web (SPA)                     FastAPI Backend",
        "  +----------------------+   REST      +--------------------------------+",
        "  |  Analyse Screen      | <-------->  |  Router Layer                  |",
        "  |  Dataset Browser     |             |    /api/support/analyse         |",
        "  |  Failure Cases       |             |    /api/dataset/records         |",
        "  |  Analytics Dashboard |             |                                 |",
        "  +----------------------+             |  +------------+ +------------+  |",
        "                                       |  | AI Service | | PII Service|  |",
        "                                       |  | (Groq API) | |(regex mask)|  |",
        "                                       |  +------------+ +------------+  |",
        "                                       |  +------------+ +------------+  |",
        "                                       |  | RAG Service| | Data Svc   |  |",
        "                                       |  | (TF-IDF)   | | (xlsx)     |  |",
        "                                       |  +------------+ +------------+  |",
        "                                       +--------------------------------+",
    ]
    story.append(CodeBlock(arch))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Service responsibilities", S["h3"]))
    for item in [
        "<b>Router layer</b> — HTTP endpoint definitions, request validation via "
        "Pydantic, response serialisation. Intentionally thin — no business logic.",
        "<b>AI Service</b> — LLM orchestration. Builds the prompt, calls Groq with "
        "forced tool-use, and extracts the structured response.",
        "<b>RAG Service</b> — Indexes the knowledge base on startup using TF-IDF, "
        "then retrieves the top-k most relevant articles per ticket before the AI call.",
        "<b>PII Service</b> — Regex-based detection and masking of Iraqi phone numbers, "
        "email addresses, and credit card numbers before any data reaches the LLM.",
        "<b>Data Service</b> — Loads the historical dataset from the Excel file, "
        "supports filtering, sorting, and pagination for the dataset browser.",
    ]:
        story.append(Paragraph(f"• {item}", S["bullet"]))

    # ── 3. Prompt Engineering ─────────────────────────────────────────────────
    story.append(Spacer(1, 0.4*cm))
    story.append(SectionHeader(3, "Prompt Engineering Strategy"))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Forced tool-use for guaranteed structured output", S["h3"]))
    story.append(Paragraph(
        "The most important prompt engineering decision in this project was choosing "
        "forced tool-use over asking the model to produce JSON in free text. With "
        "free-text JSON prompting the model occasionally adds explanation text before "
        "the JSON block, uses slightly different key names, or omits optional fields "
        "— all of which break downstream parsing. With forced tool-use the model has "
        "no choice but to populate exactly the schema defined. Pydantic validation on "
        "the output provides a second safety layer.",
        S["body"]))
    story.append(Spacer(1, 0.2*cm))

    story.append(CalloutBox(
        "<b>Implementation:</b> The tool is registered with "
        "tool_choice = {type: function, function: {name: analyze_support_ticket}}. "
        "This instructs the model to always invoke that specific function — "
        "free-text responses are not permitted.",
        kind="info"))
    story.append(Spacer(1, 0.25*cm))

    story.append(Paragraph("System prompt structure", S["h3"]))
    story.append(Paragraph(
        "The system prompt establishes five things, in order of priority:", S["body"]))
    for i, item in enumerate([
        "Role framing — telecom customer support specialist with knowledge of Iraqi "
        "telecom regulations and CMC guidelines.",
        "Hard behavioural constraints — never fabricate account details, always "
        "acknowledge when information is missing.",
        "Escalation thresholds — billing disputes over 10,000 IQD, multi-user outages, "
        "legal threats, or repeated unresolved complaints trigger human escalation.",
        "Regulatory awareness — CMC (Communications and Media Commission of Iraq) "
        "compliance for data handling and customer communication.",
        "Tone guidance — professional, empathetic, solution-oriented; no corporate jargon.",
    ], 1):
        story.append(Paragraph(f"  {i}.  {item}", S["bullet"]))

    story.append(Spacer(1, 0.25*cm))
    story.append(Paragraph("RAG context injection", S["h3"]))
    story.append(Paragraph(
        "Before each AI call, the RAG service retrieves the three most relevant "
        "knowledge base articles using TF-IDF cosine similarity and injects them into "
        "the user message. This gives the model access to current fee tables, "
        "troubleshooting workflows, and escalation policies without bloating the "
        "system prompt with static content. The knowledge base can be updated "
        "independently of the model or the prompt.",
        S["body"]))

    # ── 4. PII ────────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(SectionHeader(4, "PII Handling"))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Sending raw customer messages to a third-party LLM API carries data "
        "privacy risk. The current implementation uses a two-stage masking approach "
        "that demonstrates the correct architectural pattern.",
        S["body"]))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Two-stage masking", S["h3"]))
    pii_rows = [
        [H("Stage"), H("What happens")],
        [CB("1 — Input masking"),
         C("The customer message passes through the PII service before reaching the "
           "AI model. Iraqi phone numbers (all formats), email addresses, and credit "
           "card numbers are replaced with labelled placeholders: [PHONE_REDACTED], "
           "[EMAIL_REDACTED], [CREDIT_CARD_REDACTED].")],
        [CB("2 — Sanitised message in response"),
         C("The API response includes the sanitized_message field alongside the AI "
           "analysis so support agents can verify exactly what the model received "
           "and confirm sensitive data was handled correctly.")],
    ]
    story.append(make_table(pii_rows, [3.8*cm, TW - 3.8*cm]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Production recommendations", S["h3"]))
    story.append(Paragraph(
        "Regex masking alone is not sufficient for a live deployment. The following "
        "additions would be required before going to production:",
        S["body"]))

    prod_rows = [
        [H("Measure"), H("Description")],
        [CB("NER-based detection"),
         C("Supplement regex with a Named Entity Recognition model (Presidio, "
           "spaCy NER, or AWS Comprehend) to catch names, addresses, and other "
           "context-dependent PII that regex cannot reliably identify.")],
        [CB("Output scanning"),
         C("Run PII detection on the AI-generated draft reply before it reaches "
           "the agent — the model may inadvertently reconstruct PII from context.")],
        [CB("Encryption at rest"),
         C("All stored tickets and AI outputs should be encrypted using AES-256. "
           "Customer messages must not persist in plaintext anywhere in the pipeline.")],
        [CB("Audit logging"),
         C("Log every PII access event with agent ID, timestamp, and business "
           "justification. Required for CMC regulatory compliance.")],
        [CB("Data retention policy"),
         C("Auto-purge customer messages after case resolution. Retention period "
           "to be defined by the legal team based on CMC requirements.")],
        [CB("Anonymisation pipeline"),
         C("Before using historical tickets for model fine-tuning or analytics, "
           "run the full dataset through an anonymisation pipeline.")],
    ]
    story.append(make_table(prod_rows, [3.5*cm, TW - 3.5*cm]))
    story.append(Spacer(1, 0.25*cm))
    story.append(CalloutBox(
        "<b>CMC note:</b> Iraqi Communications and Media Commission regulations govern "
        "how telecom providers handle customer data. Using a third-party LLM API with "
        "customer messages requires explicit legal review and possibly customer consent. "
        "The masking layer reduces — but does not eliminate — this risk.",
        kind="warn"))

    # ── 5. Scale ──────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(SectionHeader(5, "Latency & Cost Optimisation at Scale"))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "The single-instance architecture is appropriate for this stage. Below are "
        "the changes that would be prioritised as usage grows, ordered by implementation "
        "priority.",
        S["body"]))
    story.append(Spacer(1, 0.2*cm))

    story.append(Paragraph("Latency reduction", S["h3"]))
    lat_rows = [
        [H("Strategy"), H("Expected impact"), H("Effort")],
        [CB("Semantic response caching"),
         C("Cache AI responses in Redis keyed by a hash of the TF-IDF vector. "
           "Near-identical tickets — common in telecom support — return instantly, "
           "eliminating 30-40% of LLM calls."),
         C("Medium")],
        [CB("Streaming responses"),
         C("Stream the AI reply to the frontend via SSE so agents see the draft "
           "building in real time. Perceived latency drops significantly even if "
           "total generation time is unchanged."),
         C("Medium")],
        [CB("RAG with FAISS"),
         C("Pre-compute embeddings for the knowledge base and use FAISS approximate "
           "nearest-neighbour search instead of recomputing TF-IDF on every request."),
         C("Medium")],
        [CB("Edge CDN for frontend"),
         C("Serve the static frontend from a CDN and co-locate the API server in "
           "the same region as the LLM provider to minimise round-trip latency."),
         C("Low")],
    ]
    story.append(make_table(lat_rows, [3.5*cm, TW - 6.0*cm, 2.5*cm]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Cost reduction", S["h3"]))
    cost_rows = [
        [H("Strategy"), H("Expected impact"), H("Effort")],
        [CB("Model tiering"),
         C("Route straightforward tickets (billing enquiries, standard plan info) "
           "to a smaller model. Reserve the 70B model for complex or ambiguous "
           "tickets. Could reduce token costs by 50-60%."),
         C("Medium")],
        [CB("Prompt compression"),
         C("The current system prompt and RAG context can be made more concise "
           "without losing instruction quality. Low effort with immediate impact "
           "on cost per call."),
         C("Low")],
        [CB("Batch processing"),
         C("For non-urgent tickets received via email or web form, batch them and "
           "process during off-peak hours to reduce peak load."),
         C("Medium")],
        [CB("Token budgeting"),
         C("Set max_tokens per request type. Add monitoring and alerting on token "
           "usage anomalies to catch runaway prompts early."),
         C("Low")],
    ]
    story.append(make_table(cost_rows, [3.5*cm, TW - 6.0*cm, 2.5*cm]))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("Scaling architecture for high volume", S["h3"]))
    scale = [
        "                    +---------------+",
        "                    |  Load Balancer |",
        "                    +-------+-------+",
        "                            |",
        "           +----------------+-----------------+",
        "           |                |                 |",
        "    +------+------+  +------+------+  +-------+-----+",
        "    |  API Pod 1  |  |  API Pod 2  |  |  API Pod 3  |",
        "    +------+------+  +------+------+  +-------+-----+",
        "           |                |                 |",
        "    +------+-----------------+-----------------+------+",
        "    |              Message Queue (Redis)              |",
        "    +-------------------------+------------------------+",
        "                              |",
        "          +-------------------+------------------+",
        "          |                   |                  |",
        "   +------+------+   +--------+------+   +-------+-----+",
        "   |  AI Worker 1|   |  AI Worker 2  |   |  AI Worker 3|",
        "   +-------------+   +---------------+   +-------------+",
    ]
    story.append(CodeBlock(scale))
    story.append(Spacer(1, 0.2*cm))
    for note in [
        "API pods handle intake and PII masking — CPU-light and horizontally scalable.",
        "The message queue decouples request intake from LLM calls, preventing "
        "thundering-herd overload during traffic spikes.",
        "AI workers scale based on queue depth using auto-scale rules.",
        "Circuit breaker pattern: if the LLM provider is unavailable, queue requests "
        "and serve cached responses rather than returning errors.",
    ]:
        story.append(Paragraph(f"• {note}", S["bullet"]))

    # ── 6. Security ───────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.4*cm))
    story.append(SectionHeader(6, "Security Considerations"))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "The current implementation covers a baseline set of security controls. "
        "The table below shows what is in place now versus what a production "
        "deployment would require.",
        S["body"]))
    story.append(Spacer(1, 0.2*cm))

    sec_rows = [
        [H("Control"), H("Current status"), H("Production requirement")],
        [CB("CORS"),
         C("Configured — only the known frontend origin is permitted."),
         C("Same, with a review process as new frontend domains are added.")],
        [CB("Input validation"),
         C("All inputs validated via Pydantic before processing."),
         C("Same — already production-grade.")],
        [CB("Rate limiting"),
         C("Not implemented."),
         C("Add via slowapi middleware with per-IP and per-agent-role limits.")],
        [CB("Authentication"),
         C("Not implemented — open API for demonstration purposes."),
         C("JWT tokens with role-based access control: agent, supervisor, admin.")],
        [CB("Audit trail"),
         C("Not implemented."),
         C("All AI analyses and agent edits logged immutably with timestamp "
           "and user ID.")],
        [CB("Secrets management"),
         C("Environment variables via .env file."),
         C("Secrets vault (e.g. AWS Secrets Manager or Railway environment "
           "variable groups with restricted access).")],
        [CB("Human-in-the-loop"),
         C("Implemented — agents review and edit every response before submission."),
         C("Same — this is a hard architectural requirement, not optional.")],
        [CB("API key exposure"),
         C("The LLM API key is server-side only, never sent to the frontend."),
         C("Same — already correct.")],
    ]
    col1 = 3.0*cm
    col2 = (TW - col1) * 0.44
    col3 = (TW - col1) * 0.56
    story.append(make_table(sec_rows, [col1, col2, col3]))
    story.append(Spacer(1, 0.35*cm))
    story.append(CalloutBox(
        "<b>Human-in-the-loop is a hard architectural requirement.</b> AI-generated "
        "draft responses never reach the customer directly. Every response goes "
        "through a support agent review step before submission. This is the primary "
        "safeguard against hallucinated account details, incorrect fee information, "
        "or inappropriate tone reaching customers.",
        kind="info"))

    return story


# ── entry point ───────────────────────────────────────────────────────────────

def main():
    out = os.path.join(os.path.dirname(__file__), "system_design.pdf")

    cover_frame = Frame(0, 0, PAGE_W, PAGE_H,
                        leftPadding=0, rightPadding=0,
                        topPadding=0, bottomPadding=0, id="cover")
    cover_tpl = PageTemplate(id="Cover", frames=[cover_frame],
                             onPage=lambda c, d: None)

    content_h = PAGE_H - (MT + 0.8*cm) - (MB + 0.6*cm)
    content_frame = Frame(ML, MB + 0.6*cm, TW, content_h, id="normal")
    normal_tpl = PageTemplate(id="Normal", frames=[content_frame],
                              onPage=header_footer)

    doc = BaseDocTemplate(
        out, pagesize=A4,
        pageTemplates=[cover_tpl, normal_tpl],
        title="TelcoAI — System Design",
        author="Muhamad Kareem",
        subject="Enterprise GenAI Customer Support Portal",
    )

    S = styles()
    doc.build(build_story(S))
    print("PDF written: " + out)


if __name__ == "__main__":
    main()
