"""Embedding input formatting utilities for support records."""

import logging
from typing import Optional

from backend.models import SupportRecord


logger = logging.getLogger(__name__)


def format_for_embedding(record: SupportRecord) -> Optional[str]:
    """
    Format a single support record for embedding input.

    Concatenates case_summary and resolution_text separated by ' -- ', with whitespace normalization.
    Returns None if record cannot be formatted (missing required fields).

    Args:
        record: A SupportRecord instance

    Returns:
        Formatted string suitable for embeddings, or None if record is invalid

    Example:
        >>> record = SupportRecord(
        ...     id="case_001",
        ...     source_type="ticket",
        ...     created_at="2026-03-01T10:15:00Z",
        ...     status="resolved",
        ...     case_summary="Customer received wrong item",
        ...     resolution_text="Shipped replacement item overnight"
        ... )
        >>> format_for_embedding(record)
        "Customer received wrong item -- Shipped replacement item overnight"
    """
    try:
        # Ensure both required fields are present and non-empty
        if not record.case_summary or not record.resolution_text:
            logger.warning(
                f"Skipping record {record.id}: missing case_summary or resolution_text"
            )
            return None

        # Normalize whitespace: strip and collapse multiple spaces
        case_text = " ".join(record.case_summary.split())
        resolution_text = " ".join(record.resolution_text.split())

        # Concatenate with -- separator
        formatted = f"{case_text} -- {resolution_text}"

        return formatted

    except AttributeError as e:
        logger.warning(f"Skipping record {record.id if hasattr(record, 'id') else 'unknown'}: {e}")
        return None


def format_batch_for_embedding(
    records: list[SupportRecord],
) -> dict[str, str]:
    """
    Format multiple support records for embedding input.

    Returns a dictionary mapping case ID to formatted embedding text.
    Silently skips records that cannot be formatted (broken/incomplete).

    Args:
        records: List of SupportRecord instances

    Returns:
        Dictionary where keys are record IDs and values are formatted strings.
        Only includes successfully formatted records.

    Example:
        >>> records = [record1, record2, record3]
        >>> formatted = format_batch_for_embedding(records)
        >>> formatted["case_001"]
        "Customer received wrong item -- Shipped replacement item overnight"
    """
    formatted_records = {}

    for record in records:
        try:
            formatted_text = format_for_embedding(record)
            if formatted_text is not None:
                formatted_records[record.id] = formatted_text
        except Exception as e:
            logger.warning(f"Unexpected error formatting record {record.id}: {e}")
            continue

    return formatted_records
