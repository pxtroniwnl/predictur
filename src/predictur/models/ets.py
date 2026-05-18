"""ETS / Holt-Winters wrapper.

ETS doesn't accept exogenous regressors natively, so this implementation
fits a linear regression of ``y`` on the exog matrix first, then fits ETS
on the residuals. At forecast time the linear contribution of the future
exog is added back to the ETS forecast. This is a standard "two-stage" trick
and lets ETS participate fairly in the comparison even though it isn't a
state-space SARIMAX.
"""

from __future__ import annotations

import warnings

import pandas as pd
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from .base import BaseForecaster


class ETSForecaster(BaseForecaster):
    """Holt-Winters (additive trend + seasonality) with optional exog regressors."""

    name = "ETS"

    def __init__(
        self,
        seasonal_periods: int = 12,
        trend: str | None = "add",
        seasonal: str | None = "add",
        damped_trend: bool = False,
    ) -> None:
        self.seasonal_periods = seasonal_periods
        self.trend = trend
        self.seasonal = seasonal
        self.damped_trend = damped_trend
        self._result = None
        self._reg: LinearRegression | None = None
        self._exog_cols: list[str] | None = None

    def fit(
        self, y: pd.Series, exog: pd.DataFrame | None = None
    ) -> "ETSForecaster":
        self._exog_cols = list(exog.columns) if exog is not None else None

        if exog is not None and len(exog.columns) > 0:
            self._reg = LinearRegression().fit(exog.values, y.values)
            residual = pd.Series(
                y.values - self._reg.predict(exog.values), index=y.index,
                name=y.name,
            )
        else:
            self._reg = None
            residual = y

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            model = ExponentialSmoothing(
                residual,
                trend=self.trend,
                seasonal=self.seasonal,
                seasonal_periods=self.seasonal_periods,
                damped_trend=self.damped_trend,
                initialization_method="estimated",
            )
            self._result = model.fit(optimized=True)
        return self

    def predict(
        self, steps: int, exog: pd.DataFrame | None = None
    ) -> pd.Series:
        if self._result is None:
            raise RuntimeError("Model is not fitted")
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            base = self._result.forecast(steps)

        if self._reg is not None and exog is not None and self._exog_cols:
            adj = self._reg.predict(exog[self._exog_cols].values)
            base = pd.Series(base.values + adj, index=base.index)
        return base
