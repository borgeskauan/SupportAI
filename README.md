# SupportAI — Support Knowledge Copilot

SupportAI is a local MVP that turns solved support cases into FAQ drafts for human review. It groups related cases using embeddings and clustering, gives each group a readable label, and generates structured answers linked to their supporting cases.

The repository implements the FAQ workflow with a Python/FastAPI backend and an Angular frontend. Documentation update suggestions remain future work.

## What is implemented

| Capability | Current behavior |
| --- | --- |
| Input validation | Loads normalized JSON records, validates them with Pydantic, and keeps resolved cases. |
| Issue clustering | Embeds case summaries and resolutions, then groups them with average-linkage hierarchical clustering using cosine distance. |
| Issue-family labeling | Uses an LLM to name each group; falls back to a generic label on labeling failure. |
| FAQ generation | Generates one draft per issue family, individually or in bulk, and validates the returned JSON against the FAQ schema. |
| Review UI | Lists drafts, shows their content and supporting evidence, and supports editing, approval, rejection, and bulk regeneration. Review changes are held in frontend memory only. |
| Support-record browsing | Displays the resolved records loaded by the backend. |
| Similarity inspection | Exposes a pairwise cosine-similarity matrix and includes a standalone interactive HTML viewer. |
| Provider handling | Includes Gemini and mock providers, plus retries and circuit-breaker handling around Gemini calls. |
| Localization | Includes English source strings and a Brazilian Portuguese frontend configuration. |

## How the workflow works

1. **Load solved cases.** On startup, the backend reads JSON files from `backend/data/`, validates each record, logs invalid entries, and filters to `status: "resolved"`.
2. **Find related issues.** It combines each case summary with its resolution, generates embeddings, and clusters the vectors. Grouping therefore considers both the problem and how it was resolved.
3. **Build issue families.** The LLM supplies a short label. Each family retains its case IDs, records, product areas, tags, and a similarity-based score.
4. **Generate drafts on request.** The API passes each family's summaries and resolutions to the LLM. The output includes a title, problem statement, cause explanation, fix steps, edge cases, and guidance on contacting support.
5. **Review the result.** The UI displays the generated content beside case evidence. Drafts start with review required; a reviewer can edit them or change their local review status.

Startup performs embedding, clustering, and labeling. FAQ generation happens separately through the UI or API. Restart the backend after changing the input files.

## Engineering choices and tradeoffs

### Inspectable grouping

[Clustering](backend/core/clustering.py) uses SciPy's average-linkage hierarchical clustering over pairwise cosine distances. A configurable distance cut controls grouping, followed by a minimum-size filter. This makes the grouping mechanism explicit, but pairwise distance storage grows quadratically with the number of cases.

The UI's **confidence score is the mean pairwise similarity within a cluster**, carried into the FAQ draft. It is not a calibrated probability that an answer is correct. Average linkage also does not guarantee that every pair in a retained cluster meets the configured similarity threshold.

### Structured generation with evidence

[FAQ generation](backend/core/faq_generation.py) parses model output as JSON and validates it with Pydantic before creating a draft. Supporting case IDs and evidence summaries remain attached to the result.

Schema validation checks the output's structure; it does not establish factual correctness. The review UI is part of the workflow for that reason.

Bulk generation is best effort: one family's failure does not discard successful drafts from other families. The response includes a `failures` array. Each bulk run replaces the backend's previous draft collection with that run's successful results.

### Provider boundaries

Separate [embedding](backend/core/embeddings_protocol.py) and [LLM](backend/core/llm_protocol.py) interfaces allow the pipeline to use Gemini or local mock implementations. Mock embeddings are deterministic hash-derived vectors, and mock text generation uses local logic. They exercise application plumbing without API calls; they do not demonstrate semantic or answer quality.

OpenAI appears in configuration enums but has no implemented provider.

### Failure handling

Both Gemini providers use the [circuit breaker](backend/core/circuit_breaker.py). The current settings allow up to five attempts for errors classified as retryable, with linear waits of 10, 20, 30, and 40 seconds. Three failed calls open the circuit; after 60 seconds, a later call can attempt recovery.

This is synchronous, process-local handling. Error classification relies on message matching, and waits block execution. Embedding failures can prevent startup; label failures receive fallback names. This implementation is not evidence of production resilience.

## Run locally

The commands below use a Unix-like shell. Use Python 3.11+ and Node.js 22.12+ in the Node 22 release line, with npm. The frontend declares Angular 21.2.

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

These model names are the repository's configured defaults, not a guarantee of current API availability. Select models available to your Gemini account if necessary. Gemini mode sends the case text used by the pipeline to the external API.

| Setting | Behavior |
| --- | --- |
| `CLUSTERING_MIN_CLUSTER_SIZE` | Defaults to 3. The single-record code path is an exception and returns a singleton. |
| `CLUSTERING_SIMILARITY_THRESHOLD` | The copied example sets 0.70; without an override, `Settings` defaults to 0.90. |
| `EMBEDDING_DIMENSION` | Controls mock vector dimensions; it is not passed as an output-dimension setting to Gemini. |

The startup loader currently uses `backend/data/`; the declared `DATA_DIR` setting is not wired into the application startup call.

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

The frontend is configured to use the real backend API. Use the draft-list regeneration action to generate the initial collection, then open a draft to inspect its evidence and review it.

After configuring `backend/.env`, `bash start.sh` is also available as a convenience launcher: it prepares dependencies and starts both services with the Portuguese UI.

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

See the [schema](backend/models/support_record.py) and [sample dataset](backend/data/sample_records.json). A single record is enough to illustrate the format; meaningful repeated-issue detection needs multiple related cases.

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

Open [backend/similarity_matrix_viewer.html](backend/similarity_matrix_viewer.html) in a browser and load that JSON file. The viewer supports threshold highlighting and record inspection, with an optional records JSON file. It is a separate local tool, not an Angular route.

## Current limitations and future work

- **No durable storage.** Backend drafts disappear on restart. Frontend edits and review statuses are not saved to the backend and disappear on page reload; regeneration also clears local overrides.
- **Review is a prototype workflow.** Approval changes local status to `Reviewed`; it does not publish content. Export and publishing are not implemented application workflows; export mockups exist under `stitch/`.
- **Documentation suggestions remain planned.** There is no implemented documentation-update generation pipeline.
- **Local batch processing.** Input normalization is external to this application. There are no platform connectors, live ingestion, background-job queue, or incremental embedding cache.
- **Quality and scale are unmeasured.** The repository does not establish answer accuracy, clustering quality, or production throughput through evaluation results or benchmarks.
- **Deployment hardening remains.** The API has no authentication and uses permissive CORS. Provider calls and retries are synchronous; circuit state and generated data are local to each process.
- **Bulk failure details are API-level.** The backend returns per-family failures, but the current frontend does not present that breakdown.

## Code map

| Path | Responsibility |
| --- | --- |
| [backend/main.py](backend/main.py) | FastAPI routes and in-memory application state. |
| [backend/startup.py](backend/startup.py) | Loading, validation, embeddings, clustering, and issue-family construction. |
| [backend/core/](backend/core/) | Clustering, labeling, FAQ generation, similarity, and provider interfaces. |
| [backend/providers/](backend/providers/) | Gemini and mock implementations. |
| [backend/models/](backend/models/) | Input, issue-family, and FAQ schemas. |
| [frontend/src/app/](frontend/src/app/) | Angular draft list, detail/edit views, records browser, and API access. |
| [stitch/](stitch/) | Design references and mockups; these do not define implemented behavior. |
