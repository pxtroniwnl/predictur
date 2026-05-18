"""Exogenous regressors: COVID intervention and Caribbean tourism events.

All regressors are built from a ``DatetimeIndex`` (month start) and returned as
a single ``DataFrame`` aligned to that index. They are designed to plug into
SARIMAX (``exog=``) and Prophet (``add_regressor``) without modification.

Regressors
----------
``covid_shock`` : 1 from Mar 2020 to Jun 2021 (peak disruption), 0 otherwise.
``covid_recovery`` : 1 from Jul 2021 to Dec 2021 (rebound phase), 0 otherwise.
``semana_santa`` : 1 in the month containing Easter Sunday (Colombia), 0 else.
``carnaval`` : 1 in the month of Carnaval de Barranquilla, 0 else.
``high_season`` : 1 in December and January, 0 else.
"""

from __future__ import annotations

from typing import Iterable

import pandas as pd

# ---------------------------------------------------------------------------
# COVID intervention windows
# ---------------------------------------------------------------------------

COVID_SHOCK_START = pd.Timestamp("2020-03-01")
COVID_SHOCK_END = pd.Timestamp("2021-06-01")  # inclusive
COVID_RECOVERY_START = pd.Timestamp("2021-07-01")
COVID_RECOVERY_END = pd.Timestamp("2021-12-01")  # inclusive


def covid_flags(index: pd.DatetimeIndex) -> pd.DataFrame:
    """Binary flags marking COVID shock and recovery windows."""
    shock = ((index >= COVID_SHOCK_START) & (index <= COVID_SHOCK_END)).astype(int)
    recovery = (
        (index >= COVID_RECOVERY_START) & (index <= COVID_RECOVERY_END)
    ).astype(int)
    return pd.DataFrame(
        {"covid_shock": shock, "covid_recovery": recovery}, index=index
    )


# ---------------------------------------------------------------------------
# Easter / Semana Santa (movable feast)
# ---------------------------------------------------------------------------


def _easter_sunday(year: int) -> pd.Timestamp:
    """Compute Easter Sunday for ``year`` (Gregorian / Western).

    Uses the anonymous Gregorian algorithm (Meeus / Jones / Butcher), which
    is the canonical formula and matches the Catholic calendar used in
    Colombia. We avoid relying on the ``holidays`` package here because the
    Colombian locale doesn't expose Easter Sunday as a public holiday name.
    """
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    L = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * L) // 451
    month = (h + L - 7 * m + 114) // 31
    day = ((h + L - 7 * m + 114) % 31) + 1
    return pd.Timestamp(year=year, month=month, day=day)


def _easter_month(year: int) -> int:
    """Return the month (1–12) containing Easter Sunday for ``year``."""
    return _easter_sunday(year).month


def semana_santa_flag(index: pd.DatetimeIndex) -> pd.Series:
    """1 in the month that contains Easter Sunday, else 0."""
    flags = [1 if ts.month == _easter_month(ts.year) else 0 for ts in index]
    return pd.Series(flags, index=index, name="semana_santa", dtype=int)


# ---------------------------------------------------------------------------
# Carnaval de Barranquilla
# ---------------------------------------------------------------------------
# Carnaval Saturday falls 50 days before Easter Sunday. We flag the month in
# which the four official Carnaval days (Sat–Tue) start.


def carnaval_flag(index: pd.DatetimeIndex) -> pd.Series:
    """1 in the month containing Carnaval de Barranquilla, else 0."""
    flags = []
    for ts in index:
        carnaval_saturday = _easter_sunday(ts.year) - pd.Timedelta(days=50)
        flags.append(1 if ts.month == carnaval_saturday.month else 0)
    return pd.Series(flags, index=index, name="carnaval", dtype=int)


# ---------------------------------------------------------------------------
# High season (Dec / Jan)
# ---------------------------------------------------------------------------


def high_season_flag(index: pd.DatetimeIndex) -> pd.Series:
    """1 in December and January (Colombian Caribbean peak), else 0."""
    flags = [(1 if ts.month in (12, 1) else 0) for ts in index]
    return pd.Series(flags, index=index, name="high_season", dtype=int)


# ---------------------------------------------------------------------------
# Combined builder
# ---------------------------------------------------------------------------


def build_exog(
    index: pd.DatetimeIndex,
    include: Iterable[str] = (
        "covid_shock",
        "covid_recovery",
        "semana_santa",
        "carnaval",
    ),
) -> pd.DataFrame:
    """Build the full exogenous regressor matrix for a given index.

    ``high_season`` (December/January flag) is intentionally excluded by
    default: it is perfectly collinear with the yearly seasonality already
    modelled by SARIMAX (s=12) and Prophet (yearly), and adding it injects
    multicollinearity that destabilises the optimisers on a short series.
    Pass ``include=(..., "high_season")`` to opt back in.
    """
    parts: list[pd.DataFrame | pd.Series] = []
    if "covid_shock" in include or "covid_recovery" in include:
        c = covid_flags(index)
        cols = [k for k in ("covid_shock", "covid_recovery") if k in include]
        parts.append(c[cols])
    if "semana_santa" in include:
        parts.append(semana_santa_flag(index))
    if "carnaval" in include:
        parts.append(carnaval_flag(index))
    if "high_season" in include:
        parts.append(high_season_flag(index))
    out = pd.concat(parts, axis=1)
    out.index.name = index.name or "Date"
    return out.astype(float)
