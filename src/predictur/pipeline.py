"""End-to-end forecasting pipeline.

Loads the master series, builds exog regressors, runs walk-forward CV for
SARIMAX, ETS, and Prophet, builds an inverse-MAPE-weighted ensemble, and
writes the metrics + per-fold predictions to ``reports/``.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .data import load_series
from .features import build_exog
from .evaluation import cross_validate, summarize_cv
from .models import ETSForecaster, ProphetForecaster, SarimaForecaster
from .models.ensemble import build_ensemble_predictions, inverse_mape_weights

REPORTS_DIR = Path("reports")


def run_pipeline(
    initial_train: int = 48,
    horizon: int = 6,
    step: int = 1,
    reports_dir: Path = REPORTS_DIR,
    verbose: bool = True,
) -> dict:
    """Run the full forecasting comparison.

    Returns a dict with keys:

    - ``cv_predictions``: long DataFrame of all base + ensemble predictions
    - ``metrics``: per-model MAE/RMSE/MAPE summary
    - ``weights``: ensemble weights actually used
    """
    y = load_series()
    exog = build_exog(y.index)
    if verbose:
        print(f"Series: {y.index[0].date()} → {y.index[-1].date()}  "
              f"({len(y)} obs)")
        print(f"Exog regressors: {list(exog.columns)}")

    factories = {
        "SARIMAX": lambda: SarimaForecaster(),
        "ETS": lambda: ETSForecaster(),
        "Prophet": lambda: ProphetForecaster(),
    }

    all_results: list[pd.DataFrame] = []
    for name, factory in factories.items():
        if verbose:
            print(f"\n=== {name} ===")
        df = cross_validate(
            factory, y, exog=exog,
            initial_train=initial_train, horizon=horizon, step=step,
            verbose=verbose,
        )
        all_results.append(df)

    base = pd.concat(all_results, ignore_index=True)
    weights = inverse_mape_weights(base)
    ensemble = build_ensemble_predictions(base, weights=weights)
    full = pd.concat([base, ensemble], ignore_index=True)

    metrics = summarize_cv(full)

    reports_dir.mkdir(parents=True, exist_ok=True)
    full.to_csv(reports_dir / "cv_predictions.csv", index=False)
    metrics.to_csv(reports_dir / "metrics.csv", index=False)
    pd.Series(weights, name="weight").to_csv(
        reports_dir / "ensemble_weights.csv"
    )

    if verbose:
        print("\n=== Ensemble weights ===")
        for m, w in weights.items():
            print(f"  {m:<10s} {w:6.3f}")
        print("\n=== Metrics (sorted by MAPE) ===")
        print(metrics.to_string(index=False))

    return {
        "cv_predictions": full,
        "metrics": metrics,
        "weights": weights,
    }


def main() -> None:
    run_pipeline()


if __name__ == "__main__":
    main()
