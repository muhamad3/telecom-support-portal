from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .models.schemas import HealthResponse
from .routers import support, dataset

settings = get_settings()

if not settings.GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY is not set. Add it to backend/.env before starting the server."
    )

app = FastAPI(
    title="Telecom Customer Support AI Portal",
    description=(
        "Enterprise GenAI-powered customer support portal for telecommunications. "
        "Provides AI-driven ticket analysis with structured outputs, RAG-enhanced "
        "context retrieval, PII detection, and human-in-the-loop editing."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

_raw_origins = settings.CORS_ORIGINS.split(",")
_origins = []
for o in _raw_origins:
    _origins.append(o.strip())

_wildcard = "*" in _origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    # credentials cannot be True when origins contains "*"
    allow_credentials=not _wildcard,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(support.router)
app.include_router(dataset.router)


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now(timezone.utc),
    )
