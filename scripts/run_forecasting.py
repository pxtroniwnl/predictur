#!/usr/bin/env python3
"""Run the full forecasting pipeline.

Usage::

    # Full pipeline: walk-forward CV + future forecast (default)
    python scripts/run_forecasting.py

    # Only future forecast (skips CV, uses existing reports/ensemble_weights.csv)
    python scripts/run_forecasting.py --forecast-only

    # Custom forecast horizon (months)
    python scripts/run_forecasting.py --forecast-only --horizon 24
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from predictur.pipeline import run_pipeline
from predictur.forecast import run_forecast


def main() -> None:
    parser = argparse.ArgumentParser(description="Predictur forecasting pipeline")
    parser.add_argument(
        "--forecast-only",
        action="store_true",
        help="Skip walk-forward CV and only generate future forecasts",
    )
    parser.add_argument(
        "--horizon",
        type=int,
        default=12,
        help="Number of future months to forecast (default: 12)",
    )
    args = parser.parse_args()

    if args.forecast_only:
        run_forecast(horizon=args.horizon, verbose=True)
    else:
        run_pipeline()
        print("\n" + "=" * 60)
        print("FUTURE FORECAST")
        print("=" * 60)
        run_forecast(horizon=args.horizon, verbose=True)


if __name__ == "__main__":
    main()
