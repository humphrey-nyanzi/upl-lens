import { KpiCard, type KpiCardProps } from "./KpiCard";

type MetricCardProps = Pick<KpiCardProps, "accent" | "context" | "detail" | "icon" | "label" | "trend" | "value" | "variant">;

export function MetricCard(props: MetricCardProps) {
  return <KpiCard {...props} />;
}
