import type { MatchSummary } from "../../api/types";
import { formatDate, matchStatus } from "../../utils/format";

export function MatchRow({ match }: { match: MatchSummary }) {
  return (
    <article className="match-row">
      <div>
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
    </article>
  );
}
