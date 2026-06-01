import type { MatchSummary, SeasonOverviewResponse, SeasonResponse, TeamResponse } from "../../api/types";
import type { LoadState, PageKey } from "../../app/types";
import { formatDate, formatScoreline, matchStatus } from "../../utils/format";
import { getTeamPoints } from "../../utils/teams";
import { EmptyState } from "../common/EmptyState";
import { TeamMarker } from "../common/TeamMarker";
import { Target, Home, TrendingUp, ArrowRight } from "lucide-react";

export function TeamSignalPanel({
  loadState,
  onPageChange,
  teams,
}: {
  loadState: LoadState;
  onPageChange: (page: PageKey) => void;
  teams: TeamResponse[];
}) {
  const rankingItems = teams.map((team) => {
    const points = getTeamPoints(team);
    const winRate = team.played_matches > 0 ? Math.round((team.wins / team.played_matches) * 100) : 0;
    const strength = Math.max(0, Math.min(5, Math.round((winRate / 100) * 5)));
    const dots = Array.from({ length: 5 }, (_, index) => index < strength);

    return {
      context: `${team.wins}W ${team.draws}D ${team.losses}L`,
      dots,
      id: team.team_name,
      label: team.team_name,
      points,
    };
  });

  return (
    <section className="panel overview-signal-card">
      <div className="section-heading compact overview-list-heading">
        <div>
          <p className="eyebrow">Team signals</p>
          <h2>Form guide</h2>
          <p>Season form signal.</p>
        </div>
      </div>
      <div className="overview-list">
        {rankingItems.length > 0 ? (
          rankingItems.slice(0, 5).map((item, index) => (
            <article className="overview-list-row signal" key={item.id}>
              <span className="overview-rank">{index + 1}</span>
              <TeamMarker className="overview-row-marker" label={item.label} size="small" />
              <strong>{item.label}</strong>
              <div className="overview-form-dots" aria-hidden="true">
                {item.dots.map((isActive, dotIndex) => (
                  <span className={isActive ? "active" : ""} key={dotIndex} />
                ))}
              </div>
              <span className="overview-points">{item.points} pts</span>
            </article>
          ))
        ) : (
          <EmptyState message={loadState === "loading" ? "Loading team rankings." : "No team rankings available yet."} />
        )}
      </div>
      <button className="text-button compact-result-link" type="button" onClick={() => onPageChange("teams")}>
        View full table
      </button>
    </section>
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
  const trendCards = [
    {
      icon: <Target size={24} />,
      page: "insights" as PageKey,
      title: "Featured insight",
      description: "Open curated football insights built from current FastAPI season data.",
      action: "Open insights",
    },
    {
      icon: <Home size={24} />,
      page: "matches" as PageKey,
      title: "Match evidence",
      description: "Review recent scorelines and match-by-match context behind overview signals.",
      action: "Open matches",
    },
    {
      icon: <TrendingUp size={24} />,
      page: "teams" as PageKey,
      title: "Team summaries",
      description: "Compare team form, results, and scoring output across the selected season.",
      action: "Open teams",
    },
  ];

  return (
    <section className="explore-panel overview-insight-strip" aria-labelledby="trends-title">
      <div className="section-heading compact overview-insight-heading">
        <div>
          <p className="eyebrow">Explore</p>
          <h2 id="trends-title">Where to go next</h2>
        </div>
      </div>
      <div className="trends-grid">
        {trendCards.map((card) => (
          <button
            className="trends-card"
            key={card.title}
            type="button"
            onClick={() => onPageChange(card.page)}
          >
            <div className="trends-card-icon" aria-hidden="true">
              {card.icon}
            </div>
            <div className="trends-card-content">
              <strong>{card.title}</strong>
              <p>{card.description}</p>
            </div>
            <div className="trends-card-action">
              <span>{card.action}</span>
              <ArrowRight size={16} />
            </div>
          </button>
        ))}
        <button
          className="trends-card trends-card-featured"
          type="button"
          onClick={() => onPageChange("insights")}
        >
          <div className="trends-card-icon featured" aria-hidden="true">
            <TrendingUp size={24} />
          </div>
          <div className="trends-card-featured-content">
            <strong>Dive deeper into the data</strong>
            <p>Move from this overview into dedicated pages for evidence, context, and analysis.</p>
            <div className="trends-card-action featured">
              <span>Explore Insights</span>
              <ArrowRight size={16} />
            </div>
          </div>
          <div className="trends-card-featured-graph" aria-hidden="true">
            <svg viewBox="0 0 200 100" preserveAspectRatio="none">
              <polyline
                points="0,80 20,70 40,75 60,50 80,55 100,30 120,35 140,20 160,25 180,10 200,15"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
        </button>
      </div>
    </section>
  );
}

function CompactResultRow({ match }: { match: MatchSummary }) {
  return (
    <article className="overview-list-row match">
      <span className="overview-date">{formatDate(match.match_date)}</span>
      <div className="overview-fixture-inline">
        <span className="overview-team-inline">
          <TeamMarker className="overview-row-marker" label={match.home_team} size="small" />
          <span>{match.home_team ?? "Home team TBC"}</span>
        </span>
        <span className="overview-inline-score">
          {formatScoreline(match.home_score, match.away_score)}
        </span>
        <span className="overview-team-inline away">
          <span>{match.away_team ?? "Away team TBC"}</span>
          <TeamMarker className="overview-row-marker" label={match.away_team} size="small" />
        </span>
      </div>
      <span className="overview-result">{matchStatus(match)}</span>
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
    <section className="panel overview-matches-card">
      <div className="section-heading compact overview-list-heading">
        <div>
          <p className="eyebrow">Recent matches</p>
          <h2>Recent matches</h2>
        </div>
      </div>
      <div className="overview-list">
        {matches.length > 0 ? (
          matches.map((match) => <CompactResultRow key={match.match_id} match={match} />)
        ) : (
          <EmptyState message={loadState === "loading" ? "Loading recent matches." : "No recent matches available yet."} />
        )}
      </div>
      <button className="text-button compact-result-link" type="button" onClick={() => onPageChange("matches")}>
        View all matches
      </button>
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
      <button className="text-button" type="button" onClick={() => onPageChange("about")}>
        Read data notes
      </button>
    </section>
  );
}
