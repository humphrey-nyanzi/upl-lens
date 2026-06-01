import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { apiClient, ApiRequestError } from "../api/client";
import type { PlayerDetailResponse } from "../api/types";
import type { PageProps } from "../app/types";
import { EmptyState } from "../components/common/EmptyState";
import { KpiCard } from "../components/common/KpiCard";
import { formatDate, formatScoreline } from "../utils/format";

function formatRole(role: string | null) {
  if (!role) return "Listed";
  return role.replace(/_/g, " ").replace(/\b\w/g, (character) => character.toUpperCase());
}

export default function PlayerDetailPage({ selectedSeason }: Pick<PageProps, "selectedSeason">) {
  const { playerSlug } = useParams();
  const [player, setPlayer] = useState<PlayerDetailResponse | null>(null);
  const [loadState, setLoadState] = useState<"loading" | "success" | "error">("loading");
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    if (!playerSlug) return;

    let ignore = false;
    setLoadState("loading");
    setErrorMessage("");

    apiClient
      .getPlayerDetail(playerSlug, selectedSeason)
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
            setErrorMessage("Player not found in the selected season data.");
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

  return (
    <article className="player-profile-page">
      <Link className="text-button" to="/players">Back to Players</Link>

      <header className="player-profile-hero">
        <p className="eyebrow">Player profile</p>
        <h1>{player.player_name}</h1>
        <p>{teams}</p>
      </header>

      <section className="metric-grid compact-metrics" aria-label="Player profile summary">
        <KpiCard accent="green" label="Goals" value={player.goals} context="Timeline goal events credited to this player." variant="compact" />
        <KpiCard accent="gold" label="Assists" value={player.assists} context="Assist events when available from the source timeline." variant="compact" />
        <KpiCard label="Appearances" value={player.appearances} context={`${player.starts} starts from lineup data.`} variant="compact" />
        <KpiCard label="Cards" value={cards} context={`${player.yellow_cards} yellow, ${player.red_cards} red.`} variant="compact" />
      </section>

      <div className="match-detail-lower-grid">
        <section className="panel">
          <div className="section-heading compact">
            <div>
              <h2>Season breakdown</h2>
              <p>Lineup and event totals grouped by season.</p>
            </div>
          </div>
          {player.season_breakdown.length > 0 ? (
            <div className="player-list compact" role="list">
              {player.season_breakdown.map((season) => (
                <div className="player-list-row static" key={season.season} role="listitem">
                  <div>
                    <strong>{season.season}</strong>
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
          <div className="section-heading compact">
            <div>
              <h2>Recent matches</h2>
              <p>Latest available match records tied to this player.</p>
            </div>
          </div>
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
    </article>
  );
}
