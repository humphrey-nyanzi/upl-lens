import type { MatchSummary } from "../../api/types";
import { formatDate, formatScoreline, matchStatus } from "../../utils/format";
import { Link } from "react-router-dom";
import { TeamMarker } from "../common/TeamMarker";

export function MatchRow({ match }: { match: MatchSummary }) {
  const homeTeam = match.home_team ?? "Home team TBC";
  const awayTeam = match.away_team ?? "Away team TBC";
  const adminNote = match.is_administrative_result
    ? match.administrative_note ?? "Result includes an administrative decision."
    : null;

  return (
    <article className="match-row">
      <div className="match-row-main">
        <span className="match-row-date">{formatDate(match.match_date)}</span>
        <div className="match-row-fixture">
          <span className="match-row-team">
            <TeamMarker label={homeTeam} size="small" />
            <strong>{homeTeam}</strong>
          </span>
          <strong className="match-row-scoreline">{formatScoreline(match.home_score, match.away_score)}</strong>
          <span className="match-row-team away">
            <strong>{awayTeam}</strong>
            <TeamMarker label={awayTeam} size="small" />
          </span>
        </div>
      </div>
      <div className="score-block">
        <span>{matchStatus(match)}</span>
        {adminNote ? <small>{adminNote}</small> : null}
      </div>
      <Link className="text-button match-row-link" to={`/matches/${match.match_id}`}>
        Open match
      </Link>
    </article>
  );
}
