# Suggested Commands

## Setup
- `pip install fastapi uvicorn pydantic` - Install core backend dependencies
- `pip install black ruff mypy pytest` - Install dev tools

## Development
- `uvicorn main:app --reload` - Start FastAPI development server
- `black .` - Format Python code
- `ruff check .` - Lint Python code
- `mypy .` - Type checking
- `pytest` - Run tests

## Project Structure
- `backend/` - Python FastAPI application
  - `models/` - Pydantic models and schemas
  - `api/` - API endpoints
  - `core/` - Core logic (processing, clustering)
  - `data/` - Sample data and fixtures
- `frontend/` - TypeScript web application (TBD)
- `tests/` - Test suite