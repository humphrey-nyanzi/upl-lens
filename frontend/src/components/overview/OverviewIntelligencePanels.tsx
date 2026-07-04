import { Link } from "react-router-dom";

import type {
  MatchIntelligenceSummary,
  OverviewDataQuality,
  OverviewNotice,
  TeamSignalSummary,
} from "../../api/types";
import { formatDate, formatPercent, formatScoreline } from "../../utils/format";
import { EmptyState } from "../common/EmptyState";
import { ReportSectionHeader } from "../common/ReportSectionHeader";
import { TeamMarker } from "../common/TeamMarker";
import {
  DataQualityNote,
  type DataQualityTone,
} from "../intelligence/DataQualityNote";
import {
  SignalChipGroup,
  type SignalChipItem,
} from "../intelligence/SignalChip";
import "./overview-intelligence.css";

export type OverviewModuleState = "loading" | "success" | "partial" | "error";

function moduleMessage(
  state: OverviewModuleState,
  loadingMessage: string,
  emptyMessage: string,
  errorMessage: string,
) {
  if (state === "loading") return loadingMessage;
  if (state === "error") return errorMessage;
  return emptyMessage;
}

function qualityTone(status: OverviewDataQuality["status"] | undefined): DataQualityTone {
  if (status === "good") return "good";
  if (status === "caution") return "caution";
  if (status === "limited") return "limited";
  return "neutral";
}

function signalItems(
  signals: Array<{ key?: string; label: string; tone?: SignalChipItem["tone"] }>,
): SignalChipItem[] {
  return signals.map((signal, index) => ({
    key: signal.key ?? `${signal.label}-${index}`,
    label: signal.label,
    tone: signal.tone,
  }));
}

function overviewLink(path: string | null) {
  if (path === "/methodology") return "/about";
  return path;
}

function formatMetricValue(value: number | null) {
  if (value === null) return "Unavailable";
  return Number.isInteger(value)
    ? value.toLocaleString()
    : value.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

function timelineLabel(status: string | null) {
  if (status === "complete") return "Complete timeline";
  if (status === "partial") return "Partial timeline";
  if (status === "unavailable") return "Timeline unavailable";
  if (status === "administrative_result") return "Administrative result";
  return "Timeline status unavailable";
}

function matchQualityTone(match: MatchIntelligenceSummary): DataQualityTone {
  if (match.is_source_anomaly || match.is_administrative_result) return "risk";
  if (match.timeline_status === "complete") return "good";
  if (match.timeline_status === "partial") return "caution";
  if (match.timeline_status === "unavailable") return "limited";
  return "neutral";
}

export function OverviewNoticePanel({
  notices,
  state,
}: {
  notices: OverviewNotice[];
  state: OverviewModuleState;
}) {
  return (
    <section className="panel overview-notice-panel">
      <ReportSectionHeader
        title="Things to notice"
        text="A short readout of the football patterns and evidence limits returned for this season."
      />
      <div className="overview-notice-list">
        {notices.length > 0 ? (
          notices.map((notice) => {
            const content = (
              <>
                <SignalChipGroup
                  items={signalItems([{ key: notice.key, label: notice.title, tone: notice.tone }])}
                  size="small"
                />
                <p>{notice.text}</p>
              </>
            );
            const linkPath = overviewLink(notice.link_path);

            return linkPath ? (
              <Link className="overview-notice-card" key={notice.key} to={linkPath}>
                {content}
              </Link>
            ) : (
              <article className="overview-notice-card" key={notice.key}>
                {content}
              </article>
            );
          })
        ) : (
          <EmptyState
            message={moduleMessage(
              state,
              "Loading season signals.",
              "No standout overview signals were returned for this season.",
              "Season signals are unavailable because the Overview intelligence request did not complete.",
            )}
          />
        )}
      </div>
    </section>
  );
}

function SignalMatchCard({ match }: { match: MatchIntelligenceSummary }) {
  const homeTeam = match.home_team ?? "Home team TBC";
  const awayTeam = match.away_team ?? "Away team TBC";
  const primarySignal = match.primary_signal ?? match.signal_labels[0]?.label ?? "No primary signal returned";

  return (
    <article className="overview-signal-match">
      <div className="overview-signal-match-heading">
        <span>{formatDate(match.match_date)}</span>
        <strong>{primarySignal}</strong>
      </div>
      <p className="overview-signal-scoreline">
        {homeTeam} <strong>{formatScoreline(match.home_score, match.away_score)}</strong> {awayTeam}
      </p>
      <SignalChipGroup
        emptyLabel="No additional signal labels"
        items={signalItems(match.signal_labels)}
        maxVisible={3}
        size="small"
      />
      <DataQualityNote
        compact
        metrics={[
          { label: "Interest", value: match.interest_score },
          { label: "Evidence", value: timelineLabel(match.timeline_status) },
        ]}
        note={match.data_quality_note}
        tone={matchQualityTone(match)}
      />
      <Link className="text-button compact-result-link" to={`/matches/${match.match_id}`}>
        Open match brief
      </Link>
    </article>
  );
}

export function RecentSignalMatchesPanel({
  matches,
  state,
}: {
  matches: MatchIntelligenceSummary[];
  state: OverviewModuleState;
}) {
  return (
    <section className="panel overview-matches-card">
      <ReportSectionHeader
        title="Recent signal matches"
        text="Matches worth opening because a scoring, timing, discipline, or evidence signal stands out."
      />
      {state === "partial" ? (
        <DataQualityNote
          compact
          note="The dedicated match-intelligence request is unavailable. These matches came from the Overview intelligence response."
          tone="caution"
        />
      ) : null}
      <div className="overview-signal-match-list">
        {matches.length > 0 ? (
          matches.slice(0, 5).map((match) => <SignalMatchCard key={match.match_id} match={match} />)
        ) : (
          <EmptyState
            message={moduleMessage(
              state,
              "Loading match signals.",
              "No signal matches were returned for this season.",
              "Match signals are unavailable because the intelligence requests did not complete.",
            )}
          />
        )}
      </div>
      <Link className="text-button compact-result-link" to="/matches">
        View match briefs
      </Link>
    </section>
  );
}

function TeamSignalCard({ signal }: { signal: TeamSignalSummary }) {
  return (
    <Link className="overview-team-card" to={`/teams/${signal.team_slug}`}>
      <div className="overview-team-card-title">
        <TeamMarker label={signal.team_name} size="small" />
        <div>
          <strong>{signal.signal}</strong>
          <span>{signal.team_name}</span>
        </div>
      </div>
      <p>
        <strong>{formatMetricValue(signal.metric_value)}</strong> {signal.metric_label}
      </p>
    </Link>
  );
}

export function TeamSignalsPanel({
  signals,
  state,
}: {
  signals: TeamSignalSummary[];
  state: OverviewModuleState;
}) {
  return (
    <section className="panel overview-signal-card">
      <ReportSectionHeader
        title="Team signals"
        text="Football-facing signals returned by the Overview intelligence layer, with the supporting value second."
      />
      <div className="overview-team-signal-grid">
        {signals.length > 0 ? (
          signals.slice(0, 5).map((signal) => (
            <TeamSignalCard key={`${signal.team_slug}-${signal.signal}`} signal={signal} />
          ))
        ) : (
          <EmptyState
            message={moduleMessage(
              state,
              "Loading team signals.",
              "No team intelligence signals were returned for this season.",
              "Team signals are unavailable because the Overview intelligence request did not complete.",
            )}
          />
        )}
      </div>
      <Link className="text-button compact-result-link" to="/teams">
        Open team board
      </Link>
    </section>
  );
}

export function OverviewCoveragePanel({
  quality,
  seasonLabel,
  state,
}: {
  quality: OverviewDataQuality | null;
  seasonLabel: string;
  state: OverviewModuleState;
}) {
  const unavailable = state === "error" || state === "loading";
  const note = unavailable
    ? state === "loading"
      ? `Loading analytical coverage for ${seasonLabel}.`
      : `Analytical coverage for ${seasonLabel} is unavailable because the Overview intelligence request did not complete.`
    : quality?.note ?? `Coverage for ${seasonLabel} has no additional source caveat.`;

  return (
    <section className="panel overview-quality-panel">
      <ReportSectionHeader
        title={`${seasonLabel} data coverage`}
        text="Coverage describes which records support interpretation. It is separate from the app's service freshness status."
      >
        <Link className="text-button" to="/about">
          Read methodology
        </Link>
      </ReportSectionHeader>
      <DataQualityNote
        metrics={
          quality
            ? [
                {
                  label: "Timeline coverage",
                  value:
                    quality.timeline_coverage_share === null
                      ? "Unavailable"
                      : formatPercent(quality.timeline_coverage_share),
                },
                { label: "Administrative results", value: quality.administrative_result_count },
                { label: "Source anomalies", value: quality.source_anomaly_count },
              ]
            : []
        }
        note={note}
        tone={qualityTone(quality?.status)}
      />
    </section>
  );
}
