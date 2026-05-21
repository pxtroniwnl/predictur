// Builds src/data.json from the master CSV (history) and the forecast CSV
// (Ensemble model = best by MAPE).
//
// Inputs:
//   ../../data/processed/master_tourism_series.csv
//   ../../reports/forecast.csv
//
// Output shape:
//   {
//     history: [{ date, year, month, occ, available, occupied, incomeVar }],
//     forecast: [{ date, year, month, horizon, yhat,
//                  yhat_lower_80, yhat_upper_80,
//                  yhat_lower_95, yhat_upper_95 }],
//     bestModel: "Ensemble"
//   }
//
// Note: legacy callers used to read `data.json` as an array. We keep
// backwards-compat by also exposing the history rows on the top level via
// `Array.from`-friendly access in components that need it.

import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = resolve(__dirname, "../..");
const HIST_CSV = resolve(ROOT, "data/processed/master_tourism_series.csv");
const FCST_CSV = resolve(ROOT, "reports/forecast.csv");
const OUT_PATH = resolve(__dirname, "../src/data.json");

const BEST_MODEL = "Ensemble";

// ---------------------------------------------------------------------------
// CSV helpers
// ---------------------------------------------------------------------------

function readCsv(path) {
  const raw = readFileSync(path, "utf8").trim();
  const [header, ...lines] = raw.split(/\r?\n/);
  const cols = header.split(",");
  return lines.map((line) => {
    const parts = line.split(",");
    const row = {};
    cols.forEach((c, i) => {
      const v = parts[i];
      row[c] = v === "" || v == null ? null : v;
    });
    return row;
  });
}

const num = (v) => (v == null ? null : parseFloat(v));

// ---------------------------------------------------------------------------
// History
// ---------------------------------------------------------------------------

const histRows = readCsv(HIST_CSV).map((row) => {
  const [y, m] = row.Date.split("-").map(Number);
  return {
    date: row.Date,
    year: y,
    month: m,
    occ: num(row.Ocupacion_Caribe),
    available: num(row.Hab_Disponibles_Caribe),
    occupied: num(row.Hab_Ocupadas_Caribe),
    incomeVar: num(row.Ingreso_Real_Var_Caribe),
  };
});

// ---------------------------------------------------------------------------
// Forecast (filter to best model only)
// ---------------------------------------------------------------------------

let forecastRows = [];
if (existsSync(FCST_CSV)) {
  forecastRows = readCsv(FCST_CSV)
    .filter((r) => r.model === BEST_MODEL)
    .map((row) => {
      const [y, m] = row.Date.split("-").map(Number);
      return {
        date: row.Date,
        year: y,
        month: m,
        horizon: parseInt(row.horizon, 10),
        yhat: num(row.yhat),
        yhat_lower_80: num(row.yhat_lower_80),
        yhat_upper_80: num(row.yhat_upper_80),
        yhat_lower_95: num(row.yhat_lower_95),
        yhat_upper_95: num(row.yhat_upper_95),
      };
    });
} else {
  console.warn(`Forecast CSV not found at ${FCST_CSV} — skipping forecast section`);
}

// ---------------------------------------------------------------------------
// Output
// ---------------------------------------------------------------------------

const out = {
  history: histRows,
  forecast: forecastRows,
  bestModel: BEST_MODEL,
};

mkdirSync(dirname(OUT_PATH), { recursive: true });
writeFileSync(OUT_PATH, JSON.stringify(out, null, 2));
console.log(
  `Wrote ${histRows.length} history rows + ${forecastRows.length} forecast rows ` +
  `(model=${BEST_MODEL}) → ${OUT_PATH}`
);
