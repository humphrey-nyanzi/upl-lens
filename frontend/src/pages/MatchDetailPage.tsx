import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { ApiRequestError, apiClient } from "../api/client";
import type { PageProps } from "../app/types";
import type { EventResponse, MatchDetailResponse, MatchStatResponse, OfficialResponse } from "../api/types";
import { TeamMarker } from "../components/common/TeamMarker";
import { formatDate, formatResult, formatSeason, matchStatus } from "../utils/format";
import { slugify } from "../utils/slugs";

type MatchDetailState = "loading" | "success" | "not_found" | "error" | "offline";

function getSafeTeamName(name: string | null) {
  return name ?? "Team TBC";
}

function formatMatchday(matchDay: number | null) {
  return matchDay === null ? null : `Matchday ${matchDay}`;
}

function formatValue(value: string | number | null | undefined) {
  if (value === null || value === undefined || value === "") return null;
  return String(value);
}

function formatTime(value: string | null) {
  return value ? value.slice(0, 5) : null;
}

function scoreValue(value: number | null) {
  return value === null ? "-" : String(value);
}

function toTitleCase(value: string) {
  return value
    .replace(/_/g, " ")
    .split(" ")
    .filter(Boolean)
    .map((word) => `${word[0]?.toUpperCase() ?? ""}${word.slice(1)}`)
    .join(" ");
}

function eventLabel(event: EventResponse) {
  if (event.event_type === "goal") return event.goal_type ? `${toTitleCase(event.goal_type)} goal` : "Goal";
  if (event.event_type === "own_goal") return "Own goal";
  if (event.event_type === "penalty_goal") return "Penalty goal";
  if (event.event_type === "yellow_card") return "Yellow card";
  if (event.event_type === "red_card") return "Red card";
  if (event.event_type === "substitution") return "Substitution";
  return event.event_type ? toTitleCase(event.event_type) : "Event";
}

function eventMinute(event: EventResponse) {
  if (event.event_minute_text) return event.event_minute_text;
  if (event.minute_total !== null) return `${event.minute_total}'`;
  return "Minute TBC";
}

function eventDescription(event: EventResponse) {
  if (event.event_type === "substitution") {
    const players = [
      event.sub_out_player_name ? `Off: ${event.sub_out_player_name}` : null,
      event.sub_in_player_name ? `On: ${event.sub_in_player_name}` : null,
    ].filter(Boolean);

    return players.length > 0 ? players.join(" · ") : "Substitution details unavailable";
  }

  return event.player_name ?? "Player not listed";
}

function getEventGroup(event: EventResponse) {
  const period = event.minute_period?.toLowerCase() ?? "";
  const minute = event.minute_total;

  if (period.includes("added") || (minute !== null && minute > 90)) return "Added time";
  if (period.includes("second") || (minute !== null && minute > 45)) return "Second half";
  return "First half";
}

function sortEvents(events: EventResponse[]) {
  return [...events].sort((left, right) => {
    const leftMinute = left.minute_total ?? 999;
    const rightMinute = right.minute_total ?? 999;
    return leftMinute - rightMinute || (left.event_index ?? 999) - (right.event_index ?? 999);
  });
}

function groupEvents(events: EventResponse[]) {
  const orderedGroups = ["First half", "Second half", "Added time"];
  const groups = new Map<string, EventResponse[]>();

  sortEvents(events).forEach((event) => {
    const group = getEventGroup(event);
    groups.set(group, [...(groups.get(group) ?? []), event]);
  });

  return orderedGroups
    .map((group) => ({ label: group, events: groups.get(group) ?? [] }))
    .filter((group) => group.events.length > 0);
}

function metadataRows(match: MatchDetailResponse) {
  return [
    { label: "Competition", value: formatValue(match.league) },
    { label: "Season", value: formatSeason(match.season) },
    { label: "Matchday", value: formatMatchday(match.match_day) },
    { label: "Date", value: formatDate(match.match_date) },
    { label: "Kickoff", value: formatTime(match.match_time) },
    { label: "Venue", value: formatValue(match.ground_name) },
    { label: "Ground address", value: formatValue(match.ground_address) },
    { label: "Man of the match", value: formatValue(match.man_of_the_match) },
  ].filter((row) => row.value);
}

function MatchDetailLoading() {
  return (
    <div className="match-detail-page" aria-busy="true">
      <div className="skeleton-card match-detail-skeleton">
        <span className="skeleton-line short"></span>
        <span className="skeleton-line title"></span>
        <span className="skeleton-line number"></span>
      </div>
      <div className="match-detail-grid">
        <div className="skeleton-card match-detail-skeleton tall">
          <span className="skeleton-line medium"></span>
          <span className="skeleton-line"></span>
          <span className="skeleton-line"></span>
          <span className="skeleton-line"></span>
        </div>
        <div className="skeleton-card match-detail-skeleton tall">
          <span className="skeleton-line medium"></span>
          <span className="skeleton-line"></span>
          <span className="skeleton-line"></span>
        </div>
      </div>
      <div className="match-detail-lower-grid">
        <div className="skeleton-card match-detail-skeleton">
          <span className="skeleton-line medium"></span>
          <span className="skeleton-line"></span>
        </div>
        <div className="skeleton-card match-detail-skeleton">
          <span className="skeleton-line medium"></span>
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
          title: "Match not found",
          text: "This match could not be found in the available UPL Lens data.",
        }
      : state === "offline"
        ? {
            title: "Data service unavailable",
            text: "UPL Lens could not load match details right now. The hosted API may be waking up.",
          }
        : {
            title: "Could not load match details",
            text: "The match report did not load. Try again or return to the match list.",
          };

  return (
    <section className="error-panel match-detail-error">
      <span className="eyebrow">Match report</span>
      <h2>{copy.title}</h2>
      <p>{copy.text}</p>
      <div className="match-detail-actions">
        <Link className="text-button" to="/matches">
          Back to Matches
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

function MatchTeamLink({ name }: { name: string | null }) {
  const safeName = getSafeTeamName(name);

  return (
    <Link className="match-detail-team-link" to={`/teams/${slugify(safeName)}`}>
      <TeamMarker label={safeName} />
      <span>{safeName}</span>
    </Link>
  );
}

function MatchTimeline({ events }: { events: EventResponse[] }) {
  const groups = useMemo(() => groupEvents(events), [events]);

  if (events.length === 0) {
    return <div className="empty-state">No timeline events are available for this match yet.</div>;
  }

  return (
    <div className="match-timeline">
      {groups.map((group) => (
        <section className="match-timeline-group" key={group.label}>
          <h3>{group.label}</h3>
          <ol>
            {group.events.map((event) => (
              <li key={event.event_row_key}>
                <span className="event-minute">{eventMinute(event)}</span>
                <div className="event-copy">
                  <strong>{eventLabel(event)}</strong>
                  <span>{event.team_name ?? "Team not listed"}</span>
                  <p>{eventDescription(event)}</p>
                </div>
              </li>
            ))}
          </ol>
        </section>
      ))}
    </div>
  );
}

function MatchStatsPanel({ stats }: { stats: MatchStatResponse[] }) {
  if (stats.length === 0) {
    return <div className="empty-state">No match stats are available for this match yet.</div>;
  }

  return (
    <div className="match-stats-list">
      {stats.map((stat) => (
        <div className="match-stat-row" key={stat.stat_row_key}>
          <strong>{stat.home_value ?? "-"}</strong>
          <span>{stat.statistic_name ? toTitleCase(stat.statistic_name) : "Statistic"}</span>
          <strong>{stat.away_value ?? "-"}</strong>
        </div>
      ))}
    </div>
  );
}

function OfficialsPanel({ officials }: { officials: OfficialResponse[] }) {
  if (officials.length === 0) {
    return <div className="empty-state">No officials are listed for this match yet.</div>;
  }

  return (
    <div className="officials-list">
      {officials.map((official) => (
        <div className="official-row" key={official.official_row_key}>
          <span>{official.role ? toTitleCase(official.role) : "Official"}</span>
          <strong>{official.official_name ?? "Name unavailable"}</strong>
        </div>
      ))}
    </div>
  );
}

function DataCompletenessNote({ match }: { match: MatchDetailResponse }) {
  const sourceCopy = match.is_source_anomaly
    ? match.source_anomaly_reason ?? "This match has a source-data anomaly."
    : "Timeline, stats, and officials are shown where available from the source match page.";

  return (
    <section className={match.is_source_anomaly ? "match-data-note anomaly" : "match-data-note"}>
      <div>
        <span className="eyebrow">Data note</span>
        <p>{sourceCopy}</p>
      </div>
      <div className="match-data-chips" aria-label="Match data completeness">
        <span>{match.has_timeline || match.events.length > 0 ? "Timeline available" : "Timeline unavailable"}</span>
        <span>{match.has_stats || match.stats.length > 0 ? "Stats available" : "Stats unavailable"}</span>
        <span>{match.has_officials || match.officials.length > 0 ? "Officials listed" : "Officials unavailable"}</span>
        {match.match_url ? (
          <a href={match.match_url} target="_blank" rel="noreferrer">
            Source page
          </a>
        ) : null}
      </div>
    </section>
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

  if (state === "loading") {
    return <MatchDetailLoading />;
  }

  if (state !== "success" || !match) {
    const errorState = state === "success" ? "error" : state;
    return <MatchDetailError state={errorState} onRetry={() => setRetryIndex((current) => current + 1)} />;
  }

  const homeTeam = getSafeTeamName(match.home_team);
  const awayTeam = getSafeTeamName(match.away_team);
  const metaRows = metadataRows(match);

  return (
    <article className="match-detail-page">
      <Link className="text-button back-link" to="/matches">
        Back to Matches
      </Link>

      <header className="match-detail-hero">
        <div className="match-detail-meta-line">
          <span>{formatSeason(match.season)}</span>
          {formatMatchday(match.match_day) ? <span>{formatMatchday(match.match_day)}</span> : null}
          <span>{formatDate(match.match_date)}</span>
          {match.ground_name ? <span>{match.ground_name}</span> : null}
        </div>

        <div className="scoreline-panel">
          <div className="scoreline-team">
            <MatchTeamLink name={match.home_team} />
          </div>
          <div className="scoreline-centre" aria-label={`${homeTeam} ${scoreValue(match.home_score)} to ${scoreValue(match.away_score)} ${awayTeam}`}>
            <strong>
              {scoreValue(match.home_score)}:{scoreValue(match.away_score)}
            </strong>
            <span>{matchStatus(match)}</span>
          </div>
          <div className="scoreline-team away">
            <MatchTeamLink name={match.away_team} />
          </div>
        </div>

        <div className="match-detail-summary">
          <strong>
            {homeTeam} vs {awayTeam}
          </strong>
          <span>{match.result ? formatResult(match.result) : "Result pending"}</span>
        </div>
      </header>

      <DataCompletenessNote match={match} />

      <div className="match-detail-grid">
        <section className="panel match-timeline-panel">
          <div className="section-heading compact">
            <div>
              <span className="eyebrow">Timeline</span>
              <h2>Match events</h2>
            </div>
          </div>
          <MatchTimeline events={match.events} />
        </section>

        <aside className="panel match-info-panel">
          <div className="section-heading compact">
            <div>
              <span className="eyebrow">Match info</span>
              <h2>Details</h2>
            </div>
          </div>
          <dl className="match-info-list">
            {metaRows.map((row) => (
              <div key={row.label}>
                <dt>{row.label}</dt>
                <dd>{row.value}</dd>
              </div>
            ))}
          </dl>
          {match.match_url ? (
            <a className="text-button source-link" href={match.match_url} target="_blank" rel="noreferrer">
              Open source page
            </a>
          ) : null}
        </aside>
      </div>

      <div className="match-detail-lower-grid">
        <section className="panel">
          <div className="section-heading compact">
            <div>
              <span className="eyebrow">Stats</span>
              <h2>Home vs away</h2>
            </div>
          </div>
          <MatchStatsPanel stats={match.stats} />
        </section>

        <section className="panel">
          <div className="section-heading compact">
            <div>
              <span className="eyebrow">Officials</span>
              <h2>Match crew</h2>
            </div>
          </div>
          <OfficialsPanel officials={match.officials} />
        </section>
      </div>

      <section className="panel related-actions-panel">
        <div className="section-heading compact">
          <div>
            <span className="eyebrow">Related</span>
            <h2>Keep exploring</h2>
          </div>
        </div>
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
          <Link className="text-button" to="/about">
            View About/data notes
          </Link>
        </div>
      </section>
    </article>
  );
}
