from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .models import FileMetadata, RecommendationResult, CostSummary, MockGenerateRequest
from .services.storage_service import (
    generate_mock_metadata,
    recommend_tiers_from_list,
    compute_costs_from_list,
)

app = FastAPI(title="TierOptimizer - storage tier optimization API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/generate-mock", response_model=List[FileMetadata])
async def generate_mock(req: MockGenerateRequest):
    df = generate_mock_metadata(n=req.n, seed=req.seed)
    records = df.to_dict(orient="records")
    cleaned = [{str(k): (v.item() if hasattr(v, 'item') else v) for k, v in r.items()} for r in records]
    return [FileMetadata(**rec) for rec in cleaned]


@app.post("/recommend-tiers", response_model=List[RecommendationResult])
async def recommend_tiers(payload: List[FileMetadata]):
    try:
        results = recommend_tiers_from_list([p.model_dump() for p in payload])
        return [RecommendationResult(**r) for r in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compute-costs", response_model=CostSummary)
async def compute_costs(payload: List[FileMetadata]):
    try:
        summary = compute_costs_from_list([p.model_dump() for p in payload])
        return CostSummary(**summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
