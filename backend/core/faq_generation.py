"""FAQ generation service for one issue family."""

import json
from uuid import uuid4

from backend.core.llm_protocol import LLM
from backend.models.faq_draft import FAQContent, FAQDraft, FAQStatus, SupportingEvidence
from backend.models.issue_family import IssueFamily


FAQ_GENERATION_PROMPT = """You are a customer support content writer.
Generate a simple, customer-facing FAQ for one repeated solved issue family.

Rules:
- Use plain and clear language.
- Be concise and practical.
- Do not mention case IDs.
- Return only valid JSON.
- JSON must include exactly these keys:
  title, problem_statement, cause_explanation, step_by_step_fix, edge_cases, when_to_contact_support
- step_by_step_fix must be an array of 3-6 short action steps.
- edge_cases must be an array (can be empty).

Issue family label:
{issue_family_label}

Supporting cases:
{supporting_cases}
"""


class FAQGenerationService:
    """Service that generates one FAQ draft from one issue family."""

    def __init__(self, llm_provider: LLM):
        """Initialize service with an injected LLM provider."""
        if llm_provider is None:
            raise ValueError("LLM provider is required")
        self.llm_provider = llm_provider

    def generate_faq_draft(self, issue_family: IssueFamily) -> FAQDraft:
        """Generate one FAQ draft from one issue family."""
        if not issue_family.records:
            raise ValueError("Issue family has no supporting records")

        prompt = self._build_prompt(issue_family)
        raw_response = self.llm_provider.generate(prompt)

        faq_content = self._parse_faq_content(raw_response)
        evidence = self._build_supporting_evidence(issue_family)

        return FAQDraft(
            faq_id=f"faq_{uuid4().hex[:10]}",
            issue_family_label=issue_family.issue_family_label,
            status=FAQStatus.DRAFT,
            review_needed=True,
            confidence_score=issue_family.confidence_score,
            supporting_case_ids=issue_family.supporting_case_ids,
            supporting_case_count=len(issue_family.supporting_case_ids),
            supporting_evidence=evidence,
            faq=faq_content,
        )

    def _build_prompt(self, issue_family: IssueFamily) -> str:
        """Build the LLM prompt from issue family records."""
        case_lines = []
        for i, record in enumerate(issue_family.records, start=1):
            case_lines.append(
                f"{i}. issue: {record.case_summary}\\n"
                f"   resolution: {record.resolution_text}"
            )

        return FAQ_GENERATION_PROMPT.format(
            issue_family_label=issue_family.issue_family_label,
            supporting_cases="\\n".join(case_lines),
        )

    def _parse_faq_content(self, raw_response: str) -> FAQContent:
        """Parse and validate JSON FAQ content from LLM output."""
        if not raw_response or not raw_response.strip():
            raise ValueError("LLM returned an empty FAQ response")

        normalized = raw_response.strip()
        if normalized.startswith("```"):
            normalized = self._extract_code_block_json(normalized)

        try:
            payload = json.loads(normalized)
        except json.JSONDecodeError as exc:
            raise ValueError(f"LLM returned non-JSON FAQ content: {exc}") from exc

        try:
            return FAQContent.model_validate(payload)
        except Exception as exc:
            raise ValueError(f"LLM returned invalid FAQ schema: {exc}") from exc

    def _extract_code_block_json(self, text: str) -> str:
        """Extract JSON from fenced code blocks if present."""
        lines = [line for line in text.splitlines() if not line.strip().startswith("```")]
        return "\n".join(lines).strip()

    def _build_supporting_evidence(self, issue_family: IssueFamily) -> list[SupportingEvidence]:
        """Convert family records into summarized evidence entries."""
        evidence: list[SupportingEvidence] = []
        for record in issue_family.records:
            evidence.append(
                SupportingEvidence(
                    case_id=record.id,
                    source_type=record.source_type.value,
                    summary=record.case_summary,
                    created_at=record.created_at,
                )
            )
        return evidence
