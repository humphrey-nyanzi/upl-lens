import { Link } from "react-router-dom";

import type { PageProps } from "../app/types";
import { EditorialTable, EditorialTableHeader } from "../components/common/EditorialTable";
import type { PlayerSummary } from "../api/types";
import { EmptyState } from "../components/common/EmptyState";
import { KpiCard } from "../components/common/KpiCard";
import { PageIntro } from "../components/common/PageIntro";
import { TeamName } from "../components/common/EditorialRows";
import { PlayerRow } from "../components/players/PlayerRow";

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
          <TeamName className="player-rank-team" label={player.primary_team ?? "Team TBC"} size="small" />
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
        text="Browse the available UPL player records with a clearer hierarchy for production, contribution, and team context."
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
            <p>Sorted by goals, then appearances. Desktop reads like a compact table; mobile collapses into player cards.</p>
          </div>
        </div>
        {topPlayers.length > 0 ? (
          <EditorialTable className="player-table-shell">
            <EditorialTableHeader
              className="player-table-header"
              columns={[
                { label: "Player" },
                { align: "right", label: "Goals" },
                { align: "right", label: "Assists" },
                { align: "right", label: "Apps" },
                { align: "right", label: "Starts" },
              ]}
            />
            <div className="player-list player-table-list" role="list">
              {topPlayers.map((player) => (
                <PlayerRow key={player.player_slug} player={player} />
              ))}
            </div>
          </EditorialTable>
        ) : (
          <EmptyState message={loadState === "loading" ? "Loading player summaries." : "No player summaries returned yet."} />
        )}
      </section>
    </>
  );
}
