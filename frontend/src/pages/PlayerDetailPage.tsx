import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { apiClient, ApiRequestError } from "../api/client";
import type { PlayerDetailResponse } from "../api/types";
import type { PageProps } from "../app/types";
import { EmptyState } from "../components/common/EmptyState";
import { KpiCard } from "../components/common/KpiCard";
import { ReportSectionHeader } from "../components/common/ReportSectionHeader";
import { formatDate, formatScoreline, formatSeason } from "../utils/format";
import { getSelectedSeasonLabel, toApiSeason } from "../utils/seasonScope";
import { getTeamSlug } from "../utils/teams";

function formatRole(role: string | null) {
  if (!role) return "Listed";
  return role.replace(/_/g, " ").replace(/\b\w/g, (character) => character.toUpperCase());
}

function buildPlayerStandfirst(player: PlayerDetailResponse, teams: string, seasonLabel: string) {
  return `${player.player_name}'s ${seasonLabel.toLowerCase()} player brief brings together scoring, creative output, appearances, discipline, and recent match involvement for ${teams}.`;
}

export default function PlayerDetailPage({ selectedSeason }: Pick<PageProps, "selectedSeason">) {
  const { playerSlug } = useParams();
  const [player, setPlayer] = useState<PlayerDetailResponse | null>(null);
  const [loadState, setLoadState] = useState<"loading" | "success" | "error">("loading");
  const [errorMessage, setErrorMessage] = useState("");
  const seasonLabel = getSelectedSeasonLabel(selectedSeason);

  useEffect(() => {
    if (!playerSlug) return;

    let ignore = false;
    setLoadState("loading");
    setErrorMessage("");

    apiClient
      .getPlayerDetail(playerSlug, toApiSeason(selectedSeason))
      .then((response) => {
        if (!ignore) {
          setPlayer(response);
          setLoadState("success");
        }
      })
      .catch((error) => {
        if (!ignore) {
          setPlayer(null);
          setLoadState("error");
          if (error instanceof ApiRequestError && error.status === 404) {
            setErrorMessage("Player not found in the current scope.");
          } else {
            setErrorMessage(error instanceof Error ? error.message : "Could not load player profile.");
          }
        }
      });

    return () => {
      ignore = true;
    };
  }, [playerSlug, selectedSeason]);

  if (loadState === "loading") {
    return (
      <div className="player-profile-page" aria-busy="true">
        <div className="skeleton-card match-detail-skeleton" />
        <div className="match-detail-lower-grid">
          <div className="skeleton-card match-detail-skeleton tall" />
          <div className="skeleton-card match-detail-skeleton tall" />
        </div>
      </div>
    );
  }

  if (!player) {
    return (
      <section className="error-panel">
        <p className="eyebrow">Player profile</p>
        <h1>{errorMessage || "Could not load player profile."}</h1>
        <div className="match-detail-actions">
          <Link className="text-button" to="/players">Back to Players</Link>
        </div>
      </section>
    );
  }

  const teams = player.teams.length > 0 ? player.teams.join(", ") : "Team TBC";
  const cards = player.yellow_cards + player.red_cards;
  const standfirst = buildPlayerStandfirst(player, teams, seasonLabel);
  const primaryTeam = player.primary_team ?? player.teams[0] ?? null;

  return (
    <article className="player-profile-page">
      <Link className="text-button" to="/players">Back to Players</Link>

      <header className="player-profile-hero">
        <p className="eyebrow">Player profile</p>
        <h1>{player.player_name}</h1>
        <p>{teams}</p>
        <p className="report-standfirst">{standfirst}</p>
      </header>

      <section className="metric-grid compact-metrics" aria-label="Player profile summary">
        <KpiCard accent="green" label="Goals" value={player.goals} context="Timeline goal events credited to this player." variant="compact" />
        <KpiCard accent="gold" label="Assists" value={player.assists} context="Assist events when available from the source timeline." variant="compact" />
        <KpiCard label="Appearances" value={player.appearances} context={`${player.starts} starts from lineup data.`} variant="compact" />
        <KpiCard label="Cards" value={cards} context={`${player.yellow_cards} yellow, ${player.red_cards} red.`} variant="compact" />
      </section>

      <div className="match-detail-lower-grid">
        <section className="panel">
          <ReportSectionHeader
            eyebrow="Season view"
            title="Output by season"
            text="Lineup and event totals are grouped by season so longer-term contribution stays easy to compare."
          />
          {player.season_breakdown.length > 0 ? (
            <div className="player-list compact" role="list">
              {player.season_breakdown.map((season) => (
                <div className="player-list-row static" key={season.season} role="listitem">
                  <div>
                    <strong>{formatSeason(season.season)}</strong>
                    <span>{season.teams.join(", ") || "Team TBC"}</span>
                  </div>
                  <dl>
                    <div><dt>G</dt><dd>{season.goals}</dd></div>
                    <div><dt>A</dt><dd>{season.assists}</dd></div>
                    <div><dt>Apps</dt><dd>{season.appearances}</dd></div>
                    <div><dt>Starts</dt><dd>{season.starts}</dd></div>
                  </dl>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState message="No season breakdown is available for this player yet." />
          )}
        </section>

        <section className="panel">
          <ReportSectionHeader
            eyebrow="Recent involvement"
            title="Latest match evidence"
            text="The latest available match records show role, contribution, and discipline in one scan line."
          />
          {player.recent_matches.length > 0 ? (
            <div className="player-match-list">
              {player.recent_matches.map((match) => (
                <Link className="player-match-row" to={`/matches/${match.match_id}`} key={match.match_id}>
                  <div>
                    <strong>
                      {match.home_team ?? "Home"} {formatScoreline(match.home_score, match.away_score)} {match.away_team ?? "Away"}
                    </strong>
                    <span>{formatDate(match.match_date)} · {formatRole(match.squad_role)}</span>
                  </div>
                  <small>{match.goals} G · {match.assists} A · {match.yellow_cards + match.red_cards} cards</small>
                </Link>
              ))}
            </div>
          ) : (
            <EmptyState message="No recent match records are available for this player yet." />
          )}
        </section>
      </div>

      <section className="panel related-actions-panel">
        <ReportSectionHeader
          eyebrow="Next step"
          title="Follow the signal"
          text="Move from this player brief into the broader player pool, team context, or supporting match evidence."
        />
        <div className="match-detail-actions">
          <Link className="text-button" to="/players">Back to Players</Link>
          {primaryTeam ? (
            <Link className="text-button" to={`/teams/${getTeamSlug(primaryTeam)}`}>
              View {primaryTeam}
            </Link>
          ) : null}
          <Link className="text-button" to="/matches">
            View match briefs
          </Link>
        </div>
      </section>
    </article>
  );
}
