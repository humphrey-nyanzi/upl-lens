import type { MatchSummary } from "../../api/types";
import { formatDate, matchStatus } from "../../utils/format";
import { Link } from "react-router-dom";

export function MatchRow({ match }: { match: MatchSummary }) {
  return (
    <article className="match-row">
      <div className="match-row-main">
        <span>{formatDate(match.match_date)}</span>
        <strong>
          {match.home_team ?? "Home team TBC"} vs {match.away_team ?? "Away team TBC"}
        </strong>
      </div>
      <div className="score-block">
        <strong>
          {match.home_score ?? "-"}:{match.away_score ?? "-"}
        </strong>
        <span>{matchStatus(match)}</span>
      </div>
      <Link className="text-button match-row-link" to={`/matches/${match.match_id}`}>
        Open match
      </Link>
    </article>
  );
}
