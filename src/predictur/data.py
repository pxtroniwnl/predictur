"""Data loading utilities for the master tourism series."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd

# Resolve the project root from this file's location so that loading works
# regardless of the caller's current working directory (notebooks, scripts,
# tests, etc.). ``__file__`` lives at ``<root>/src/predictur/data.py``.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CSV = PROJECT_ROOT / "data" / "processed" / "master_tourism_series.csv"
TARGET_COL = "Ocupacion_Caribe"


def load_series(
    csv_path: Optional[Path] = None,
    target: str = TARGET_COL,
    freq: str = "MS",
) -> pd.Series:
    """Load the target series indexed by month-start datetime.

    Parameters
    ----------
    csv_path : Path, optional
        Path to the master CSV. Defaults to ``data/processed/master_tourism_series.csv``.
    target : str
        Column name to extract. Defaults to ``Ocupacion_Caribe``.
    freq : str
        Pandas frequency string for the resulting index. ``MS`` = month start.

    Returns
    -------
    pd.Series
        Series of floats indexed by ``DatetimeIndex`` with monthly frequency.
    """
    path = Path(csv_path) if csv_path else DEFAULT_CSV
    df = pd.read_csv(path, parse_dates=["Date"])
    df = df.sort_values("Date").set_index("Date")
    s = df[target].astype(float)
    s.index = pd.DatetimeIndex(s.index, freq=freq)
    s.name = target
    return s


def load_full_frame(csv_path: Optional[Path] = None, freq: str = "MS") -> pd.DataFrame:
    """Load the full master CSV with all columns indexed by date."""
    path = Path(csv_path) if csv_path else DEFAULT_CSV
    df = pd.read_csv(path, parse_dates=["Date"])
    df = df.sort_values("Date").set_index("Date")
    df.index = pd.DatetimeIndex(df.index, freq=freq)
    return df
