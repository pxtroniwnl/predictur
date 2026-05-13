# Predictur — Agent Guide

## Project

Tourism demand forecasting for the Colombian Caribbean. Python-based data
stack (data engineering, time series, dashboard).

## Current state

No build/test/lint tooling. No framework decision. 69 raw DANE `.xlsx` files
in `data/raw/` (74 MB), one master CSV in `data/processed/`.

## Structure

| Path | Purpose |
|---|---|
| `data/raw/` | EMA `.xlsx` files (jun 2020 – feb 2026) |
| `data/processed/master_tourism_series.csv` | Merged time series for Caribe |
| `scripts/download_ema.py` | Download raw data from DANE |
| `scripts/extract_ema_data.py` | Extract + merge into master CSV |

## Commands

```bash
pip install requests          # for download_ema.py
python scripts/download_ema.py

python scripts/extract_ema_data.py   # produces master CSV
```

Both scripts are safe to re-run (skip existing files, dedup by latest
revision).

## Data pipeline

1. `download_ema.py` — downloads per-month Excel files from DANE.
   Handles 3 URL conventions DANE has used over time.
2. `extract_ema_data.py` — reads all `.xlsx` files, extracts occupancy,
   room supply/demand, and real income variation for the **Caribe** region,
   deduplicates keeping the latest revision per date, writes a single CSV.

Output columns: `Date`, `Ocupacion_Caribe`, `Hab_Disponibles_Caribe`,
`Hab_Ocupadas_Caribe`, `Ingreso_Real_Var_Caribe`.

## DANE format quirks

- Sheet names changed prefix between years (5.x → 4.x, 8.x → 7.x).
  Scripts search by keyword, not exact name.
- Year format varies: `"2020(p)"`, `"2020 (p)"`, `"2023p"`, plain `2019`.
- Month names have trailing spaces in early files.
- Header row position varies by 1-2 rows across years.

## What to know before starting

- Propose stack (Python version, package manager, frameworks) before wiring.
- `data/` should stay out of version control.
- No `.gitignore` exists yet.
