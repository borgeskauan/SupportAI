# Setup and First Run - Backend

## Issues Encountered and Fixed

### 1. Missing Dependencies
**Issue**: `ModuleNotFoundError: No module named 'fastapi'`
**Solution**: 
- Created virtual environment: `python -m venv .venv`
- Updated requirements.txt to use flexible version constraints (>= instead of ==) to handle wheel availability
- Installed with: `pip install -r requirements.txt`

### 2. Path Resolution Issue
**Issue**: Data directory path was incorrect in startup.py
**Original**: `Path(__file__).parent.parent / "data"`
**Fixed**: `Path(__file__).parent / "data"`
- The data directory is in `backend/data/`, not at project root

### 3. Module Import Issue
**Issue**: Running `python main.py` from backend directory failed with `ModuleNotFoundError: No module named 'backend'`
**Solution**: Run from project root with: `python -m backend.main`

## Successful Server Startup

### Requirements Updated
```
fastapi>=0.104.0
uvicorn>=0.24.0
pydantic>=2.0.0
python-multipart>=0.0.6
pytest>=7.0.0
pytest-asyncio>=0.21.0
```

Installed versions:
- fastapi 0.135.1
- pydantic 2.12.5
- uvicorn 0.42.0

### Running the Server
```bash
cd /home/orion/CentralHub/Studies/Main/SupportAI
source .venv/bin/activate
python -m backend.main
```

### Verification
✅ Server starts successfully on port 8000
✅ Loads 5 sample records from backend/data/sample_records.json
✅ Health check endpoint returns: `{"status": "healthy", "records_loaded": 5}`
✅ Records endpoint serves all 5 records with full schema validation

## Notes
- FastAPI shows deprecation warnings about `on_event` decorator (use lifespan handlers in future)
- All 5 sample records are properly validated and served
- Schema validation is working correctly
