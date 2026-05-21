"""Operational forecasting: train on the full series, predict future months.

Each base model is re-fit on the complete available history and produces
point forecasts plus confidence intervals for the requested horizon.

The ensemble forecast is a weighted average of the three base model point
forecasts, using the inverse-MAPE weights derived from walk-forward CV
(loaded from ``reports/ensemble_weights.csv`` if available, otherwise
computed on-the-fly from ``reports/metrics.csv``).

Output
------
``reports/forecast.csv`` — one row per (model, future date) with columns:

    Date, model, yhat, yhat_lower_80, yhat_upper_80,
    yhat_lower_95, yhat_upper_95, horizon

``horizon`` is the number of months ahead (1 = next month, 12 = one year out).
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from .data import load_series, PROJECT_ROOT
from .features import build_exog
from .models import ETSForecaster, ProphetForecaster, SarimaForecaster

REPORTS_DIR = PROJECT_ROOT / "reports"


# ---------------------------------------------------------------------------
# Interval helpers
# ---------------------------------------------------------------------------

def _sarimax_intervals(result, steps: int, exog, alpha_list=(0.20, 0.05)):
    """Return point + CI from a fitted SARIMAX result object."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        fc = result.get_forecast(steps=steps, exog=exog)
    point = fc.predicted_mean
    rows = {"yhat": point}
    for alpha in alpha_list:
        pct = int(round((1 - alpha) * 100))
        ci = fc.conf_int(alpha=alpha)
        rows[f"yhat_lower_{pct}"] = ci.iloc[:, 0].values
        rows[f"yhat_upper_{pct}"] = ci.iloc[:, 1].values
    return pd.DataFrame(rows, index=point.index)


def _prophet_intervals(model, future_df):
    """Return point + CI from a fitted Prophet model."""
    fc = model.predict(future_df)
    return pd.DataFrame({
        "yhat":         fc["yhat"].values,
        "yhat_lower_80": fc["yhat_lower"].values,   # Prophet default is 80%
        "yhat_upper_80": fc["yhat_upper"].values,
        # Prophet doesn't expose 95% natively; approximate via scaling
        "yhat_lower_95": fc["yhat"].values - 1.96 / 1.28 * (fc["yhat"].values - fc["yhat_lower"].values),
        "yhat_upper_95": fc["yhat"].values + 1.96 / 1.28 * (fc["yhat_upper"].values - fc["yhat"].values),
    }, index=pd.DatetimeIndex(fc["ds"].values))


def _ets_intervals(result, steps: int, alpha_list=(0.20, 0.05)):
    """Return point + CI from a fitted Holt-Winters result.

    statsmodels ExponentialSmoothing.simulate() gives us prediction intervals
    via simulation (1 000 paths). This is the recommended approach for ETS.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        point = result.forecast(steps)
        # simulate 1 000 paths to get empirical quantiles
        sim = result.simulate(nsimulations=steps, repetitions=1_000, error="add")

    rows = {"yhat": point.values}
    for alpha in alpha_list:
        pct = int(round((1 - alpha) * 100))
        lo = np.quantile(sim, alpha / 2, axis=1)
        hi = np.quantile(sim, 1 - alpha / 2, axis=1)
        rows[f"yhat_lower_{pct}"] = lo
        rows[f"yhat_upper_{pct}"] = hi
    return pd.DataFrame(rows, index=point.index)


# ---------------------------------------------------------------------------
# Per-model full-series forecasters
# ---------------------------------------------------------------------------

def _forecast_sarimax(
    y: pd.Series,
    exog_train: pd.DataFrame,
    exog_future: pd.DataFrame,
    horizon: int,
) -> pd.DataFrame:
    m = SarimaForecaster()
    m.fit(y, exog=exog_train)
    df = _sarimax_intervals(m._result, steps=horizon, exog=exog_future)
    df.index.name = "Date"
    df["model"] = "SARIMAX"
    return df.reset_index()


def _forecast_ets(
    y: pd.Series,
    exog_train: pd.DataFrame,
    exog_future: pd.DataFrame,
    horizon: int,
) -> pd.DataFrame:
    m = ETSForecaster()
    m.fit(y, exog=exog_train)

    # ETS two-stage: get base ETS intervals then add back the linear exog term
    df = _ets_intervals(m._result, steps=horizon)

    if m._reg is not None and m._exog_cols:
        adj = m._reg.predict(exog_future[m._exog_cols].values)
        for col in df.columns:
            if col != "model":
                df[col] = df[col].values + adj

    # Rebuild index: ETS forecast() returns integer index after the train end
    future_idx = pd.date_range(
        start=y.index[-1] + pd.offsets.MonthBegin(1),
        periods=horizon,
        freq="MS",
    )
    df.index = future_idx
    df.index.name = "Date"
    df["model"] = "ETS"
    return df.reset_index()


def _forecast_prophet(
    y: pd.Series,
    exog_train: pd.DataFrame,
    exog_future: pd.DataFrame,
    horizon: int,
) -> pd.DataFrame:
    m = ProphetForecaster()
    m.fit(y, exog=exog_train)

    future_idx = pd.date_range(
        start=y.index[-1] + pd.offsets.MonthBegin(1),
        periods=horizon,
        freq="MS",
    )
    future_df = pd.DataFrame({"ds": future_idx})
    for col in m._exog_cols:
        future_df[col] = exog_future[col].values

    df = _prophet_intervals(m._model, future_df)
    df.index.name = "Date"
    df["model"] = "Prophet"
    return df.reset_index()


# ---------------------------------------------------------------------------
# Ensemble
# ---------------------------------------------------------------------------

def _build_ensemble_forecast(
    base_forecasts: list[pd.DataFrame],
    weights: dict[str, float],
) -> pd.DataFrame:
    """Weighted average of point forecasts; intervals via weighted average too."""
    pivot_point = (
        pd.concat(base_forecasts)
        .pivot(index="Date", columns="model", values="yhat")
    )
    w = pd.Series({m: weights.get(m, 0.0) for m in pivot_point.columns})
    w = w / w.sum()

    yhat = (pivot_point * w).sum(axis=1)

    # Weighted average of intervals (conservative but transparent)
    ci_cols = ["yhat_lower_80", "yhat_upper_80", "yhat_lower_95", "yhat_upper_95"]
    ci_frames = {}
    for col in ci_cols:
        pivot_ci = (
            pd.concat(base_forecasts)
            .pivot(index="Date", columns="model", values=col)
        )
        ci_frames[col] = (pivot_ci * w).sum(axis=1)

    out = pd.DataFrame({"yhat": yhat, **ci_frames})
    out.index.name = "Date"
    out["model"] = "Ensemble"
    return out.reset_index()


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_forecast(
    horizon: int = 12,
    weights: Optional[dict[str, float]] = None,
    reports_dir: Path = REPORTS_DIR,
    verbose: bool = True,
) -> pd.DataFrame:
    """Train all models on the full series and forecast the next ``horizon`` months.

    Parameters
    ----------
    horizon : int
        Number of future months to forecast. Default 12 (one year ahead).
    weights : dict, optional
        Ensemble weights ``{model_name: weight}``. If ``None``, loaded from
        ``reports/ensemble_weights.csv``; if that file doesn't exist either,
        equal weights are used.
    reports_dir : Path
        Directory where ``forecast.csv`` will be written.
    verbose : bool
        Print progress to stdout.

    Returns
    -------
    pd.DataFrame
        Long-format frame with columns:
        ``Date, model, yhat, yhat_lower_80, yhat_upper_80,
        yhat_lower_95, yhat_upper_95, horizon``.
    """
    y = load_series()
    exog_train = build_exog(y.index)

    # Build future exog index
    future_idx = pd.date_range(
        start=y.index[-1] + pd.offsets.MonthBegin(1),
        periods=horizon,
        freq="MS",
    )
    exog_future = build_exog(future_idx)

    if verbose:
        print(f"Training on full series: {y.index[0].date()} → {y.index[-1].date()} ({len(y)} obs)")
        print(f"Forecasting {horizon} months: {future_idx[0].date()} → {future_idx[-1].date()}")

    # Load ensemble weights
    if weights is None:
        weights_path = reports_dir / "ensemble_weights.csv"
        if weights_path.exists():
            w_df = pd.read_csv(weights_path, index_col=0)
            weights = w_df["weight"].to_dict()
            if verbose:
                print(f"Loaded ensemble weights from {weights_path.name}")
        else:
            weights = {"SARIMAX": 1/3, "ETS": 1/3, "Prophet": 1/3}
            if verbose:
                print("No weights file found — using equal weights")

    # Fit and forecast each base model
    base_forecasts: list[pd.DataFrame] = []

    if verbose:
        print("\n--- SARIMAX ---")
    df_sarima = _forecast_sarimax(y, exog_train, exog_future, horizon)
    base_forecasts.append(df_sarima)

    if verbose:
        print("--- ETS ---")
    df_ets = _forecast_ets(y, exog_train, exog_future, horizon)
    base_forecasts.append(df_ets)

    if verbose:
        print("--- Prophet ---")
    df_prophet = _forecast_prophet(y, exog_train, exog_future, horizon)
    base_forecasts.append(df_prophet)

    # Ensemble
    df_ensemble = _build_ensemble_forecast(base_forecasts, weights)
    all_forecasts = pd.concat(base_forecasts + [df_ensemble], ignore_index=True)

    # Add horizon column (months ahead, 1-based)
    date_to_horizon = {d: i + 1 for i, d in enumerate(future_idx)}
    all_forecasts["horizon"] = all_forecasts["Date"].map(date_to_horizon)

    # Clip to valid occupancy range [0, 100]
    for col in ["yhat", "yhat_lower_80", "yhat_upper_80", "yhat_lower_95", "yhat_upper_95"]:
        all_forecasts[col] = all_forecasts[col].clip(0, 100)

    # Round to 4 decimal places
    num_cols = ["yhat", "yhat_lower_80", "yhat_upper_80", "yhat_lower_95", "yhat_upper_95"]
    all_forecasts[num_cols] = all_forecasts[num_cols].round(4)

    # Save
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_path = reports_dir / "forecast.csv"
    all_forecasts.to_csv(out_path, index=False)

    if verbose:
        print(f"\nSaved {len(all_forecasts)} rows → {out_path}")
        print("\n=== Ensemble forecast (point) ===")
        ens = all_forecasts[all_forecasts.model == "Ensemble"][["Date", "yhat", "yhat_lower_95", "yhat_upper_95"]]
        print(ens.to_string(index=False))

    return all_forecasts
