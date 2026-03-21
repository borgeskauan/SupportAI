# Support Knowledge Copilot - Project Overview

## Purpose
MVP that turns historical solved support cases into reusable knowledge through FAQ draft generation and documentation update suggestions.

## Architecture
- **Backend**: Python with FastAPI, serves JSON files as initial data source
- **Frontend**: TypeScript with web UI
- **Database**: JSON files (MVP stage)

## Core Features (MVP)
1. **FAQ Generation**: Generate draft FAQs from repeated solved support issues
2. **Documentation Suggestions**: Generate documentation update suggestions (TBD)

## Key Concepts
- Input: Pre-normalized support records (one per case/conversation)
- Sources: tickets, chat logs, escalations, call transcripts, refund reasons
- Processing: Semantic similarity clustering using embeddings
- Output: Draft customer-facing FAQs with evidence and confidence scores

## Status Workflow
- Draft → Reviewed → Rejected

## Current Phase
Building backend foundation with normalized schema and core generation pipeline.