# Normalized Support Record Schema

## Overview

The normalized support record schema represents a unified data model for support cases across all source types (tickets, chat logs, escalations, call transcripts, and refund reasons). This schema is used throughout the MVP to ensure consistent handling of support data.

## Schema Definition

### Required Fields

| Field | Type | Format | Description |
|-------|------|--------|-------------|
| `id` | string | - | Unique identifier for the support case (e.g., "case_001", "ticket_12345") |
| `source_type` | enum | See below | Type of support source |
| `created_at` | datetime | ISO 8601 | Timestamp when the case was created |
| `status` | enum | See below | Current status of the case |
| `case_summary` | string | - | Summary of the customer's issue or problem |
| `resolution_text` | string | - | Summary of how the issue was resolved |

### Optional Fields

| Field | Type | Format | Description |
|-------|------|--------|-------------|
| `customer_message` | string | - | Original message or complaint from the customer |
| `product_area` | string | - | Product category or area affected (e.g., "checkout", "billing") |
| `tags` | array[string] | - | Labels or tags for categorization |
| `severity` | string | - | Severity level (e.g., "low", "medium", "high") |
| `sentiment` | string | - | Customer sentiment (e.g., "frustrated", "satisfied", "neutral") |

### Enumerations

#### SupportSourceType
```
- ticket
- chat_log
- escalation
- call_transcript
- refund_reason
```

#### SupportStatus
```
- resolved
- unresolved
```

Note: Only **resolved** cases are used in the generation pipeline.

## Example Record

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

## Implementation

### Backend (Python + Pydantic)

The schema is implemented as a Pydantic model for runtime validation and serialization:

**File**: `backend/models/support_record.py`

```python
from backend.models import SupportRecord, SupportSourceType, SupportStatus

# Create a record
record = SupportRecord(
    id="case_001",
    source_type=SupportSourceType.TICKET,
    created_at="2026-03-01T10:15:00Z",
    status=SupportStatus.RESOLVED,
    case_summary="Customer issue...",
    resolution_text="Resolution..."
)

# Validate from dict
data = {"id": "case_001", ...}
record = SupportRecord(**data)  # Raises ValidationError if invalid

# Serialize to JSON
json_data = record.model_dump(mode="json")
```

### Validation on Startup

The backend validates all records on application startup:

**File**: `backend/startup.py`

```python
from backend.startup import validate_records_on_startup

# This runs automatically on app startup
records = validate_records_on_startup()
# Returns: List[SupportRecord] (resolved only)
# Logs any validation errors
```

### Frontend (TypeScript)

The schema is implemented as TypeScript types for type safety:

**File**: `frontend/types/support-record.ts`

```typescript
import { SupportRecord, SupportSourceType, SupportStatus } from "./support-record";
import { validateSupportRecord, filterResolvedOnly } from "../utils/validate";

// Type-safe record handling
const record: SupportRecord = {
  id: "case_001",
  source_type: SupportSourceType.TICKET,
  created_at: "2026-03-01T10:15:00Z",
  status: SupportStatus.RESOLVED,
  case_summary: "...",
  resolution_text: "..."
};

// Validate runtime data
const validation = validateSupportRecord(unknownData);
if (validation.isValid) {
  const records: SupportRecord[] = unknownData;
} else {
  console.error(validation.errors);
}

// Filter to resolved cases
const resolved = filterResolvedOnly(records);
```

## Validation Rules

### Type Validation
- All required fields must be present and non-null
- Field types must match schema definitions
- `created_at` must be a valid ISO 8601 datetime

### Enum Validation
- `source_type` must be one of the defined source types
- `status` must be either "resolved" or "unresolved"

### Field-Specific Rules
- `id`: Non-empty string
- `case_summary`: Non-empty string
- `resolution_text`: Non-empty string
- `tags`: If present, must be an array of strings
- `severity`: If present, recommended values are "low", "medium", "high" (but accepts any string)
- `sentiment`: If present, recommended values are "frustrated", "satisfied", "neutral" (but accepts any string)

## Validation Methods

### Python

**Validate single record:**
```python
from backend.core import validate_record

is_valid, record, error = validate_record(data_dict)
if is_valid:
    print(f"Valid: {record.id}")
else:
    print(f"Invalid: {error}")
```

**Validate JSON file:**
```python
from backend.core import validate_file
from pathlib import Path

valid_records, invalid_records = validate_file(Path("records.json"))
print(f"Loaded {len(valid_records)} valid records")
for invalid in invalid_records:
    print(f"Record {invalid['index']} failed: {invalid['errors']}")
```

**Filter resolved cases:**
```python
from backend.core import filter_resolved_only

resolved = filter_resolved_only(all_records)
```

### TypeScript

**Validate single record:**
```typescript
import { validateSupportRecord } from "../utils/validate";

const validation = validateSupportRecord(unknownData);
if (validation.isValid) {
  console.log("Valid record");
} else {
  console.error("Validation errors:", validation.errors);
}
```

**Parse JSON:**
```typescript
import { parseSupportRecords } from "../utils/validate";

try {
  const records = parseSupportRecords(jsonString);
  console.log(`Loaded ${records.length} records`);
} catch (error) {
  console.error("Failed to parse:", error);
}
```

## Integration Points

### API Endpoints

**GET /health**
- Returns: `{ status: "healthy", records_loaded: number }`

**GET /records**
- Returns: `{ total: number, records: SupportRecord[] }`

### Data Flow

1. **Load**: JSON files from `backend/data/`
2. **Validate**: Each record against schema on app startup
3. **Filter**: Keep only resolved records
4. **Store**: In app state for API access
5. **Serialize**: Convert to JSON for frontend consumption
6. **Validate (Frontend)**: Type-safe validation in TypeScript

## Future Considerations

- Add custom validators for specific fields (e.g., email format in customer_message)
- Add support for nested objects if issue categorization becomes more complex
- Add version field to track schema evolution
- Add audit fields (created_by, updated_at, updated_by) if needed
