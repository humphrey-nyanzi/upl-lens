import type { ReactNode } from "react";

import { formatScoreline, matchStatus } from "../../utils/format";
import type { MatchSummary } from "../../api/types";
import { TeamMarker } from "./TeamMarker";

type StatusPillProps = {
  tone?: "default" | "muted" | "warning" | "success";
  value: string;
};

type TeamNameProps = {
  align?: "left" | "right";
  className?: string;
  label: string | null | undefined;
  markerPosition?: "before" | "after";
  size?: "small" | "medium";
  sublabel?: ReactNode;
};

type MatchFixtureLineProps = {
  className?: string;
  homeTeam: string | null | undefined;
  awayTeam: string | null | undefined;
  homeScore: number | null;
  awayScore: number | null;
  markerSize?: "small" | "medium";
  scoreClassName?: string;
};

export function StatusPill({ tone = "default", value }: StatusPillProps) {
  return <span className={`status-pill ${tone}`}>{value}</span>;
}

export function getMatchStatusTone(match: Pick<MatchSummary, "is_forfeit" | "is_source_anomaly" | "result">) {
  if (match.is_source_anomaly) return "warning" as const;
  if (match.is_forfeit) return "warning" as const;
  if (match.result) return "success" as const;
  return "muted" as const;
}

export function MatchStatusPill({ match }: { match: Pick<MatchSummary, "is_forfeit" | "is_source_anomaly" | "result"> }) {
  const label = match.is_source_anomaly ? "Source issue" : matchStatus(match as MatchSummary);
  return <StatusPill tone={getMatchStatusTone(match)} value={label} />;
}

export function TeamName({
  align = "left",
  className,
  label,
  markerPosition = "before",
  size = "small",
  sublabel,
}: TeamNameProps) {
  const safeLabel = label ?? "Team TBC";
  const classes = ["editorial-team", align === "right" ? "is-right" : "", className].filter(Boolean).join(" ");
  const marker = <TeamMarker label={safeLabel} size={size} />;

  return (
    <span className={classes}>
      {markerPosition === "before" ? marker : null}
      <span className="editorial-team-copy">
        <strong>{safeLabel}</strong>
        {sublabel ? <small>{sublabel}</small> : null}
      </span>
      {markerPosition === "after" ? marker : null}
    </span>
  );
}

export function MatchFixtureLine({
  className,
  homeTeam,
  awayTeam,
  homeScore,
  awayScore,
  markerSize = "small",
  scoreClassName,
}: MatchFixtureLineProps) {
  const classes = ["editorial-fixture-line", className].filter(Boolean).join(" ");
  const scoreClasses = ["editorial-scoreline", scoreClassName].filter(Boolean).join(" ");

  return (
    <div className={classes}>
      <TeamName label={homeTeam} size={markerSize} />
      <strong className={scoreClasses}>{formatScoreline(homeScore, awayScore)}</strong>
      <TeamName align="right" label={awayTeam} markerPosition="after" size={markerSize} />
    </div>
  );
}

export function StatCell({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="editorial-stat-cell">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}

export function StatComparisonRow({
  awayValue,
  homeValue,
  label,
}: {
  awayValue: ReactNode;
  homeValue: ReactNode;
  label: string;
}) {
  return (
    <div className="match-stat-row editorial-table-row">
      <strong>{homeValue}</strong>
      <span>{label}</span>
      <strong>{awayValue}</strong>
    </div>
  );
}
