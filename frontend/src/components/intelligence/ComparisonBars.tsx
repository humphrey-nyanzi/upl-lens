export type IntelligenceTone = "green" | "gold" | "navy" | "risk" | "muted";

export type ComparisonBarSegment = {
  label: string;
  value: number;
  tone?: IntelligenceTone;
};

export type HorizontalComparisonBarProps = {
  label?: string;
  segments: ComparisonBarSegment[];
  total?: number;
  showValues?: boolean;
  valueFormatter?: (value: number) => string;
};

export type ShareSegment = {
  label: string;
  value: number;
  tone?: IntelligenceTone;
};

export type StackedShareBarProps = {
  label?: string;
  segments: ShareSegment[];
  valueFormatter?: (value: number, share: number) => string;
  showLegend?: boolean;
};

const defaultValueFormatter = (value: number) => value.toLocaleString();

function safePositiveValue(value: number) {
  return Number.isFinite(value) && value > 0 ? value : 0;
}

export function HorizontalComparisonBar({
  label,
  segments,
  showValues = true,
  total,
  valueFormatter = defaultValueFormatter,
}: HorizontalComparisonBarProps) {
  const safeSegments = segments.map((segment) => ({ ...segment, value: safePositiveValue(segment.value) }));
  const safeTotal = safePositiveValue(total ?? safeSegments.reduce((sum, segment) => sum + segment.value, 0));

  return (
    <div className="horizontal-comparison-bar" aria-label={label}>
      {label ? <strong className="comparison-bar-label">{label}</strong> : null}
      {safeTotal > 0 ? (
        <div className="comparison-bar-track">
          {safeSegments.map((segment) => {
            const share = segment.value / safeTotal;
            return (
              <span
                aria-label={`${segment.label}: ${valueFormatter(segment.value)}`}
                className={`comparison-bar-segment tone-${segment.tone ?? "muted"}`}
                key={segment.label}
                style={{ width: `${Math.max(share * 100, segment.value > 0 ? 4 : 0)}%` }}
              />
            );
          })}
        </div>
      ) : (
        <span className="comparison-bar-empty">No comparison data yet.</span>
      )}
      {showValues ? (
        <div className="comparison-bar-values">
          {safeSegments.map((segment) => (
            <span key={segment.label}>
              {segment.label} <strong>{valueFormatter(segment.value)}</strong>
            </span>
          ))}
        </div>
      ) : null}
    </div>
  );
}

export function StackedShareBar({
  label,
  segments,
  showLegend = true,
  valueFormatter,
}: StackedShareBarProps) {
  const safeSegments = segments.map((segment) => ({ ...segment, value: safePositiveValue(segment.value) }));
  const total = safeSegments.reduce((sum, segment) => sum + segment.value, 0);

  return (
    <div className="stacked-share-bar" aria-label={label}>
      {label ? <strong className="comparison-bar-label">{label}</strong> : null}
      {total > 0 ? (
        <div className="stacked-share-track">
          {safeSegments.map((segment) => {
            const share = segment.value / total;
            const formatted = valueFormatter
              ? valueFormatter(segment.value, share)
              : `${defaultValueFormatter(segment.value)} (${Math.round(share * 100)}%)`;
            return (
              <span
                aria-label={`${segment.label}: ${formatted}`}
                className={`stacked-share-segment tone-${segment.tone ?? "muted"}`}
                key={segment.label}
                style={{ width: `${share * 100}%` }}
              />
            );
          })}
        </div>
      ) : (
        <span className="comparison-bar-empty">No share data yet.</span>
      )}
      {showLegend ? (
        <div className="stacked-share-legend">
          {safeSegments.map((segment) => {
            const share = total > 0 ? segment.value / total : 0;
            const formatted = valueFormatter
              ? valueFormatter(segment.value, share)
              : `${defaultValueFormatter(segment.value)} (${Math.round(share * 100)}%)`;
            return (
              <span key={segment.label}>
                <i className={`tone-${segment.tone ?? "muted"}`} aria-hidden="true" />
                {segment.label} <strong>{formatted}</strong>
              </span>
            );
          })}
        </div>
      ) : null}
    </div>
  );
}
