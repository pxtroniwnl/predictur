// Formateadores neutros en español

const MONTHS_ES = [
  "ene", "feb", "mar", "abr", "may", "jun",
  "jul", "ago", "sep", "oct", "nov", "dic",
];

const MONTHS_ES_LONG = [
  "enero", "febrero", "marzo", "abril", "mayo", "junio",
  "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
];

export function fmtMonth(date, long = false) {
  if (!(date instanceof Date)) date = new Date(date);
  const m = date.getUTCMonth();
  const y = date.getUTCFullYear();
  return `${(long ? MONTHS_ES_LONG : MONTHS_ES)[m]} ${y}`;
}

export function fmtPct(n, decimals = 1) {
  if (n == null || Number.isNaN(n)) return "—";
  const v = n.toFixed(decimals);
  return `${v}%`;
}

export function fmtSigned(n, decimals = 1) {
  if (n == null || Number.isNaN(n)) return "—";
  const sign = n > 0 ? "+" : "";
  return `${sign}${n.toFixed(decimals)}%`;
}

export function fmtNumber(n, decimals = 1) {
  if (n == null || Number.isNaN(n)) return "—";
  return n.toLocaleString("es-CO", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

export function parseDate(s) {
  // 2019-01-01 → Date UTC
  return new Date(`${s}T00:00:00Z`);
}
