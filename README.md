# Support Knowledge Copilot

## Project overview
Support Knowledge Copilot is an MVP that turns historical solved support cases into reusable knowledge.

The project has two main parts:
- a backend that reads normalized support records, detects repeated solved issues, and generates knowledge outputs
- a frontend that lets users run the generation flow and review the generated outputs

## MVP scope
The MVP focuses on two core capabilities:
- FAQ draft generation from repeated solved support issues
- documentation update suggestions from repeated solved support issues

At this stage, the project should stay focused on the core generation workflow.

## Input data
The system consumes pre-normalized support records from JSON files.

Supported source types:
- tickets
- chat logs
- escalations
- call transcripts
- refund reasons

One record represents one support case or conversation.

Only solved cases are used in the generation pipeline.

## Backend
The backend is responsible for:
- loading normalized support records
- validating the input schema
- detecting repeated solved issues
- generating FAQ drafts
- generating documentation update suggestions
- storing generated outputs
- exposing an API for the frontend

## Frontend
The frontend is responsible for:
- listing generated outputs
- opening a detailed view for each generated item
- allowing review actions such as edit, approve, reject, and export
- triggering generation and regeneration through the backend API

## Tech stack
### Backend
- Python
- API layer for frontend consumption
- JSON files as the initial data source

### Frontend
- TypeScript
- web UI consuming the backend API

## Current implementation direction
The project will be built step by step.

The recommended order is:
1. backend foundation
2. one feature at a time
3. frontend after the related backend flow exists

## Current feature status
### FAQ generation
This feature is already narrowed down and can be built first.

### Documentation update suggestions
This feature will be specified separately before implementation.

## Out of scope for now
- external platform integrations
- real-time ingestion
- analytics dashboards
- trend visualizations
- live support tooling
- publishing workflows

## Goal of this repository
This repository is meant to hold a focused MVP that demonstrates a complete end-to-end workflow:
- load solved support data
- identify repeated issues
- generate knowledge outputs
- review those outputs in a frontend
