import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { ChartEmptyState, ChartTooltip } from "../charts/ChartPrimitives";
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

const toneColors: Record<NonNullable<MiniBarDatum["tone"]>, string> = {
  gold: "var(--color-accent-gold)",
  green: "var(--color-chart-green-muted)",
  muted: "rgba(15, 23, 32, 0.18)",
  risk: "var(--color-risk)",
};

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
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ bottom: 0, left: -22, right: 8, top: 8 }}>
                <CartesianGrid stroke="var(--color-chart-grid)" strokeDasharray="3 6" vertical={false} />
                <XAxis
                  axisLine={false}
                  dataKey="label"
                  interval={0}
                  tick={{ fill: "var(--color-text-muted)", fontSize: 11 }}
                  tickLine={false}
                />
                <YAxis
                  axisLine={false}
                  tick={{ fill: "var(--color-text-muted)", fontSize: 11 }}
                  tickFormatter={(value) => (valueFormatter ? valueFormatter(Number(value)) : String(value))}
                  tickLine={false}
                />
                <Tooltip content={<ChartTooltip />} cursor={{ fill: "var(--color-chart-cursor)" }} />
                <Bar dataKey="value" name="Value" radius={[6, 6, 2, 2]}>
                  {chartData.map((item) => (
                    <Cell fill={toneColors[item.tone ?? "green"]} key={item.key} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
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
