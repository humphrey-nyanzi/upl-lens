import {
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Link } from "react-router-dom";

import { ChartEmptyState, ChartTooltip } from "../charts/ChartPrimitives";
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

const scatterColors: Record<IntelligenceTone, string> = {
  gold: "var(--color-accent-gold)",
  green: "var(--color-green)",
  muted: "rgba(15, 23, 32, 0.3)",
  navy: "var(--color-text)",
  risk: "var(--color-risk)",
};

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
  const renderPointLabel = (item: ScatterDatum) => (
    <>
      <span>{item.label}</span>
      <strong>{formatPointValue(item)}</strong>
    </>
  );

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
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ bottom: 14, left: -18, right: 16, top: 16 }}>
                <CartesianGrid stroke="var(--color-chart-grid)" strokeDasharray="3 6" />
                <XAxis
                  dataKey="x"
                  name={xLabel}
                  tick={{ fill: "var(--color-text-muted)", fontSize: 11 }}
                  tickFormatter={(value) => (xFormatter ? xFormatter(Number(value)) : String(value))}
                  type="number"
                />
                <YAxis
                  dataKey="y"
                  name={yLabel}
                  tick={{ fill: "var(--color-text-muted)", fontSize: 11 }}
                  tickFormatter={(value) => (yFormatter ? yFormatter(Number(value)) : String(value))}
                  type="number"
                />
                <Tooltip content={<ChartTooltip />} cursor={{ stroke: "var(--color-chart-grid)" }} />
                <Scatter data={chartData} name={`${xLabel} / ${yLabel}`}>
                  {chartData.map((item) => (
                    <Cell fill={scatterColors[item.tone ?? "green"]} key={item.id} />
                  ))}
                </Scatter>
              </ScatterChart>
            </ResponsiveContainer>
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
                    {renderPointLabel(item)}
                  </Link>
                ) : (
                  renderPointLabel(item)
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
