"""Main FastAPI application."""

import logging

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.startup import (
    validate_records_on_startup,
    setup_logging,
    initialize_embedding_provider,
    initialize_llm_provider,
    generate_embeddings_and_cluster,
    generate_labels_for_clusters,
    build_issue_families,
)
from backend.core.faq_generation import FAQGenerationService
from backend.core.similarity import compute_similarity_matrix


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


class GenerateFAQRequest(BaseModel):
    """Payload for generating one FAQ draft from one issue family."""

    issue_family_index: int = Field(..., ge=0, description="Zero-based index from /clusters")

# Store validated records in app state
@app.on_event("startup")
async def startup_event():
    """Validate records, initialize services, and cluster on startup."""
    logger.info("Starting up Support Knowledge Copilot...")
    
    # Validate and load records
    records = validate_records_on_startup()
    app.state.records = records
    logger.info(f"Loaded {len(records)} resolved support records")
    
    # Initialize embedding provider
    embedding_provider = initialize_embedding_provider()
    app.state.embedding_provider = embedding_provider
    
    # Initialize LLM provider
    llm_provider = initialize_llm_provider()
    app.state.llm_provider = llm_provider
    app.state.faq_drafts = {}
    
    # Generate embeddings and cluster records
    if records:
        embeddings, clusters = generate_embeddings_and_cluster(records, embedding_provider)
        app.state.record_embeddings = embeddings
        
        # Generate labels for clusters
        labeled_clusters = generate_labels_for_clusters(clusters, records, llm_provider)
        app.state.issue_clusters = labeled_clusters
        app.state.issue_families = build_issue_families(labeled_clusters, records)
        
        logger.info(f"Generated {len(embeddings)} embeddings and identified {len(labeled_clusters)} issue families")
    else:
        app.state.record_embeddings = {}
        app.state.issue_clusters = []
        app.state.issue_families = []
        app.state.faq_drafts = {}
    
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


@app.get("/clusters")
async def list_clusters():
    """List standardized issue families with full supporting records."""
    issue_families = getattr(app.state, "issue_families", [])

    return {
        "total": len(issue_families),
        "clusters": [family.model_dump(mode="json") for family in issue_families],
    }


@app.get("/similarity-matrix")
async def get_similarity_matrix():
    """
    Get pairwise cosine similarity matrix for all record embeddings.

    Returns:
        JSON with record_ids (axis labels) and N×N similarity matrix
    """
    if not app.state.record_embeddings:
        return {
            "record_ids": [],
            "similarity_matrix": [],
            "metadata": {
                "dimension": 0,
                "records_counted": 0,
                "method": "cosine",
            },
        }

    try:
        record_ids, similarity_matrix = compute_similarity_matrix(app.state.record_embeddings)
        
        return {
            "record_ids": record_ids,
            "similarity_matrix": similarity_matrix.tolist(),
            "metadata": {
                "dimension": app.state.record_embeddings[record_ids[0]].__len__() if record_ids else 0,
                "records_counted": len(record_ids),
                "method": "cosine",
            },
        }
    except Exception as e:
        logger.error(f"Error computing similarity matrix: {e}")
        return {
            "error": str(e),
            "record_ids": [],
            "similarity_matrix": [],
        }


@app.post("/faqs/generate")
async def generate_faq(request: GenerateFAQRequest):
    """Generate one FAQ draft from one issue family by index."""
    issue_families = getattr(app.state, "issue_families", [])
    llm_provider = getattr(app.state, "llm_provider", None)

    if llm_provider is None:
        raise HTTPException(status_code=500, detail="LLM provider not initialized")

    if request.issue_family_index >= len(issue_families):
        raise HTTPException(status_code=404, detail="Issue family index out of range")

    target_family = issue_families[request.issue_family_index]
    service = FAQGenerationService(llm_provider)

    try:
        draft = service.generate_faq_draft(target_family)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.error(f"Unexpected FAQ generation error: {exc}")
        raise HTTPException(status_code=500, detail="FAQ generation failed") from exc

    app.state.faq_drafts[draft.faq_id] = draft

    return draft.model_dump(mode="json")


@app.get("/faqs")
async def list_faqs():
    """List generated FAQ drafts currently stored in memory."""
    faq_drafts = getattr(app.state, "faq_drafts", {})

    return {
        "total": len(faq_drafts),
        "faqs": [draft.model_dump(mode="json") for draft in faq_drafts.values()],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
