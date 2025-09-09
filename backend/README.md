# TierOptimizer backend

FastAPI backend for TierOptimizer — exposes endpoints to generate mock file metadata, recommend storage tiers and compute cost summaries based on the notebook logic from `Cloud.ipynb`.

Run locally (create a venv first):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Available endpoints:

- GET /health
- POST /generate-mock -> accepts {n: int, seed: int}
- POST /recommend-tiers -> accepts list of FileMetadata
- POST /compute-costs -> accepts list of FileMetadata (or with recommended_tier)

## CI / pull request

This repository includes a GitHub Actions workflow that runs the backend test-suite on Python 3.11 and 3.12. When you open a pull request the CI will run tests automatically. Before opening a PR, ensure tests pass locally with:

```bash
cd backend
pytest -q
```
