import { Link } from "react-router-dom";
import { BookOpen, Clock3, LineChart } from "lucide-react";

import type { PageProps } from "../app/types";
import { EmptyState } from "../components/common/EmptyState";
import { KpiCard } from "../components/common/KpiCard";
import { PageIntro } from "../components/common/PageIntro";
import { formatPercent } from "../utils/format";

export function InsightsListPage({ goalTiming, loadState, selectedSeason }: PageProps) {
  const intervalCount = goalTiming?.intervals.length ?? 0;
  const peakShare = goalTiming?.intervals.find((interval) => interval.rank === 1)?.share ?? null;

  return (
    <>
      <PageIntro
        eyebrow="Promoted analysis"
        title="Insights Library"
        text="Curated football analyses promoted from validated research and backed by FastAPI season data."
      />

      <section className="metric-grid compact-metrics" aria-label="Insight library summary">
        <KpiCard
          accent="green"
          label="Published insights"
          value={goalTiming ? 1 : 0}
          context="Goal Timing is the current promoted insight."
          variant="compact"
        />
        <KpiCard
          accent="gold"
          label="Peak window share"
          value={peakShare !== null ? formatPercent(peakShare) : "N/A"}
          context="Top regular-time scoring share from the selected season."
          variant="compact"
        />
        <KpiCard
          label="Intervals analysed"
          value={intervalCount}
          context="Regular-time windows available for this insight."
          variant="compact"
        />
      </section>

      <section className="panel">
        <div className="section-heading compact">
          <div>
            <h2>Available insights</h2>
            <p>Open each insight to review method, chart evidence, and season context.</p>
          </div>
        </div>

        {goalTiming ? (
          <article className="surface-muted insight-library-card">
            <div className="insight-library-icon" aria-hidden="true">
              <LineChart size={18} />
            </div>
            <div className="insight-library-copy">
              <strong>Goal Timing</strong>
              <p>
                Understand when goals are scored in the selected season and which windows carry the strongest scoring signal.
              </p>
              <div className="insight-library-meta">
                <span>
                  <Clock3 size={13} aria-hidden="true" /> Season {selectedSeason}
                </span>
                <span>
                  <BookOpen size={13} aria-hidden="true" /> Promoted insight
                </span>
              </div>
            </div>
            <Link className="text-button" to="/insights/goal-timing">
              Open insight
            </Link>
          </article>
        ) : (
          <EmptyState
            message={
              loadState === "loading"
                ? "Loading insights for the selected season."
                : "No promoted insights are available for this season yet."
            }
          />
        )}
      </section>
    </>
  );
}
