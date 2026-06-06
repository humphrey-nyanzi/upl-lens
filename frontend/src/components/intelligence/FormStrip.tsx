export type FormResult = "W" | "D" | "L" | "N/A";

export type FormStripItem = {
  id: string;
  result: FormResult;
  label?: string;
  href?: string;
};

export type FormStripProps = {
  items: FormStripItem[];
  emptyLabel?: string;
  compact?: boolean;
};

const resultLabel: Record<FormResult, string> = {
  D: "Draw",
  L: "Loss",
  "N/A": "Not available",
  W: "Win",
};

export function FormStrip({ compact = false, emptyLabel = "No recent form available.", items }: FormStripProps) {
  if (items.length === 0) return <span className="form-strip-empty">{emptyLabel}</span>;

  return (
    <div className={`form-strip ${compact ? "form-strip-compact" : ""}`} aria-label="Recent form">
      {items.map((item) => {
        const content = (
          <>
            <strong>{item.result}</strong>
            <span>{item.label ?? resultLabel[item.result]}</span>
          </>
        );

        return item.href ? (
          <a className={`form-strip-item result-${item.result.toLowerCase().replace("/", "-")}`} href={item.href} key={item.id}>
            {content}
          </a>
        ) : (
          <span className={`form-strip-item result-${item.result.toLowerCase().replace("/", "-")}`} key={item.id}>
            {content}
          </span>
        );
      })}
    </div>
  );
}
