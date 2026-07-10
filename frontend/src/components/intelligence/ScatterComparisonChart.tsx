import {
  CartesianGrid,
  Cell,
  ReferenceLine,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { ChartTooltip, ResponsiveChartFrame } from "../charts/ChartPrimitives";
import type { IntelligenceTone } from "./ComparisonBars";
import type { ScatterDatum } from "./ScatterComparisonPlot";

type ScatterComparisonChartProps = {
  chartData: ScatterDatum[];
  referenceX?: number | null;
  referenceXLabel?: string;
  referenceY?: number | null;
  referenceYLabel?: string;
  xFormatter?: (value: number) => string;
  xLabel: string;
  yFormatter?: (value: number) => string;
  yLabel: string;
};

const scatterColors: Record<IntelligenceTone, string> = {
  gold: "var(--color-accent-gold)",
  green: "var(--color-green)",
  muted: "rgba(15, 23, 32, 0.3)",
  navy: "var(--color-text)",
  risk: "var(--color-risk)",
};

const referenceLabelStyle = {
  fill: "var(--color-text-muted)",
  fontSize: 10,
};

export function ScatterComparisonChart({
  chartData,
  referenceX,
  referenceXLabel,
  referenceY,
  referenceYLabel,
  xFormatter,
  xLabel,
  yFormatter,
  yLabel,
}: ScatterComparisonChartProps) {
  return (
    <ResponsiveChartFrame>
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
        {typeof referenceX === "number" ? (
          <ReferenceLine
            label={referenceXLabel ? { ...referenceLabelStyle, position: "insideTopRight", value: referenceXLabel } : undefined}
            stroke="rgba(15, 23, 32, 0.34)"
            strokeDasharray="4 4"
            x={referenceX}
          />
        ) : null}
        {typeof referenceY === "number" ? (
          <ReferenceLine
            label={referenceYLabel ? { ...referenceLabelStyle, position: "insideTopLeft", value: referenceYLabel } : undefined}
            stroke="rgba(15, 23, 32, 0.34)"
            strokeDasharray="4 4"
            y={referenceY}
          />
        ) : null}
        <Tooltip content={<ChartTooltip />} cursor={{ stroke: "var(--color-chart-grid)" }} />
        <Scatter data={chartData} name={`${xLabel} / ${yLabel}`}>
          {chartData.map((item) => (
            <Cell fill={scatterColors[item.tone ?? "green"]} key={item.id} />
          ))}
        </Scatter>
      </ScatterChart>
    </ResponsiveChartFrame>
  );
}
