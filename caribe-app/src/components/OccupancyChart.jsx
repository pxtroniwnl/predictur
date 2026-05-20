import { useMemo, useEffect, useState, useRef } from "react";
import { scaleLinear, scaleTime } from "d3-scale";
import { line as d3line, curveMonotoneX, area as d3area } from "d3-shape";
import { extent, max } from "d3-array";
import { motion, AnimatePresence } from "framer-motion";
import { parseDate, fmtMonth, fmtPct, fmtSigned } from "../lib/format";

/**
 * Gráfico héroe que se queda sticky a la izquierda mientras el lector scrollea.
 * Recibe una "scene" con instrucciones de qué resaltar.
 *
 * scene = {
 *   id,
 *   metric: "occ" | "incomeVar",
 *   range: [startISO, endISO],     // recorte del eje X (opcional, sino todo)
 *   highlight: [startISO, endISO], // banda destacada
 *   annotations: [{ date, label, dy?, dx?, value? }],
 *   refLines: [{ y, label }],
 *   tone: "calm" | "alarm" | "rebound" | "steady",
 * }
 */
export default function OccupancyChart({ data, scene, width = 720, height = 460 }) {
  const M = { top: 32, right: 32, bottom: 44, left: 56 };
  const innerW = width - M.left - M.right;
  const innerH = height - M.top - M.bottom;

  const metric = scene?.metric ?? "occ";

  // Aviso visual cuando cambia métrica → escala distinta
  const yAccessor = (d) => d[metric];

  const visible = useMemo(() => {
    const rows = data
      .map((d) => ({ ...d, _date: parseDate(d.date) }))
      .filter((d) => yAccessor(d) != null && !Number.isNaN(yAccessor(d)));
    if (!scene?.range) return rows;
    const [a, b] = scene.range.map(parseDate);
    return rows.filter((d) => d._date >= a && d._date <= b);
  }, [data, scene?.range, metric]);

  const xDomain = extent(visible, (d) => d._date);
  // Para income (puede ser muy grande positivo), recortamos el eje a percentil para no aplastar
  const yDomain = useMemo(() => {
    if (metric === "occ") return [0, 70];
    const vals = visible.map(yAccessor);
    const lo = Math.min(-100, Math.min(...vals));
    const hi = Math.max(100, Math.max(...vals));
    // recortar a un máximo razonable
    return [Math.max(lo, -120), Math.min(hi, 1600)];
  }, [visible, metric]);

  const x = scaleTime().domain(xDomain).range([0, innerW]);
  const y = scaleLinear().domain(yDomain).nice().range([innerH, 0]);

  const lineGen = d3line()
    .x((d) => x(d._date))
    .y((d) => y(yAccessor(d)))
    .curve(curveMonotoneX);

  const areaGen = d3area()
    .x((d) => x(d._date))
    .y0(y(metric === "occ" ? 0 : 0))
    .y1((d) => y(yAccessor(d)))
    .curve(curveMonotoneX);

  const linePath = lineGen(visible);
  const areaPath = areaGen(visible);

  // ticks de año
  const yearTicks = useMemo(() => {
    if (!xDomain[0]) return [];
    const startY = xDomain[0].getUTCFullYear();
    const endY = xDomain[1].getUTCFullYear();
    const ticks = [];
    for (let y = startY; y <= endY; y++) {
      ticks.push(new Date(Date.UTC(y, 0, 1)));
    }
    return ticks;
  }, [xDomain[0]?.getTime(), xDomain[1]?.getTime()]);

  const yTicks = y.ticks(metric === "occ" ? 6 : 6);

  // Banda highlight
  const band = useMemo(() => {
    if (!scene?.highlight) return null;
    const [a, b] = scene.highlight.map(parseDate);
    const xa = Math.max(0, x(a));
    const xb = Math.min(innerW, x(b));
    if (xb <= xa) return null;
    return { x: xa, w: xb - xa };
  }, [scene?.highlight, x, innerW]);

  const tone = scene?.tone ?? "calm";
  const lineColor = {
    calm: "#0d7377",
    alarm: "#e76f51",
    rebound: "#c47b3a",
    steady: "#0d7377",
  }[tone];
  const areaColor = {
    calm: "#0d737715",
    alarm: "#e76f5120",
    rebound: "#c47b3a18",
    steady: "#0d737712",
  }[tone];

  // Animación del path: hacemos draw on enter usando key=scene.id
  return (
    <div className="w-full h-full flex items-center justify-center select-none">
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full max-w-[820px] h-auto"
        role="img"
        aria-label="Gráfico de la serie histórica de turismo del Caribe"
      >
        <defs>
          <linearGradient id={`area-${tone}`} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor={lineColor} stopOpacity="0.22" />
            <stop offset="100%" stopColor={lineColor} stopOpacity="0" />
          </linearGradient>
        </defs>

        <g transform={`translate(${M.left},${M.top})`}>
          {/* Banda highlight */}
          <AnimatePresence>
            {band && (
              <motion.rect
                key={scene.id + "-band"}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.5 }}
                x={band.x}
                y={0}
                width={band.w}
                height={innerH}
                fill={tone === "alarm" ? "#e76f5110" : "#0d737710"}
              />
            )}
          </AnimatePresence>

          {/* Grid Y */}
          {yTicks.map((t) => (
            <g key={t} transform={`translate(0,${y(t)})`}>
              <line
                x1={0}
                x2={innerW}
                stroke="#d8cfc1"
                strokeWidth={t === 0 ? 1.5 : 0.6}
                strokeDasharray={t === 0 ? "0" : "2,3"}
              />
              <text
                x={-10}
                y={4}
                textAnchor="end"
                className="fill-[#8a8378] tabular"
                style={{ fontSize: 11, fontFamily: "Inter" }}
              >
                {metric === "occ" ? `${t}%` : (t > 0 ? `+${t}%` : `${t}%`)}
              </text>
            </g>
          ))}

          {/* Reference lines */}
          {(scene?.refLines || []).map((rl, i) => (
            <g key={i} transform={`translate(0,${y(rl.y)})`}>
              <line x1={0} x2={innerW} stroke="#1a1a1a" strokeDasharray="4,4" strokeWidth={0.8} />
              {rl.label && (
                <text
                  x={innerW - 6}
                  y={-6}
                  textAnchor="end"
                  className="fill-[#1a1a1a]"
                  style={{ fontSize: 10, fontFamily: "Inter", fontWeight: 600, letterSpacing: 0.4 }}
                >
                  {rl.label}
                </text>
              )}
            </g>
          ))}

          {/* X axis */}
          {yearTicks.map((t) => (
            <g key={t.getTime()} transform={`translate(${x(t)},${innerH})`}>
              <line y2={6} stroke="#8a8378" />
              <text
                y={20}
                textAnchor="middle"
                className="fill-[#4a4a4a] tabular"
                style={{ fontSize: 11, fontFamily: "Inter", fontWeight: 500 }}
              >
                {t.getUTCFullYear()}
              </text>
            </g>
          ))}

          {/* Area + Line */}
          <motion.path
            key={scene?.id + "-area"}
            d={areaPath}
            fill={`url(#area-${tone})`}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6 }}
          />
          <motion.path
            key={scene?.id + "-line"}
            d={linePath}
            fill="none"
            stroke={lineColor}
            strokeWidth={2}
            strokeLinecap="round"
            strokeLinejoin="round"
            initial={{ pathLength: 0, opacity: 0.4 }}
            animate={{ pathLength: 1, opacity: 1 }}
            transition={{ duration: 1.2, ease: "easeInOut" }}
          />

          {/* Annotations */}
          <AnimatePresence mode="popLayout">
            {(scene?.annotations || []).map((a, i) => {
              const d = visible.find((v) => v.date === a.date);
              if (!d) return null;
              const cx = x(d._date);
              const cy = y(yAccessor(d));
              const dx = a.dx ?? 12;
              const dy = a.dy ?? -28;
              const valueLabel =
                a.value === false
                  ? null
                  : metric === "occ"
                  ? fmtPct(yAccessor(d), 1)
                  : fmtSigned(yAccessor(d), 1);

              return (
                <motion.g
                  key={`${scene.id}-ann-${i}`}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.5, delay: 0.4 + i * 0.15 }}
                >
                  <circle cx={cx} cy={cy} r={5} fill={lineColor} stroke="#f7f3ec" strokeWidth={2} />
                  <line
                    x1={cx}
                    y1={cy}
                    x2={cx + dx}
                    y2={cy + dy}
                    stroke="#1a1a1a"
                    strokeWidth={0.8}
                  />
                  <g transform={`translate(${cx + dx},${cy + dy})`}>
                    <text
                      x={dx > 0 ? 4 : -4}
                      y={-2}
                      textAnchor={dx > 0 ? "start" : "end"}
                      className="fill-[#1a1a1a]"
                      style={{
                        fontSize: 11,
                        fontFamily: "Fraunces",
                        fontWeight: 600,
                        fontStyle: "italic",
                      }}
                    >
                      {a.label}
                    </text>
                    {valueLabel && (
                      <text
                        x={dx > 0 ? 4 : -4}
                        y={12}
                        textAnchor={dx > 0 ? "start" : "end"}
                        className="fill-[#4a4a4a] tabular"
                        style={{ fontSize: 10.5, fontFamily: "Inter", fontWeight: 500 }}
                      >
                        {valueLabel}
                      </text>
                    )}
                  </g>
                </motion.g>
              );
            })}
          </AnimatePresence>

          {/* Y axis label */}
          <text
            x={-M.left + 8}
            y={-12}
            className="fill-[#4a4a4a]"
            style={{ fontSize: 10.5, fontFamily: "Inter", fontWeight: 600, letterSpacing: 1.2 }}
          >
            {metric === "occ"
              ? "OCUPACIÓN HOTELERA (%)"
              : "VARIACIÓN REAL DEL INGRESO (% interanual)"}
          </text>
        </g>
      </svg>
    </div>
  );
}
