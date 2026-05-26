import type { MatchSummary, SeasonOverviewResponse, SeasonResponse, TeamResponse } from "../../api/types";
import type { LoadState, PageKey } from "../../app/types";
import { formatDate } from "../../utils/format";
import { EmptyState } from "../common/EmptyState";
import { TopFiveCard, type TopFiveItem } from "../common/TopFiveCard";
import { MatchRow } from "../matches/MatchRow";

export function TeamSignalPanel({ teams, loadState }: { teams: TeamResponse[]; loadState: LoadState }) {
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
      page: "goal-timing" as PageKey,
      status: "Timing",
      title: "Goal window signal",
      description: "See which regular-time periods shape the scoring pattern.",
    },
    {
      page: "matches" as PageKey,
      status: "Evidence",
      title: "Recent match context",
      description: "Move from the overview into scorelines and match evidence.",
    },
    {
      page: "teams" as PageKey,
      status: "Teams",
      title: "Top-team preview",
      description: "Compare records and scoring summaries from cleaned match data.",
    },
  ];

  return (
    <section className="explore-panel" aria-labelledby="explore-title">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Insight strip</p>
          <h2 id="explore-title">What to inspect next</h2>
          <p>Three quick routes from the league overview into the evidence behind the numbers.</p>
        </div>
        <button className="text-button dark" type="button" onClick={() => onPageChange("goal-timing")}>
          View all insights
        </button>
      </div>
      <div className="explore-grid">
        {exploreCards.map((card) => (
          <button className="explore-card" key={card.title} type="button" onClick={() => onPageChange(card.page)}>
            <span>{card.status}</span>
            <strong>{card.title}</strong>
            <p>{card.description}</p>
          </button>
        ))}
      </div>
    </section>
  );
}

export function RecentMatchPanel({ matches, loadState }: { matches: MatchSummary[]; loadState: LoadState }) {
  return (
    <section className="panel">
      <div className="section-heading compact">
        <div>
          <h2>Recent matches</h2>
          <p>Latest scorelines for context around the season view.</p>
        </div>
      </div>
      <div className="match-list">
        {matches.length > 0 ? (
          matches.map((match) => <MatchRow key={match.match_id} match={match} />)
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
