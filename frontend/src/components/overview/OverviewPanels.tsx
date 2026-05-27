import type { MatchSummary, SeasonOverviewResponse, SeasonResponse, TeamResponse } from "../../api/types";
import type { LoadState, PageKey } from "../../app/types";
import { formatDate, matchStatus } from "../../utils/format";
import { EmptyState } from "../common/EmptyState";
import { TeamMarker } from "../common/TeamMarker";
import { TopFiveCard, type TopFiveItem } from "../common/TopFiveCard";

export function TeamSignalPanel({
  loadState,
  onPageChange,
  teams,
}: {
  loadState: LoadState;
  onPageChange: (page: PageKey) => void;
  teams: TeamResponse[];
}) {
  const rankingItems: TopFiveItem[] = teams.map((team) => {
    const points = team.wins * 3 + team.draws;
    const winRate = team.matches_played > 0 ? Math.round((team.wins / team.matches_played) * 100) : 0;

    return {
      context: `${team.wins}W ${team.draws}D ${team.losses}L - ${winRate}% wins`,
      id: team.team_name,
      label: team.team_name,
      value: points,
    };
  });

  return (
    <TopFiveCard
      emptyMessage={loadState === "loading" ? "Loading team rankings." : "No team rankings returned yet."}
      eyebrow="Top 5 teams"
      items={rankingItems}
      action={
        <button className="text-button top-five-link" type="button" onClick={() => onPageChange("teams")}>
          View team insights
        </button>
      }
      title="League leaders"
      valueLabel="By estimated points from cleaned team records."
    />
  );
}

export function EventSignalPanel({ eventBreakdown }: { eventBreakdown: Array<{ eventType: string; label: string; count: number }> }) {
  return (
    <section className="panel">
      <div className="section-heading compact">
        <div>
          <h2>Event coverage</h2>
          <p>Timeline signals available for the selected season.</p>
        </div>
      </div>
      <div className="breakdown-list">
        {eventBreakdown.length > 0 ? (
          eventBreakdown.slice(0, 6).map((item) => (
            <div className="breakdown-row" key={item.eventType}>
              <span>{item.label}</span>
              <strong>{item.count.toLocaleString()}</strong>
            </div>
          ))
        ) : (
          <EmptyState message="No event totals returned for this season yet." />
        )}
      </div>
    </section>
  );
}

export function ExplorePreview({ onPageChange }: { onPageChange: (page: PageKey) => void }) {
  const exploreCards = [
    {
      marker: "90",
      page: "goal-timing" as PageKey,
      status: "Timing",
      title: "Goal windows",
      description: "Find the scoring periods shaping this season.",
    },
    {
      marker: "FT",
      page: "matches" as PageKey,
      status: "Evidence",
      title: "Match evidence",
      description: "Check the scorelines behind the overview.",
    },
    {
      marker: "5",
      page: "teams" as PageKey,
      status: "Teams",
      title: "Team form",
      description: "Compare leaders from cleaned match records.",
    },
  ];

  return (
    <section className="explore-panel overview-insight-strip" aria-labelledby="explore-title">
      <div className="section-heading compact overview-insight-heading">
        <div>
          <p className="eyebrow">Next reads</p>
          <h2 id="explore-title">What to inspect next</h2>
        </div>
        <button className="text-button dark overview-insight-action" type="button" onClick={() => onPageChange("goal-timing")}>
          View all insights
        </button>
      </div>
      <div className="explore-grid overview-insight-grid">
        {exploreCards.map((card) => (
          <button className="explore-card overview-insight-card" key={card.title} type="button" onClick={() => onPageChange(card.page)}>
            <span className="overview-insight-marker" aria-hidden="true">
              {card.marker}
            </span>
            <div className="overview-insight-copy">
              <span>{card.status}</span>
              <strong>{card.title}</strong>
              <p>{card.description}</p>
            </div>
          </button>
        ))}
      </div>
    </section>
  );
}

function CompactResultRow({ match }: { match: MatchSummary }) {
  const homeScore = match.home_score ?? "-";
  const awayScore = match.away_score ?? "-";

  return (
    <article className="compact-result-row">
      <div className="compact-result-main">
        <span className="compact-result-meta">
          {formatDate(match.match_date)}
          {match.match_day ? ` · Matchday ${match.match_day}` : ""}
        </span>
        <strong className="compact-result-fixture">
          <span className="compact-result-team">
            <TeamMarker label={match.home_team} size="small" />
            <span>{match.home_team ?? "Home team TBC"}</span>
          </span>
          <span className="compact-result-separator">vs</span>
          <span className="compact-result-team">
            <TeamMarker label={match.away_team} size="small" />
            <span>{match.away_team ?? "Away team TBC"}</span>
          </span>
        </strong>
      </div>
      <div className="compact-result-score">
        <strong>
          {homeScore}:{awayScore}
        </strong>
        <span>{matchStatus(match)}</span>
      </div>
    </article>
  );
}

export function RecentMatchPanel({
  loadState,
  matches,
  onPageChange,
}: {
  loadState: LoadState;
  matches: MatchSummary[];
  onPageChange: (page: PageKey) => void;
}) {
  return (
    <section className="panel">
      <div className="section-heading compact">
        <div>
          <h2>Recent matches</h2>
          <p>Latest scorelines for context around the season view.</p>
        </div>
        <button className="text-button compact-result-link" type="button" onClick={() => onPageChange("matches")}>
          View all matches
        </button>
      </div>
      <div className="match-list">
        {matches.length > 0 ? (
          matches.map((match) => <CompactResultRow key={match.match_id} match={match} />)
        ) : (
          <EmptyState message={loadState === "loading" ? "Loading recent matches." : "No matches returned for this season yet."} />
        )}
      </div>
    </section>
  );
}

export function OverviewDataNote({
  onPageChange,
  selectedSeasonInfo,
  overview,
}: {
  onPageChange: (page: PageKey) => void;
  selectedSeasonInfo: SeasonResponse | undefined;
  overview: SeasonOverviewResponse | null;
}) {
  return (
    <section className="panel">
      <div className="section-heading compact">
        <div>
          <h2>Data note</h2>
          <p>
            This view uses official UPL match data. The selected season currently covers{" "}
            {selectedSeasonInfo
              ? `${formatDate(overview?.first_match_date ?? selectedSeasonInfo.first_match_date)} to ${formatDate(
                  overview?.latest_match_date ?? selectedSeasonInfo.last_match_date,
                )}`
              : "the available match window"}
            .
          </p>
        </div>
      </div>
      <button className="text-button" type="button" onClick={() => onPageChange("methodology")}>
        Read data notes
      </button>
    </section>
  );
}
