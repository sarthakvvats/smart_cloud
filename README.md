# TierOptimizer (smart_cloud)

TierOptimizer is a lightweight prototype backend that analyzes file metadata and recommends storage tier moves (hot/warm/cold) to reduce cost while preserving access performance. The core logic was extracted from a research notebook and exposed as a small FastAPI service with tests and CI.

Quick summary
- Backend: FastAPI
- Core logic: `backend/app/notebook_adapter.py` (reward, recommendation, movement matrix, cost calc)
- Models: Pydantic v2 (`backend/app/models.py`)
- Tests: pytest in `backend/tests`
- CI: GitHub Actions runs backend tests on Python 3.11 and 3.12

Quickstart (local)
1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies and run the backend (from repo root):

```bash
pip install -r backend/requirements.txt
pip install -r backend/requirements-dev.txt
cd backend
uvicorn app.main:app --reload --port 8000
```

3. Run tests:

```bash
cd backend
pytest -q
```

Notes
- The API expects `FileMetadata.last_accessed` as an epoch float (seconds since epoch).
- For large datasets, replace in-memory pandas operations with a streaming/batch approach.
- The repository contains a sample CI workflow at `.github/workflows/ci.yml` which runs tests in the `backend` directory.

Contact / Contributing
- Open a PR against `main`. Use the PR template in `.github/PULL_REQUEST_TEMPLATE.md` to guide your submission.
