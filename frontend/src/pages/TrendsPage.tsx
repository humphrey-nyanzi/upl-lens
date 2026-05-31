import { useMemo } from "react";
import { CalendarRange, BarChartBig, Flag } from "lucide-react";

import type { PageProps } from "../app/types";
import { EmptyState } from "../components/common/EmptyState";
import { KpiCard } from "../components/common/KpiCard";
import { PageIntro } from "../components/common/PageIntro";
import { formatDate } from "../utils/format";

export function TrendsPage({ data, loadState }: PageProps) {
  const sortedSeasons = useMemo(() => {
    return [...data.seasons].sort((left, right) => right.season.localeCompare(left.season));
  }, [data.seasons]);

  const latestSeason = sortedSeasons[0];
  const earliestSeason = sortedSeasons.at(-1);
  const totalMatches = sortedSeasons.reduce((total, season) => total + season.match_count, 0);
  const averageMatches = sortedSeasons.length > 0 ? Math.round(totalMatches / sortedSeasons.length) : 0;

  return (
    <>
      <PageIntro
        eyebrow="Historical context"
        title="Trends"
        text="Season-level comparisons to keep current insights grounded in broader league context."
      />

      <section className="metric-grid compact-metrics" aria-label="Trends summary">
        <KpiCard
          accent="green"
          icon={<CalendarRange size={18} />}
          label="Seasons tracked"
          value={sortedSeasons.length}
          context={
            earliestSeason && latestSeason
              ? `${earliestSeason.season} to ${latestSeason.season}`
              : "Season range unavailable"
          }
          variant="compact"
        />
        <KpiCard
          accent="gold"
          icon={<BarChartBig size={18} />}
          label="Matches recorded"
          value={totalMatches}
          context="Total matches across available seasons."
          variant="compact"
        />
        <KpiCard
          icon={<Flag size={18} />}
          label="Average per season"
          value={averageMatches}
          context="Approximate match count per recorded season."
          variant="compact"
        />
      </section>

      <section className="panel">
        <div className="section-heading compact">
          <div>
            <h2>Season snapshots</h2>
            <p>Quick view of coverage and known date windows from currently loaded season metadata.</p>
          </div>
        </div>

        {sortedSeasons.length > 0 ? (
          <div className="breakdown-list">
            {sortedSeasons.map((season) => (
              <article className="breakdown-row" key={season.season}>
                <strong>{season.season}</strong>
                <span>
                  {season.match_count.toLocaleString()} matches · {season.team_count.toLocaleString()} teams ·{" "}
                  {formatDate(season.first_match_date)} to {formatDate(season.last_match_date)}
                </span>
              </article>
            ))}
          </div>
        ) : (
          <EmptyState
            message={loadState === "loading" ? "Loading season trend summaries." : "No season trend data available yet."}
          />
        )}
      </section>
    </>
  );
}
