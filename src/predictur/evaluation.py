"""Walk-forward time-series cross-validation and evaluation metrics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def mae(y_true: pd.Series, y_pred: pd.Series) -> float:
    return float(np.mean(np.abs(y_true.values - y_pred.values)))


def rmse(y_true: pd.Series, y_pred: pd.Series) -> float:
    return float(np.sqrt(np.mean((y_true.values - y_pred.values) ** 2)))


def mape(y_true: pd.Series, y_pred: pd.Series, eps: float = 1e-8) -> float:
    """Mean Absolute Percentage Error, in percent.

    Skips entries where |y_true| < ``eps`` to avoid division blow-ups (the
    occupancy series is bounded above ~9 so this is defensive).
    """
    y_t = y_true.values.astype(float)
    y_p = y_pred.values.astype(float)
    mask = np.abs(y_t) >= eps
    if not mask.any():
        return float("nan")
    return float(np.mean(np.abs((y_t[mask] - y_p[mask]) / y_t[mask])) * 100.0)


def all_metrics(y_true: pd.Series, y_pred: pd.Series) -> dict[str, float]:
    return {"MAE": mae(y_true, y_pred), "RMSE": rmse(y_true, y_pred),
            "MAPE": mape(y_true, y_pred)}


# ---------------------------------------------------------------------------
# Walk-forward splitter
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Fold:
    """A single walk-forward fold."""
    fold_id: int
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp
    train_idx: pd.DatetimeIndex
    test_idx: pd.DatetimeIndex


def walk_forward_splits(
    index: pd.DatetimeIndex,
    initial_train: int = 48,
    horizon: int = 6,
    step: int = 1,
) -> Iterator[Fold]:
    """Yield walk-forward folds with an expanding training window.

    Parameters
    ----------
    index : DatetimeIndex
        Full series index (must be sorted, monotonic).
    initial_train : int
        Size of the training window for the first fold (in observations).
    horizon : int
        Number of consecutive observations to predict per fold.
    step : int
        Number of observations the training window grows by between folds.

    Yields
    ------
    Fold
        Each fold expands the training window and rolls the test window forward.
    """
    n = len(index)
    if initial_train + horizon > n:
        raise ValueError(
            f"Series too short: need at least {initial_train + horizon} "
            f"obs, got {n}"
        )

    fold_id = 0
    train_size = initial_train
    while train_size + horizon <= n:
        train_idx = index[:train_size]
        test_idx = index[train_size:train_size + horizon]
        yield Fold(
            fold_id=fold_id,
            train_end=train_idx[-1],
            test_start=test_idx[0],
            test_end=test_idx[-1],
            train_idx=train_idx,
            test_idx=test_idx,
        )
        fold_id += 1
        train_size += step


# ---------------------------------------------------------------------------
# CV runner
# ---------------------------------------------------------------------------


def cross_validate(
    model_factory,
    y: pd.Series,
    exog: pd.DataFrame | None = None,
    initial_train: int = 48,
    horizon: int = 6,
    step: int = 1,
    verbose: bool = False,
) -> pd.DataFrame:
    """Run walk-forward CV for a single model and return a tidy results frame.

    ``model_factory`` must be a zero-arg callable that returns a fresh
    instance implementing the ``BaseForecaster`` protocol from ``models.base``.

    Returns
    -------
    pd.DataFrame
        Columns: ``fold_id, Date, y_true, y_pred, model``.
    """
    rows: list[dict] = []
    for fold in walk_forward_splits(y.index, initial_train, horizon, step):
        model = model_factory()
        y_train = y.loc[fold.train_idx]
        x_train = exog.loc[fold.train_idx] if exog is not None else None
        x_test = exog.loc[fold.test_idx] if exog is not None else None

        model.fit(y_train, exog=x_train)
        y_hat = model.predict(steps=len(fold.test_idx), exog=x_test)
        y_hat = pd.Series(np.asarray(y_hat), index=fold.test_idx)

        if verbose:
            print(
                f"fold {fold.fold_id:>2} | train→{fold.train_end.date()} "
                f"| test {fold.test_start.date()}→{fold.test_end.date()}"
            )
        for ts in fold.test_idx:
            rows.append({
                "fold_id": fold.fold_id,
                "Date": ts,
                "y_true": float(y.loc[ts]),
                "y_pred": float(y_hat.loc[ts]),
                "model": getattr(model, "name", model.__class__.__name__),
            })
    return pd.DataFrame(rows)


def summarize_cv(cv_results: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per-model metrics across all folds."""
    summary = []
    for model_name, group in cv_results.groupby("model"):
        m = all_metrics(group["y_true"], group["y_pred"])
        m["model"] = model_name
        m["n_obs"] = len(group)
        m["n_folds"] = group["fold_id"].nunique()
        summary.append(m)
    return (
        pd.DataFrame(summary)
        [["model", "MAE", "RMSE", "MAPE", "n_folds", "n_obs"]]
        .sort_values("MAPE")
        .reset_index(drop=True)
    )
