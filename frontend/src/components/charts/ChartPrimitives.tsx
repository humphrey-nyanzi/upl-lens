import type { ReactElement, ReactNode } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { ChartPanel } from "../common/Surface";

type ChartDatum = {
  color?: string;
  label: string;
  value: number;
};

type TrendDatum = {
  label: string;
  value: number;
};

type ChartTooltipPayload = {
  color?: string;
  name?: string;
  payload?: Record<string, unknown>;
  value?: number | string;
};

type ChartTooltipProps = {
  active?: boolean;
  label?: number | string;
  payload?: ChartTooltipPayload[];
};

type ChartShellProps = {
  children: ReactElement;
  height?: number;
};

type ChartCardProps = {
  children: ReactNode;
  eyebrow?: string;
  text?: string;
  title: string;
};

type LegendItem = {
  color: string;
  label: string;
};

type BarChartProps = {
  data: ChartDatum[];
  height?: number;
  valueLabel?: string;
};

type TrendLineChartProps = {
  data: TrendDatum[];
  height?: number;
  valueLabel?: string;
};

const chartColors = {
  axis: "#7f8d99",
  grid: "rgba(169, 182, 191, 0.16)",
  green: "#16a34a",
  gold: "#f5b82e",
  line: "#9bd44a",
};

export function InsightChartCard({ children, eyebrow, text, title }: ChartCardProps) {
  return (
    <ChartPanel eyebrow={eyebrow} text={text} title={title}>
      {children}
    </ChartPanel>
  );
}

export function ChartEmptyState({ message = "No chart data available yet." }: { message?: string }) {
  return <div className="chart-empty-state">{message}</div>;
}

export function ChartLegend({ items }: { items: LegendItem[] }) {
  return (
    <div className="chart-legend" aria-label="Chart legend">
      {items.map((item) => (
        <span key={item.label}>
          <i aria-hidden="true" style={{ backgroundColor: item.color }} />
          {item.label}
        </span>
      ))}
    </div>
  );
}

export function ChartTooltip({ active, label, payload }: ChartTooltipProps) {
  if (!active || !payload?.length) return null;

  return (
    <div className="chart-tooltip">
      <strong>{label}</strong>
      {payload.map((item) => (
        <span key={`${item.name ?? "value"}-${item.value}`}>
          {item.name ?? "Value"}: {typeof item.value === "number" ? item.value.toLocaleString() : item.value}
        </span>
      ))}
    </div>
  );
}

function ChartShell({ children, height = 280 }: ChartShellProps) {
  return (
    <div className="chart-shell" style={{ height }}>
      <ResponsiveContainer width="100%" height="100%">
        {children}
      </ResponsiveContainer>
    </div>
  );
}

export function RankingBarChart({ data, height, valueLabel = "Value" }: BarChartProps) {
  if (data.length === 0) return <ChartEmptyState />;

  return (
    <ChartShell height={height}>
      <BarChart data={data} layout="vertical" margin={{ bottom: 6, left: 8, right: 18, top: 6 }}>
        <CartesianGrid horizontal={false} stroke={chartColors.grid} />
        <XAxis
          axisLine={false}
          dataKey="value"
          tick={{ fill: chartColors.axis, fontSize: 11 }}
          tickLine={false}
          type="number"
        />
        <YAxis
          axisLine={false}
          dataKey="label"
          tick={{ fill: chartColors.axis, fontSize: 12 }}
          tickLine={false}
          type="category"
          width={72}
        />
        <Tooltip content={<ChartTooltip />} cursor={{ fill: "rgba(169, 182, 191, 0.08)" }} />
        <Bar dataKey="value" name={valueLabel} radius={[0, 5, 5, 0]}>
          {data.map((item) => (
            <Cell fill={item.color ?? chartColors.green} key={item.label} />
          ))}
        </Bar>
      </BarChart>
    </ChartShell>
  );
}

export function DistributionBarChart({ data, height, valueLabel = "Value" }: BarChartProps) {
  if (data.length === 0) return <ChartEmptyState />;

  return (
    <ChartShell height={height}>
      <BarChart data={data} margin={{ bottom: 2, left: -22, right: 4, top: 10 }}>
        <CartesianGrid stroke={chartColors.grid} vertical={false} />
        <XAxis
          axisLine={false}
          dataKey="label"
          interval={0}
          tick={{ fill: chartColors.axis, fontSize: 11 }}
          tickLine={false}
        />
        <YAxis axisLine={false} tick={{ fill: chartColors.axis, fontSize: 11 }} tickLine={false} />
        <Tooltip content={<ChartTooltip />} cursor={{ fill: "rgba(169, 182, 191, 0.08)" }} />
        <Bar dataKey="value" name={valueLabel} radius={[5, 5, 0, 0]}>
          {data.map((item) => (
            <Cell fill={item.color ?? chartColors.green} key={item.label} />
          ))}
        </Bar>
      </BarChart>
    </ChartShell>
  );
}

export function TrendLineChart({ data, height, valueLabel = "Value" }: TrendLineChartProps) {
  if (data.length === 0) return <ChartEmptyState />;

  return (
    <ChartShell height={height}>
      <LineChart data={data} margin={{ bottom: 2, left: -22, right: 8, top: 10 }}>
        <CartesianGrid stroke={chartColors.grid} vertical={false} />
        <XAxis dataKey="label" tick={{ fill: chartColors.axis, fontSize: 11 }} tickLine={false} />
        <YAxis axisLine={false} tick={{ fill: chartColors.axis, fontSize: 11 }} tickLine={false} />
        <Tooltip content={<ChartTooltip />} cursor={{ stroke: chartColors.grid }} />
        <Line
          activeDot={{ fill: chartColors.gold, r: 5, stroke: "rgba(245, 184, 46, 0.36)" }}
          dataKey="value"
          dot={{ fill: chartColors.line, r: 3 }}
          name={valueLabel}
          stroke={chartColors.line}
          strokeWidth={2}
          type="monotone"
        />
      </LineChart>
    </ChartShell>
  );
}

export function GoalTimingHeatmap({ data, height, valueLabel = "Goals" }: BarChartProps) {
  if (data.length === 0) return <ChartEmptyState message="No regular-time goal timing data available yet." />;

  return <DistributionBarChart data={data} height={height} valueLabel={valueLabel} />;
}
