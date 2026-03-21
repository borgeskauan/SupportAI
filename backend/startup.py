"""
Startup validation module.

Validates all support records on application startup to ensure data integrity.
"""

import logging
import sys
from pathlib import Path

from backend.core import validate_file, filter_resolved_only
from backend.models import SupportRecord


logger = logging.getLogger(__name__)


def validate_records_on_startup(data_dir: Path = None) -> list[SupportRecord]:
    """
    Validate all support records in the data directory on app startup.

    This function:
    1. Loads all JSON files from the data directory
    2. Validates each record against the schema
    3. Filters to only include resolved cases
    4. Reports any validation errors
    5. Returns the cleaned dataset for use

    Args:
        data_dir: Path to directory containing JSON record files.
                 Defaults to 'backend/data'

    Returns:
        List of validated SupportRecord objects (resolved only)

    Raises:
        SystemExit: If validation fails critically
    """
    if data_dir is None:
        data_dir = Path(__file__).parent / "data"

    logger.info(f"Validating support records from {data_dir}")

    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        raise FileNotFoundError(f"Data directory not found: {data_dir}")

    all_records = []
    total_errors = 0

    # Find all JSON files
    json_files = sorted(data_dir.glob("*.json"))
    if not json_files:
        logger.warning(f"No JSON files found in {data_dir}")
        return []

    for json_file in json_files:
        logger.info(f"Loading {json_file.name}...")
        try:
            valid_records, invalid_records = validate_file(json_file)
            all_records.extend(valid_records)

            if invalid_records:
                total_errors += len(invalid_records)
                for invalid in invalid_records:
                    logger.error(
                        f"  Invalid record at index {invalid['index']}: {invalid['errors']}"
                    )
            else:
                logger.info(f"  ✓ Loaded {len(valid_records)} valid records")

        except Exception as e:
            logger.error(f"Failed to load {json_file.name}: {e}")
            total_errors += 1

    # Filter to resolved cases only
    resolved_records = filter_resolved_only(all_records)

    # Summary
    logger.info(f"Validation complete:")
    logger.info(f"  Total records loaded: {len(all_records)}")
    logger.info(f"  Resolved records: {len(resolved_records)}")
    logger.info(f"  Unresolved records: {len(all_records) - len(resolved_records)}")
    logger.info(f"  Validation errors: {total_errors}")

    if total_errors > 0:
        logger.warning("Some records had validation errors (see details above)")

    return resolved_records


def setup_logging(level=logging.INFO):
    """Configure logging for startup validation."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
