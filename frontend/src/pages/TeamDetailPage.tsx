import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { apiClient } from "../api/client";
import type { EventResponse, MatchSummary } from "../api/types";
import type { PageProps } from "../app/types";
import { EmptyState } from "../components/common/EmptyState";
import { KpiCard } from "../components/common/KpiCard";
import { TeamMarker } from "../components/common/TeamMarker";
import { formatDate, formatSeason } from "../utils/format";
import {
  formatGoalDifference,
  getOpponent,
  getTeamGoalDifference,
  getTeamMatchResult,
  getTeamPoints,
  getTeamSlug,
  getTeamWinRate,
  summarizeTeamEvents,
} from "../utils/teams";

type TeamProfileState = "idle" | "loading" | "success" | "error";

function scoreline(match: MatchSummary) {
  return `${match.home_score ?? "-"}:${match.away_score ?? "-"}`;
}

function TeamProfileSkeleton() {
  return (
    <div className="team-profile-page" aria-busy="true">
      <div className="skeleton-card team-profile-skeleton">
        <span className="skeleton-line short"></span>
        <span className="skeleton-line title"></span>
        <span className="skeleton-line"></span>
      </div>
      <div className="metric-grid compact-metrics">
        {[0, 1, 2, 3].map((item) => (
          <div className="skeleton-card match-detail-skeleton" key={item}>
            <span className="skeleton-line medium"></span>
            <span className="skeleton-line number"></span>
          </div>
        ))}
      </div>
      <div className="match-detail-lower-grid">
        <div className="skeleton-card match-detail-skeleton tall"></div>
        <div className="skeleton-card match-detail-skeleton tall"></div>
      </div>
    </div>
  );
}

function RecentMatches({ matches, teamName }: { matches: MatchSummary[]; teamName: string }) {
  if (matches.length === 0) {
    return <EmptyState message="No recent matches are available for this team in the selected season yet." />;
  }

  return (
    <div className="team-profile-match-list">
      {matches.map((match) => {
        const opponent = getOpponent(match, teamName);
        const result = getTeamMatchResult(match, teamName);

        return (
          <Link className="team-profile-match-row" to={`/matches/${match.match_id}`} key={match.match_id}>
            <div>
              <span>{formatDate(match.match_date)}</span>
              <strong>{opponent.opponent ?? "Opponent TBC"}</strong>
              {match.ground_name ? <small>{match.ground_name}</small> : null}
            </div>
            <div className="team-profile-match-meta">
              <span>{opponent.isHome ? "Home" : "Away"}</span>
              <strong>{scoreline(match)}</strong>
              <span>{result}</span>
            </div>
          </Link>
        );
      })}
    </div>
  );
}

function EventSummary({ events }: { events: EventResponse[] }) {
  if (events.length === 0) {
    return <EmptyState message="No team event summary is available for this season yet." />;
  }

  const summary = summarizeTeamEvents(events);

  return (
    <div className="team-event-summary">
      <div>
        <span>Goals</span>
        <strong>{summary.goals}</strong>
      </div>
      <div>
        <span>Yellow cards</span>
        <strong>{summary.yellowCards}</strong>
      </div>
      <div>
        <span>Red cards</span>
        <strong>{summary.redCards}</strong>
      </div>
      <div>
        <span>Substitutions</span>
        <strong>{summary.substitutions}</strong>
      </div>
    </div>
  );
}

export default function TeamDetailPage({ data, loadState, onRefresh, selectedSeason }: PageProps) {
  const { teamSlug } = useParams();
  const team = data.teams.find((row) => getTeamSlug(row.team_name) === teamSlug);
  const [teamMatches, setTeamMatches] = useState<MatchSummary[]>([]);
  const [teamEvents, setTeamEvents] = useState<EventResponse[]>([]);
  const [profileState, setProfileState] = useState<TeamProfileState>("idle");
  const [profileError, setProfileError] = useState("");

  useEffect(() => {
    if (!team || !selectedSeason) return;

    let ignore = false;
    setProfileState("loading");
    setProfileError("");

    Promise.all([
      apiClient.getTeamMatches(selectedSeason, team.team_name, 12),
      apiClient.getTeamEvents(selectedSeason, team.team_name, 200),
    ])
      .then(([matches, events]) => {
        if (!ignore) {
          setTeamMatches(matches);
          setTeamEvents(events);
          setProfileState("success");
        }
      })
      .catch((error) => {
        if (!ignore) {
          setTeamMatches([]);
          setTeamEvents([]);
          setProfileState("error");
          setProfileError(error instanceof Error ? error.message : "Could not load team profile details.");
        }
      });

    return () => {
      ignore = true;
    };
  }, [selectedSeason, team]);

  const fallbackMatches = useMemo(() => {
    if (!team) return [];
    return [...data.matches]
      .filter((match) => match.home_team === team.team_name || match.away_team === team.team_name)
      .sort((left, right) => (right.match_date ?? "").localeCompare(left.match_date ?? "") || right.match_id - left.match_id)
      .slice(0, 12);
  }, [data.matches, team]);

  if (loadState === "loading" && !team) {
    return <TeamProfileSkeleton />;
  }

  if (!team) {
    return (
      <section className="error-panel" role="alert">
        <span className="eyebrow">Team profile</span>
        <h2>Team not found</h2>
        <p>This team could not be found for the selected season.</p>
        <div className="match-detail-actions">
          <Link className="text-button" to="/teams">
            Back to Teams
          </Link>
        </div>
      </section>
    );
  }

  const points = getTeamPoints(team);
  const goalDifference = getTeamGoalDifference(team);
  const winRate = Math.round(getTeamWinRate(team) * 100);
  const goalsPerMatch = team.matches_played > 0 ? team.goals_for / team.matches_played : 0;
  const concededPerMatch = team.matches_played > 0 ? team.goals_against / team.matches_played : 0;
  const recentMatches = profileState === "success" ? teamMatches : fallbackMatches;

  return (
    <article className="team-profile-page">
      <Link className="text-button back-link" to="/teams">
        Back to Teams
      </Link>

      <header className="team-profile-hero">
        <TeamMarker label={team.team_name} size="medium" />
        <div>
          <span className="eyebrow">Team profile</span>
          <h1>{team.team_name}</h1>
          <p>
            {formatSeason(selectedSeason)} · {team.matches_played} matches · {team.wins}W {team.draws}D {team.losses}L ·{" "}
            {formatGoalDifference(goalDifference)} GD
          </p>
        </div>
      </header>

      {profileState === "error" ? (
        <section className="error-panel compact-error" role="alert">
          <span className="eyebrow">Team profile details</span>
          <h2>Team profile unavailable for this season</h2>
          <p>{profileError || "Recent matches and event details could not be loaded. The summary remains available."}</p>
          <button className="text-button" type="button" onClick={onRefresh}>
            Retry season data
          </button>
        </section>
      ) : null}

      <section className="metric-grid compact-metrics" aria-label="Record summary">
        <KpiCard label="Matches" value={team.matches_played} context="Season matches in the team summary." variant="compact" />
        <KpiCard accent="green" label="Wins" value={team.wins} context={`${points} points safely derived from W/D/L.`} variant="compact" />
        <KpiCard label="Draws" value={team.draws} context={`${winRate}% win rate.`} variant="compact" />
        <KpiCard accent="risk" label="Losses" value={team.losses} context="Recorded losses in available results." variant="compact" />
      </section>

      <section className="panel">
        <div className="section-heading compact">
          <div>
            <span className="eyebrow">Scoring profile</span>
            <h2>Goals for and against</h2>
          </div>
        </div>
        <div className="team-scoring-grid">
          <div>
            <span>Goals for</span>
            <strong>{team.goals_for}</strong>
            <small>{goalsPerMatch.toFixed(2)} per match</small>
          </div>
          <div>
            <span>Goals against</span>
            <strong>{team.goals_against}</strong>
            <small>{concededPerMatch.toFixed(2)} conceded per match</small>
          </div>
          <div>
            <span>Goal difference</span>
            <strong>{formatGoalDifference(goalDifference)}</strong>
            <small>Derived from goals for and against</small>
          </div>
          <div>
            <span>Points</span>
            <strong>{points}</strong>
            <small>3 for a win, 1 for a draw</small>
          </div>
        </div>
      </section>

      <div className="match-detail-lower-grid">
        <section className="panel">
          <div className="section-heading compact">
            <div>
              <span className="eyebrow">Recent matches</span>
              <h2>Team results</h2>
            </div>
          </div>
          {profileState === "loading" && fallbackMatches.length === 0 ? (
            <div className="skeleton-card team-profile-skeleton">
              <span className="skeleton-line medium"></span>
              <span className="skeleton-line"></span>
              <span className="skeleton-line"></span>
            </div>
          ) : (
            <RecentMatches matches={recentMatches} teamName={team.team_name} />
          )}
        </section>

        <section className="panel">
          <div className="section-heading compact">
            <div>
              <span className="eyebrow">Events</span>
              <h2>Team event summary</h2>
            </div>
          </div>
          {profileState === "loading" ? (
            <div className="skeleton-card team-profile-skeleton">
              <span className="skeleton-line medium"></span>
              <span className="skeleton-line"></span>
              <span className="skeleton-line short"></span>
            </div>
          ) : (
            <EventSummary events={teamEvents} />
          )}
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
          <Link className="text-button" to="/teams">
            Back to Teams
          </Link>
          <Link className="text-button" to={`/matches?team=${encodeURIComponent(team.team_name)}`}>
            View matches involving this team
          </Link>
          <Link className="text-button" to="/insights">
            View Insights
          </Link>
          <Link className="text-button" to="/about">
            View About/data notes
          </Link>
        </div>
      </section>
    </article>
  );
}
