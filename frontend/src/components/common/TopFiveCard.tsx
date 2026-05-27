import type { ReactNode } from "react";

import { TeamMarker } from "./TeamMarker";

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
            return (
              <li className={index === 0 ? "leader" : undefined} key={item.id}>
                <span className="top-five-rank">{index + 1}</span>
                <TeamMarker className="top-five-marker" label={item.label} initials={item.marker} />
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
