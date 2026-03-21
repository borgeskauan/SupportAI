"""Validation and embedding formatting utilities for support records."""

import json
from pathlib import Path
from typing import Optional

from pydantic import ValidationError

from backend.models import SupportRecord, SupportStatus
from backend.core.embeddings import format_for_embedding, format_batch_for_embedding


def validate_record(data: dict) -> tuple[bool, Optional[SupportRecord], Optional[str]]:
    """
    Validate a single support record.

    Args:
        data: Dictionary containing support record fields

    Returns:
        Tuple of (is_valid, record, error_message)
        - is_valid: Whether the record passed validation
        - record: Parsed SupportRecord if valid, None otherwise
        - error_message: Error details if validation failed, None otherwise
    """
    try:
        record = SupportRecord(**data)
        return True, record, None
    except ValidationError as e:
        return False, None, str(e)


def validate_file(file_path: Path) -> tuple[list[SupportRecord], list[dict]]:
    """
    Validate all support records in a JSON file.

    Expects a JSON file with either:
    - A single object (one record)
    - An array of objects (multiple records)

    Args:
        file_path: Path to the JSON file

    Returns:
        Tuple of (valid_records, invalid_records)
        - valid_records: List of successfully validated SupportRecord objects
        - invalid_records: List of dicts with 'data' and 'errors' keys
    """
    valid_records = []
    invalid_records = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        raise ValueError(f"Failed to read JSON file {file_path}: {e}")

    # Normalize to list format
    records_data = data if isinstance(data, list) else [data]

    for i, record_data in enumerate(records_data):
        is_valid, record, error = validate_record(record_data)
        if is_valid:
            valid_records.append(record)
        else:
            invalid_records.append({"index": i, "data": record_data, "errors": error})

    return valid_records, invalid_records


def filter_resolved_only(records: list[SupportRecord]) -> list[SupportRecord]:
    """
    Filter records to include only resolved cases.

    Args:
        records: List of support records

    Returns:
        Filtered list containing only resolved records
    """
    return [r for r in records if r.status == SupportStatus.RESOLVED]
