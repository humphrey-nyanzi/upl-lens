export type SignalTone = "positive" | "neutral" | "warning" | "risk" | "muted";

export type SignalChipProps = {
  label: string;
  tone?: SignalTone;
  description?: string | null;
  size?: "small" | "medium";
};

export type SignalChipItem = {
  key?: string;
  label: string;
  tone?: SignalTone;
  description?: string | null;
};

export type SignalChipGroupProps = {
  items: SignalChipItem[];
  emptyLabel?: string;
  size?: "small" | "medium";
  maxVisible?: number;
  overflowLabel?: string;
  overflowMode?: "disclosure" | "inline-summary";
};

export function SignalChip({ description, label, size = "medium", tone = "neutral" }: SignalChipProps) {
  const accessibleLabel = description ? `${label}: ${description}` : label;

  return (
    <span
      aria-label={accessibleLabel}
      className={`signal-chip signal-chip-${tone} signal-chip-${size}`}
      title={description ?? undefined}
    >
      {label}
    </span>
  );
}

export function SignalChipGroup({
  emptyLabel,
  items,
  maxVisible,
  overflowLabel = "Additional signals",
  overflowMode = "disclosure",
  size = "medium",
}: SignalChipGroupProps) {
  if (items.length === 0) {
    return emptyLabel ? <span className="signal-chip-group-empty">{emptyLabel}</span> : null;
  }

  const visibleItems = maxVisible ? items.slice(0, maxVisible) : items;
  const overflowItems = maxVisible ? items.slice(maxVisible) : [];
  const remainingCount = overflowItems.length;

  return (
    <div className="signal-chip-group">
      {visibleItems.map((item, index) => (
        <SignalChip
          description={item.description}
          key={item.key ?? `${item.label}-${index}`}
          label={item.label}
          size={size}
          tone={item.tone}
        />
      ))}
      {remainingCount && overflowMode === "inline-summary" ? (
        <span
          aria-label={`${remainingCount} more ${remainingCount === 1 ? "signal" : "signals"}: ${overflowItems
            .map((item) => (item.description ? `${item.label}: ${item.description}` : item.label))
            .join(", ")}`}
          className={`signal-chip signal-chip-muted signal-chip-${size} signal-chip-overflow-summary`}
        >
          +{remainingCount}: {overflowItems.map((item) => item.label).join(", ")}
        </span>
      ) : null}
      {remainingCount && overflowMode === "disclosure" ? (
        <details className={`signal-chip-overflow signal-chip-overflow-${size}`}>
          <summary
            aria-label={`Show ${remainingCount} more ${remainingCount === 1 ? "signal" : "signals"}`}
            className={`signal-chip signal-chip-muted signal-chip-${size}`}
          >
            +{remainingCount}
          </summary>
          <ul className="signal-chip-overflow-list" aria-label={overflowLabel}>
            {overflowItems.map((item, index) => (
              <li key={item.key ?? `${item.label}-overflow-${index}`}>
                <SignalChip description={item.description} label={item.label} size={size} tone={item.tone} />
              </li>
            ))}
          </ul>
        </details>
      ) : null}
    </div>
  );
}
