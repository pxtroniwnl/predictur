import { motion } from "framer-motion";
import { ArrowDown } from "lucide-react";

export default function Hero() {
  return (
    <section className="relative min-h-screen flex flex-col justify-between px-6 sm:px-10 pt-24 pb-12 grain">
      {/* Sutil banner superior */}
      <div className="flex items-center gap-3 text-[11px] uppercase tracking-[0.22em] text-[var(--color-ink-mute)]">
        <span className="w-8 h-px bg-[var(--color-rule)]" />
        <span>Una historia con datos</span>
        <span className="w-8 h-px bg-[var(--color-rule)]" />
      </div>

      <div className="max-w-5xl mx-auto w-full grow flex flex-col justify-center">
        <motion.h1
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, ease: "easeOut" }}
          className="font-serif text-[clamp(2.6rem,8vw,7rem)] leading-[0.95] tracking-tight text-[var(--color-ink)]"
          style={{ fontVariationSettings: "'opsz' 144" }}
        >
          La cicatriz <span className="italic text-[var(--color-coral)]">y el regreso</span>
          <br />
          del Caribe.
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, ease: "easeOut", delay: 0.25 }}
          className="mt-10 max-w-2xl text-lg sm:text-xl text-[var(--color-ink-soft)] leading-relaxed font-serif"
        >
          En marzo de 2020, los hoteles del Caribe colombiano pasaron del{" "}
          <span className="text-[var(--color-ink)] font-semibold">31% de ocupación</span> al{" "}
          <span className="text-[var(--color-coral)] font-semibold">9% en cuatro semanas</span>.
          Los ingresos cayeron <span className="text-[var(--color-coral)] font-semibold">96%</span>.
          Esto es lo que pasó después.
        </motion.p>
      </div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.2, duration: 0.8 }}
        className="flex flex-col items-center gap-3 text-[var(--color-ink-mute)]"
      >
        <span className="text-xs uppercase tracking-[0.25em]">Desplázate</span>
        <ArrowDown className="w-4 h-4 animate-bounce" />
      </motion.div>
    </section>
  );
}
