"""Data models for generated FAQ drafts."""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class FAQStatus(str, Enum):
    """Review workflow states for FAQ drafts."""

    DRAFT = "draft"
    REVIEWED = "reviewed"
    REJECTED = "rejected"


class SupportingEvidence(BaseModel):
    """Summarized evidence from one supporting support case."""

    case_id: str = Field(..., description="Support case ID")
    source_type: str = Field(..., description="Source type of the support case")
    summary: str = Field(..., description="Short issue summary from the case")
    created_at: datetime = Field(..., description="Case creation timestamp")


class FAQContent(BaseModel):
    """Customer-facing FAQ content sections."""

    title: str = Field(..., description="FAQ title in customer-facing language")
    problem_statement: str = Field(..., description="Clear explanation of the recurring problem")
    cause_explanation: str = Field(..., description="Likely cause in simple terms")
    step_by_step_fix: list[str] = Field(
        ...,
        min_length=1,
        description="Ordered steps customers can follow",
    )
    edge_cases: list[str] = Field(
        default_factory=list,
        description="Common exceptions or caveats customers should know",
    )
    when_to_contact_support: str = Field(
        ...,
        description="Clear escalation guidance for customers",
    )


class FAQDraft(BaseModel):
    """Generated FAQ draft output."""

    faq_id: str = Field(..., description="Unique FAQ draft identifier")
    issue_family_label: str = Field(..., description="Issue family label that this FAQ covers")
    status: FAQStatus = Field(
        default=FAQStatus.DRAFT,
        description="Review lifecycle status",
    )
    review_needed: bool = Field(
        default=True,
        description="Whether human review is required before publishing",
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score inherited from repeated issue detection",
    )
    supporting_case_ids: list[str] = Field(
        ...,
        description="Supporting case IDs tied to this draft",
    )
    supporting_case_count: int = Field(
        ...,
        ge=0,
        description="Number of supporting cases",
    )
    supporting_evidence: list[SupportingEvidence] = Field(
        default_factory=list,
        description="Summarized evidence list from supporting cases",
    )
    faq: FAQContent = Field(..., description="Generated FAQ sections")

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "faq_id": "faq_001",
                "issue_family_label": "Missing confirmation email after successful payment",
                "status": "draft",
                "review_needed": True,
                "confidence_score": 0.87,
                "supporting_case_ids": ["case_001", "case_017", "case_032"],
                "supporting_case_count": 3,
                "supporting_evidence": [
                    {
                        "case_id": "case_001",
                        "source_type": "ticket",
                        "summary": "Paid successfully but never received confirmation email.",
                        "created_at": "2026-03-01T10:15:00Z",
                    }
                ],
                "faq": {
                    "title": "Why did I not receive my confirmation email?",
                    "problem_statement": "Some customers complete payment but do not immediately receive the confirmation email.",
                    "cause_explanation": "This usually happens due to delayed delivery, spam filtering, or a temporary notification issue.",
                    "step_by_step_fix": [
                        "Check your spam or promotions folder.",
                        "Confirm the email address used at checkout.",
                        "Wait a few minutes and refresh your inbox.",
                        "If it still does not arrive, contact support to resend it.",
                    ],
                    "edge_cases": [
                        "Payment can succeed even if the email is delayed.",
                        "A typo in the email address can block delivery.",
                    ],
                    "when_to_contact_support": "Contact support if payment succeeded and no email arrives after checking spam and waiting a few minutes.",
                },
            }
        }
