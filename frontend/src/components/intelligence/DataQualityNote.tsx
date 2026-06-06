export type DataQualityTone = "good" | "caution" | "limited" | "risk" | "neutral";

export type DataQualityMetric = {
  label: string;
  value: string | number;
  detail?: string | null;
};

export type DataQualityNoteProps = {
  title?: string;
  tone?: DataQualityTone;
  note?: string | null;
  metrics?: DataQualityMetric[];
  compact?: boolean;
};

const defaultTitles: Record<DataQualityTone, string> = {
  caution: "Read with context",
  good: "Data coverage",
  limited: "Limited coverage",
  neutral: "Data note",
  risk: "Data caveat",
};

export function DataQualityNote({
  compact = false,
  metrics = [],
  note,
  title,
  tone = "neutral",
}: DataQualityNoteProps) {
  if (!note && metrics.length === 0) return null;

  return (
    <aside className={`data-quality-note data-quality-${tone} ${compact ? "data-quality-compact" : ""}`}>
      <div className="data-quality-note-copy">
        <strong>{title ?? defaultTitles[tone]}</strong>
        {note ? <p>{note}</p> : null}
      </div>
      {metrics.length ? (
        <dl className="data-quality-metrics">
          {metrics.map((metric) => (
            <div key={metric.label}>
              <dt>{metric.label}</dt>
              <dd>
                <strong>{metric.value}</strong>
                {metric.detail ? <span>{metric.detail}</span> : null}
              </dd>
            </div>
          ))}
        </dl>
      ) : null}
    </aside>
  );
}
