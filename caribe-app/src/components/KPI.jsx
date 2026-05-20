export default function KPI({ value, label, sub, accent = "teal" }) {
  const color = {
    teal: "text-[var(--color-teal)]",
    coral: "text-[var(--color-coral)]",
    ink: "text-[var(--color-ink)]",
  }[accent];

  return (
    <div className="border-t border-[var(--color-rule)] pt-4">
      <div className={`font-serif text-4xl sm:text-5xl tabular leading-none ${color}`}>
        {value}
      </div>
      <div className="mt-3 text-xs uppercase tracking-[0.18em] text-[var(--color-ink-mute)] font-medium">
        {label}
      </div>
      {sub && (
        <div className="mt-1 text-sm text-[var(--color-ink-soft)] leading-snug">
          {sub}
        </div>
      )}
    </div>
  );
}
