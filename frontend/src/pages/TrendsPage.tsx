import { useCallback, useEffect, useMemo, useState } from "react";

import { apiClient } from "../api/client";
import type {
  DataQualityStatus,
  SeasonTrendRow,
  SeasonTrendsResponse,
} from "../api/types";
import type { PageProps } from "../app/types";
import { DisclosureSection } from "../components/common/DisclosureSection";
import { PageIntro } from "../components/common/PageIntro";
import { ShowMoreList } from "../components/common/ShowMoreList";
import {
  DataQualityNote,
  type DataQualityTone,
} from "../components/intelligence/DataQualityNote";
import { InsightEmptyState } from "../components/intelligence/InsightEmptyState";
import { MiniBarChart } from "../components/intelligence/MiniBarChart";
import {
  SignalChip,
  type SignalTone,
} from "../components/intelligence/SignalChip";
import { StackedShareBar } from "../components/intelligence/ComparisonBars";
import {
  SeasonCoverageRows,
  TrendPanelTakeaway,
  TrendsLead,
  deriveTrendsNarrative,
  type TrendsNarrative,
} from "../components/trends/TrendsNarrative";
import { formatDate, formatPercent, formatSeason } from "../utils/format";

type TrendLoadState = "loading" | "success" | "error";

const statusPriority: Record<DataQualityStatus, number> = {
  good: 0,
  caution: 1,
  limited: 2,
};

function sortSeasonsAscending(rows: SeasonTrendRow[]) {
  return rows.toSorted((left, right) =>
    left.season.localeCompare(right.season),
  );
}

function formatNumber(value: number | null | undefined) {
  if (value === null || value === undefined) return "Unavailable";
  return value.toLocaleString();
}

function formatRate(value: number | null | undefined) {
  if (value === null || value === undefined) return "Unavailable";
  return value.toFixed(2);
}

function formatShare(value: number | null | undefined) {
  if (value === null || value === undefined) return "Unavailable";
  return formatPercent(value);
}

function formatStatus(status: DataQualityStatus) {
  if (status === "good") return "Good";
  if (status === "caution") return "Caution";
  return "Limited";
}

function signalToneForStatus(status: DataQualityStatus): SignalTone {
  if (status === "good") return "positive";
  if (status === "caution") return "warning";
  return "muted";
}

function qualityToneForStatus(
  status: DataQualityStatus,
): DataQualityTone {
  if (status === "good") return "good";
  if (status === "caution") return "caution";
  return "limited";
}

function getOverallStatus(rows: SeasonTrendRow[]): DataQualityStatus {
  return rows.reduce<DataQualityStatus>((current, row) => {
    return statusPriority[row.data_quality_status] >
      statusPriority[current]
      ? row.data_quality_status
      : current;
  }, "good");
}

function getSeasonRange(
  summary: SeasonTrendsResponse["summary"],
  rows: SeasonTrendRow[],
) {
  const earliest = summary.earliest_season ?? rows[0]?.season ?? null;
  const latest = summary.latest_season ?? rows.at(-1)?.season ?? null;

  if (!earliest || !latest) return "Across available seasons";
  if (earliest === latest) return formatSeason(earliest);

  return `${formatSeason(earliest)} to ${formatSeason(latest)}`;
}

function TrendsLoadingState() {
  return (
    <div
      className="trends-page"
      aria-busy="true"
      aria-label="Loading season trends"
    >
      <section className="page-intro skeleton-panel">
        <span className="skeleton-line short" />
        <span className="skeleton-line title" />
        <span className="skeleton-line medium" />
      </section>
      <section className="trends-lead skeleton-panel">
        <span className="skeleton-line title" />
        <span className="skeleton-line medium" />
        <div className="trends-lead-metrics">
          {Array.from({ length: 3 }, (_, index) => (
            <article className="metric-delta skeleton-card" key={index}>
              <span className="skeleton-line short" />
              <span className="skeleton-line number" />
              <span className="skeleton-line medium" />
            </article>
          ))}
        </div>
      </section>
      <section className="trends-chart-grid">
        {Array.from({ length: 4 }, (_, index) => (
          <article
            className="panel trends-chart-panel skeleton-panel"
            key={index}
          >
            <span className="skeleton-line medium" />
            <span className="skeleton-line" />
            <span className="trends-chart-skeleton" />
          </article>
        ))}
      </section>
    </div>
  );
}

function TrendsChartGrid({
  cardsData,
  chartRows,
  goalsData,
  highScoringData,
  narrative,
}: {
  cardsData: Array<{
    key: string;
    label: string;
    value: number;
    secondaryValue: number;
    tone: "gold" | "muted";
  }>;
  chartRows: SeasonTrendRow[];
  goalsData: Array<{
    key: string;
    label: string;
    value: number;
    secondaryValue: number;
    tone: "green" | "muted";
  }>;
  highScoringData: Array<{
    key: string;
    label: string;
    value: number;
    secondaryValue: number;
    tone: "gold";
  }>;
  narrative: TrendsNarrative;
}) {
  return (
    <section
      className="trends-chart-grid"
      aria-label="League trend charts"
    >
      <article className="panel trends-chart-panel">
        <MiniBarChart
          data={highScoringData}
          description="Share of recorded matches with at least three scoreline goals."
          emptyLabel="High-scoring match share is not available yet."
          height="regular"
          title="High-scoring match share"
          valueFormatter={(value) => formatPercent(value)}
        />
        <TrendPanelTakeaway text={narrative.highScoring} />
      </article>

      <article className="panel trends-chart-panel">
        <MiniBarChart
          data={goalsData}
          description="Timeline-recorded goals per match. Muted bars mark seasons with limited timeline evidence."
          emptyLabel="Timeline scoring-rate data is not available yet."
          height="regular"
          title="Scoring over time"
          valueFormatter={(value) => value.toFixed(2)}
        />
        <TrendPanelTakeaway text={narrative.scoring} />
      </article>

      <article className="panel trends-chart-panel trends-chart-panel-result">
        <div className="section-heading compact">
          <div>
            <h2>Result balance</h2>
            <p>
              Home wins, draws, and away wins across available match
              scorelines.
            </p>
          </div>
        </div>
        <ShowMoreList
          className="trends-stacked-list"
          getKey={(row) => row.season}
          initialCount={4}
          itemNoun="season"
          items={chartRows}
          renderItem={(row) => (
            <StackedShareBar
              label={formatSeason(row.season)}
              segments={[
                {
                  label: "Home wins",
                  value: row.home_wins,
                  tone: "green",
                },
                { label: "Draws", value: row.draws, tone: "muted" },
                {
                  label: "Away wins",
                  value: row.away_wins,
                  tone: "gold",
                },
              ]}
              valueFormatter={(value, share) =>
                `${value.toLocaleString()} (${formatPercent(share)})`
              }
            />
          )}
        />
        <TrendPanelTakeaway text={narrative.resultBalance} />
      </article>

      <article className="panel trends-chart-panel">
        <MiniBarChart
          data={cardsData}
          description="Timeline-recorded cards per match. Muted bars mark seasons with limited timeline evidence."
          emptyLabel="Card-rate trend data is not available yet."
          height="regular"
          title="Discipline over time"
          valueFormatter={(value) => value.toFixed(2)}
        />
        <TrendPanelTakeaway text={narrative.cards} />
      </article>
    </section>
  );
}

function TrendsCoveragePanel({
  coverageTotals,
  overallStatus,
  rows,
  timelineGoalGap,
}: {
  coverageTotals: {
    administrativeResults: number;
    complete: number;
    partial: number;
    sourceAnomalies: number;
    withoutCoverage: number;
  };
  overallStatus: DataQualityStatus;
  rows: SeasonTrendRow[];
  timelineGoalGap: number;
}) {
  return (
    <section className="panel trends-coverage-panel">
      <div className="section-heading compact">
        <div>
          <h2>Timeline coverage by season</h2>
          <p>
            Compare which seasons support event-led scoring and discipline
            interpretation.
          </p>
        </div>
        <SignalChip
          label={formatStatus(overallStatus)}
          size="small"
          tone={signalToneForStatus(overallStatus)}
        />
      </div>

      <div className="trends-coverage-grid">
        <SeasonCoverageRows rows={rows} />
        <DataQualityNote
          title="Trend reading note"
          tone={qualityToneForStatus(overallStatus)}
          note={
            timelineGoalGap > 0
              ? `Scoreline goals and timeline goals differ by ${timelineGoalGap.toLocaleString()} across the available seasons, so event-led comparisons should be read with coverage in mind.`
              : "Scoreline results support the cleanest comparison. Timeline-dependent scoring and discipline readings still depend on the coverage shown for each season."
          }
          metrics={[
            {
              label: "Complete timelines",
              value: coverageTotals.complete.toLocaleString(),
            },
            {
              label: "Partial timelines",
              value: coverageTotals.partial.toLocaleString(),
            },
            {
              label: "Without timeline coverage",
              value: coverageTotals.withoutCoverage.toLocaleString(),
            },
            {
              label: "Source anomalies",
              value: coverageTotals.sourceAnomalies.toLocaleString(),
            },
            {
              label: "Admin results",
              value: coverageTotals.administrativeResults.toLocaleString(),
            },
          ]}
        />
      </div>
    </section>
  );
}

function TrendsSeasonTable({
  tableRows,
}: {
  tableRows: SeasonTrendRow[];
}) {
  return (
    <DisclosureSection
      className="panel trends-table-panel"
      description="Open the reference table when you need the exact trend rows behind the charts."
      eyebrow="Reference"
      title="Season comparison"
    >
      <div className="trends-season-table">
        <table>
          <thead>
            <tr>
              <th scope="col">Season</th>
              <th scope="col">Matches</th>
              <th scope="col">Teams</th>
              <th scope="col">Timeline goals/match</th>
              <th scope="col">Cards/match</th>
              <th scope="col">Home / Draw / Away</th>
              <th scope="col">High-scoring</th>
              <th scope="col">Timeline coverage</th>
              <th scope="col">Data status</th>
            </tr>
          </thead>
          <tbody>
            {tableRows.map((row) => {
              const covered =
                row.timeline_complete_match_count +
                row.timeline_partial_match_count;

              return (
                <tr key={row.season}>
                  <td data-label="Season">
                    <strong>{formatSeason(row.season)}</strong>
                    <span>
                      {formatDate(row.first_match_date)} to{" "}
                      {formatDate(row.last_match_date)}
                    </span>
                  </td>
                  <td data-label="Matches">{formatNumber(row.match_count)}</td>
                  <td data-label="Teams">{formatNumber(row.team_count)}</td>
                  <td data-label="Timeline goals/match">
                    {formatRate(row.goals_per_match)}
                  </td>
                  <td data-label="Cards/match">
                    {formatRate(row.cards_per_match)}
                  </td>
                  <td data-label="Home / Draw / Away">
                    {row.home_wins.toLocaleString()} /{" "}
                    {row.draws.toLocaleString()} /{" "}
                    {row.away_wins.toLocaleString()}
                  </td>
                  <td data-label="High-scoring">
                    {formatShare(row.high_scoring_match_share)}
                  </td>
                  <td data-label="Timeline coverage">
                    <div className="trends-table-coverage-cell">
                      <strong>{formatShare(row.timeline_coverage_share)}</strong>
                      <span>
                        {covered.toLocaleString()} of{" "}
                        {row.match_count.toLocaleString()} matches
                        {row.timeline_partial_match_count > 0
                          ? `; ${row.timeline_partial_match_count.toLocaleString()} partial`
                          : ""}
                      </span>
                    </div>
                  </td>
                  <td data-label="Data status">
                    <SignalChip
                      label={formatStatus(row.data_quality_status)}
                      size="small"
                      tone={signalToneForStatus(row.data_quality_status)}
                    />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </DisclosureSection>
  );
}

export function TrendsPage({
  onRefresh,
  selectedSeason,
}: PageProps) {
  const [trendData, setTrendData] =
    useState<SeasonTrendsResponse | null>(null);
  const [loadState, setLoadState] =
    useState<TrendLoadState>("loading");
  const [errorMessage, setErrorMessage] = useState(
    "Could not load season trends.",
  );

  const loadTrends = useCallback(async () => {
    setLoadState("loading");
    try {
      const response = await apiClient.getSeasonTrends();
      setTrendData(response);
      setLoadState("success");
    } catch (error) {
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Could not load season trends.",
      );
      setTrendData(null);
      setLoadState("error");
    }
  }, []);

  useEffect(() => {
    void loadTrends();
  }, [loadTrends]);

  const rows = useMemo(
    () => sortSeasonsAscending(trendData?.seasons ?? []),
    [trendData],
  );
  const summary = trendData?.summary;
  const tableRows = useMemo(() => rows.toReversed(), [rows]);
  const narrative = useMemo(() => deriveTrendsNarrative(rows), [rows]);

  const goalsData = rows
    .filter((row) => row.goals_per_match !== null)
    .map((row) => ({
      key: row.season,
      label: formatSeason(row.season),
      value: row.goals_per_match ?? 0,
      secondaryValue: row.timeline_goal_count,
      tone:
        row.data_quality_status === "limited"
          ? ("muted" as const)
          : ("green" as const),
    }));

  const cardsData = rows
    .filter((row) => row.cards_per_match !== null)
    .map((row) => ({
      key: row.season,
      label: formatSeason(row.season),
      value: row.cards_per_match ?? 0,
      secondaryValue: row.total_card_count,
      tone:
        row.data_quality_status === "limited"
          ? ("muted" as const)
          : ("gold" as const),
    }));

  const highScoringData = rows
    .filter((row) => row.high_scoring_match_share !== null)
    .map((row) => ({
      key: row.season,
      label: formatSeason(row.season),
      value: row.high_scoring_match_share ?? 0,
      secondaryValue: row.high_scoring_match_count,
      tone: "gold" as const,
    }));

  const coverageTotals = rows.reduce(
    (totals, row) => ({
      complete: totals.complete + row.timeline_complete_match_count,
      partial: totals.partial + row.timeline_partial_match_count,
      withoutCoverage:
        totals.withoutCoverage +
        Math.max(
          row.match_count -
            row.timeline_complete_match_count -
            row.timeline_partial_match_count,
          0,
        ),
      sourceAnomalies:
        totals.sourceAnomalies + row.source_anomaly_count,
      administrativeResults:
        totals.administrativeResults + row.administrative_result_count,
    }),
    {
      complete: 0,
      partial: 0,
      withoutCoverage: 0,
      sourceAnomalies: 0,
      administrativeResults: 0,
    },
  );
  const coverageTotal =
    coverageTotals.complete +
    coverageTotals.partial +
    coverageTotals.withoutCoverage;
  const coverageShare =
    coverageTotal > 0
      ? (coverageTotals.complete + coverageTotals.partial) / coverageTotal
      : null;
  const overallStatus =
    rows.length > 0 ? getOverallStatus(rows) : "limited";
  const seasonRange = summary
    ? getSeasonRange(summary, rows)
    : "Across available seasons";
  const timelineGoalGap =
    summary &&
    summary.total_scoreline_goals !== summary.total_timeline_goals
      ? Math.abs(
          summary.total_scoreline_goals - summary.total_timeline_goals,
        )
      : 0;

  const handleRetry = () => {
    onRefresh();
    void loadTrends();
  };

  if (loadState === "loading") {
    return <TrendsLoadingState />;
  }

  if (loadState === "error") {
    return (
      <section className="error-panel trends-error-panel" role="alert">
        <h2>Could not load season trends.</h2>
        <p>{errorMessage}</p>
        <button
          className="text-button"
          type="button"
          onClick={handleRetry}
        >
          Retry trends
        </button>
      </section>
    );
  }

  if (!trendData || rows.length === 0 || !summary) {
    return (
      <InsightEmptyState
        title="Historical trend data is not available yet."
        message="UPL Lens will show season comparisons here once trend rows are returned by the data service."
      />
    );
  }

  return (
    <div className="trends-page">
      <PageIntro
        variant="dense"
        eyebrow="League evolution"
        title="Trends"
        text="Compare how scoring, high-scoring matches, result balance, discipline, and evidence coverage changed across the available league record."
      />

      <TrendsLead
        coverageShare={coverageShare}
        narrative={narrative}
        rows={rows}
        seasonRange={seasonRange}
        selectedSeason={selectedSeason}
        summary={summary}
      />
      <TrendsChartGrid
        cardsData={cardsData}
        chartRows={rows}
        goalsData={goalsData}
        highScoringData={highScoringData}
        narrative={narrative}
      />
      <TrendsCoveragePanel
        coverageTotals={coverageTotals}
        overallStatus={overallStatus}
        rows={rows}
        timelineGoalGap={timelineGoalGap}
      />
      <TrendsSeasonTable tableRows={tableRows} />
    </div>
  );
}
