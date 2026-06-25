import type { CSSProperties, ReactElement, ReactNode } from "react";
import { cloneElement, useLayoutEffect, useRef, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  LabelList,
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
  isPeak?: boolean;
  label: string;
  peakLabel?: string;
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

type ChartElement = ReactElement<{ height?: number; width?: number }>;

type ChartShellProps = {
  children: ChartElement;
  height?: number;
};

type ResponsiveChartFrameProps = {
  children: ChartElement;
  className?: string;
  height?: number;
  style?: CSSProperties;
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
  largeMetric?: string | null;
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
  grid: "var(--color-chart-grid)",
  line: "var(--color-green)",
  tooltipCursor: "var(--color-chart-cursor)",
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
  largeMetric,
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
      largeMetric={largeMetric}
      legend={legend}
      text={text}
      title={title}
    />
  );
}

export function ChartEmptyState({ message = "No chart data available yet." }: { message?: string }) {
  return (
    <div className="chart-empty-state" role="status">
      {message}
    </div>
  );
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

export function ResponsiveChartFrame({
  children,
  className = "chart-fill-frame",
  height,
  style,
}: ResponsiveChartFrameProps) {
  const frameRef = useRef<HTMLDivElement | null>(null);
  const [measuredSize, setMeasuredSize] = useState<{ height: number; width: number } | null>(null);

  useLayoutEffect(() => {
    const frame = frameRef.current;
    if (!frame) return;

    let animationFrame = 0;
    const updateMeasuredSize = () => {
      const rect = frame.getBoundingClientRect();
      const nextSize = {
        height: Math.floor(rect.height),
        width: Math.floor(rect.width),
      };

      if (nextSize.width <= 0 || nextSize.height <= 0) return;

      setMeasuredSize((currentSize) => {
        if (currentSize?.width === nextSize.width && currentSize.height === nextSize.height) {
          return currentSize;
        }
        return nextSize;
      });
    };

    animationFrame = window.requestAnimationFrame(updateMeasuredSize);

    if (typeof ResizeObserver === "undefined") {
      return () => window.cancelAnimationFrame(animationFrame);
    }

    const observer = new ResizeObserver(updateMeasuredSize);
    observer.observe(frame);

    return () => {
      window.cancelAnimationFrame(animationFrame);
      observer.disconnect();
    };
  }, []);

  return (
    <div ref={frameRef} className={className} style={{ ...style, ...(height ? { height, minHeight: height } : {}) }}>
      {measuredSize ? (
        cloneElement(children, { height: measuredSize.height, width: measuredSize.width })
      ) : (
        <div className="chart-measurement-placeholder" aria-hidden="true" />
      )}
    </div>
  );
}

function ChartShell({ children, height = 280 }: ChartShellProps) {
  return <ResponsiveChartFrame className="chart-shell" height={height}>{children}</ResponsiveChartFrame>;
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
      <BarChart data={data} margin={{ bottom: 0, left: -18, right: 6, top: 14 }}>
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
        <Bar barSize={26} dataKey="value" maxBarSize={38} name={valueLabel} radius={[7, 7, 2, 2]}>
          <LabelList
            dataKey="peakLabel"
            fill="var(--color-accent-gold-text)"
            fontSize={11}
            fontWeight={600}
            position="top"
          />
          {data.map((item) => (
            <Cell
              className={item.isPeak ? "chart-bar-peak" : undefined}
              fill={item.color ?? chartColors.green}
              key={item.label}
              stroke={item.isPeak ? "var(--color-accent-gold-text)" : "transparent"}
              strokeWidth={item.isPeak ? 2 : 0}
            />
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
          activeDot={{ fill: chartColors.gold, r: 5, stroke: "var(--color-gold-soft)" }}
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
