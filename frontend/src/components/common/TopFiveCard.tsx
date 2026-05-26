import type { ReactNode } from "react";

export type TopFiveItem = {
  context?: string;
  id: string;
  label: string;
  marker?: string;
  value: number | string;
};

type TopFiveCardProps = {
  action?: ReactNode;
  emptyMessage?: string;
  eyebrow?: string;
  items: TopFiveItem[];
  title: string;
  valueLabel?: string;
};

function getInitials(label: string) {
  return label
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}

function getStableMarkerTone(label: string) {
  const toneCount = 5;
  const hash = Array.from(label).reduce((total, character) => total + character.charCodeAt(0), 0);

  return (hash % toneCount) + 1;
}

export function TopFiveCard({
  action,
  emptyMessage = "No ranking data available yet.",
  eyebrow,
  items,
  title,
  valueLabel,
}: TopFiveCardProps) {
  return (
    <section className="top-five-card">
      <div className="surface-heading compact">
        <div>
          {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
          <h2>{title}</h2>
          {valueLabel ? <p>{valueLabel}</p> : null}
        </div>
      </div>

      {items.length > 0 ? (
        <ol className="top-five-list">
          {items.slice(0, 5).map((item, index) => {
            const marker = item.marker ?? getInitials(item.label);
            const markerTone = getStableMarkerTone(item.label);

            return (
              <li className={index === 0 ? "leader" : undefined} key={item.id}>
                <span className="top-five-rank">{index + 1}</span>
                <span className="top-five-marker" data-tone={markerTone} aria-hidden="true">
                  {marker}
                </span>
                <span className="top-five-label">
                  <strong>{item.label}</strong>
                  {item.context ? <small>{item.context}</small> : null}
                </span>
                <strong className="top-five-value">
                  {typeof item.value === "number" ? item.value.toLocaleString() : item.value}
                </strong>
              </li>
            );
          })}
        </ol>
      ) : (
        <div className="empty-state">{emptyMessage}</div>
      )}

      {action ? <div className="top-five-action">{action}</div> : null}
    </section>
  );
}
