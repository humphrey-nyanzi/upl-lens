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
};

export function SignalChip({ description, label, size = "medium", tone = "neutral" }: SignalChipProps) {
  return (
    <span className={`signal-chip signal-chip-${tone} signal-chip-${size}`} title={description ?? undefined}>
      {label}
      {description ? <span className="visually-hidden">: {description}</span> : null}
    </span>
  );
}

export function SignalChipGroup({ emptyLabel, items, maxVisible, size = "medium" }: SignalChipGroupProps) {
  if (items.length === 0) {
    return emptyLabel ? <span className="signal-chip-group-empty">{emptyLabel}</span> : null;
  }

  const visibleItems = maxVisible ? items.slice(0, maxVisible) : items;
  const remainingCount = maxVisible && items.length > maxVisible ? items.length - maxVisible : 0;

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
      {remainingCount ? <SignalChip label={`+${remainingCount}`} size={size} tone="muted" /> : null}
    </div>
  );
}
