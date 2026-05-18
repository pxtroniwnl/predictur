"""Prophet wrapper with custom regressors and yearly seasonality."""

from __future__ import annotations

import logging
import os

import pandas as pd

# Silence Prophet/Stan chatter before import.
logging.getLogger("prophet").setLevel(logging.ERROR)
logging.getLogger("cmdstanpy").setLevel(logging.ERROR)
os.environ.setdefault("PROPHET_DISABLE_PLOT", "1")

from prophet import Prophet  # noqa: E402

from .base import BaseForecaster


class ProphetForecaster(BaseForecaster):
    """Prophet wrapper aligned with the BaseForecaster interface.

    Uses additive yearly seasonality (12-month cycle) and registers each
    column of the exog matrix as a regressor. Daily/weekly seasonality is
    disabled because the data is monthly.
    """

    name = "Prophet"

    def __init__(
        self,
        yearly_seasonality: int = 10,
        seasonality_mode: str = "additive",
        changepoint_prior_scale: float = 0.05,
        regressor_prior_scale: float = 1.0,
    ) -> None:
        self.yearly_seasonality = yearly_seasonality
        self.seasonality_mode = seasonality_mode
        self.changepoint_prior_scale = changepoint_prior_scale
        self.regressor_prior_scale = regressor_prior_scale
        self._model: Prophet | None = None
        self._exog_cols: list[str] = []
        self._train_end: pd.Timestamp | None = None

    def _new_model(self) -> Prophet:
        m = Prophet(
            yearly_seasonality=self.yearly_seasonality,
            weekly_seasonality=False,
            daily_seasonality=False,
            seasonality_mode=self.seasonality_mode,
            changepoint_prior_scale=self.changepoint_prior_scale,
        )
        for col in self._exog_cols:
            m.add_regressor(col, prior_scale=self.regressor_prior_scale)
        return m

    def fit(
        self, y: pd.Series, exog: pd.DataFrame | None = None
    ) -> "ProphetForecaster":
        self._exog_cols = list(exog.columns) if exog is not None else []
        df = pd.DataFrame({"ds": y.index, "y": y.values})
        if exog is not None:
            for col in self._exog_cols:
                df[col] = exog[col].values

        self._model = self._new_model()
        self._model.fit(df)
        self._train_end = y.index[-1]
        return self

    def predict(
        self, steps: int, exog: pd.DataFrame | None = None
    ) -> pd.Series:
        if self._model is None or self._train_end is None:
            raise RuntimeError("Model is not fitted")

        future_idx = pd.date_range(
            start=self._train_end + pd.offsets.MonthBegin(1),
            periods=steps,
            freq="MS",
        )
        future = pd.DataFrame({"ds": future_idx})
        if self._exog_cols:
            if exog is None:
                raise ValueError("Prophet was fit with regressors but exog is None")
            for col in self._exog_cols:
                future[col] = exog[col].values
        forecast = self._model.predict(future)
        return pd.Series(forecast["yhat"].values, index=future_idx, name="yhat")
