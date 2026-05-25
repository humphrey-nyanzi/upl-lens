import type { MatchSummary } from "../../api/types";
import { formatDate, matchStatus } from "../../utils/format";

export function MatchRow({ compact = false, match }: { compact?: boolean; match: MatchSummary }) {
  return (
    <article className={compact ? "match-row compact" : "match-row"}>
      <div>
        <span>
          {formatDate(match.match_date)}
          {match.match_day ? ` / MD ${match.match_day}` : ""}
        </span>
        <strong>
          {match.home_team ?? "Home team TBC"} vs {match.away_team ?? "Away team TBC"}
        </strong>
        {!compact && match.ground_name ? <p>{match.ground_name}</p> : null}
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
