# How to Run SupportAI

This guide explains how to set up and run the Support Knowledge Copilot project.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Setup

### 1. Create and Activate Virtual Environment

Create a Python virtual environment to isolate project dependencies:

```bash
python3 -m venv venv
```

Activate the virtual environment:

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 2. Install Dependencies

Install all required Python packages from `backend/requirements.txt`:

```bash
pip install -r backend/requirements.txt
```

This will install:
- **FastAPI** (>=0.104.0) - Web framework for the backend API
- **Uvicorn** (>=0.24.0) - ASGI server
- **Pydantic** (>=2.0.0) - Data validation
- **python-multipart** (>=0.0.6) - File upload support
- **pytest** (>=7.0.0) - Testing framework
- **pytest-asyncio** (>=0.21.0) - Async testing support

### 3. Prepare Input Data

The backend requires normalized support records in JSON format placed in `backend/data/`:

```
backend/data/
└── sample_records.json
```

Records should follow the schema defined in `./SCHEMA.md` and include:
- Support case/problem text
- Resolution text
- Source type (tickets, chat logs, escalations, call transcripts, refund reasons)
- Only resolved cases are processed

## Running the Backend

### Before starting (One Command)

For the easiest setup, run from the project root:

```bash
source venv/bin/activate && pip install -r backend/requirements.txt
```

### Manual Run

Start the FastAPI server directly:

```bash
python -m uvicorn backend.main:app --reload
```

Either way will:
- Start the server on **http://localhost:8000**
- Enable hot-reload for development (server restarts on code changes)
- Validate all records in `backend/data/` on startup
- Filter to only include resolved support cases

### Access the API

- **API documentation**: http://localhost:8000/docs (interactive Swagger UI)
- **Alternative docs**: http://localhost:8000/redoc (ReDoc)

## Project Structure

The backend has been organized separately from the frontend:

```
SupportAI/
├── backend/
│   ├── main.py              # FastAPI application entry point
│   ├── startup.py           # Startup validation and logging setup
│   ├── config.py            # Configuration and environment variables
│   ├── core/                # Core validation and filtering logic
│   ├── models/              # Pydantic data models
│   ├── providers/           # LLM and embedding providers
│   ├── data/                # Input JSON records
│   ├── Backend-Spec.md      # Backend specification and requirements
│   ├── SCHEMA.md            # Data schema definition
│   ├── HOW_TO_RUN.md        # This file - Backend setup guide
│   └── requirements.txt     # Python dependencies
├── frontend/                # Angular frontend application
├── stitch/                  # Design components (HTML/UI)
├── README.md                # Main project documentation
└── venv/                    # Python virtual environment
```

## Key Features

- **FAQ Draft Generation** - Automatically generates FAQ drafts from repeated solved issues
- **Documentation Suggestions** - Suggests documentation updates based on patterns
- **Record Validation** - Validates input records on startup
- **Semantic Similarity Detection** - Groups similar issues using embeddings (minimum cluster size: 3)
- **Cross-Source Support** - Handles tickets, chat logs, escalations, call transcripts, and refund reasons

## Testing

Run tests with pytest:

```bash
pytest
```

For async test support:

```bash
pytest -v
```

## Troubleshooting

- **Port already in use**: Change the port with `python -m uvicorn backend.main:app --reload --port 8001`
- **Missing dependencies**: Ensure you ran `pip install -r backend/requirements.txt` from the project root
- **Validation errors**: Check that JSON files in `backend/data/` follow the `./SCHEMA.md` format
