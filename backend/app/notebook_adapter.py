from __future__ import annotations

from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def df_from_payload(payload: List[dict]) -> pd.DataFrame:
    """Create a DataFrame from a list of dicts without mutating input.

    RORO: receives a list of dicts, returns a DataFrame.
    """
    return pd.DataFrame(payload).copy()


def generate_mock_metadata(n: int = 100, seed: Optional[int] = None) -> pd.DataFrame:
    """Generate deterministic mock file metadata similar to the notebook.

    Returns a DataFrame with columns: filename, access_freq, size_MB, last_accessed, tier
    """
    if seed is not None:
        np.random.seed(seed)

    # Represent last_accessed as an epoch timestamp (seconds) for numeric consistency
    now_ts = datetime.now().timestamp()
    # simulate last accessed within the past 365 days
    days_ago = np.random.randint(0, 365, size=n)
    last_accessed_ts = [float((datetime.now() - timedelta(days=int(d))).timestamp()) for d in days_ago]
    df = pd.DataFrame({
        "filename": [f"file_{i:05d}.dat" for i in range(n)],
        "access_freq": np.random.rand(n),
        "size_MB": np.random.uniform(0.1, 10.0, n),
        "last_accessed": last_accessed_ts,
        "tier": np.random.choice(["hot", "warm", "cold"], n),
    })

    return df


def calculate_reward(access: float, size: float, target_tier: str) -> float:
    """Deterministic reward formula ported from the notebook.

    Keeps numeric result stable and rounded to 3 decimals.
    """
    if target_tier == "hot":
        reward = (1.0 * access) - (0.2 * size)
    elif target_tier == "warm":
        reward = (0.6 * access) - (0.1 * size)
    else:
        reward = (0.2 * access) - (0.05 * size)

    return round(float(reward), 3)


def recommend_best_tier(df: pd.DataFrame) -> pd.DataFrame:
    """Return a new DataFrame with recommended_tier and simulated_reward columns.

    The function does not mutate the input DataFrame; it returns a copy.
    """
    df2 = df.copy().reset_index(drop=True)
    tiers = ["hot", "warm", "cold"]

    def best_and_reward(row) -> Tuple[str, float]:
        rewards = {t: calculate_reward(float(row["access_freq"]), float(row["size_MB"]), t) for t in tiers}
        # pick the (tier, reward) with maximum reward then return tier and reward
        best_tier, best_reward = max(rewards.items(), key=lambda kv: kv[1])
        return best_tier, best_reward

    recs = df2.apply(lambda r: best_and_reward(r), axis=1)
    df2["recommended_tier"] = [r[0] for r in recs]
    df2["simulated_reward"] = [r[1] for r in recs]

    return df2


def needs_movement_flag(df: pd.DataFrame) -> pd.DataFrame:
    """Add a boolean needs_movement column (copy returned).
    """
    df2 = df.copy()
    if "recommended_tier" not in df2.columns:
        df2 = recommend_best_tier(df2)
    df2["needs_movement"] = df2["tier"] != df2["recommended_tier"]
    return df2


def movement_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Return a transition matrix (current tier -> recommended tier) for files that need movement.

    The returned DataFrame has tiers as row/column indices and integer counts.
    """
    df2 = needs_movement_flag(df)
    movement_df = df2[df2["needs_movement"]]
    if movement_df.empty:
        # return an empty 3x3 frame with tiers
        tiers = ["cold", "warm", "hot"]
        return pd.DataFrame(0, index=tiers, columns=tiers)

    transition = movement_df.groupby(["tier", "recommended_tier"]).size().unstack(fill_value=0)
    # ensure consistent ordering
    for t in ["cold", "warm", "hot"]:
        if t not in transition.columns:
            transition[t] = 0
        if t not in transition.index:
            transition.loc[t] = 0
    transition = transition[["cold", "warm", "hot"]].loc[["cold", "warm", "hot"]]
    return transition.astype(int)


def movement_summary(df: pd.DataFrame) -> Dict[str, int]:
    """Return a compact dict summarizing movements as 'src → dst': count."""
    df2 = needs_movement_flag(df)
    move_map: Dict[Tuple[str, str], int] = {}
    for _, row in df2.iterrows():
        src = str(row["tier"])
        dst = str(row.get("recommended_tier", src))
        if src == dst:
            continue
        key: Tuple[str, str] = (src, dst)
        move_map.setdefault(key, 0)
        move_map[key] += 1

    return {f"{s} → {d}": cnt for (s, d), cnt in move_map.items()}


def generate_clean_normalized_dataset(n: int = 1000, seed: Optional[int] = 42) -> pd.DataFrame:
    """Generate a larger synthetic dataset with reasonable feature distributions and normalization.

    This mirrors the notebook's 'generate_clean_normalized_dataset' but avoids sklearn dependency.
    """
    if seed is not None:
        np.random.seed(seed)

    now = datetime.now()
    access_freq = np.clip(np.random.normal(0.5, 0.2, n), 0, 1)
    size_MB = np.clip(np.random.normal(500, 200, n), 10, 1000)
    last_access_days = np.clip(np.random.normal(15, 10, n), 0, 60)

    df = pd.DataFrame({
        "filename": [f"file_{i:04d}.dat" for i in range(n)],
        "access_freq": np.round(access_freq, 3),
        "size_MB": np.round(size_MB, 2),
        # store last_accessed as an epoch float (seconds since epoch) to keep types numeric
        "last_accessed": [float((now - timedelta(days=int(d))).timestamp()) for d in last_access_days],
        "file_type": np.random.choice([".log", ".csv", ".jpg", ".pdf", ".bin"], n),
        "user_group": np.random.choice(["analytics", "logs", "ml", "infra", "admin"], n),
    })

    def assign_tier(p: float) -> str:
        if p > 0.7:
            return "hot"
        if p > 0.3:
            return "warm"
        return "cold"

    df["tier"] = df["access_freq"].apply(assign_tier)

    # Normalization: min-max on selected numeric arrays
    numeric = pd.DataFrame({
        "access_freq": access_freq,
        "size_MB": size_MB,
        "last_accessed_days": last_access_days,
    })
    norm = (numeric - numeric.min()) / (numeric.max() - numeric.min())
    df[["access_freq", "size_MB", "last_accessed_days"]] = norm[["access_freq", "size_MB", "last_accessed_days"]]

    return df


def generate_access_time_series(df: pd.DataFrame, days: int = 30, seed: Optional[int] = 42) -> pd.DataFrame:
    """Create a time-series (days columns) of access counts per file.

    Returns a DataFrame with columns day_1 .. day_N and filename.
    """
    if seed is not None:
        np.random.seed(seed)

    access_matrix = []
    for _, row in df.iterrows():
        base = float(row.get("access_freq", 0.5)) * 10
        pattern = np.clip(np.random.normal(loc=base, scale=2.0, size=days), 0, 10)
        access_matrix.append(pattern)

    cols = [f"day_{i+1}" for i in range(days)]
    access_df = pd.DataFrame(access_matrix, columns=cols)
    access_df["filename"] = df["filename"].values
    return access_df


def compute_costs(df: pd.DataFrame, tier_cost_per_gb: Optional[Dict[str, float]] = None) -> Dict[str, float]:
    """Compute total_before/after and savings. Expects size_MB and tier columns; recommended_tier optional.

    Returns a dict with total_before, total_after, savings.
    """
    if tier_cost_per_gb is None:
        tier_cost_per_gb = {"hot": 0.10, "warm": 0.05, "cold": 0.01}

    df2 = df.copy()
    df2["size_GB"] = df2["size_MB"] / 1024.0
    df2["original_cost"] = df2.apply(lambda r: r["size_GB"] * tier_cost_per_gb.get(r.get("tier", "cold"), 0.01), axis=1)
    df2["agent_tier"] = df2.get("recommended_tier", df2["tier"])
    df2["agent_cost"] = df2.apply(lambda r: r["size_GB"] * tier_cost_per_gb.get(r.get("agent_tier", "cold"), 0.01), axis=1)

    total_before = float(df2["original_cost"].sum())
    total_after = float(df2["agent_cost"].sum())
    return {"total_before": total_before, "total_after": total_after, "savings": total_before - total_after}
