#!/usr/bin/env python3
"""Download EMA (Encuesta Mensual de Alojamiento) raw data from DANE.

Usage:
    python scripts/download_ema.py

Downloads Excel files to ``data/raw/``.  Skips files that already exist
so the script is safe to re-run for incremental downloads.

URL conventions
---------------
* 2020-2022:
  investigaciones/boletines/ema/anexos-EMA-{mes_completo}-{año}.xlsx
* 2023+ (new path):
  operaciones/EMA/anex-EMA-{abr3}{año}.xlsx
"""

import logging
import time
from pathlib import Path
from typing import List, Tuple

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DATA_DIR = Path("data/raw")
OLD_BASE = "https://www.dane.gov.co/files/investigaciones/boletines/ema/"
NEW_BASE = "https://www.dane.gov.co/files/operaciones/EMA/"
TIMEOUT = 60
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # seconds, multiplied by attempt number

# (full_name, 3-letter abbreviation) -- Spanish month names as used by DANE
MESES: List[Tuple[str, str]] = [
    ("enero", "ene"),
    ("febrero", "feb"),
    ("marzo", "mar"),
    ("abril", "abr"),
    ("mayo", "may"),
    ("junio", "jun"),
    ("julio", "jul"),
    ("agosto", "ago"),
    ("septiembre", "sep"),
    ("octubre", "oct"),
    ("noviembre", "nov"),
    ("diciembre", "dic"),
]

# (year, start_month_index, end_month_index)  -- 0-based
CALENDAR: List[Tuple[int, int, int]] = [
    (2020, 5, 11),  # junio – diciembre
    (2021, 0, 11),  # enero – diciembre
    (2022, 0, 11),  # enero – diciembre
    (2023, 0, 11),  # enero – diciembre
    (2024, 0, 11),  # enero – diciembre
    (2025, 0, 11),  # enero – diciembre
    (2026, 0, 1),   # enero – febrero
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _candidate_urls(year: int, month_idx: int) -> List[str]:
    """Return download URLs in priority order for *year* and *month_idx*.

    DANE changed the URL convention twice:

    1. **2023+** → new path with 3-letter abbreviated month:
       ``operaciones/EMA/anex-EMA-{abr}{año}.xlsx``

    2. **2020–2022** → old path with full month name:
       ``investigaciones/boletines/ema/anexos-EMA-{full}-{año}.xlsx``

       Mid-2022 the old path itself switched from full to abbreviated
       names (e.g. ``abril`` → ``abr``).  The fallback below handles
       both variants.
    """
    full, abbr = MESES[month_idx]
    urls: List[str] = []
    if year >= 2023:
        urls.append(f"{NEW_BASE}anex-EMA-{abbr}{year}.xlsx")
    urls.append(f"{OLD_BASE}anexos-EMA-{full}-{year}.xlsx")
    urls.append(f"{OLD_BASE}anexos-EMA-{abbr}-{year}.xlsx")
    return urls


def _dest_path(year: int, month_idx: int) -> Path:
    """Return local destination path (consistent naming regardless of source URL)."""
    full, _ = MESES[month_idx]
    return DATA_DIR / f"anexos-EMA-{full}-{year}.xlsx"


def _download(url: str, dest: Path) -> bool:
    """Download *url* to *dest* with retries.

    Returns ``True`` on success, ``False`` on permanent failure (404).
    Transient errors (timeout, connection reset, 5xx) are retried.
    """
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, timeout=TIMEOUT, stream=True)
            if resp.status_code == 404:
                return False
            resp.raise_for_status()
            dest.write_bytes(resp.content)
            return True
        except (requests.RequestException, OSError) as exc:
            log.warning(
                "Attempt %d/%d for %s: %s", attempt, MAX_RETRIES, url, exc
            )
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF * attempt)
    return False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    """Download all EMA data files into ``data/raw/``."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ok = skipped = failed = 0

    for year, start, end in CALENDAR:
        for month_idx in range(start, end + 1):
            dest = _dest_path(year, month_idx)

            if dest.exists() and dest.stat().st_size > 0:
                log.info("Skipped  %s (already exists)", dest.name)
                skipped += 1
                continue

            urls = _candidate_urls(year, month_idx)
            downloaded = False

            for url in urls:
                if _download(url, dest):
                    log.info("Downloaded %s", dest.name)
                    downloaded = True
                    ok += 1
                    break

            if not downloaded:
                log.warning("Not found  %s (tried %d URL(s))", dest.name, len(urls))
                failed += 1

    log.info(
        "Done — %d downloaded, %d skipped (already exist), %d not found",
        ok,
        skipped,
        failed,
    )


if __name__ == "__main__":
    main()
