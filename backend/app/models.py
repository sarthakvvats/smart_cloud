from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field
from datetime import datetime


class FileMetadata(BaseModel):
    filename: str
    access_freq: float = Field(ge=0.0, le=1.0)
    size_MB: float = Field(gt=0.0)
    last_accessed: float
    tier: Literal["hot", "warm", "cold"]


class RecommendationResult(BaseModel):
    filename: str
    current_tier: Literal["hot", "warm", "cold"]
    recommended_tier: Literal["hot", "warm", "cold"]
    simulated_reward: float


class CostSummary(BaseModel):
    total_before: float
    total_after: float
    savings: float


class MockGenerateRequest(BaseModel):
    n: int = 100
    seed: int | None = None
