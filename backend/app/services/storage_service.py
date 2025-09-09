from __future__ import annotations

from typing import List
import pandas as pd

from .. import notebook_adapter as nb


def generate_mock_metadata(n: int = 100, seed: int | None = None) -> pd.DataFrame:
    """Wrapper forwarding to notebook_adapter.generate_mock_metadata."""
    return nb.generate_mock_metadata(n=n, seed=seed)


def recommend_tiers_from_list(payload: List[dict]) -> List[dict]:
    df = pd.DataFrame(payload)
    rec_df = nb.recommend_best_tier(df)
    results = []
    for _, row in rec_df.iterrows():
        results.append(
            {
                "filename": row["filename"],
                "current_tier": row.get("tier", "cold"),
                "recommended_tier": row["recommended_tier"],
                "simulated_reward": float(row["simulated_reward"]),
            }
        )
    return results


def compute_costs_from_list(payload: List[dict]) -> dict:
    df = pd.DataFrame(payload)
    return nb.compute_costs(df)
