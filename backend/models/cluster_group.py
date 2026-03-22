"""Data model for clustered issue families."""

from typing import Optional

from pydantic import BaseModel, Field

from backend.models import SupportRecord


class ClusterGroup(BaseModel):
    """
    Represents a group of similar support cases (issue family).
    
    Cases in the same cluster are semantically similar based on
    case_summary and resolution_text embeddings.
    """

    cluster_id: str = Field(
        ...,
        description="Unique identifier for this cluster",
        examples=["cluster_001", "issue_family_payment_issues"],
    )
    record_ids: list[str] = Field(
        ...,
        description="List of support case IDs in this cluster",
        examples=[["case_001", "case_017", "case_032"]],
    )
    similarity_threshold: float = Field(
        ...,
        description="Similarity threshold used to form this cluster (0-1)",
        ge=0.0,
        le=1.0,
        examples=[0.70],
    )
    confidence_score: float = Field(
        default=0.0,
        description="Average pairwise similarity within cluster (0-1)",
        ge=0.0,
        le=1.0,
    )
    size: int = Field(
        default=0,
        description="Number of records in this cluster",
        ge=0,
    )
    label: Optional[str] = Field(
        default=None,
        description="Human-readable label for this issue family",
        examples=["Payment Email Confirmation Issues"],
    )

    class Config:
        """Pydantic model configuration."""

        json_schema_extra = {
            "example": {
                "cluster_id": "cluster_001",
                "record_ids": ["case_001", "case_017", "case_032"],
                "similarity_threshold": 0.70,
                "confidence_score": 0.85,
                "size": 3,
                "label": "Payment Email Confirmation Issues",
            }
        }

    @property
    def is_singleton(self) -> bool:
        """Check if this cluster contains only one record."""
        return len(self.record_ids) == 1
