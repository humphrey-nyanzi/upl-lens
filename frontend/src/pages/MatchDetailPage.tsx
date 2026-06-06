import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ApiRequestError, apiClient } from "../api/client";
import type {
  EventResponse,
  MatchDetailResponse,
  MatchEventPhaseSummary,
  MatchKeyMoment,
  MatchStatResponse,
  OfficialResponse,
  ScoreProgressionPoint as ApiScoreProgressionPoint,
} from "../api/types";
import type { PageProps } from "../app/types";
import { StatComparisonRow } from "../components/common/EditorialRows";
import { EmptyState } from "../components/common/EmptyState";
import { ReportSectionHeader } from "../components/common/ReportSectionHeader";
import { TeamMarker } from "../components/common/TeamMarker";
import {
  DataQualityNote,
  HorizontalComparisonBar,
  MetricDelta,
  ScoreProgression,
  SignalChipGroup,
  TimelineRail,
  type DataQualityTone,
  type SignalChipItem,
  type TimelineRailEvent,
} from "../components/intelligence";
import { formatDate, formatResult, formatScoreline, formatSeason } from "../utils/format";
import { slugify } from "../utils/slugs";

type MatchDetailState = "loading" | "success" | "not_found" | "error" | "offline";

const goalEventTypes = new Set(["goal", "own_goal", "penalty_goal"]);

function getSafeTeamName(name: string | null) {
  return name ?? "Team TBC";
}

function formatMatchday(matchDay: number | null) {
  return matchDay === null ? "Matchday TBC" : `Matchday ${matchDay}`;
}

function formatTime(value: string | null) {
  return value ? value.slice(0, 5) : null;
}

function formatValue(value: string | number | null | undefined) {
  if (value === null || value === undefined || value === "") return null;
  return String(value);
}

function toTitleCase(value: string | null | undefined) {
  if (!value) return "";
  return value
    .replace(/_/g, " ")
    .split(" ")
    .filter(Boolean)
    .map((word) => `${word[0]?.toUpperCase() ?? ""}${word.slice(1)}`)
    .join(" ");
}

function phaseLabel(phase: MatchEventPhaseSummary["phase"]) {
  if (phase === "first_half") return "First half";
  if (phase === "second_half") return "Second half";
  if (phase === "final_15") return "Final 15";
  return "Added time";
}

function timelineToneFromEventType(eventType: string | null | undefined): TimelineRailEvent["tone"] {
  if (!eventType) return "neutral";
  if (goalEventTypes.has(eventType)) return "goal";
  if (eventType === "red_card") return "red";
  if (eventType === "yellow_card") return "card";
  if (eventType === "substitution") return "substitution";
  if (eventType === "administrative_result" || eventType === "source_caveat") return "warning";
  return "neutral";
}

function toSignalItems(match: MatchDetailResponse): SignalChipItem[] {
  return (match.intelligence_summary?.signal_labels ?? []).map((signal) => ({
    key: signal.key,
    label: signal.label,
    tone: signal.tone,
  }));
}

function toTimelineEvents(match: MatchDetailResponse): TimelineRailEvent[] {
  if (match.key_moments.length > 0) {
    return match.key_moments.map((moment, index) => ({
      id: `${moment.label}-${moment.minute_text ?? moment.minute ?? "tbc"}-${index}`,
      eventType: moment.event_type,
      label: moment.label,
      minute: moment.minute,
      minuteText: moment.minute_text,
      teamName: moment.team_name,
      tone: timelineToneFromEventType(moment.event_type),
    }));
  }

  return match.events
    .filter((event) => goalEventTypes.has(event.event_type ?? "") || event.event_type === "red_card" || event.event_type === "yellow_card")
    .slice(0, 12)
    .map((event) => ({
      id: event.event_row_key,
      eventType: event.event_type,
      label: toTitleCase(event.event_type) || "Event",
      minute: event.minute_total,
      minuteText: event.event_minute_text,
      teamName: event.team_name,
      tone: timelineToneFromEventType(event.event_type),
    }));
}

function toProgressionPoints(points: ApiScoreProgressionPoint[]) {
  return points.map((point) => ({
    awayScore: point.away_score,
    eventType: point.event_type,
    homeScore: point.home_score,
    minute: point.minute,
    minuteText: point.minute_text,
    scoringTeam: point.scoring_team,
  }));
}

function dataQualityTone(match: MatchDetailResponse): DataQualityTone {
  if (match.is_source_anomaly || match.is_administrative_result) return "risk";
  if (match.timeline_status === "partial") return "caution";
  if (match.timeline_status === "unavailable") return "limited";
  if (match.timeline_status === "complete") return "good";
  return "neutral";
}

function evidenceQualityNote(match: MatchDetailResponse) {
  if (match.is_source_anomaly) return match.source_anomaly_reason ?? "This source record carries an anomaly.";
  if (match.is_administrative_result) return match.administrative_note ?? "This match was recorded as an administrative result.";
  if (match.timeline_note) return match.timeline_note;
  return "Timeline, stats, and officials are shown where available from the source match page.";
}

function getMetadataRows(match: MatchDetailResponse) {
  return [
    { label: "Competition", value: formatValue(match.league) },
    { label: "Season", value: formatSeason(match.season) },
    { label: "Matchday", value: formatMatchday(match.match_day) },
    { label: "Date", value: formatDate(match.match_date) },
    { label: "Kickoff", value: formatTime(match.match_time) },
    { label: "Venue", value: formatValue(match.ground_name) },
    { label: "Ground address", value: formatValue(match.ground_address) },
    { label: "Result type", value: match.is_administrative_result ? "Administrative result" : "Played result" },
    { label: "Administrative note", value: formatValue(match.administrative_note) },
    { label: "Man of the match", value: formatValue(match.man_of_the_match) },
  ].filter((row) => row.value);
}

function MatchDetailLoading() {
  return (
    <div className="match-brief-page" aria-busy="true">
      <div className="skeleton-card match-brief-skeleton hero">
        <span className="skeleton-line short"></span>
        <span className="skeleton-line title"></span>
        <span className="skeleton-line number"></span>
      </div>
      <div className="match-brief-grid">
        <div className="skeleton-card match-brief-skeleton tall">
          <span className="skeleton-line medium"></span>
          <span className="skeleton-line"></span>
          <span className="skeleton-line"></span>
          <span className="skeleton-line"></span>
        </div>
        <div className="skeleton-card match-brief-skeleton tall">
          <span className="skeleton-line medium"></span>
          <span className="skeleton-line"></span>
          <span className="skeleton-line"></span>
        </div>
      </div>
    </div>
  );
}

function MatchDetailError({
  state,
  onRetry,
}: {
  state: Exclude<MatchDetailState, "loading" | "success">;
  onRetry: () => void;
}) {
  const copy =
    state === "not_found"
      ? {
          title: "Match brief unavailable",
          text: "This match could not be found in the available UPL Lens data.",
        }
      : state === "offline"
        ? {
            title: "Match brief unavailable",
            text: "UPL Lens could not load match details right now. The hosted API may be waking up.",
          }
        : {
            title: "Match brief unavailable",
            text: "The match intelligence brief did not load. Try again or return to Matches.",
          };

  return (
    <section className="error-panel match-detail-error">
      <span className="eyebrow">Match intelligence</span>
      <h2>{copy.title}</h2>
      <p>{copy.text}</p>
      <div className="match-detail-actions">
        <Link className="text-button" to="/matches">
          Return to Matches
        </Link>
        {state !== "not_found" ? (
          <button className="text-button" type="button" onClick={onRetry}>
            Retry
          </button>
        ) : null}
      </div>
    </section>
  );
}

function MatchTeamLink({ markerPosition = "before", name }: { markerPosition?: "before" | "after"; name: string | null }) {
  const safeName = getSafeTeamName(name);
  const marker = <TeamMarker label={safeName} />;

  return (
    <Link className="match-detail-team-link" to={`/teams/${slugify(safeName)}`}>
      {markerPosition === "before" ? marker : null}
      <span>{safeName}</span>
      {markerPosition === "after" ? marker : null}
    </Link>
  );
}

function KeyMomentsPanel({ moments }: { moments: MatchKeyMoment[] }) {
  if (moments.length === 0) {
    return (
      <EmptyState message="No key moments are available from the event timeline for this match." title="No key moments available" />
    );
  }

  return (
    <ol className="key-moment-list">
      {moments.map((moment, index) => (
        <li className="key-moment-card" key={`${moment.label}-${moment.minute_text ?? moment.minute ?? "tbc"}-${index}`}>
          <span>{moment.minute_text ?? (moment.minute === null ? "Minute TBC" : `${moment.minute}'`)}</span>
          <div>
            <strong>{moment.label}</strong>
            <p>{moment.reason}</p>
            <small>
              {[moment.team_name, moment.player_name, toTitleCase(moment.event_type)].filter(Boolean).join(" · ") ||
                "Timeline context"}
            </small>
          </div>
        </li>
      ))}
    </ol>
  );
}

function EventPhasePanel({ phases }: { phases: MatchEventPhaseSummary[] }) {
  if (phases.length === 0 || phases.every((phase) => phase.total_events === 0)) {
    return <EmptyState message="No event phase summary is available for this match." />;
  }

  return (
    <div className="phase-summary-list">
      {phases.map((phase) => (
        <article className="phase-summary-card" key={phase.phase}>
          <div>
            <strong>{phaseLabel(phase.phase)}</strong>
            <span>{phase.total_events} events</span>
          </div>
          <HorizontalComparisonBar
            segments={[
              { label: "Goals", value: phase.goals, tone: "green" },
              { label: "Yellows", value: phase.yellow_cards, tone: "gold" },
              { label: "Reds", value: phase.red_cards, tone: "risk" },
              { label: "Subs", value: phase.substitutions, tone: "muted" },
            ]}
            showValues
            total={Math.max(phase.total_events, phase.goals + phase.yellow_cards + phase.red_cards + phase.substitutions)}
          />
        </article>
      ))}
    </div>
  );
}

function MatchStatsPanel({ stats }: { stats: MatchStatResponse[] }) {
  if (stats.length === 0) {
    return <EmptyState message="No match stats are available." />;
  }

  return (
    <div className="match-stats-list">
      {stats.map((stat) => (
        <StatComparisonRow
          awayValue={stat.away_value ?? "-"}
          homeValue={stat.home_value ?? "-"}
          key={stat.stat_row_key}
          label={stat.statistic_name ? toTitleCase(stat.statistic_name) : "Statistic"}
        />
      ))}
    </div>
  );
}

function OfficialsPanel({ officials }: { officials: OfficialResponse[] }) {
  if (officials.length === 0) {
    return <EmptyState message="No officials are listed for this match." />;
  }

  return (
    <div className="officials-list compact">
      {officials.map((official) => (
        <div className="official-row" key={official.official_row_key}>
          <span>{official.role ? toTitleCase(official.role) : "Official"}</span>
          <strong>{official.official_name ?? "Name unavailable"}</strong>
        </div>
      ))}
    </div>
  );
}

export default function MatchDetailPage(_props: PageProps) {
  const { matchId } = useParams();
  const numericMatchId = Number(matchId);
  const [match, setMatch] = useState<MatchDetailResponse | null>(null);
  const [state, setState] = useState<MatchDetailState>("loading");
  const [retryIndex, setRetryIndex] = useState(0);

  useEffect(() => {
    if (!Number.isFinite(numericMatchId)) {
      setState("not_found");
      return;
    }

    let ignore = false;

    async function loadMatchDetail() {
      setState("loading");

      try {
        const detail = await apiClient.getMatchDetail(numericMatchId);
        if (!ignore) {
          setMatch(detail);
          setState("success");
        }
      } catch (error) {
        if (ignore) return;

        setMatch(null);
        if (error instanceof ApiRequestError && error.status === 404) {
          setState("not_found");
        } else if (error instanceof TypeError) {
          setState("offline");
        } else {
          setState("error");
        }
      }
    }

    void loadMatchDetail();

    return () => {
      ignore = true;
    };
  }, [numericMatchId, retryIndex]);

  const timelineEvents = useMemo(() => (match ? toTimelineEvents(match) : []), [match]);
  const progressionPoints = useMemo(() => (match ? toProgressionPoints(match.score_progression) : []), [match]);

  if (state === "loading") {
    return <MatchDetailLoading />;
  }

  if (state !== "success" || !match) {
    const errorState = state === "success" ? "error" : state;
    return <MatchDetailError state={errorState} onRetry={() => setRetryIndex((current) => current + 1)} />;
  }

  const homeTeam = getSafeTeamName(match.home_team);
  const awayTeam = getSafeTeamName(match.away_team);
  const intelligence = match.intelligence_summary;
  const signalItems = toSignalItems(match);
  const scoreline = formatScoreline(match.home_score, match.away_score);
  const metadataRows = getMetadataRows(match);
  const eventCardCount = match.events.filter((event) => event.event_type === "yellow_card" || event.event_type === "red_card").length;

  return (
    <article className="match-brief-page">
      <Link className="text-button back-link" to="/matches">
        Back to Matches
      </Link>

      <header className="match-brief-hero">
        <div className="match-detail-meta-line">
          <span>{formatSeason(match.season)}</span>
          <span>{formatMatchday(match.match_day)}</span>
          <span>{formatDate(match.match_date)}</span>
          {match.ground_name ? <span>{match.ground_name}</span> : null}
        </div>

        <div className="scoreline-panel match-brief-scoreline">
          <div className="scoreline-team">
            <MatchTeamLink name={match.home_team} />
          </div>
          <div className="scoreline-centre" aria-label={`${homeTeam} ${scoreline} ${awayTeam}`}>
            <strong>{scoreline}</strong>
            <span>{match.result ? formatResult(match.result) : "Result pending"}</span>
          </div>
          <div className="scoreline-team away">
            <MatchTeamLink markerPosition="after" name={match.away_team} />
          </div>
        </div>

        <div className="match-brief-headline">
          <p className="eyebrow">{intelligence?.primary_signal ?? "Match intelligence brief"}</p>
          <h1>
            {homeTeam} {scoreline} {awayTeam}
          </h1>
          <p>
            {intelligence?.summary_text ??
              "This brief uses the recorded scoreline, available timeline events, stats, officials, and source notes to show what can be read from this match."}
          </p>
          <SignalChipGroup items={signalItems} emptyLabel="No major match signal" maxVisible={5} />
        </div>
      </header>

      <DataQualityNote
        tone={dataQualityTone(match)}
        note={evidenceQualityNote(match)}
        metrics={[
          { label: "Timeline", value: match.timeline_status ?? "Unknown", detail: `${match.timeline_issue_count} issue(s)` },
          { label: "Events", value: match.events.length },
          { label: "Stats", value: match.has_stats || match.stats.length > 0 ? "Available" : "Unavailable" },
          { label: "Officials", value: match.has_officials || match.officials.length > 0 ? "Listed" : "Unavailable" },
        ]}
      />

      <section className="panel match-intelligence-summary-panel">
        <ReportSectionHeader
          eyebrow="Why it matters"
          title="Match intelligence summary"
          text="Computed match signals sit above the source record so the page explains why this fixture is worth reading."
        />
        <div className="match-brief-summary-grid">
          <MetricDelta label="Interest score" value={intelligence?.interest_score ?? 0} context="Computed signal score" />
          <MetricDelta label="Scoring pattern" value={intelligence?.scoring_pattern ?? "Not flagged"} context="Read with timeline coverage." />
          <MetricDelta label="Decisive phase" value={intelligence?.decisive_phase ?? "Not flagged"} context="Based on captured events." />
          <MetricDelta label="Discipline" value={intelligence?.discipline_pattern ?? "Not flagged"} context={`${eventCardCount} captured card event(s).`} />
          <MetricDelta label="Evidence" value={intelligence?.evidence_quality ?? match.timeline_status ?? "Unknown"} context="Timeline-backed sections depend on coverage." />
        </div>
      </section>

      <section className="panel">
        <ReportSectionHeader
          eyebrow="Key moments"
          title="What shaped the match"
          text="These selected moments explain the match signal before the fuller timeline evidence."
        />
        <KeyMomentsPanel moments={match.key_moments} />
      </section>

      <div className="match-brief-grid">
        <section className="panel">
          <TimelineRail
            description="Goals, cards, and decisive source notes are plotted as readable match evidence rather than a source-event dump."
            emptyLabel="No key timeline moments are available for this match."
            events={timelineEvents}
            title="Timeline rail"
          />
        </section>

        <section className="panel">
          <ReportSectionHeader
            eyebrow="Score changes"
            title="Score progression"
            text="The score progression is based on captured goal events from the match timeline."
          />
          <ScoreProgression
            awayTeam={awayTeam}
            emptyLabel="Score progression is unavailable because no goal timeline was captured for this match."
            homeTeam={homeTeam}
            points={progressionPoints}
          />
        </section>
      </div>

      <section className="panel">
        <ReportSectionHeader
          eyebrow="Phase summary"
          title="Event concentration"
          text="This shows where captured events appear in the match without treating event volume as tactical momentum."
        />
        <EventPhasePanel phases={match.event_phase_summary} />
      </section>

      <div className="match-detail-lower-grid">
        <section className="panel">
          <ReportSectionHeader
            eyebrow="Supporting stats"
            title="Match stats comparison"
            text="Stats sit below the brief as supporting source evidence for the recorded result."
          />
          <MatchStatsPanel stats={match.stats} />
        </section>

        <section className="panel">
          <ReportSectionHeader
            eyebrow="Source context"
            title="Officials and recorded details"
            text="Officials are listed as source context only until official/referee signals are supported by the intelligence layer."
          />
          <OfficialsPanel officials={match.officials} />
          <dl className="match-info-list compact">
            {metadataRows.map((row) => (
              <div key={row.label}>
                <dt>{row.label}</dt>
                <dd>{row.value}</dd>
              </div>
            ))}
          </dl>
          {match.match_url ? (
            <a className="text-button source-link" href={match.match_url} target="_blank" rel="noreferrer">
              Open official source
            </a>
          ) : null}
        </section>
      </div>

      <section className="panel related-actions-panel">
        <ReportSectionHeader
          eyebrow="Next step"
          title="Follow the match context"
          text="Move from this brief into team dossiers, the wider match triage list, or season trend context."
        />
        <div className="match-detail-actions">
          <Link className="text-button" to="/matches">
            Back to Matches
          </Link>
          <Link className="text-button" to={`/teams/${slugify(homeTeam)}`}>
            View {homeTeam}
          </Link>
          <Link className="text-button" to={`/teams/${slugify(awayTeam)}`}>
            View {awayTeam}
          </Link>
          <Link className="text-button" to="/trends">
            View Trends
          </Link>
          {match.match_url ? (
            <a className="text-button" href={match.match_url} target="_blank" rel="noreferrer">
              Open official source
            </a>
          ) : null}
        </div>
      </section>
    </article>
  );
}
