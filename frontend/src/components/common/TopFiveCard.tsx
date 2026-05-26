import type { ReactNode } from "react";

export type TopFiveItem = {
  context?: string;
  id: string;
  label: string;
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
        {action}
      </div>

      {items.length > 0 ? (
        <ol className="top-five-list">
          {items.slice(0, 5).map((item, index) => (
            <li className={index === 0 ? "leader" : undefined} key={item.id}>
              <span className="top-five-rank">{index + 1}</span>
              <span className="top-five-label">
                <strong>{item.label}</strong>
                {item.context ? <small>{item.context}</small> : null}
              </span>
              <strong className="top-five-value">{typeof item.value === "number" ? item.value.toLocaleString() : item.value}</strong>
            </li>
          ))}
        </ol>
      ) : (
        <div className="empty-state">{emptyMessage}</div>
      )}
    </section>
  );
}
