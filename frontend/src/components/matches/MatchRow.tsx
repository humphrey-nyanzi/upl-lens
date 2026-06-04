import type { MatchSummary } from "../../api/types";
import { formatDate } from "../../utils/format";
import { buildMatchBriefLead, getMatchBriefSignals } from "../../utils/matchBriefs";
import { Link } from "react-router-dom";
import { MatchFixtureLine, MatchStatusPill, StatusPill } from "../common/EditorialRows";

export function MatchRow({ match }: { match: MatchSummary }) {
  const signals = getMatchBriefSignals(match).slice(0, 3);
  const briefLead = buildMatchBriefLead(match);

  return (
    <article className="match-row">
      <div className="match-row-main">
        <span className="match-row-date">{formatDate(match.match_date)}</span>
        <MatchFixtureLine
          awayScore={match.away_score}
          awayTeam={match.away_team}
          homeScore={match.home_score}
          homeTeam={match.home_team}
          markerSize="medium"
        />
        <p className="match-row-lead">{briefLead}</p>
        {signals.length > 0 ? (
          <div className="match-row-signals" aria-label="Brief signals">
            {signals.map((signal) => (
              <StatusPill key={`${match.match_id}-${signal.key}`} tone={signal.tone} value={signal.label} />
            ))}
          </div>
        ) : null}
      </div>
      <div className="score-block">
        <MatchStatusPill match={match} />
      </div>
      <Link className="text-button match-row-link" to={`/matches/${match.match_id}`}>
        Open brief
      </Link>
    </article>
  );
}
