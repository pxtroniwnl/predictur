"""SARIMAX wrapper with annual seasonality and exogenous regressors."""

from __future__ import annotations

import warnings

import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

from .base import BaseForecaster


class SarimaForecaster(BaseForecaster):
    """SARIMAX(p,d,q)(P,D,Q,12) wrapper.

    Default orders (1,1,1)(1,1,1,12) are a robust monthly baseline. Exogenous
    regressors (COVID flags, holidays) are passed through to SARIMAX directly.
    """

    name = "SARIMAX"

    def __init__(
        self,
        order: tuple[int, int, int] = (1, 1, 1),
        seasonal_order: tuple[int, int, int, int] = (0, 1, 1, 12),
        enforce_stationarity: bool = True,
        enforce_invertibility: bool = True,
    ) -> None:
        self.order = order
        self.seasonal_order = seasonal_order
        self.enforce_stationarity = enforce_stationarity
        self.enforce_invertibility = enforce_invertibility
        self._result = None
        self._exog_cols: list[str] | None = None

    def fit(
        self, y: pd.Series, exog: pd.DataFrame | None = None
    ) -> "SarimaForecaster":
        self._exog_cols = list(exog.columns) if exog is not None else None
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = SARIMAX(
                y,
                exog=exog,
                order=self.order,
                seasonal_order=self.seasonal_order,
                enforce_stationarity=self.enforce_stationarity,
                enforce_invertibility=self.enforce_invertibility,
            )
            self._result = model.fit(disp=False, maxiter=200)
        return self

    def predict(
        self, steps: int, exog: pd.DataFrame | None = None
    ) -> pd.Series:
        if self._result is None:
            raise RuntimeError("Model is not fitted")
        if self._exog_cols and exog is not None:
            exog = exog[self._exog_cols]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            forecast = self._result.get_forecast(steps=steps, exog=exog)
        return forecast.predicted_mean
