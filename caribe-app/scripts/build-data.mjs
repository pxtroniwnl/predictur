// Convierte master_tourism_series.csv en src/data.json con el shape que usa la app.
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const CSV_PATH = resolve(__dirname, "../../master_tourism_series.csv");
const OUT_PATH = resolve(__dirname, "../src/data.json");

const raw = readFileSync(CSV_PATH, "utf8").trim();
const [header, ...lines] = raw.split(/\r?\n/);
const cols = header.split(",");

const records = lines.map((line) => {
  const parts = line.split(",");
  const row = {};
  cols.forEach((c, i) => {
    row[c] = parts[i] === "" || parts[i] == null ? null : parts[i];
  });
  const date = row.Date;
  const [y, m] = date.split("-").map(Number);
  return {
    date,
    year: y,
    month: m,
    occ: parseFloat(row.Ocupacion_Caribe),
    available: parseFloat(row.Hab_Disponibles_Caribe),
    occupied: parseFloat(row.Hab_Ocupadas_Caribe),
    incomeVar: row.Ingreso_Real_Var_Caribe == null ? null : parseFloat(row.Ingreso_Real_Var_Caribe),
  };
});

mkdirSync(dirname(OUT_PATH), { recursive: true });
writeFileSync(OUT_PATH, JSON.stringify(records, null, 2));
console.log(`Wrote ${records.length} records to ${OUT_PATH}`);
