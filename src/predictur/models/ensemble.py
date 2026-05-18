"""Weighted ensemble combining the per-fold predictions of base models.

The ensemble is computed *post-hoc* from the CV results dataframe rather than
re-fit during walk-forward. Weights are inversely proportional to each base
model's overall MAPE on the validation folds (so the worst model pulls less
weight). This is simple, transparent, and avoids leaking test data.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from ..evaluation import mape


def inverse_mape_weights(cv_results: pd.DataFrame) -> dict[str, float]:
    """Compute weights ∝ 1 / MAPE per model, normalised to sum to 1."""
    weights = {}
    for model, group in cv_results.groupby("model"):
        m = mape(group["y_true"], group["y_pred"])
        weights[model] = 1.0 / m if m > 0 else 0.0
    total = sum(weights.values())
    if total == 0:
        n = len(weights)
        return {k: 1.0 / n for k in weights}
    return {k: v / total for k, v in weights.items()}


def build_ensemble_predictions(
    cv_results: pd.DataFrame,
    weights: dict[str, float] | None = None,
    name: str = "Ensemble",
) -> pd.DataFrame:
    """Combine per-model CV predictions into a single weighted forecast.

    Returns a frame in the same long format as ``cv_results`` (with
    ``model == name``), suitable for concatenation and re-summarising.
    """
    if weights is None:
        weights = inverse_mape_weights(cv_results)

    pivot = cv_results.pivot_table(
        index=["fold_id", "Date"], columns="model", values="y_pred"
    )
    truth = (
        cv_results.groupby(["fold_id", "Date"])["y_true"]
        .first()
        .rename("y_true")
    )

    # Align weights to whatever models are actually in the pivot
    w = pd.Series({m: weights.get(m, 0.0) for m in pivot.columns})
    if w.sum() == 0:
        w = pd.Series(1.0 / len(pivot.columns), index=pivot.columns)
    else:
        w = w / w.sum()

    y_pred = (pivot * w).sum(axis=1)
    out = pd.concat([truth, y_pred.rename("y_pred")], axis=1).reset_index()
    out["model"] = name
    return out[["fold_id", "Date", "y_true", "y_pred", "model"]]
