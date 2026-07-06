import { Info } from "lucide-react";

import type {
  DataQualityStatus,
  SeasonTrendRow,
  SeasonTrendsResponse,
} from "../../api/types";
import { formatPercent, formatSeason } from "../../utils/format";
import { isAllSeasonsSelection } from "../../utils/seasonScope";
import { MetricDelta } from "../intelligence/MetricDelta";
import { SignalChip, type SignalTone } from "../intelligence/SignalChip";
import { StackedShareBar } from "../intelligence/ComparisonBars";
import "./trends-narrative.css";

type NumericTrendKey =
  | "cards_per_match"
  | "goals_per_match"
  | "high_scoring_match_share";

export type TrendsNarrative = {
  cards: string;
  highScoring: string;
  leadEvidence: string;
  leadHeadline: string;
  resultBalance: string;
  scoring: string;
};

function scorelineRate(row: SeasonTrendRow) {
  return row.match_count > 0
    ? row.scoreline_goal_count / row.match_count
    : null;
}

function comparableRows(
  rows: SeasonTrendRow[],
  key: NumericTrendKey,
  excludeLimited = false,
) {
  return rows.filter((row) => {
    const value = row[key];
    return (
      value !== null &&
      Number.isFinite(value) &&
      (!excludeLimited || row.data_quality_status !== "limited")
    );
  });
}

function describeRateExtremes(
  rows: SeasonTrendRow[],
  key: "cards_per_match" | "goals_per_match",
  noun: string,
) {
  const usable = comparableRows(rows, key, true);
  if (usable.length === 0) {
    return `Timeline coverage is too limited to rank ${noun} across seasons.`;
  }

  if (usable.length === 1) {
    const row = usable[0];
    return `${formatSeason(row.season)} records ${row[key]?.toFixed(2)} ${noun}; seasons marked limited are not ranked against it.`;
  }

  const highest = usable.reduce((current, row) =>
    (row[key] ?? 0) > (current[key] ?? 0) ? row : current,
  );
  const lowest = usable.reduce((current, row) =>
    (row[key] ?? 0) < (current[key] ?? 0) ? row : current,
  );
  const highValue = highest[key] ?? 0;
  const lowValue = lowest[key] ?? 0;

  if (Math.abs(highValue - lowValue) < 0.005) {
    return `Comparable seasons hold near ${highValue.toFixed(2)} ${noun}.`;
  }

  return `${formatSeason(highest.season)} has the highest comparable rate at ${highValue.toFixed(2)} ${noun}, versus ${lowValue.toFixed(2)} in ${formatSeason(lowest.season)}.`;
}

function describeHighScoring(rows: SeasonTrendRow[]) {
  const usable = comparableRows(rows, "high_scoring_match_share");
  if (usable.length === 0) {
    return "Three-plus-goal match shares are unavailable for comparison.";
  }

  if (usable.length === 1) {
    return `${formatSeason(usable[0].season)} records ${formatPercent(usable[0].high_scoring_match_share ?? 0)} of matches with at least three goals.`;
  }

  const highest = usable.reduce((current, row) =>
    (row.high_scoring_match_share ?? 0) >
    (current.high_scoring_match_share ?? 0)
      ? row
      : current,
  );
  const lowest = usable.reduce((current, row) =>
    (row.high_scoring_match_share ?? 0) <
    (current.high_scoring_match_share ?? 0)
      ? row
      : current,
  );

  return `Three-plus-goal matches were most common in ${formatSeason(highest.season)} at ${formatPercent(highest.high_scoring_match_share ?? 0)}, compared with ${formatPercent(lowest.high_scoring_match_share ?? 0)} in ${formatSeason(lowest.season)}.`;
}

function dominantResult(row: SeasonTrendRow) {
  const outcomes = [
    { key: "home", label: "Home wins", share: row.home_win_share ?? 0 },
    { key: "draw", label: "Draws", share: row.draw_share ?? 0 },
    { key: "away", label: "Away wins", share: row.away_win_share ?? 0 },
  ];
  const peak = Math.max(...outcomes.map((outcome) => outcome.share));
  const leaders = outcomes.filter(
    (outcome) => Math.abs(outcome.share - peak) < 0.0005,
  );
  return leaders.length === 1 ? leaders[0] : null;
}

function describeResultBalance(rows: SeasonTrendRow[]) {
  if (rows.length === 0) return "Result balance is unavailable.";

  const leaders = rows
    .map((row) => ({ row, result: dominantResult(row) }))
    .filter(
      (
        item,
      ): item is {
        row: SeasonTrendRow;
        result: NonNullable<ReturnType<typeof dominantResult>>;
      } => item.result !== null,
    );

  if (leaders.length === 0) {
    return "No single result type leads the available season rows.";
  }

  const counts = leaders.reduce<Record<string, number>>((current, item) => {
    current[item.result.key] = (current[item.result.key] ?? 0) + 1;
    return current;
  }, {});
  const dominantKey = Object.entries(counts).reduce((current, entry) =>
    entry[1] > current[1] ? entry : current,
  )[0];
  const dominantRows = leaders.filter(
    (item) => item.result.key === dominantKey,
  );
  const peak = dominantRows.reduce((current, item) =>
    item.result.share > current.result.share ? item : current,
  );

  return `${peak.result.label} led in ${dominantRows.length} of ${rows.length} seasons, peaking at ${formatPercent(peak.result.share)} in ${formatSeason(peak.row.season)}.`;
}

export function deriveTrendsNarrative(
  rows: SeasonTrendRow[],
): TrendsNarrative {
  const scorelineRows = rows.filter((row) => scorelineRate(row) !== null);
  const earliest = scorelineRows[0];
  const latest = scorelineRows.at(-1);
  let leadHeadline = describeHighScoring(rows);
  let leadEvidence =
    "This comparison uses available scorelines and keeps timeline-dependent readings caveated.";

  if (earliest && latest && earliest !== latest) {
    const earliestRate = scorelineRate(earliest) ?? 0;
    const latestRate = scorelineRate(latest) ?? 0;
    const difference = latestRate - earliestRate;
    const direction =
      Math.abs(difference) < 0.005
        ? "held steady"
        : difference > 0
          ? "rose"
          : "fell";
    leadHeadline =
      direction === "held steady"
        ? `Available scorelines show scoring held near ${latestRate.toFixed(2)} goals per match.`
        : `Available scorelines show scoring ${direction} by ${Math.abs(difference).toFixed(2)} goals per match.`;
    leadEvidence = `${formatSeason(earliest.season)} averaged ${earliestRate.toFixed(2)} scoreline goals per match; ${formatSeason(latest.season)} averages ${latestRate.toFixed(2)}.`;
  } else if (latest) {
    const latestRate = scorelineRate(latest) ?? 0;
    leadHeadline = `${formatSeason(latest.season)} averages ${latestRate.toFixed(2)} scoreline goals per match in available records.`;
    leadEvidence =
      "One usable season supports a snapshot, not a claim about league evolution.";
  }

  return {
    cards: describeRateExtremes(rows, "cards_per_match", "cards per match"),
    highScoring: describeHighScoring(rows),
    leadEvidence,
    leadHeadline,
    resultBalance: describeResultBalance(rows),
    scoring: describeRateExtremes(
      rows,
      "goals_per_match",
      "timeline goals per match",
    ),
  };
}

function formatScopeSelection(selectedSeason: string) {
  if (!selectedSeason || isAllSeasonsSelection(selectedSeason)) {
    return "The global season selector applies to season-specific routes and does not filter these charts.";
  }

  return `${formatSeason(selectedSeason)} remains selected for other routes; Trends still compares every available season.`;
}

export function TrendsLead({
  coverageShare,
  narrative,
  rows,
  seasonRange,
  selectedSeason,
  summary,
}: {
  coverageShare: number | null;
  narrative: TrendsNarrative;
  rows: SeasonTrendRow[];
  seasonRange: string;
  selectedSeason: string;
  summary: SeasonTrendsResponse["summary"];
}) {
  const latest = rows.at(-1);
  const latestScorelineRate = latest ? scorelineRate(latest) : null;
  const latestDominantResult = latest ? dominantResult(latest) : null;

  return (
    <section className="trends-lead" aria-labelledby="trends-lead-title">
      <div className="trends-lead-copy">
        <h2 id="trends-lead-title">{narrative.leadHeadline}</h2>
        <p>{narrative.leadEvidence}</p>
      </div>
      <div className="trends-lead-metrics" aria-label="Latest football signals">
        <MetricDelta
          context={
            latest
              ? `${formatSeason(latest.season)} from recorded scorelines.`
              : "Latest season unavailable."
          }
          label="Scoreline goals/match"
          tone="positive"
          value={
            latestScorelineRate === null
              ? "Unavailable"
              : latestScorelineRate.toFixed(2)
          }
        />
        <MetricDelta
          context="Matches with at least three goals."
          label="High-scoring share"
          tone="positive"
          value={
            latest?.high_scoring_match_share == null
              ? "Unavailable"
              : formatPercent(latest.high_scoring_match_share)
          }
        />
        <MetricDelta
          context={
            latest ? `${formatSeason(latest.season)} result balance.` : undefined
          }
          label="Most common result"
          tone="neutral"
          value={latestDominantResult?.label ?? "No clear leader"}
        />
      </div>
      <div className="trends-scope-note">
        <Info aria-hidden="true" size={18} />
        <div>
          <strong>All-seasons comparison</strong>
          <p>{formatScopeSelection(selectedSeason)}</p>
          <small>
            {seasonRange}: {summary.total_matches.toLocaleString()} recorded
            matches. Timeline present for {coverageShare === null
              ? "an unavailable share"
              : formatPercent(coverageShare)}
            .
          </small>
        </div>
      </div>
    </section>
  );
}

export function TrendPanelTakeaway({ text }: { text: string }) {
  return (
    <p className="trends-panel-takeaway">
      <strong>What the data shows</strong>
      <span>{text}</span>
    </p>
  );
}

function signalToneForStatus(status: DataQualityStatus): SignalTone {
  if (status === "good") return "positive";
  if (status === "caution") return "warning";
  return "muted";
}

export function SeasonCoverageRows({ rows }: { rows: SeasonTrendRow[] }) {
  return (
    <div
      className="trends-season-coverage-list"
      aria-label="Timeline coverage by season"
    >
      {rows.map((row) => {
        const covered =
          row.timeline_complete_match_count +
          row.timeline_partial_match_count;
        const notCovered = Math.max(row.match_count - covered, 0);

        return (
          <article className="trends-season-coverage-row" key={row.season}>
            <div className="trends-season-coverage-heading">
              <strong>{formatSeason(row.season)}</strong>
              <div>
                <span>
                  {row.timeline_coverage_share === null
                    ? "Unavailable"
                    : formatPercent(row.timeline_coverage_share)}
                </span>
                <SignalChip
                  label={
                    row.data_quality_status === "good"
                      ? "Good"
                      : row.data_quality_status === "caution"
                        ? "Caution"
                        : "Limited"
                  }
                  size="small"
                  tone={signalToneForStatus(row.data_quality_status)}
                />
              </div>
            </div>
            <StackedShareBar
              segments={[
                { label: "Timeline present", tone: "green", value: covered },
                { label: "Not present", tone: "muted", value: notCovered },
              ]}
              showLegend={false}
            />
            <p className="trends-season-coverage-meta">
              {row.timeline_complete_match_count.toLocaleString()} complete,{" "}
              {row.timeline_partial_match_count.toLocaleString()} partial,{" "}
              {notCovered.toLocaleString()} without timeline coverage
            </p>
            {row.data_quality_note ? (
              <p className="trends-season-coverage-note">
                {row.data_quality_note}
              </p>
            ) : null}
          </article>
        );
      })}
    </div>
  );
}
