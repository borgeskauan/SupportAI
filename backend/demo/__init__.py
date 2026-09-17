"""Explicit synthetic scenario shared by the local demo and mock providers."""

import json
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def load_scenario() -> dict:
    """Load the bundled fixture, never user datasets or environment configuration."""
    return json.loads(Path(__file__).with_name("scenario.json").read_text(encoding="utf-8"))


def receipt_records() -> list[dict]:
    scenario = load_scenario()
    return [record for record in scenario["records"] if record["id"] in scenario["case_ids"]]


def receipt_embedding_texts() -> set[str]:
    """Match the actual summary/resolution input, not keywords or a family label."""
    return {
        f'{record["case_summary"]} -- {record["resolution_text"]}'
        for record in receipt_records()
    }
