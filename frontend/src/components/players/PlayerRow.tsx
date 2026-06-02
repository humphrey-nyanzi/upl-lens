import { Link } from "react-router-dom";

import type { PlayerSummary } from "../../api/types";
import { StatCell, TeamName } from "../common/EditorialRows";

export function PlayerRow({ player }: { player: PlayerSummary }) {
  const teamLabel = player.primary_team ?? player.teams[0] ?? "Team TBC";

  return (
    <Link className="player-list-row editorial-table-row" to={`/players/${player.player_slug}`} role="listitem">
      <div className="player-row-identity">
        <strong>{player.player_name}</strong>
        <TeamName className="player-row-team" label={teamLabel} size="small" />
      </div>
      <div className="player-row-stats">
        <StatCell label="Goals" value={player.goals} />
        <StatCell label="Assists" value={player.assists} />
        <StatCell label="Apps" value={player.appearances} />
        <StatCell label="Starts" value={player.starts} />
      </div>
    </Link>
  );
}
