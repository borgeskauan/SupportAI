# SupportAI developer reference

See the [README](../README.md) for the product overview, screenshots, and local setup. Run commands below from the repository root unless stated otherwise.

## Use Gemini

Set the following values in `backend/.env`, including your API key:

```dotenv
EMBEDDING_PROVIDER=gemini
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-embedding-001
LLM_MODEL=gemini-2.0-flash
```

These are the model names configured in the repository. Replace them if your account uses different models. Gemini sends case text to Google's API.

The example configuration uses local mock providers and needs no API key. Mock comparisons use hash-derived vectors rather than semantic meaning, so the sample cases may produce no qualifying groups. OpenAI support is not implemented.

## Brazilian Portuguese

In `frontend/`, replace `npm start` with:

```bash
npm run ng -- serve --configuration=pt-BR
```

Alternatively, after configuring `backend/.env`, run `bash start.sh` from the repository root to prepare dependencies and start both services with the Portuguese UI.

## Case format

Save cases as JSON files in `backend/data/`, then restart the backend. Each file can contain one case or a list of cases. For example:

```json
{
  "id": "case_001",
  "source_type": "ticket",
  "created_at": "2026-03-01T10:15:00Z",
  "status": "resolved",
  "case_summary": "Payment succeeded but the confirmation email was missing.",
  "resolution_text": "Checked spam and re-sent the confirmation email.",
  "product_area": "checkout",
  "tags": ["email", "confirmation"]
}
```

Use `ticket`, `chat_log`, `escalation`, `call_transcript`, or `refund_reason` for `source_type`. These describe where a case came from; the app does not import from those systems automatically.

See the [sample cases](../backend/data/sample_records.json) and [full field definitions](../backend/models/support_record.py). Include several cases about the same problem so the app can identify recurring issues.

## Inspect case similarities

Keep the backend running. In another terminal at the repository root, save the comparison data and case records:

```bash
source venv/bin/activate
curl -fsS http://localhost:8000/similarity-matrix -o /tmp/supportai-similarity.json
curl -fsS http://localhost:8000/records | python -c 'import json, sys; json.dump(json.load(sys.stdin)["records"], sys.stdout)' > /tmp/supportai-records.json
```

Open the [standalone viewer](../backend/similarity_matrix_viewer.html) in a desktop browser and load both files into their matching fields. Adjust the highlight threshold to explore closer matches, then click a cell to read the cases.

The current viewer requires both matrix and records JSON files. Use a window wider than 1200 pixels and scroll within the viewer to see the heatmap. Its layout can clip rotated column labels.

## API

Interactive API documentation is available at [localhost:8000/docs](http://localhost:8000/docs) while the backend is running.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/health` | Application status and loaded-record count. |
| GET | `/records` | Loaded resolved support records. |
| GET | `/clusters` | Named groups and their supporting cases. |
| GET | `/similarity-matrix` | Case IDs and similarity scores for each pair. |
| POST | `/faqs/generate/{index}` | Generate a draft for one group; numbering starts at 0. |
| POST | `/faqs/generate` | Generate drafts for all groups; return drafts and failures. |
| GET | `/faqs` | List drafts currently held in backend memory. |

## Configuration

| Setting | Behavior |
| --- | --- |
| `CLUSTERING_MIN_CLUSTER_SIZE` | Minimum cases per group, normally 3. An input containing only one case is handled separately and returns a one-case group. |
| `CLUSTERING_SIMILARITY_THRESHOLD` | Higher values require closer matches. The example configuration uses 0.70; the code defaults to 0.90 if no value is set. |
| `EMBEDDING_DIMENSION` | Size of the numeric representation used in mock mode. Does not set Gemini's output size. |

Input is always read from `backend/data/`; the `DATA_DIR` setting is currently unused.

## Implementation notes

- [Grouping](../backend/core/clustering.py) uses SciPy's average-linkage hierarchical clustering with cosine distance. The threshold applies to grouping, so not every pair must meet it. Comparing all pairs requires memory that grows with the square of the case count.
- [FAQ generation](../backend/core/faq_generation.py) checks the answer structure with Pydantic and attaches case IDs and summaries. Bulk generation returns a `failures` array for groups it could not process; these details are not shown in the interface yet.
- [Embedding](../backend/core/embeddings_protocol.py) and [text-generation](../backend/core/llm_protocol.py) interfaces support Gemini and local mocks.
- [Gemini error handling](../backend/core/circuit_breaker.py) retries temporary failures and pauses further calls after repeated failures. Retries block the current operation. Failures while comparing cases can prevent startup; failed group naming uses fallback labels.
- The API allows requests from any origin (permissive CORS) and has no authentication. Embeddings and drafts are not stored permanently.
