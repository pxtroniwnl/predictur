# Caribe en cifras

Narrativa visual interactiva sobre la ocupación hotelera del Caribe colombiano (2019 – 2026). Construida como un *scrollytelling* de cuatro actos: la línea base prepandemia, el colapso de 2020, el rebote de 2021 y la nueva normalidad.

Los datos provienen de la **Encuesta Mensual de Alojamiento (EMA)** del DANE, procesados por el pipeline Python de este mismo repositorio.

---

## Stack

| Capa | Tecnología |
|---|---|
| Framework UI | React 19 |
| Build | Vite 8 |
| Estilos | Tailwind CSS v4 |
| Animaciones | Framer Motion 12 |
| Gráficos | D3 (d3-scale, d3-shape, d3-array) |
| Scroll trigger | react-intersection-observer |
| Iconos | lucide-react |

---

## Estructura

```
caribe-app/
├── public/
│   ├── favicon.svg
│   └── icons.svg
├── scripts/
│   └── build-data.mjs      # convierte el CSV maestro a src/data.json
├── src/
│   ├── assets/
│   │   └── hero.png
│   ├── components/
│   │   ├── Hero.jsx         # portada animada con título y subtítulo
│   │   ├── KPI.jsx          # tarjeta de métrica destacada
│   │   ├── OccupancyChart.jsx  # gráfico de línea D3 sincronizado con el scroll
│   │   ├── Pull.jsx         # cita destacada entre actos
│   │   └── Scrolly.jsx      # contenedor de scrollytelling (sticky + steps)
│   ├── lib/
│   │   └── format.js        # helpers de formato numérico
│   ├── App.jsx              # narrativa completa: 4 actos + KPIs + cierre
│   ├── data.json            # serie temporal generada por build-data.mjs
│   ├── index.css            # variables CSS, tipografía, drop-cap
│   └── main.jsx
├── index.html
├── vite.config.js
├── eslint.config.js
└── package.json
```

---

## Primeros pasos

### 1. Instalar dependencias

```bash
cd caribe-app
npm install
```

### 2. Regenerar los datos (opcional)

Si actualizaste el CSV maestro en `data/processed/master_tourism_series.csv`, regenera el JSON que consume la app:

```bash
# desde la raíz del repositorio
node caribe-app/scripts/build-data.mjs
```

El script lee `data/processed/master_tourism_series.csv` y escribe `caribe-app/src/data.json` con el shape que espera `OccupancyChart`.

### 3. Servidor de desarrollo

```bash
npm run dev
```

Abre [http://localhost:5173](http://localhost:5173).

### 4. Build de producción

```bash
npm run build       # genera dist/
npm run preview     # sirve dist/ localmente para verificar
```

---

## Cómo funciona el scrollytelling

El componente `Scrolly` mantiene un gráfico **sticky** a la derecha mientras el usuario desplaza los bloques de texto (*steps*) a la izquierda. Cada `<Step>` activa una **escena** diferente en `OccupancyChart` vía `react-intersection-observer`.

Una escena define:

```js
{
  metric: "occ" | "incomeVar",   // qué variable graficar
  range: ["YYYY-MM-DD", "..."],  // ventana temporal visible
  tone: "calm" | "alarm" | "rebound" | "steady",  // paleta de color
  highlight: ["inicio", "fin"],  // franja sombreada opcional
  refLines: [{ y, label }],      // líneas de referencia horizontales
  annotations: [{ date, label, dx, dy }],  // etiquetas sobre puntos
}
```

Los cuatro actos y sus escenas están definidos en `App.jsx` como arrays de objetos planos, lo que hace fácil añadir o reordenar pasos sin tocar los componentes.

---

## Datos

`src/data.json` es un array de objetos con esta forma:

```json
{
  "date": "2020-04-01",
  "year": 2020,
  "month": 4,
  "occ": 9.31,
  "available": 21.97,
  "occupied": 4.22,
  "incomeVar": -96.46
}
```

| Campo | Descripción |
|---|---|
| `occ` | Porcentaje de ocupación hotelera |
| `available` | Índice de habitaciones disponibles (base 2019 = 100) |
| `occupied` | Índice de habitaciones ocupadas (base 2019 = 100) |
| `incomeVar` | Variación real interanual del ingreso (%). `null` en 2019 por falta de base |

---

## Narrativa

La app cuenta cuatro actos:

| Acto | Período | Hilo conductor |
|---|---|---|
| I — El paraíso | 2019 | Estacionalidad estable, 48,5% de ocupación promedio |
| II — El colapso | 2020 | Cierre de fronteras, caída al 9,3%, ingresos −96,5% |
| III — El rebote engañoso | 2021 | Crecimientos de 4 dígitos por efecto base; récord histórico de 60,8% en octubre |
| IV — La nueva normalidad | 2022–2026 | Ocupación promedio 52% en 2025, pero la oferta creció más rápido que la demanda |
