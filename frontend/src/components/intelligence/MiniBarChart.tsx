import { lazy, Suspense } from "react";

import { ChartEmptyState } from "../charts/ChartPrimitives";
import type { IntelligenceTone } from "./ComparisonBars";

export type MiniBarDatum = {
  key: string;
  label: string;
  value: number;
  secondaryValue?: number | null;
  tone?: Exclude<IntelligenceTone, "navy">;
};

export type MiniBarChartProps = {
  title?: string;
  description?: string;
  data: MiniBarDatum[];
  valueFormatter?: (value: number) => string;
  emptyLabel?: string;
  height?: "compact" | "regular";
};

const MiniBarChartCanvas = lazy(() =>
  import("./MiniBarChartCanvas").then((module) => ({ default: module.MiniBarChartCanvas })),
);

export function MiniBarChart({
  data,
  description,
  emptyLabel = "No chart data available yet.",
  height = "regular",
  title,
  valueFormatter,
}: MiniBarChartProps) {
  const chartData = data.map((item) => ({
    ...item,
    displayValue: valueFormatter ? valueFormatter(item.value) : item.value.toLocaleString(),
  }));

  return (
    <section className={`mini-bar-chart mini-bar-chart-${height}`} aria-label={title}>
      {title || description ? (
        <div className="intelligence-chart-heading">
          {title ? <h3>{title}</h3> : null}
          {description ? <p>{description}</p> : null}
        </div>
      ) : null}
      {chartData.length ? (
        <>
          <div className="mini-chart-canvas">
            <Suspense fallback={<ChartEmptyState message="Loading chart." />}>
              <MiniBarChartCanvas chartData={chartData} valueFormatter={valueFormatter} />
            </Suspense>
          </div>
          <div className="chart-value-list compact" aria-label="Readable chart values">
            {chartData.map((item) => (
              <span key={item.key}>
                <strong>{item.label}</strong>
                {item.displayValue}
              </span>
            ))}
          </div>
        </>
      ) : (
        <ChartEmptyState message={emptyLabel} />
      )}
    </section>
  );
}