"""Data model for standardized repeated-issue detection output."""

from pydantic import BaseModel, Field

from backend.models.support_record import SupportRecord


class IssueFamily(BaseModel):
    """Represents a clustered issue family with full supporting records."""

    issue_family_label: str = Field(
        ...,
        description="Human-readable label for this issue family",
        examples=["Payment Email Confirmation Issues"],
    )
    supporting_case_ids: list[str] = Field(
        ...,
        description="List of supporting support case IDs for this issue family",
        examples=[["case_001", "case_017", "case_032"]],
    )
    confidence_score: float = Field(
        ...,
        description="Confidence score for this issue family (0-1)",
        ge=0.0,
        le=1.0,
        examples=[0.85],
    )
    product_areas: list[str] = Field(
        default_factory=list,
        description="Unique product areas represented in this issue family",
        examples=[["checkout", "billing"]],
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Unique tags aggregated from all supporting records",
        examples=[["email", "receipt", "payment"]],
    )
    records: list[SupportRecord] = Field(
        default_factory=list,
        description="Full supporting records for this issue family",
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "issue_family_label": "Payment Email Confirmation Issues",
                "supporting_case_ids": ["case_001", "case_017", "case_032"],
                "confidence_score": 0.85,
                "product_areas": ["billing", "checkout"],
                "tags": ["email", "payment", "receipt"],
                "records": [],
            }
        }