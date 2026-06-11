import { Fragment, type ReactNode, useState } from "react";

type ShowMoreListProps<T> = {
  as?: "div" | "ol" | "ul";
  className?: string;
  empty?: ReactNode;
  getKey: (item: T, index: number) => string | number;
  initialCount?: number;
  itemNoun?: string;
  items: T[];
  renderItem: (item: T, index: number) => ReactNode;
};

export function ShowMoreList<T>({
  as: ListElement = "div",
  className,
  empty = null,
  getKey,
  initialCount = 6,
  itemNoun = "item",
  items,
  renderItem,
}: ShowMoreListProps<T>) {
  const [expanded, setExpanded] = useState(false);
  const hasOverflow = items.length > initialCount;
  const visibleItems = expanded || !hasOverflow ? items : items.slice(0, initialCount);
  const remainingCount = Math.max(items.length - initialCount, 0);

  if (items.length === 0) return <>{empty}</>;

  return (
    <div className="show-more-region">
      <ListElement className={className}>
        {visibleItems.map((item, index) => (
          <Fragment key={getKey(item, index)}>
            {renderItem(item, index)}
          </Fragment>
        ))}
      </ListElement>
      {hasOverflow ? (
        <div className="show-more-actions">
          <button
            aria-expanded={expanded}
            className="text-button compact-result-link"
            type="button"
            onClick={() => setExpanded((current) => !current)}
          >
            {expanded
              ? "Show less"
              : `Show ${remainingCount.toLocaleString()} more ${remainingCount === 1 ? itemNoun : `${itemNoun}s`}`}
          </button>
        </div>
      ) : null}
    </div>
  );
}
