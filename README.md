# SupportAI — Support Knowledge Copilot

SupportAI is a local MVP that turns solved support cases into FAQ drafts for human review. It groups related cases using embeddings and clustering, gives each group a readable label, and generates structured answers linked to their supporting cases.

The repository implements the FAQ workflow with a Python/FastAPI backend and an Angular frontend. Documentation update suggestions remain future work.

![FAQ detail showing a generated draft alongside three supporting cases and review controls](docs/images/faq-detail.png)

*Running app with synthetic cases and mock providers. Confidence reflects repeated-text cluster similarity, not answer accuracy; this demonstrates the interface, not measured AI quality or production readiness.*

## Workflow

1. **Load solved cases.** At startup, the backend validates JSON files in `backend/data/`, logs invalid entries, and keeps resolved cases.
2. **Group related cases.** It embeds each case's summary and resolution, then clusters similar vectors into *issue families*: groups of related support cases.
3. **Label each family.** An LLM names the group; the backend retains its supporting records and a similarity score.
4. **Generate FAQ drafts.** On request, the LLM turns each family's summaries and resolutions into a problem statement, cause, fix steps, edge cases, and guidance on contacting support.
5. **Review with evidence.** The Angular UI displays drafts beside their supporting cases and provides edit, approve, reject, and bulk-regeneration actions.

The UI also includes a support-record browser and English/Brazilian Portuguese localization. A separate HTML viewer lets you inspect similarities between cases.

Restart the backend after changing input files. FAQ generation is triggered separately through the UI or API.

## Engineering choices and tradeoffs

### Clustering and confidence

[Clustering](backend/core/clustering.py) uses SciPy's average-linkage hierarchical clustering over pairwise cosine distances. A similarity setting controls where the clustering tree is cut; a minimum-size filter then removes small groups. Pairwise distance storage grows quadratically with the number of cases.

The UI's **confidence score measures average similarity within a cluster, not answer accuracy**. Average linkage does not guarantee that every pair meets the configured threshold.

![Standalone similarity matrix viewer showing four groups of synthetic cases with a 0.90 highlight threshold](docs/images/similarity-matrix.png)

*Viewer loaded from `GET /similarity-matrix`: 12 synthetic cases in four repeated-text groups, using mock embeddings.*

### Structured generation with evidence

[FAQ generation](backend/core/faq_generation.py) validates the model's JSON output with Pydantic and attaches supporting case IDs and summaries. This checks structure, not factual correctness; drafts still need human review.

Bulk generation continues when a family fails and returns a `failures` array alongside successful drafts. Each run replaces the previous draft collection. The UI currently does not display the per-family failure breakdown.

### Gemini and mock providers

Separate [embedding](backend/core/embeddings_protocol.py) and [LLM](backend/core/llm_protocol.py) interfaces support Gemini and local mocks. Mocks use hash-derived vectors and local text-generation logic to exercise the workflow without API calls; they cannot demonstrate semantic or answer quality.

OpenAI appears in configuration enums but has no implemented provider.

### Failure handling

Both Gemini providers use a [circuit breaker](backend/core/circuit_breaker.py): retryable failures get up to five attempts with linear waits of 10, 20, 30, and 40 seconds. Three failed calls open the circuit; a later call can test recovery after 60 seconds.

Retries block execution and classify errors by message matching. Circuit state is local to each process. Embedding failures can prevent startup; labeling failures use fallback names.

## Run locally

Prerequisites: a Unix-like shell, Python 3.11+, Node.js 22.x (22.12 or later), and npm. The frontend uses Angular 21.2.

### 1. Configure the backend

From the repository root:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
```

The example configuration selects mock providers, so no API key is needed for an initial run. Mock mode may produce few or no qualifying clusters with the sample data.

For real embeddings and generated text, edit `backend/.env`:

```dotenv
EMBEDDING_PROVIDER=gemini
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-embedding-001
LLM_MODEL=gemini-2.0-flash
```

These are the repository's default model names; replace them if unavailable to your account. Gemini mode sends case text to the external API.

| Setting | Behavior |
| --- | --- |
| `CLUSTERING_MIN_CLUSTER_SIZE` | Defaults to 3. The single-record code path is an exception and returns a singleton. |
| `CLUSTERING_SIMILARITY_THRESHOLD` | The copied example sets 0.70; without an override, `Settings` defaults to 0.90. |
| `EMBEDDING_DIMENSION` | Controls mock vector dimensions; it is not passed as an output-dimension setting to Gemini. |

Input is read from `backend/data/`; the declared `DATA_DIR` setting is currently unused.

### 2. Start the backend

From the repository root, with the virtual environment active:

```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Wait for startup to finish. API documentation is available at [localhost:8000/docs](http://localhost:8000/docs).

### 3. Start the frontend

In a second terminal:

```bash
cd frontend
npm ci
npm start
```

Open [localhost:4200](http://localhost:4200). For Brazilian Portuguese, replace `npm start` with:

```bash
npm run ng -- serve --configuration=pt-BR
```

The UI connects to the backend API. Use the draft-list regeneration action to create drafts, then open one to review its content and evidence.

Alternatively, after configuring `backend/.env`, run `bash start.sh` to prepare dependencies and start both services with the Portuguese UI.

## Input format

Each JSON file can contain one record or an array of records. Supported `source_type` values are `ticket`, `chat_log`, `escalation`, `call_transcript`, and `refund_reason`. These are normalized categories, not external integrations.

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

See the [schema](backend/models/support_record.py) and [sample dataset](backend/data/sample_records.json). Repeated-issue detection needs multiple related cases.

## API and inspection tools

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/health` | Application status and loaded-record count. |
| GET | `/records` | Loaded resolved support records. |
| GET | `/clusters` | Labeled issue families with supporting records. |
| GET | `/similarity-matrix` | Record IDs and the pairwise cosine-similarity matrix. |
| POST | `/faqs/generate/{index}` | Generate a draft for a zero-based issue-family index. |
| POST | `/faqs/generate` | Generate drafts for all families; return successes and failures. |
| GET | `/faqs` | List drafts currently held in backend memory. |

To inspect similarities, save the matrix response:

```bash
curl http://localhost:8000/similarity-matrix -o /tmp/supportai-similarity.json
```

Open the [standalone viewer](backend/similarity_matrix_viewer.html) in a browser and load the JSON file. It supports threshold highlighting and optional records JSON for case inspection.

## Current limitations and future work

- **No durable storage.** Backend drafts disappear on restart. Frontend edits and review statuses are not saved to the backend and disappear on page reload; regeneration also clears local overrides.
- **No export or publishing.** Approval only changes local status to `Reviewed`. Export screens under `stitch/` are mockups.
- **Future work:** documentation-update suggestions.
- **Batch input only.** Records must already be normalized. There are no platform connectors, live ingestion, background jobs, or incremental embedding cache.
- **No published evaluations or benchmarks** for answer accuracy, clustering quality, or throughput.
- **Local prototype deployment.** The API has no authentication and uses permissive CORS.
