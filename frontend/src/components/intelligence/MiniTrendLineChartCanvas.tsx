import { CartesianGrid, Line, LineChart, Tooltip, XAxis, YAxis } from "recharts";

import { ChartTooltip, ResponsiveChartFrame } from "../charts/ChartPrimitives";
import type { MiniTrendDatum } from "./MiniTrendLineChart";

type MiniTrendChartDatum = MiniTrendDatum & { displayValue: string };

type MiniTrendLineChartCanvasProps = {
  chartData: MiniTrendChartDatum[];
  valueFormatter?: (value: number) => string;
  valueLabel: string;
};

type TrendDotProps = {
  cx?: number;
  cy?: number;
  payload?: MiniTrendChartDatum;
};

const toneColors: Record<NonNullable<MiniTrendDatum["tone"]>, string> = {
  gold: "var(--color-accent-gold)",
  green: "var(--color-chart-green-muted)",
  muted: "rgba(15, 23, 32, 0.28)",
  risk: "var(--color-risk)",
};

function TrendDot({ cx, cy, payload }: TrendDotProps) {
  if (typeof cx !== "number" || typeof cy !== "number") return null;

  const color = toneColors[payload?.tone ?? "green"];

  return <circle cx={cx} cy={cy} r={4} fill={color} stroke="var(--color-surface)" strokeWidth={2} />;
}

export function MiniTrendLineChartCanvas({ chartData, valueFormatter, valueLabel }: MiniTrendLineChartCanvasProps) {
  return (
    <ResponsiveChartFrame>
      <LineChart data={chartData} margin={{ bottom: 0, left: -22, right: 12, top: 12 }}>
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
        <Tooltip content={<ChartTooltip />} cursor={{ stroke: "var(--color-chart-grid)" }} />
        <Line
          activeDot={{ fill: "var(--color-accent-gold)", r: 5, stroke: "var(--color-surface)", strokeWidth: 2 }}
          dataKey="value"
          dot={<TrendDot />}
          name={valueLabel}
          stroke="var(--color-green)"
          strokeWidth={2.25}
          type="monotone"
        />
      </LineChart>
    </ResponsiveChartFrame>
  );
}
