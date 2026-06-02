import type { MatchSummary } from "../../api/types";
import { formatDate } from "../../utils/format";
import { Link } from "react-router-dom";
import { MatchFixtureLine, MatchStatusPill } from "../common/EditorialRows";

export function MatchRow({ match }: { match: MatchSummary }) {
  const adminNote = match.is_administrative_result
    ? match.administrative_note ?? "Result includes an administrative decision."
    : null;

  return (
    <article className="match-row">
      <div className="match-row-main">
        <span className="match-row-date">{formatDate(match.match_date)}</span>
        <MatchFixtureLine awayScore={match.away_score} awayTeam={match.away_team} homeScore={match.home_score} homeTeam={match.home_team} />
      </div>
      <div className="score-block">
        <MatchStatusPill match={match} />
        {adminNote ? <small>{adminNote}</small> : null}
      </div>
      <Link className="text-button match-row-link" to={`/matches/${match.match_id}`}>
        Open match
      </Link>
    </article>
  );
}
