from pydantic import BaseModel, Field, field_validator
from enum import Enum
from datetime import datetime


class IssueCategory(str, Enum):
    TECHNICAL = "Technical"
    BILLING = "Billing"
    NETWORK = "Network"
    ACCOUNT = "Account"
    SERVICE = "Service"
    GENERAL = "General"


class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class SupportRequest(BaseModel):
    customer_message: str = Field(..., min_length=1, description="The customer's support message")


class AIAnalysis(BaseModel):
    category: IssueCategory
    draft_reply: str
    recommended_next_step: str
    escalation_decision: bool
    escalation_reason: str | None = None
    risk_level: RiskLevel
    risk_justification: str
    sentiment: str | None = None
    confidence_score: float | None = None

    @field_validator("escalation_decision", mode="before")
    @classmethod
    def coerce_bool(cls, v):
        """Accept string booleans the LLM occasionally returns ('true'/'false')."""
        if isinstance(v, str):
            if v.lower() == "true":
                return True
            if v.lower() == "false":
                return False
        return v


class SupportResponse(BaseModel):
    analysis: AIAnalysis
    sanitized_message: str
    rag_context: list[str] = []


class SubmitRequest(BaseModel):
    edited_reply: str
    agent_notes: str | None = None
    approved_escalation: bool | None = None


class SubmitResponse(BaseModel):
    status: str
    submitted_at: datetime
    edited_reply: str


class DatasetRecord(BaseModel):
    id: int
    issue_type: str
    message: str
    priority: str


class DatasetResponse(BaseModel):
    records: list[DatasetRecord]
    total: int
    page: int
    page_size: int


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime
