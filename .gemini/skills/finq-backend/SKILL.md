---
name: finq-backend
description: Development workflow for the FINQ FastAPI Python Backend. Use when touching database models, API handlers, and AI logic in the finq-backend directory.
author: SEC_extractor
version: 1.0.0
---

# 🚀 FinQ Backend Engineering Workflow

**Objective**: Guide agents when interacting with the Python backend to build new endpoints or debug existing API bugs efficiently.

## Core Rules
1. **Always Work within Virtual Environments**: Commands must be run scoped to `venv`. Always prefix script runs contextually:
   ```bash
   cd finq-backend
   source venv/bin/activate
   # Then run tools/python
   ```
2. **Schema Separation**: Pydantic models (in `app/schemas/`) must be entirely separate from SQLAlchemy models (in `app/models/`).
3. **Database Changes**: Modifying anything inside `finq-backend/app/models/` requires:
   ```bash
   cd finq-backend
   alembic revision --autogenerate -m "describe change"
   alembic upgrade head
   ```

## Routine Commands
### Running the Backend Locally
To debug endpoints:
```bash
cd finq-backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```
*Note*: WebSockets are on `/api/ws/` and AI endpoints are via Gemini under `/api/chat/`. Keep an eye out for `app/services/financial_analyzer.py` handling Quota Exceeded (429) errors, which is a known architectural quirk.

### Testing
Always validate your changes dynamically using `pytest`. The Pytest root is explicitly inside `finq-backend/tests/`.
```bash
cd finq-backend
source venv/bin/activate
pytest tests/
```
