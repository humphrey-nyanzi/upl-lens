import {
  CalendarDays,
  CheckCircle2,
  CircleHelp,
  Database,
  RefreshCw,
  Target,
  TriangleAlert,
  Workflow,
} from "lucide-react";

import type { HealthResponse } from "../api/types";
import type { PageProps } from "../app/types";
import {
  MethodologyBoundary,
  MethodologyCollection,
  MethodologyContact,
  MethodologyHero,
  MethodologyInterpretation,
  MethodologyTrust,
  type MethodologyFreshnessRow,
  type MethodologyServiceStatus,
} from "../components/methodology/MethodologySections";
import { formatDate } from "../utils/format";
import {
  getSelectedSeasonLabel,
  isAllSeasonsSelection,
} from "../utils/seasonScope";

function formatHealthStatus(
  value: string | undefined | null,
  fallback: string,
) {
  if (!value) return fallback;
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function getServiceStatus(
  apiOnline: boolean,
  health: HealthResponse | null,
): MethodologyServiceStatus {
  if (!health) {
    return {
      detail: "No current health response is available.",
      icon: <CircleHelp size={22} />,
      label: "Status unavailable",
      meta: "Unknown",
    };
  }

  if (apiOnline) {
    return {
      detail: "The API and database currently report OK.",
      icon: <CheckCircle2 size={22} />,
      label: "Service available",
      meta: "Current check: OK",
    };
  }

  return {
    detail: `API: ${formatHealthStatus(health.api, "Unknown")}. Database: ${formatHealthStatus(health.database, "Unknown")}.`,
    icon: <TriangleAlert size={22} />,
    label: "Service check needed",
    meta: "Current check: attention",
  };
}

export function MethodologyPage({
  apiOnline,
  data,
  overview,
  selectedSeason,
  selectedSeasonInfo,
}: PageProps) {
  const seasonLabel = getSelectedSeasonLabel(
    selectedSeason,
    selectedSeasonInfo,
  );
  const health = data.health;
  const matchCount =
    overview?.match_count ??
    selectedSeasonInfo?.match_count ??
    data.matches.length;
  const completedMatches = data.matches.filter(
    (match) => match.home_score !== null && match.away_score !== null,
  ).length;
  const scoringCoverageShare =
    overview && overview.scoreline_goal_count > 0
      ? Math.min(
          overview.timeline_goal_count / overview.scoreline_goal_count,
          1,
        )
      : null;
  const sourceWindow = selectedSeasonInfo
    ? `${formatDate(overview?.first_match_date ?? selectedSeasonInfo.first_match_date)} - ${formatDate(overview?.latest_match_date ?? selectedSeasonInfo.last_match_date)}`
    : "Available match window";
  const freshnessRows: MethodologyFreshnessRow[] = [
    {
      icon: <RefreshCw size={16} />,
      label: "Latest staging refresh",
      value: health?.latest_staging_completed_at
        ? formatDate(health.latest_staging_completed_at)
        : "Unknown",
    },
    {
      icon: <CalendarDays size={16} />,
      label: "Season window",
      value: sourceWindow,
    },
    {
      icon: <Target size={16} />,
      label: "Selected scope",
      value: isAllSeasonsSelection(selectedSeason)
        ? `${seasonLabel} archive`
        : `${seasonLabel} season`,
    },
    {
      icon: <Database size={16} />,
      label: "Matches covered",
      value: `${completedMatches} of ${matchCount}`,
      status:
        matchCount > 0 && completedMatches === matchCount
          ? "All loaded"
          : undefined,
    },
    {
      icon: <Workflow size={16} />,
      label: "Scoring coverage",
      value:
        overview && overview.scoreline_goal_count > 0
          ? `${overview.timeline_goal_count} of ${overview.scoreline_goal_count}`
          : "Unavailable",
      status:
        scoringCoverageShare !== null && scoringCoverageShare >= 0.9
          ? "90%+"
          : undefined,
    },
  ];

  return (
    <article className="methodology-page">
      <MethodologyHero />
      <MethodologyBoundary />
      <MethodologyCollection freshnessRows={freshnessRows} />
      <MethodologyInterpretation />
      <MethodologyTrust
        serviceStatus={getServiceStatus(apiOnline, health)}
      />
      <MethodologyContact />
    </article>
  );
}
