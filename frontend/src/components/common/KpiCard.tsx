import type { ReactNode } from "react";

export type KpiCardProps = {
  accent?: "green" | "gold" | "neutral" | "risk";
  className?: string;
  context?: string;
  detail?: string;
  icon?: ReactNode;
  label: string;
  meta?: string;
  trend?: string;
  value: number | string;
  variant?: "default" | "featured" | "compact";
};

export function KpiCard({
  accent = "neutral",
  className,
  context,
  detail,
  icon,
  label,
  meta,
  trend,
  value,
  variant = "default",
}: KpiCardProps) {
  const displayValue = typeof value === "number" ? value.toLocaleString() : value;
  const supportingText = context ?? detail;
  const classNames = ["kpi-card", `accent-${accent}`, `kpi-${variant}`, icon ? "has-icon" : "no-icon", className].filter(Boolean).join(" ");

  return (
    <article className={classNames}>
      {icon ? (
        <div className="kpi-icon" aria-hidden="true">
          {icon}
        </div>
      ) : null}
      <div>
        <span>{label}</span>
        <strong>{displayValue}</strong>
        {supportingText ? <p>{supportingText}</p> : null}
        {trend ?? meta ? <em>{trend ?? meta}</em> : null}
      </div>
    </article>
  );
}
