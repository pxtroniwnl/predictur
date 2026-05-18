"""Common interface for all forecasters used in walk-forward CV."""

from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd


class BaseForecaster(ABC):
    """Minimal protocol every model wrapper implements.

    The wrappers smooth over the API differences between statsmodels SARIMAX,
    statsmodels ETS, Prophet, and the ensemble combiner so that
    ``evaluation.cross_validate`` can drive them all the same way.
    """

    name: str = "base"

    @abstractmethod
    def fit(self, y: pd.Series, exog: pd.DataFrame | None = None) -> "BaseForecaster":
        """Fit on a training series ``y`` (DatetimeIndex, monthly)."""

    @abstractmethod
    def predict(self, steps: int, exog: pd.DataFrame | None = None) -> pd.Series:
        """Forecast the next ``steps`` observations after the training end."""
