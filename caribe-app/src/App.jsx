import data from "./data.json";
import Hero from "./components/Hero";
import Scrolly, { Step } from "./components/Scrolly";
import OccupancyChart from "./components/OccupancyChart";
import Pull from "./components/Pull";
import KPI from "./components/KPI";

// ====== ESCENAS ======
// Cada acto narrativo define un set de "scenes" sincronizadas con los <Step>.

const ACT1_SCENES = [
  {
    id: "a1-s0",
    metric: "occ",
    range: ["2019-01-01", "2019-12-01"],
    tone: "calm",
    refLines: [{ y: 48.5, label: "PROMEDIO 2019 · 48,5%" }],
    annotations: [],
  },
  {
    id: "a1-s1",
    metric: "occ",
    range: ["2019-01-01", "2019-12-01"],
    tone: "calm",
    refLines: [{ y: 48.5, label: "PROMEDIO 2019 · 48,5%" }],
    annotations: [
      { date: "2019-12-01", label: "Temporada alta", dx: -16, dy: -34 },
      { date: "2019-05-01", label: "Valle de mayo", dx: 14, dy: 26 },
    ],
  },
  {
    id: "a1-s2",
    metric: "occ",
    range: ["2019-01-01", "2020-02-01"],
    tone: "calm",
    refLines: [{ y: 48.5, label: "PROMEDIO 2019" }],
    annotations: [
      { date: "2020-01-01", label: "Pico previo", dx: 14, dy: -28 },
    ],
  },
];

const ACT2_SCENES = [
  {
    id: "a2-s0",
    metric: "occ",
    range: ["2019-01-01", "2020-12-01"],
    tone: "alarm",
    highlight: ["2020-03-01", "2020-08-01"],
    annotations: [
      { date: "2020-03-01", label: "Cierre de fronteras", dx: -16, dy: -34 },
    ],
  },
  {
    id: "a2-s1",
    metric: "occ",
    range: ["2019-01-01", "2020-12-01"],
    tone: "alarm",
    highlight: ["2020-03-01", "2020-08-01"],
    annotations: [
      { date: "2020-04-01", label: "Punto cero", dx: 14, dy: -28 },
      { date: "2020-08-01", label: "Hoteles vacíos", dx: 12, dy: 22 },
    ],
  },
  {
    id: "a2-s2",
    metric: "incomeVar",
    range: ["2020-01-01", "2020-12-01"],
    tone: "alarm",
    refLines: [{ y: 0, label: "0 · NIVEL DE 2019" }],
    annotations: [
      { date: "2020-04-01", label: "Caída de ingresos", dx: 16, dy: 34 },
    ],
  },
];

const ACT3_SCENES = [
  {
    id: "a3-s0",
    metric: "incomeVar",
    range: ["2020-01-01", "2022-06-01"],
    tone: "rebound",
    refLines: [{ y: 0, label: "BASE 2019" }],
    annotations: [
      { date: "2021-04-01", label: "+1.440% interanual", dx: 14, dy: -32 },
    ],
  },
  {
    id: "a3-s1",
    metric: "occ",
    range: ["2020-01-01", "2022-06-01"],
    tone: "rebound",
    highlight: ["2021-06-01", "2021-12-01"],
    refLines: [{ y: 48.5, label: "PROMEDIO 2019" }],
    annotations: [
      { date: "2021-10-01", label: "Récord histórico", dx: -14, dy: -30 },
    ],
  },
];

const ACT4_SCENES = [
  {
    id: "a4-s0",
    metric: "occ",
    range: ["2019-01-01", "2026-02-01"],
    tone: "steady",
    refLines: [{ y: 48.5, label: "PROMEDIO 2019" }],
    annotations: [],
  },
  {
    id: "a4-s1",
    metric: "occ",
    range: ["2019-01-01", "2026-02-01"],
    tone: "steady",
    refLines: [
      { y: 48.5, label: "2019 · 48,5%" },
      { y: 52.0, label: "2025 · 52,0%" },
    ],
    annotations: [
      { date: "2025-01-01", label: "Hoy", dx: 14, dy: -28 },
    ],
  },
  {
    id: "a4-s2",
    metric: "occ",
    range: ["2019-01-01", "2026-02-01"],
    tone: "steady",
    highlight: ["2024-01-01", "2026-02-01"],
    refLines: [{ y: 48.5, label: "PROMEDIO 2019" }],
    annotations: [
      { date: "2025-12-01", label: "Última observación", dx: -16, dy: -34 },
    ],
  },
];

// Helpers de tipografía
function ActHeader({ kicker, title, lede }) {
  return (
    <div className="max-w-3xl mx-auto px-6 mb-16 sm:mb-24 text-center">
      <p className="text-xs uppercase tracking-[0.3em] text-[var(--color-coral)] font-semibold mb-5">
        {kicker}
      </p>
      <h2
        className="font-serif text-[clamp(2rem,5vw,3.6rem)] leading-[1.05] tracking-tight"
        style={{ fontVariationSettings: "'opsz' 144" }}
      >
        {title}
      </h2>
      {lede && (
        <p className="mt-6 text-lg text-[var(--color-ink-soft)] font-serif leading-relaxed">
          {lede}
        </p>
      )}
    </div>
  );
}

function P({ children, lead = false }) {
  return (
    <p
      className={`font-serif leading-relaxed text-[var(--color-ink)] ${
        lead ? "text-xl sm:text-2xl" : "text-base sm:text-lg"
      } mb-5`}
    >
      {children}
    </p>
  );
}

function StepLabel({ children }) {
  return (
    <p className="text-[10.5px] uppercase tracking-[0.28em] text-[var(--color-ink-mute)] font-semibold mb-3">
      {children}
    </p>
  );
}

export default function App() {
  return (
    <div className="bg-[var(--color-paper)] text-[var(--color-ink)]">
      {/* Top nav minúscula */}
      <nav className="fixed top-0 left-0 right-0 z-50 px-6 sm:px-10 py-5 backdrop-blur-md bg-[var(--color-paper)]/70 border-b border-[var(--color-rule)]/60">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-[var(--color-coral)]" />
            <span className="text-xs uppercase tracking-[0.22em] text-[var(--color-ink-soft)] font-semibold">
              Caribe en cifras
            </span>
          </div>
          <span className="hidden sm:block text-[10.5px] uppercase tracking-[0.22em] text-[var(--color-ink-mute)]">
            Turismo · 2019 — 2026
          </span>
        </div>
      </nav>

      {/* HERO */}
      <Hero />

      {/* INTRO ENSAYO */}
      <section className="px-6 sm:px-10 py-24 sm:py-36 max-w-3xl mx-auto">
        <p className="drop-cap font-serif text-lg sm:text-xl leading-[1.7] text-[var(--color-ink)]">
          Hay regiones del país donde el turismo no es un sector económico: es la
          forma en que se ordena el calendario, en que se planea la vida, en que
          se mide el éxito. El Caribe colombiano —Cartagena, Santa Marta, San
          Andrés, Barranquilla, Riohacha— vive de los meses altos para sobrevivir
          a los meses bajos. Y durante los últimos siete años, esa fórmula fue
          puesta a prueba como nunca antes.
        </p>
        <p className="mt-6 font-serif text-lg sm:text-xl leading-[1.7] text-[var(--color-ink-soft)]">
          Esta es la historia de 86 meses, contada con tres números que se
          publican mes a mes en silencio: la ocupación hotelera, las habitaciones
          disponibles y el cambio en los ingresos. Tres números que, leídos en
          orden, narran un colapso, un rebote engañoso y una recuperación
          incompleta.
        </p>
      </section>

      {/* ACTO 1 — EL PARAÍSO */}
      <section className="border-t border-[var(--color-rule)] pt-20 sm:pt-32">
        <ActHeader
          kicker="Acto I · 2019"
          title="El paraíso, antes de que cambiara todo."
          lede="Un año estable, predecible, con una estacionalidad que los hoteleros conocían de memoria."
        />

        <div className="max-w-7xl mx-auto px-6 sm:px-10">
          <Scrolly graphic={(i) => <OccupancyChart data={data} scene={ACT1_SCENES[i]} />}>
            <Step>
              <StepLabel>Línea base</StepLabel>
              <P lead>
                En 2019, los hoteles del Caribe colombiano operaron con una ocupación
                promedio del <strong>48,5%</strong>.
              </P>
              <P>
                Una cifra que parece modesta —menos de la mitad de las camas
                ocupadas, en promedio— pero que escondía algo más interesante: una
                regularidad casi metronómica. Mes con mes, el sector sabía qué
                esperar.
              </P>
            </Step>

            <Step>
              <StepLabel>La estacionalidad</StepLabel>
              <P>
                Los picos llegaban en <strong>diciembre</strong>, con la temporada de
                fin de año, y a comienzos de cada mes nuevo. Los valles, en mayo y
                septiembre, cuando los viajeros del norte vuelven a casa y todavía
                no comienza el verano del sur.
              </P>
              <P>
                Esa onda regular era la base sobre la cual se calculaban
                inversiones, se contrataba personal y se planeaba la siguiente
                temporada.
              </P>
            </Step>

            <Step>
              <StepLabel>Enero de 2020</StepLabel>
              <P>
                El año comenzó mejor que cualquier enero reciente. La ocupación
                tocó <strong>55,1%</strong> en enero y <strong>51,4%</strong> en febrero.
              </P>
              <P>
                Nadie en el Caribe sabía aún que las próximas semanas iban a redefinir
                lo que la palabra <em>temporada</em> significa.
              </P>
            </Step>
          </Scrolly>
        </div>
      </section>

      <Pull source="Marzo de 2020">
        En cuatro semanas, el Caribe pasó de tener tres de cada diez camas
        ocupadas a tener menos de una.
      </Pull>

      {/* ACTO 2 — EL COLAPSO */}
      <section className="border-t border-[var(--color-rule)] pt-20 sm:pt-32 bg-[var(--color-paper-dim)]">
        <ActHeader
          kicker="Acto II · 2020"
          title="El colapso."
          lede="Lo que cuatro semanas hicieron con un sector que tarda años en construirse."
        />

        <div className="max-w-7xl mx-auto px-6 sm:px-10">
          <Scrolly graphic={(i) => <OccupancyChart data={data} scene={ACT2_SCENES[i]} />}>
            <Step>
              <StepLabel>El cierre</StepLabel>
              <P lead>
                El 16 de marzo de 2020, Colombia cerró sus fronteras. Los aviones
                dejaron de aterrizar.
              </P>
              <P>
                La línea, hasta ese mes acostumbrada a moverse en una franja entre
                el 40% y el 55%, se desploma fuera de cualquier patrón histórico.
              </P>
            </Step>

            <Step>
              <StepLabel>El punto cero</StepLabel>
              <P>
                En <strong>abril</strong>, la ocupación tocó el <strong>9,3%</strong>.
                En mayo, el <strong>9,1%</strong>. Las cifras más bajas de toda la serie.
              </P>
              <P>
                No era una crisis de demanda: era un sector apagado por decreto.
                Los hoteles seguían existiendo, las habitaciones disponibles bajaron
                un 78% porque muchos cerraron por completo, y aun así los pocos que
                operaban casi no tenían clientes.
              </P>
            </Step>

            <Step>
              <StepLabel>El golpe en los ingresos</StepLabel>
              <P>
                Cambiamos el indicador. Esta es la <em>variación real del ingreso</em>{" "}
                comparada contra el mismo mes del año anterior.
              </P>
              <P>
                En abril de 2020 los ingresos cayeron <strong>96,5%</strong> frente
                a abril de 2019. No es que el sector haya tenido un mal mes: es que
                el sector, durante un mes, prácticamente dejó de existir.
              </P>
            </Step>
          </Scrolly>
        </div>
      </section>

      <Pull source="Una nota sobre los porcentajes">
        Cuando la base es cero, cualquier cosa parece un milagro.
      </Pull>

      {/* ACTO 3 — EL REBOTE ENGAÑOSO */}
      <section className="border-t border-[var(--color-rule)] pt-20 sm:pt-32">
        <ActHeader
          kicker="Acto III · 2021"
          title="El rebote que parecía un milagro."
          lede="Por qué los titulares de 2021 hablaban de crecimientos de cuatro dígitos."
        />

        <div className="max-w-7xl mx-auto px-6 sm:px-10">
          <Scrolly graphic={(i) => <OccupancyChart data={data} scene={ACT3_SCENES[i]} />}>
            <Step>
              <StepLabel>El gráfico imposible</StepLabel>
              <P lead>
                En abril de 2021, los ingresos del sector hotelero del Caribe
                crecieron <strong>1.440%</strong> frente a abril del año anterior.
              </P>
              <P>
                El número es real. La interpretación, no tanto. Cuando el punto de
                comparación es un mes en el que el sector ganó casi nada,
                cualquier mejora se ve como una explosión. Los porcentajes mienten
                cuando la base es minúscula.
              </P>
            </Step>

            <Step>
              <StepLabel>Lo que sí pasó</StepLabel>
              <P>
                Si dejamos de mirar la variación porcentual y miramos la ocupación
                en términos absolutos, la historia es más sobria pero más honesta.
              </P>
              <P>
                A partir de junio de 2021 la línea volvió a su rango histórico. En
                octubre tocó un <strong>60,8%</strong>, el valor más alto de toda la
                serie. La gente regresó. Pero la cicatriz —los 12 meses anteriores—
                no se borra.
              </P>
            </Step>
          </Scrolly>
        </div>
      </section>

      {/* ACTO 4 — LA NUEVA NORMALIDAD */}
      <section className="border-t border-[var(--color-rule)] pt-20 sm:pt-32 bg-[var(--color-paper-dim)]">
        <ActHeader
          kicker="Acto IV · 2022 — 2026"
          title="La nueva normalidad."
          lede="Mirando los siete años juntos, ¿hacia dónde regresamos?"
        />

        <div className="max-w-7xl mx-auto px-6 sm:px-10">
          <Scrolly graphic={(i) => <OccupancyChart data={data} scene={ACT4_SCENES[i]} />}>
            <Step>
              <StepLabel>Toda la serie</StepLabel>
              <P lead>
                Esta es la curva completa. Siete años en una sola línea.
              </P>
              <P>
                Lo primero que llama la atención es que la pendiente, después de
                2022, es suave. La crisis quedó atrás. La normalidad, también.
              </P>
            </Step>

            <Step>
              <StepLabel>Volvimos. Pero a otro lugar.</StepLabel>
              <P>
                El promedio de ocupación en 2025 fue del <strong>52,0%</strong>.
                En 2019, había sido del 48,5%.
              </P>
              <P>
                A primera vista, mejoramos. Tres puntos porcentuales son tres
                puntos porcentuales. Pero el indicador completo cuenta otra cosa.
              </P>
            </Step>

            <Step>
              <StepLabel>El detalle que cambia el cuadro</StepLabel>
              <P>
                Las habitaciones disponibles en 2025 son, en promedio,{" "}
                <strong>5,3% mayores</strong> que en 2019. Hay más oferta. Más
                hoteles, más camas, más inversión.
              </P>
              <P>
                La ocupación creció menos que la oferta. Eso significa que la
                demanda volvió, pero no creció al mismo ritmo. El Caribe atrae
                hoy a más viajeros que antes del COVID, pero los reparte entre
                muchos más operadores.
              </P>
            </Step>
          </Scrolly>
        </div>
      </section>

      {/* RESUMEN KPIs */}
      <section className="border-t border-[var(--color-rule)] py-24 sm:py-36">
        <div className="max-w-6xl mx-auto px-6 sm:px-10">
          <h3 className="font-serif text-3xl sm:text-4xl mb-12 max-w-2xl">
            Siete años, en cuatro cifras.
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            <KPI
              value="48,5%"
              label="Ocupación 2019"
              sub="línea base de prepandemia"
              accent="ink"
            />
            <KPI
              value="9,3%"
              label="Abril 2020"
              sub="el mes más bajo de toda la serie"
              accent="coral"
            />
            <KPI
              value="−96,5%"
              label="Ingresos abril 2020"
              sub="caída interanual real"
              accent="coral"
            />
            <KPI
              value="52,0%"
              label="Ocupación 2025"
              sub="promedio anual hoy"
              accent="teal"
            />
          </div>
        </div>
      </section>

      {/* CIERRE REFLEXIVO */}
      <section className="border-t border-[var(--color-rule)] bg-[var(--color-deep)] text-[var(--color-paper)] py-28 sm:py-40">
        <div className="max-w-3xl mx-auto px-6 sm:px-10">
          <p className="text-[11px] uppercase tracking-[0.3em] text-[var(--color-coral-dim)] font-semibold mb-8">
            Por qué importa
          </p>
          <h3
            className="font-serif text-[clamp(2rem,5vw,3.6rem)] leading-[1.05] tracking-tight mb-10"
            style={{ fontVariationSettings: "'opsz' 144" }}
          >
            Los hoteles no son solo edificios.
          </h3>
          <div className="space-y-6 text-lg sm:text-xl font-serif leading-relaxed text-[var(--color-paper)]/85">
            <p>
              Detrás de cada punto del gráfico hay personas. Camareros, recepcionistas,
              cocineros, guías, taxistas, vendedoras de mango biche en la playa,
              músicos que tocan champeta en los bares de Getsemaní. Cuando la
              ocupación baja al 9%, lo que baja no es una métrica: es una nómina.
            </p>
            <p>
              El turismo del Caribe colombiano genera, según el DANE, alrededor de
              uno de cada cinco empleos formales de la región. Su recuperación no
              es un asunto de hoteleros. Es un asunto de territorio.
            </p>
            <p className="pt-4 border-t border-[var(--color-paper)]/15 text-[var(--color-paper)]/70 text-base">
              La buena noticia: la línea regresó. La advertencia: la línea regresó,
              pero el suelo bajo ella se movió. La oferta creció más rápido que la
              demanda. La próxima década del Caribe no se decidirá por cuántos
              hoteles abren —ya hay— sino por cuántos viajeros se sienten llamados
              a llenarlos.
            </p>
          </div>
        </div>
      </section>

      {/* MÉTODO */}
      <section className="py-24 px-6 sm:px-10 max-w-3xl mx-auto">
        <h4 className="text-xs uppercase tracking-[0.28em] text-[var(--color-ink-mute)] font-semibold mb-6">
          Datos y método
        </h4>
        <div className="space-y-4 text-sm sm:text-base text-[var(--color-ink-soft)] font-serif leading-relaxed">
          <p>
            La serie utilizada cubre 86 observaciones mensuales, de enero de 2019
            a febrero de 2026, y describe el comportamiento agregado del sector
            hotelero del Caribe colombiano.
          </p>
          <p>
            Las variables analizadas son la ocupación hotelera (porcentaje de
            habitaciones ocupadas sobre las disponibles), las habitaciones
            disponibles —indexadas a una base 100 promedio en 2019— y la variación
            real interanual del ingreso del sector.
          </p>
          <p>
            La variación interanual del ingreso queda sin valor para los meses de
            2019 porque carece de referente del año anterior. Por la misma razón,
            las cifras del segundo trimestre de 2021 muestran crecimientos de
            cuatro dígitos: el efecto base es real, pero la magnitud porcentual
            no debe interpretarse como recuperación absoluta.
          </p>
        </div>
      </section>

      <footer className="border-t border-[var(--color-rule)] py-10 px-6 text-center">
        <p className="text-[10.5px] uppercase tracking-[0.28em] text-[var(--color-ink-mute)]">
          Caribe en cifras · una historia visual con datos
        </p>
      </footer>
    </div>
  );
}
