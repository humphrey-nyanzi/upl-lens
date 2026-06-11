import { lazy, Suspense } from "react";
import { Link } from "react-router-dom";

import { ChartEmptyState } from "../charts/ChartPrimitives";
import type { IntelligenceTone } from "./ComparisonBars";

export type ScatterDatum = {
  id: string;
  label: string;
  x: number;
  y: number;
  group?: string | null;
  tone?: IntelligenceTone;
  href?: string;
};

export type ScatterComparisonPlotProps = {
  title?: string;
  description?: string;
  xLabel: string;
  yLabel: string;
  data: ScatterDatum[];
  xFormatter?: (value: number) => string;
  yFormatter?: (value: number) => string;
  emptyLabel?: string;
};

const ScatterComparisonChart = lazy(() =>
  import("./ScatterComparisonChart").then((module) => ({ default: module.ScatterComparisonChart })),
);

function PointLabel({
  item,
  xFormatter,
  yFormatter,
}: {
  item: ScatterDatum;
  xFormatter?: (value: number) => string;
  yFormatter?: (value: number) => string;
}) {
  const value = `${xFormatter ? xFormatter(item.x) : item.x.toLocaleString()} / ${
    yFormatter ? yFormatter(item.y) : item.y.toLocaleString()
  }`;

  return (
    <>
      <span>{item.label}</span>
      <strong>{value}</strong>
    </>
  );
}

export function ScatterComparisonPlot({
  data,
  description,
  emptyLabel = "No comparison data available yet.",
  title,
  xFormatter,
  xLabel,
  yFormatter,
  yLabel,
}: ScatterComparisonPlotProps) {
  const chartData = data.filter((item) => Number.isFinite(item.x) && Number.isFinite(item.y));
  const formatPointValue = (item: ScatterDatum) =>
    `${xFormatter ? xFormatter(item.x) : item.x.toLocaleString()} / ${yFormatter ? yFormatter(item.y) : item.y.toLocaleString()}`;

  return (
    <section className="scatter-comparison-plot" aria-label={title}>
      {title || description ? (
        <div className="intelligence-chart-heading">
          {title ? <h3>{title}</h3> : null}
          {description ? <p>{description}</p> : null}
        </div>
      ) : null}
      {chartData.length ? (
        <>
          <div className="scatter-chart-canvas">
            <Suspense fallback={<ChartEmptyState message="Loading comparison chart." />}>
              <ScatterComparisonChart
                chartData={chartData}
                xFormatter={xFormatter}
                xLabel={xLabel}
                yFormatter={yFormatter}
                yLabel={yLabel}
              />
            </Suspense>
          </div>
          <div className="scatter-axis-labels" aria-hidden="true">
            <span>{xLabel}</span>
            <span>{yLabel}</span>
          </div>
          <ul className="scatter-point-list" aria-label="Comparison points">
            {chartData.slice(0, 8).map((item) => (
              <li key={item.id}>
                {item.href ? (
                  <Link to={item.href} aria-label={`Open ${item.label}: ${formatPointValue(item)}`}>
                    <PointLabel item={item} xFormatter={xFormatter} yFormatter={yFormatter} />
                  </Link>
                ) : (
                  <PointLabel item={item} xFormatter={xFormatter} yFormatter={yFormatter} />
                )}
              </li>
            ))}
          </ul>
        </>
      ) : (
        <ChartEmptyState message={emptyLabel} />
      )}
    </section>
  );
}
