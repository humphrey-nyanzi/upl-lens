export type RankingItem = {
  context?: string;
  label: string;
  value: number | string;
};

type RankingListProps = {
  actionLabel?: string;
  items: RankingItem[];
  title: string;
};

export function RankingList({ actionLabel, items, title }: RankingListProps) {
  return (
    <div className="ranking-card">
      <div className="panel-heading compact">
        <div>
          <h2>{title}</h2>
          <p>{items.length > 0 ? "Quick leaders from the selected season." : "No ranking data available yet."}</p>
        </div>
      </div>
      <ol className="ranking-list">
        {items.map((item, index) => (
          <li key={`${item.label}-${index}`}>
            <span className="rank-number">{index + 1}</span>
            <span className="rank-label">
              <strong>{item.label}</strong>
              {item.context ? <small>{item.context}</small> : null}
            </span>
            <strong className="rank-value">{typeof item.value === "number" ? item.value.toLocaleString() : item.value}</strong>
          </li>
        ))}
      </ol>
      {actionLabel ? <button className="ghost-button" type="button">{actionLabel}</button> : null}
    </div>
  );
}
