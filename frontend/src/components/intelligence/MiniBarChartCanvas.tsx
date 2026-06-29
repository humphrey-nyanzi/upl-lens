import { Bar, BarChart, CartesianGrid, Cell, Tooltip, XAxis, YAxis } from "recharts";

import { ChartTooltip, ResponsiveChartFrame } from "../charts/ChartPrimitives";
import type { MiniBarDatum } from "./MiniBarChart";

type MiniBarChartCanvasProps = {
  chartData: Array<MiniBarDatum & { displayValue: string }>;
  valueFormatter?: (value: number) => string;
};

const toneColors: Record<NonNullable<MiniBarDatum["tone"]>, string> = {
  gold: "var(--color-accent-gold)",
  green: "var(--color-chart-green-muted)",
  muted: "rgba(15, 23, 32, 0.18)",
  risk: "var(--color-risk)",
};

export function MiniBarChartCanvas({ chartData, valueFormatter }: MiniBarChartCanvasProps) {
  return (
    <ResponsiveChartFrame>
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
    </ResponsiveChartFrame>
  );
}