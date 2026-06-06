import { Link } from "react-router-dom";

import type { PlayerSummary } from "../../api/types";
import { StatCell, TeamName } from "../common/EditorialRows";
import { SignalChipGroup } from "../intelligence";
import type { SignalTone } from "../intelligence/SignalChip";

function formatShare(value: number | null) {
  if (value === null || value === undefined) return "Starts share unavailable";
  return `${Math.round(value * 100)}% starts share`;
}

export function PlayerRow({ player }: { player: PlayerSummary }) {
  const teamLabel = player.primary_team ?? player.teams[0] ?? "Team TBC";
  const cardsLabel =
    player.cards > 0
      ? `${player.yellow_cards}Y · ${player.red_cards}R`
      : "No cards in available data";
  const labels = player.profile_labels.map((label) => ({
    key: label.key,
    label: label.label,
    tone: label.tone as SignalTone,
  }));

  return (
    <Link className="player-list-row editorial-table-row" to={`/players/${player.player_slug}`} role="listitem">
      <div className="player-row-identity">
        <strong>{player.player_name}</strong>
        <TeamName className="player-row-team" label={teamLabel} size="small" />
        <span>{player.teams.length > 1 ? player.teams.join(", ") : formatShare(player.starts_share)}</span>
        <SignalChipGroup emptyLabel="No contribution labels yet" items={labels} maxVisible={3} size="small" />
      </div>
      <div className="player-row-stats">
        <StatCell label="Goals" value={player.goals} />
        <StatCell label="Assists" value={player.assists} />
        <StatCell label="Apps" value={player.appearances} />
        <StatCell label="Starts" value={player.starts} />
        <StatCell label="G+A" value={player.goal_contributions} />
        <StatCell label="Cards" value={cardsLabel} />
      </div>
    </Link>
  );
}
