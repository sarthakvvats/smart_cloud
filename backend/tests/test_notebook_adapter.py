import pytest
import pandas as pd

from app import notebook_adapter as nb


def test_generate_mock_metadata_shape_and_types():
    df = nb.generate_mock_metadata(n=10, seed=1)
    assert len(df) == 10
    assert "filename" in df.columns
    assert df["access_freq"].between(0, 1).all()


def test_recommend_best_tier_adds_columns():
    df = nb.generate_mock_metadata(n=5, seed=2)
    rec = nb.recommend_best_tier(df)
    assert "recommended_tier" in rec.columns
    assert "simulated_reward" in rec.columns


def test_movement_matrix_and_summary():
    df = pd.DataFrame(
        [
            {"filename": "a", "access_freq": 0.9, "size_MB": 1, "last_accessed": 0.1, "tier": "cold"},
            {"filename": "b", "access_freq": 0.1, "size_MB": 0.5, "last_accessed": 0.2, "tier": "hot"},
        ]
    )
    rec = nb.recommend_best_tier(df)
    mat = nb.movement_matrix(rec)
    summ = nb.movement_summary(rec)
    assert isinstance(mat, pd.DataFrame)
    assert isinstance(summ, dict)
