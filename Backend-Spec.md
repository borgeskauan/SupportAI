## Goal

Generate **draft customer-facing FAQs** from repeated **solved** support issues across normalized support records.

## Sources

All are included:

* tickets
* chat logs
* escalations
* call transcripts
* refund reasons

## Input format

* pre-normalized JSON files
* one record per support case / conversation
* call transcripts stored as cleaned summary + resolution
* unresolved cases excluded entirely

## Repeated issue detection

A repeated issue is:

**semantic similarity on normalized case text using embeddings**, based on:

* case/problem text
* resolution text

### Grouping behavior

* cross-source grouping allowed
* cross-product grouping allowed
* product area kept only as metadata
* minimum cluster size is configurable
* default minimum cluster size = `3`

## Recency

Use the easiest option:

**all historical cases equally**

## FAQ generation trigger

Run only when the user clicks the single action button:

* **Generate / Regenerate FAQs**

No automatic generation on load.

## Evidence display

Use the easiest option:

**summarized evidence only**

Show:

* source type
* case ID
* short summary
* maybe created_at

Do not show raw excerpts for MVP.

## FAQ output

Each generated FAQ draft contains:

* title
* problem statement
* cause explanation
* step-by-step fix
* edge cases
* when to contact support
* issue family label
* supporting case count
* supporting case IDs
* summarized supporting evidence
* confidence score
* review-needed badge

## Status workflow

Use lightweight review states:

* Draft
* Reviewed
* Rejected

## UI actions

Use:

* Generate / Regenerate FAQs
* Edit
* Approve
* Reject
* Export

## Regeneration behavior

* overwrite only
* no version history

---

# Recommended JSON schema for the MVP

Use one unified record schema like this:

```json
{
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
  "sentiment": "frustrated"
}
```

## Required fields

* id
* source_type
* created_at
* status
* case_summary
* resolution_text

## Optional fields

* customer_message
* product_area
* tags
* severity
* sentiment

For the MVP, the core clustering should depend mostly on:

* `case_summary`
* `resolution_text`

---

# Output schema for generated FAQ drafts

```json
{
  "faq_id": "faq_001",
  "issue_family_label": "Missing confirmation email after successful payment",
  "status": "draft",
  "review_needed": true,
  "confidence_score": 0.87,
  "supporting_case_ids": ["case_001", "case_017", "case_032"],
  "supporting_case_count": 3,
  "supporting_evidence": [
    {
      "case_id": "case_001",
      "source_type": "ticket",
      "summary": "Paid successfully but never received confirmation email.",
      "created_at": "2026-03-01T10:15:00Z"
    }
  ],
  "faq": {
    "title": "Why didn’t I receive my confirmation email?",
    "problem_statement": "Some customers complete payment successfully but do not receive the confirmation email immediately.",
    "cause_explanation": "This can happen delayed email delivery, spam filtering, or temporary notification failures.",
    "step_by_step_fix": [
      "Check the spam or promotions folder.",
      "Verify the email address used at checkout.",
      "Wait a few minutes and refresh your inbox.",
      "If still missing, contact support so the email can be re-sent."
    ],
    "edge_cases": [
      "The payment may be successful even if the email was delayed.",
      "Typos in the email address can prevent delivery."
    ],
    "when_to_contact_support": "Contact support if payment was successful and no email arrives after checking spam and waiting several minutes."
  }
}
```
