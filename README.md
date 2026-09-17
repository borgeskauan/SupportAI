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

If generation fails for one group, the app continues with the others.

### Gemini or local demo mode

- **Gemini** compares case text and generates answers through Google's API. It requires an API key and sends case text to that service.
- **Mock mode** runs locally without an API key. It uses simulated comparisons and template answers to exercise the interface. The screenshots use this mode with synthetic cases.

Mock mode can leave the FAQ list empty because the sample cases may not form qualifying groups. Use Gemini to explore AI-generated results.

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

To use Gemini, follow the [configuration guide](docs/developer-reference.md#use-gemini).

### 2. Start the backend

From the repository root, with the virtual environment active:

```bash
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Wait for startup to finish before opening the app.

### 3. Open the app

In a second terminal:

```bash
cd frontend
npm ci
npm start
```

Open [localhost:4200](http://localhost:4200), click **Generate / Regenerate FAQs**, then open a draft to review its answer and supporting cases. [Brazilian Portuguese setup](docs/developer-reference.md#brazilian-portuguese) is also available.

## Add your own cases

Use the [sample cases](backend/data/sample_records.json) as a starting point. Save your files in `backend/data/`, then restart the backend. Include several solved cases about the same problem so the app can identify recurring issues. See the [case format guide](docs/developer-reference.md#case-format) for the required fields.

## Current scope

- **Temporary work.** Generated drafts are kept in backend memory and disappear on restart. Edits and review statuses are kept in the browser and disappear on reload or regeneration.
- **Review only.** Approving a draft marks it as `Reviewed` locally. Export and publishing are not implemented; screens under `stitch/` are design mockups.
- **File-based input.** Cases must be prepared in the expected JSON format. There are no automatic imports, live updates, or background processing.
- **Local prototype.** The API has no login or access controls. Answer quality, grouping quality, and performance have not been benchmarked.
- **Planned:** suggestions for updating existing documentation.

For API endpoints, configuration options, similarity viewer instructions, and implementation notes, see the [developer reference](docs/developer-reference.md).
