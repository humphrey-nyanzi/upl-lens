import type { ReactNode } from "react";

type SurfaceProps = {
  action?: ReactNode;
  children: ReactNode;
  eyebrow?: string;
  text?: string;
  title?: string;
};

type ChartPanelProps = {
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
  title?: string;
};

type InsightCardProps = {
  action?: ReactNode;
  metric?: ReactNode;
  text: string;
  title: string;
};

type RankingCardProps = {
  action?: ReactNode;
  children: ReactNode;
  subtitle?: string;
  title: string;
};

type MatchCardProps = {
  meta?: string;
  score: string;
  status: string;
  teams: string;
};

type DataStatusCardProps = {
  detail: string;
  label: string;
  tone?: "live" | "warning" | "error";
  value: string;
};

export function SectionPanel({ action, children, eyebrow, text, title }: SurfaceProps) {
  return (
    <section className="section-panel">
      {title ? (
        <div className="surface-heading">
          <div>
            {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
            <h2>{title}</h2>
            {text ? <p>{text}</p> : null}
          </div>
          {action}
        </div>
      ) : null}
      {children}
    </section>
  );
}

export function PageHero({ action, children, eyebrow, text, title }: SurfaceProps) {
  return (
    <section className="page-hero">
      <div>
        {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
        {title ? <h1>{title}</h1> : null}
        {text ? <p>{text}</p> : null}
      </div>
      {action}
      {children}
    </section>
  );
}

export function InsightCard({ action, metric, text, title }: InsightCardProps) {
  return (
    <article className="insight-card">
      <div>
        <span>Insight</span>
        <h2>{title}</h2>
        <p>{text}</p>
      </div>
      {metric ? <div className="insight-card-metric">{metric}</div> : null}
      {action}
    </article>
  );
}

export function RankingCard({ action, children, subtitle, title }: RankingCardProps) {
  return (
    <section className="ranking-card">
      <div className="surface-heading compact">
        <div>
          <h2>{title}</h2>
          {subtitle ? <p>{subtitle}</p> : null}
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}

export function ChartPanel({
  action,
  caveat,
  chart,
  children,
  className,
  emptyMessage = "No chart data available yet.",
  eyebrow,
  isEmpty = false,
  isLoading = false,
  legend,
  text,
  title,
}: ChartPanelProps) {
  const body = chart ?? children;

  return (
    <section className={className ? `chart-panel ${className}` : "chart-panel"}>
      <div className="surface-heading">
        <div>
          {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
          {title ? <h2>{title}</h2> : null}
          {text ? <p>{text}</p> : null}
        </div>
        {action}
      </div>
      <div className="chart-panel-body" aria-busy={isLoading || undefined}>
        {isLoading ? <div className="chart-loading-state">Loading chart data...</div> : null}
        {!isLoading && isEmpty ? <div className="chart-empty-state">{emptyMessage}</div> : null}
        {!isLoading && !isEmpty ? body : null}
      </div>
      {legend ? <div className="chart-panel-legend">{legend}</div> : null}
      {caveat ? <div className="chart-panel-caveat">{caveat}</div> : null}
    </section>
  );
}

export function MatchCard({ meta, score, status, teams }: MatchCardProps) {
  return (
    <article className="match-card">
      <div>
        {meta ? <span>{meta}</span> : null}
        <strong>{teams}</strong>
      </div>
      <div className="match-card-score">
        <strong>{score}</strong>
        <span>{status}</span>
      </div>
    </article>
  );
}

export function DataStatusCard({ detail, label, tone = "live", value }: DataStatusCardProps) {
  return (
    <article className={`data-status-card ${tone}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      <p>{detail}</p>
    </article>
  );
}
