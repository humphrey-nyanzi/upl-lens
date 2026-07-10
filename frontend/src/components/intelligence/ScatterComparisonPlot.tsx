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
  maxPreviewPoints?: number;
  showReferenceGuides?: boolean;
};

const ScatterComparisonChart = lazy(() =>
  import("./ScatterComparisonChart").then((module) => ({ default: module.ScatterComparisonChart })),
);

function median(values: number[]) {
  if (!values.length) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const midpoint = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[midpoint] : (sorted[midpoint - 1] + sorted[midpoint]) / 2;
}

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

function ScatterPointListItem({
  formatPointValue,
  item,
  xFormatter,
  yFormatter,
}: {
  formatPointValue: (item: ScatterDatum) => string;
  item: ScatterDatum;
  xFormatter?: (value: number) => string;
  yFormatter?: (value: number) => string;
}) {
  return (
    <li>
      {item.href ? (
        <Link to={item.href} aria-label={`Open ${item.label}: ${formatPointValue(item)}`}>
          <PointLabel item={item} xFormatter={xFormatter} yFormatter={yFormatter} />
        </Link>
      ) : (
        <PointLabel item={item} xFormatter={xFormatter} yFormatter={yFormatter} />
      )}
    </li>
  );
}

export function ScatterComparisonPlot({
  data,
  description,
  emptyLabel = "No comparison data available yet.",
  maxPreviewPoints = 8,
  showReferenceGuides = true,
  title,
  xFormatter,
  xLabel,
  yFormatter,
  yLabel,
}: ScatterComparisonPlotProps) {
  const chartData = data.filter((item) => Number.isFinite(item.x) && Number.isFinite(item.y));
  const previewPoints = chartData.slice(0, maxPreviewPoints);
  const overflowPoints = chartData.slice(maxPreviewPoints);
  const referenceX = showReferenceGuides && chartData.length > 1 ? median(chartData.map((item) => item.x)) : null;
  const referenceY = showReferenceGuides && chartData.length > 1 ? median(chartData.map((item) => item.y)) : null;
  const hasReferenceGuides = referenceX !== null || referenceY !== null;
  const comparisonContext = hasReferenceGuides
    ? "Median guides mark the middle of this filtered comparison, so points beyond a guide sit above the typical value shown here."
    : "Each point compares the two axis values for one visible item in this filtered view.";
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
                referenceX={referenceX}
                referenceXLabel={`Median ${xLabel}`}
                referenceY={referenceY}
                referenceYLabel={`Median ${yLabel}`}
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
          <p className="scatter-reference-note">{comparisonContext}</p>
          <ul className="scatter-point-list" aria-label="Comparison point preview">
            {previewPoints.map((item) => (
              <ScatterPointListItem
                formatPointValue={formatPointValue}
                item={item}
                key={item.id}
                xFormatter={xFormatter}
                yFormatter={yFormatter}
              />
            ))}
          </ul>
          {overflowPoints.length ? (
            <details className="scatter-point-overflow">
              <summary>Show {overflowPoints.length} more comparison points</summary>
              <ul className="scatter-point-list" aria-label="Additional comparison points">
                {overflowPoints.map((item) => (
                  <ScatterPointListItem
                    formatPointValue={formatPointValue}
                    item={item}
                    key={item.id}
                    xFormatter={xFormatter}
                    yFormatter={yFormatter}
                  />
                ))}
              </ul>
            </details>
          ) : null}
        </>
      ) : (
        <ChartEmptyState message={emptyLabel} />
      )}
    </section>
  );
}
