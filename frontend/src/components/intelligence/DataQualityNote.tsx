export type DataQualityTone = "good" | "caution" | "limited" | "risk" | "neutral";
export type DataQualityVariant = "evidence" | "caveat" | "freshness" | "source";
export type DataQualityTopic =
  | "coverage"
  | "events"
  | "lineups"
  | "methodology"
  | "officials"
  | "players"
  | "source"
  | "stats"
  | "timeline";

export type DataQualityMetric = {
  label: string;
  value: string | number;
  detail?: string | null;
};

export type DataQualityNoteProps = {
  title?: string;
  tone?: DataQualityTone;
  variant?: DataQualityVariant;
  topic?: DataQualityTopic;
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

const variantTitles: Record<DataQualityVariant, string> = {
  caveat: "Data caveat",
  evidence: "Evidence note",
  freshness: "Freshness note",
  source: "Source boundary",
};

const topicLabels: Record<DataQualityTopic, string> = {
  coverage: "Coverage",
  events: "Events",
  lineups: "Lineups",
  methodology: "Methodology",
  officials: "Officials",
  players: "Players",
  source: "Source",
  stats: "Stats",
  timeline: "Timeline",
};

const emptyMetrics: DataQualityMetric[] = [];

export function DataQualityNote({
  compact = false,
  metrics = emptyMetrics,
  note,
  title,
  tone = "neutral",
  topic,
  variant,
}: DataQualityNoteProps) {
  if (!note && metrics.length === 0) return null;

  const resolvedVariant = variant ?? "evidence";
  const resolvedTitle = title ?? (variant ? variantTitles[variant] : defaultTitles[tone]);

  return (
    <aside
      className={`data-quality-note data-quality-${tone} data-quality-${resolvedVariant} ${
        topic ? `data-quality-topic-${topic}` : ""
      } ${compact ? "data-quality-compact" : ""}`}
    >
      <div className="data-quality-note-copy">
        <div className="data-quality-note-heading">
          <strong>{resolvedTitle}</strong>
          {topic ? <span>{topicLabels[topic]}</span> : null}
        </div>
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
