from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException

from ..models.schemas import (
    SupportRequest,
    SupportResponse,
    SubmitRequest,
    SubmitResponse,
)
from ..services import ai_service, pii_service, rag_service

router = APIRouter(prefix="/api/support", tags=["Support"])


@router.post(
    "/analyze",
    response_model=SupportResponse,
    summary="Analyze a customer support ticket",
    description="Processes a customer message through PII detection, RAG retrieval, "
    "and AI analysis. Returns structured analysis including category, "
    "draft reply, next steps, escalation decision, and risk level.",
)
async def analyze_ticket(request: SupportRequest):
    sanitized = pii_service.mask_pii(request.customer_message)

    rag_context = rag_service.retrieve(request.customer_message)

    try:
        analysis = await ai_service.analyze_ticket(sanitized, rag_context)
    except Exception as exc:
        # Log the full error server-side; return a safe message to the client
        # so raw LLM output and internal details are never exposed.
        import logging
        logging.getLogger(__name__).error("AI analysis failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="The AI analysis service is temporarily unavailable. Please try again.",
        )

    return SupportResponse(
        analysis=analysis,
        sanitized_message=sanitized,
        rag_context=rag_context,
    )


@router.post(
    "/submit",
    response_model=SubmitResponse,
    summary="Submit an agent-edited response",
    description="Allows a human agent to submit their edited version of the "
    "AI-generated draft reply. Supports adding agent notes and "
    "overriding the escalation decision.",
)
async def submit_response(request: SubmitRequest):
    return SubmitResponse(
        status="submitted",
        submitted_at=datetime.now(timezone.utc),
        edited_reply=request.edited_reply,
    )
