"""Normalized support record schema."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SupportSourceType(str, Enum):
    """Supported source types for support records."""

    TICKET = "ticket"
    CHAT_LOG = "chat_log"
    ESCALATION = "escalation"
    CALL_TRANSCRIPT = "call_transcript"
    REFUND_REASON = "refund_reason"


class SupportStatus(str, Enum):
    """Status of a support case."""

    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"


class SupportRecord(BaseModel):
    """
    Normalized support case or conversation record.

    This schema represents a single support case across all source types.
    """

    # Required fields
    id: str = Field(
        ...,
        description="Unique identifier for the support case",
        examples=["case_001", "ticket_12345"],
    )
    source_type: SupportSourceType = Field(
        ...,
        description="Type of support source",
        examples=["ticket", "chat_log"],
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the case was created (ISO 8601 format)",
        examples=["2026-03-01T10:15:00Z"],
    )
    status: SupportStatus = Field(
        ...,
        description="Current status of the support case",
        examples=["resolved"],
    )
    case_summary: str = Field(
        ...,
        description="Summary of the customer's issue or problem",
        examples=[
            "Customer completed payment successfully but did not receive confirmation email."
        ],
    )
    resolution_text: str = Field(
        ...,
        description="Summary of how the issue was resolved",
        examples=[
            "Agent confirmed payment succeeded, asked customer to check spam, then re-triggered email successfully."
        ],
    )

    # Optional fields
    customer_message: Optional[str] = Field(
        None,
        description="Original message or complaint from the customer",
        examples=["I paid but never got the confirmation email."],
    )
    product_area: Optional[str] = Field(
        None,
        description="Product category or area affected",
        examples=["checkout", "billing", "authentication"],
    )
    tags: Optional[list[str]] = Field(
        None,
        description="Labels or tags for categorization",
        examples=[["email", "receipt", "checkout"]],
    )
    severity: Optional[str] = Field(
        None,
        description="Severity level of the issue",
        examples=["low", "medium", "high"],
    )
    sentiment: Optional[str] = Field(
        None,
        description="Overall customer sentiment or mood",
        examples=["frustrated", "satisfied", "neutral"],
    )

    class Config:
        """Pydantic model configuration."""

        # Allow population by field name
        use_enum_values = False
        # Add examples for OpenAPI docs
        json_schema_extra = {
            "example": {
                "id": "case_001",
                "source_type": "ticket",
                "created_at": "2026-03-01T10:15:00Z",
                "status": "resolved",
                "product_area": "checkout",
                "customer_message": "I paid but never got the confirmation email.",
                "case_summary": "Customer completed payment successfully but did not receive confirmation email.",
                "resolution_text": "Agent confirmed payment succeeded, asked customer to check spam, then re-triggered email successfully.",
                "tags": ["email", "receipt", "checkout"],
                "severity": "medium",
                "sentiment": "frustrated",
            }
        }
