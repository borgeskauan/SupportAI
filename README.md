# SupportAI — Support Knowledge Copilot

SupportAI turns solved support cases into FAQ drafts. It finds recurring problems, drafts answers from previous resolutions, and shows the original cases alongside each draft so you can review and edit it.

This local prototype is built with Python/FastAPI and Angular. The interface is available in English and Brazilian Portuguese.

![FAQ detail showing a generated draft alongside three supporting cases and review controls](docs/images/faq-detail.png)

*A FAQ draft beside its supporting cases. Captured in the running app with synthetic cases and local demo mode.*

## How it works

1. **Add solved cases.** Place case files in `backend/data/`. On startup, the app checks their format and loads resolved cases.
2. **Find recurring problems.** The app compares case summaries and resolutions, groups similar cases, and names each group. These groups appear as *issue families* in the interface.
3. **Generate drafts.** Click **Generate / Regenerate FAQs** to create answers covering the problem, likely cause, fix steps, exceptions, and when to contact support.
4. **Review each answer.** Read the supporting cases beside the draft, edit the text, then approve or reject it. You can also browse all loaded cases under **Support Records**.

Grouping runs at startup; FAQ generation is a separate step. Restart the backend after changing case files. Generating again replaces the current drafts and clears local edits and review statuses.

## Understanding the results

### Related cases and confidence

The app groups cases based on how similar their summaries and resolutions are. A stricter similarity setting requires closer matches, and small groups are filtered out.

**Confidence describes the average similarity of cases in a group, not the accuracy of the answer.** Individual cases in a group can still differ.

The separate similarity viewer shows these comparisons as a color grid. Click a cell to inspect the two cases it compares.

![Standalone similarity matrix viewer showing four groups of synthetic cases with a 0.90 highlight threshold](docs/images/similarity-matrix.png)

*Twelve synthetic cases in four groups with repeated text. Captured in the standalone viewer using data from the app's local demo mode.*

### Drafts with supporting evidence

Each draft includes the cases used to generate it. The app checks that the answer has the required sections; you review the content against the evidence before using it.

If generation fails for one group, the app continues with the others. Failure details are available in the API response but are not shown in the interface yet.

### Gemini or local demo mode

- **Gemini** compares case text and generates answers through Google's API. It requires an API key and sends case text to that service.
- **Mock mode** runs locally without an API key. It uses simulated comparisons and template answers to exercise the interface. The screenshots use this mode with synthetic cases.

Mock mode can leave the FAQ list empty because the sample cases may not form qualifying groups. It is useful for trying the workflow; use Gemini to explore AI-generated results. OpenAI support is not implemented.

## Run locally

Prerequisites: a Unix-like shell, Python 3.11+, Node.js 22.x (22.12 or later), and npm. The frontend uses Angular 21.2.

### 1. Set up the backend

From the repository root:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r backend/requirements.txt
if [ ! -f backend/.env ]; then cp backend/.env.example backend/.env; fi
```

This installs the backend dependencies and creates a configuration file if you do not already have one. The example configuration uses mock mode.

<details>
<summary>Use Gemini</summary>

Set the following values in `backend/.env`, including your API key:

```dotenv
EMBEDDING_PROVIDER=gemini
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-embedding-001
LLM_MODEL=gemini-2.0-flash
```

These are the model names configured in the repository. Replace them if your account uses different models.

</details>

### 2. Start the backend

From the repository root, with the virtual environment active:

```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Wait for startup to finish. API documentation is available at [localhost:8000/docs](http://localhost:8000/docs).

### 3. Open the app

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

Click **Generate / Regenerate FAQs**, then open a draft to review its answer and supporting cases.

Alternatively, after configuring `backend/.env`, run `bash start.sh` to prepare dependencies and start both services with the Portuguese UI.

## Add your own cases

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

See the [sample cases](backend/data/sample_records.json) and [full field definitions](backend/models/support_record.py). Include several cases about the same problem so the app can identify recurring issues.

## Inspect case similarities

Keep the backend running. In another terminal at the repository root, save the comparison data and case records:

```bash
source venv/bin/activate
curl -fsS http://localhost:8000/similarity-matrix -o /tmp/supportai-similarity.json
curl -fsS http://localhost:8000/records | python -c 'import json, sys; json.dump(json.load(sys.stdin)["records"], sys.stdout)' > /tmp/supportai-records.json
```

Open the [standalone viewer](backend/similarity_matrix_viewer.html) in a desktop browser and load both files into their matching fields. Adjust the highlight threshold to explore closer matches, then click a cell to read the cases.

## Current scope

- **Temporary work.** Generated drafts are kept in backend memory and disappear on restart. Edits and review statuses are kept in the browser and disappear on reload or regeneration.
- **Review only.** Approving a draft marks it as `Reviewed` locally. Export and publishing are not implemented; screens under `stitch/` are design mockups.
- **File-based input.** Cases must be prepared in the expected JSON format. There are no automatic imports, live updates, or background processing.
- **Local prototype.** The API has no login or access controls. Answer quality, grouping quality, and performance have not been benchmarked.
- **Planned:** suggestions for updating existing documentation.

<details>
<summary>Developer reference: API, configuration, and implementation</summary>

### API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/health` | Application status and loaded-record count. |
| GET | `/records` | Loaded resolved support records. |
| GET | `/clusters` | Named groups and their supporting cases. |
| GET | `/similarity-matrix` | Case IDs and similarity scores for each pair. |
| POST | `/faqs/generate/{index}` | Generate a draft for one group; numbering starts at 0. |
| POST | `/faqs/generate` | Generate drafts for all groups; return drafts and failures. |
| GET | `/faqs` | List drafts currently held in backend memory. |

### Configuration

| Setting | Behavior |
| --- | --- |
| `CLUSTERING_MIN_CLUSTER_SIZE` | Minimum cases per group, normally 3. An input containing only one case is handled separately and returns a one-case group. |
| `CLUSTERING_SIMILARITY_THRESHOLD` | Higher values require closer matches. The example configuration uses 0.70; the code defaults to 0.90 if no value is set. |
| `EMBEDDING_DIMENSION` | Size of the numeric representation used in mock mode. Does not set Gemini's output size. |

Input is always read from `backend/data/`; the `DATA_DIR` setting is currently unused.

### Implementation notes

- [Grouping](backend/core/clustering.py) uses SciPy's average-linkage hierarchical clustering with cosine distance. The threshold applies to grouping, so not every pair must meet it. Comparing all pairs requires memory that grows with the square of the case count.
- [FAQ generation](backend/core/faq_generation.py) checks the answer structure with Pydantic and attaches case IDs and summaries. Bulk generation returns a `failures` array for groups it could not process.
- [Embedding](backend/core/embeddings_protocol.py) and [text-generation](backend/core/llm_protocol.py) interfaces support Gemini and local mocks. Mock comparisons use hash-derived vectors rather than semantic meaning.
- [Gemini error handling](backend/core/circuit_breaker.py) retries temporary failures and pauses further calls after repeated failures. Retries block the current operation. Failures while comparing cases can prevent startup; failed group naming uses fallback labels.
- The API allows requests from any origin (permissive CORS) and has no authentication. Embeddings and drafts are not stored permanently.

</details>
