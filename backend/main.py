"""Main FastAPI application."""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.startup import validate_records_on_startup, setup_logging


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Support Knowledge Copilot",
    description="API for generating and managing FAQ drafts from solved support cases",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store validated records in app state
@app.on_event("startup")
async def startup_event():
    """Validate records on startup."""
    logger.info("Starting up Support Knowledge Copilot...")
    records = validate_records_on_startup()
    app.state.records = records
    logger.info("Startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Support Knowledge Copilot")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "records_loaded": len(app.state.records),
    }


@app.get("/records")
async def list_records():
    """List all loaded support records."""
    return {
        "total": len(app.state.records),
        "records": [record.model_dump(mode="json") for record in app.state.records],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
