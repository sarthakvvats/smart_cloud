# Intelligent Cloud Storage Tier Optimization (smart_cloud / TierOptimizer)

This repository started as a research prototype (in `Cloud.ipynb`) that explores cloud storage tier optimization using Reinforcement Learning (PPO) and access-pattern modeling. During sprint/hackathon work we extracted the core notebook logic into a compact, testable backend service named TierOptimizer and added tests and CI to make the work easy to demo and extend.

Two complementary entry points in this repo:

- Cloud.ipynb — the original notebook: data ingestion, PPO training experiments, visualizations, and research notes.
- backend/ — a FastAPI backend that exposes the notebook inference logic as HTTP endpoints for quick demos and integration.

Why both?

- The notebook is the experimental record (figures, PPO training, trace analysis).
- The backend is the engineering slice: the notebook's decision logic reimplemented as pure functions, validated by tests and ready to be integrated into a demo or a frontend.

Key features

- Research-grade prototype:
  - Reinforcement Learning (PPO) exploration in `Cloud.ipynb` (experimental, training code and plots).
  - Latency- and cost-aware reward formulations used during experiments.
- Production-lite backend (TierOptimizer):
  - FastAPI endpoints: `/generate-mock`, `/recommend-tiers`, `/compute-costs`, `/health`.
  - Canonical implementation in `backend/app/notebook_adapter.py` (reward, tier recommendation, movement matrix, cost calc).
  - Pydantic v2 models for input/output validation (`backend/app/models.py`).
  - Thin service layer (`backend/app/services/storage_service.py`) to isolate IO from core logic.
  - Unit tests under `backend/tests` and a GitHub Actions CI workflow that runs them on Python 3.11/3.12.

Data & cost model

- Original notebook used synthetic and WTA/Google trace subsets for evaluation.
- Current backend uses synthetic mock generators for demos. If you want to reproduce experiments, place the trace CSV next to `Cloud.ipynb` and follow the notebook cells.
- Example cost model used in experiments (INR per GB, illustrative):
  - Cold Tier: ₹0.33/GB (high latency)
  - Warm Tier: ₹0.825/GB
  - Hot Tier: ₹2.145/GB (low latency)

Compatibility & data types

- `FileMetadata.last_accessed` in the backend is represented as an epoch float (seconds since epoch) for numeric consistency across generators and Pydantic validation.

Quickstart (backend demo)

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

3. Run tests (recommended before opening PRs):

```bash
cd backend
pytest -q
```

How the backend extends `Cloud.ipynb`

- Extracted core algorithms into `notebook_adapter.py` so the same logic can be called from code (notebook -> library).
- Added small, deterministic mock data generators so the API can demo behavior without large trace files.
- Normalized timestamp handling and numpy scalar conversions so Pydantic models accept API inputs/outputs without errors.
- Added unit tests to protect behavior and a CI workflow to run those tests automatically on PRs.

Contributing & PRs

- We included a PR template (`.github/PULL_REQUEST_TEMPLATE.md`) and CI (`.github/workflows/ci.yml`). Run tests locally before opening a PR.
- If you intend to include the original dataset (`google_cluster_trace_25k.csv`), place it next to `Cloud.ipynb` and reference the notebook cells for the evaluation pipeline.

Notes and next steps

- The current backend uses in-memory pandas operations; for larger datasets switch to batching or a job/worker design.
- If you want datetimes instead of epoch floats, we can update Pydantic models to accept ISO datetimes and convert in the adapter.
- Confirm license placement: a `license.md` exists; ensure a canonical `LICENSE` file is present if you plan to redistribute.

Contact / Acknowledgements

- Original dataset and design inspiration: Workflow Trace Archive (WTA), Google Cloud traces.
- To propose changes, open a PR against `main` on the fork and tag reviewers.

## How to reproduce notebook experiments (quick checklist)

If you want to re-run the experiments in `Cloud.ipynb` and compare results with the backend outputs, follow this checklist. The right column shows the notebook concept/section and the backend function that implements the same logic (useful when validating parity).

1. Prepare dataset

- Notebook: data ingestion and preprocessing cells (load CSV, clean, sample)
- Backend mapping: `notebook_adapter.generate_clean_normalized_dataset` (for synthetic data) or use `df_from_payload` with your preprocessed DataFrame

2. Feature normalization & tier assignment

- Notebook: normalization & heuristic tier assignment cells
- Backend mapping: `notebook_adapter.generate_clean_normalized_dataset` (normalization), `notebook_adapter.recommend_best_tier` (recommendation)

3. Reward function / scoring

- Notebook: reward formula cells used by PPO training and evaluation
- Backend mapping: `notebook_adapter.calculate_reward`

4. Recommendation inference

- Notebook: inference/evaluation cells where per-file rewards are computed
- Backend mapping: `notebook_adapter.recommend_best_tier` (returns `recommended_tier` and `simulated_reward`)

5. Movement summary and transition matrix

- Notebook: aggregation/transition visualization cells
- Backend mapping: `notebook_adapter.movement_summary`, `notebook_adapter.movement_matrix`

6. Cost calculation and comparison

- Notebook: cost model & experiment-summary cells
- Backend mapping: `notebook_adapter.compute_costs`

7. Time-series access simulation (optional)

- Notebook: per-file time-series generation cells
- Backend mapping: `notebook_adapter.generate_access_time_series`

Quick verification steps

- Start the backend (see Quickstart above) and call `/generate-mock` to produce a deterministic dataset. Use the generated records, POST them to `/recommend-tiers`, then call `/compute-costs` on the original vs recommended tiers and compare the numbers to the notebook's evaluation cells.
- If you want to reproduce PPO training and visualizations, run the notebook cells; the backend is intended for inference/demo (not training).
