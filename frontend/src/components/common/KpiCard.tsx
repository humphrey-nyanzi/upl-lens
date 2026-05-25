type KpiCardProps = {
  accent?: "green" | "gold" | "neutral";
  detail: string;
  label: string;
  meta?: string;
  value: number | string;
};

export function KpiCard({ accent = "neutral", detail, label, meta, value }: KpiCardProps) {
  const displayValue = typeof value === "number" ? value.toLocaleString() : value;

  return (
    <article className={`kpi-card accent-${accent}`}>
      <div className="kpi-icon" aria-hidden="true" />
      <div>
        <span>{label}</span>
        <strong>{displayValue}</strong>
        <p>{detail}</p>
        {meta ? <em>{meta}</em> : null}
      </div>
    </article>
  );
}
