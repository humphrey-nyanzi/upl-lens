export type MetricDeltaProps = {
  label: string;
  value: string | number;
  context?: string;
  delta?: string | number | null;
  tone?: "positive" | "neutral" | "warning" | "risk";
};

export function MetricDelta({ context, delta, label, tone = "neutral", value }: MetricDeltaProps) {
  const displayValue = typeof value === "number" ? value.toLocaleString() : value;
  const displayDelta = typeof delta === "number" ? delta.toLocaleString() : delta;

  return (
    <article className={`metric-delta metric-delta-${tone}`}>
      <span>{label}</span>
      <strong>{displayValue}</strong>
      {context ? <p>{context}</p> : null}
      {displayDelta ? <em>{displayDelta}</em> : null}
    </article>
  );
}
