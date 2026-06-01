import { Link } from "react-router-dom";

import type { PageProps } from "../app/types";
import type { PlayerSummary } from "../api/types";
import { EmptyState } from "../components/common/EmptyState";
import { KpiCard } from "../components/common/KpiCard";
import { PageIntro } from "../components/common/PageIntro";

function sortPlayers(players: PlayerSummary[], metric: keyof Pick<PlayerSummary, "goals" | "assists" | "appearances" | "starts">) {
  return [...players].sort((left, right) => right[metric] - left[metric] || left.player_name.localeCompare(right.player_name));
}

function PlayerRankCard({ label, player, value }: { label: string; player: PlayerSummary | undefined; value: number }) {
  return (
    <article className="player-rank-card">
      <span>{label}</span>
      {player ? (
        <>
          <Link to={`/players/${player.player_slug}`}>{player.player_name}</Link>
          <strong>{value.toLocaleString()}</strong>
          <small>{player.primary_team ?? "Team TBC"}</small>
        </>
      ) : (
        <p>No player data yet.</p>
      )}
    </article>
  );
}

export function PlayersPage({ data, loadState, selectedSeason }: PageProps) {
  const players = data.players;
  const byGoals = sortPlayers(players, "goals");
  const byAssists = sortPlayers(players, "assists");
  const byAppearances = sortPlayers(players, "appearances");
  const byStarts = sortPlayers(players, "starts");
  const topPlayers = byGoals.slice(0, 30);

  return (
    <>
      <PageIntro
        eyebrow="Player profiles"
        title="Players"
        text="Browse the available UPL player records by goals, assists, appearances, starts, and cards from the cleaned API data."
      />

      <section className="metric-grid compact-metrics" aria-label="Player summary">
        <KpiCard label="Players tracked" value={players.length} context={`Distinct player profiles in ${selectedSeason || "the selected season"}.`} variant="compact" />
        <KpiCard accent="green" label="Top scorer" value={byGoals[0]?.goals ?? 0} context={byGoals[0]?.player_name ?? "No scorer data yet."} variant="compact" />
        <KpiCard accent="gold" label="Most appearances" value={byAppearances[0]?.appearances ?? 0} context={byAppearances[0]?.player_name ?? "No lineup data yet."} variant="compact" />
      </section>

      <section className="player-rank-grid" aria-label="Player leaderboard cards">
        <PlayerRankCard label="Goals" player={byGoals[0]} value={byGoals[0]?.goals ?? 0} />
        <PlayerRankCard label="Assists" player={byAssists[0]} value={byAssists[0]?.assists ?? 0} />
        <PlayerRankCard label="Appearances" player={byAppearances[0]} value={byAppearances[0]?.appearances ?? 0} />
        <PlayerRankCard label="Starts" player={byStarts[0]} value={byStarts[0]?.starts ?? 0} />
      </section>

      <section className="panel">
        <div className="section-heading">
          <div>
            <h2>Player list</h2>
            <p>Sorted by goals, then appearances. Click a player name to open their profile.</p>
          </div>
        </div>
        {topPlayers.length > 0 ? (
          <div className="player-list" role="list">
            {topPlayers.map((player) => (
              <Link className="player-list-row" to={`/players/${player.player_slug}`} key={player.player_slug} role="listitem">
                <div>
                  <strong>{player.player_name}</strong>
                  <span>{player.primary_team ?? player.teams[0] ?? "Team TBC"}</span>
                </div>
                <dl>
                  <div>
                    <dt>G</dt>
                    <dd>{player.goals}</dd>
                  </div>
                  <div>
                    <dt>A</dt>
                    <dd>{player.assists}</dd>
                  </div>
                  <div>
                    <dt>Apps</dt>
                    <dd>{player.appearances}</dd>
                  </div>
                  <div>
                    <dt>Starts</dt>
                    <dd>{player.starts}</dd>
                  </div>
                </dl>
              </Link>
            ))}
          </div>
        ) : (
          <EmptyState message={loadState === "loading" ? "Loading player summaries." : "No player summaries returned yet."} />
        )}
      </section>
    </>
  );
}
