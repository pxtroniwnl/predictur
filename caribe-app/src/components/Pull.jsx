// Pull-quote para resaltar frases clave entre escenas
export default function Pull({ children, source }) {
  return (
    <figure className="my-16 sm:my-24 max-w-3xl mx-auto px-6 text-center">
      <blockquote
        className="font-serif italic text-[clamp(1.6rem,3.4vw,2.6rem)] leading-tight text-[var(--color-ink)]"
        style={{ fontVariationSettings: "'opsz' 144" }}
      >
        <span className="text-[var(--color-coral)] mr-1">“</span>
        {children}
        <span className="text-[var(--color-coral)] ml-1">”</span>
      </blockquote>
      {source && (
        <figcaption className="mt-6 text-xs uppercase tracking-[0.22em] text-[var(--color-ink-mute)]">
          {source}
        </figcaption>
      )}
    </figure>
  );
}
