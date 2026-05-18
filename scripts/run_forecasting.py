#!/usr/bin/env python3
"""Run the full forecasting comparison pipeline.

Usage::

    python scripts/run_forecasting.py

Trains SARIMAX, ETS and Prophet under walk-forward CV (initial 48 months,
horizon 6, step 1), builds an inverse-MAPE-weighted ensemble, and writes
metrics + per-fold predictions to ``reports/``.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make ``src/`` importable when running as a plain script.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from predictur.pipeline import run_pipeline


if __name__ == "__main__":
    run_pipeline()
