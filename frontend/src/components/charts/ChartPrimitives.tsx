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
import { formatPercent } from "../../utils/format";

type ChartDatum = {
  color?: string;
  label: string;
  rank?: number | null;
  share?: number;
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
  action?: ReactNode;
  caveat?: ReactNode;
  chart?: ReactNode;
  children?: ReactNode;
  className?: string;
  emptyMessage?: string;
  eyebrow?: string;
  isEmpty?: boolean;
  isLoading?: boolean;
  legend?: ReactNode;
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
  axis: "var(--color-text-muted)",
  gold: "var(--color-accent-gold)",
  green: "var(--color-accent-green)",
  grid: "rgba(169, 182, 191, 0.13)",
  line: "var(--color-accent-lime)",
  tooltipCursor: "rgba(169, 182, 191, 0.075)",
};

export function InsightChartCard({
  action,
  caveat,
  chart,
  children,
  className,
  emptyMessage,
  eyebrow,
  isEmpty,
  isLoading,
  legend,
  text,
  title,
}: ChartCardProps) {
  return (
    <ChartPanel
      action={action}
      caveat={caveat}
      chart={chart ?? children}
      className={className}
      emptyMessage={emptyMessage}
      eyebrow={eyebrow}
      isEmpty={isEmpty}
      isLoading={isLoading}
      legend={legend}
      text={text}
      title={title}
    />
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
          {item.color ? (
            <i aria-hidden="true" className="chart-tooltip-marker" style={{ backgroundColor: item.color }} />
          ) : null}
          {item.name ?? "Value"}: {typeof item.value === "number" ? item.value.toLocaleString() : item.value}
          {typeof item.payload?.share === "number" ? ` · ${formatPercent(item.payload.share)}` : ""}
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
        <Tooltip content={<ChartTooltip />} cursor={{ fill: chartColors.tooltipCursor }} />
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
      <BarChart data={data} margin={{ bottom: 0, left: -24, right: 4, top: 12 }}>
        <CartesianGrid stroke={chartColors.grid} strokeDasharray="3 6" vertical={false} />
        <XAxis
          axisLine={false}
          dataKey="label"
          interval={0}
          tick={{ fill: chartColors.axis, fontSize: 11 }}
          tickLine={false}
        />
        <YAxis axisLine={false} tick={{ fill: chartColors.axis, fontSize: 11 }} tickLine={false} />
        <Tooltip content={<ChartTooltip />} cursor={{ fill: chartColors.tooltipCursor }} />
        <Bar barSize={28} dataKey="value" maxBarSize={42} name={valueLabel} radius={[8, 8, 2, 2]}>
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
