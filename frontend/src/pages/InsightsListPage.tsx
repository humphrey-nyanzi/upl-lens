import { Link } from "react-router-dom";
import { ArrowRight, BookOpen, Clock3, LineChart, NotebookPen, ShieldCheck, SlidersHorizontal } from "lucide-react";

import type { PageProps } from "../app/types";
import { EmptyState } from "../components/common/EmptyState";
import { KpiCard } from "../components/common/KpiCard";
import { PageIntro } from "../components/common/PageIntro";
import { formatPercent, formatSeasonScope } from "../utils/format";

export function InsightsListPage({ featuredGoalTiming, loadState }: PageProps) {
  const intervalCount = featuredGoalTiming?.intervals.length ?? 0;
  const peakShare = featuredGoalTiming?.intervals.find((interval) => interval.rank === 1)?.share ?? null;
  const scopeLabel = featuredGoalTiming
    ? formatSeasonScope(featuredGoalTiming.scope_key, featuredGoalTiming.season_count)
    : "Featured scope unavailable";

  return (
    <>
      <PageIntro
        eyebrow="Promoted analysis"
        title="Insights Library"
        text="Curated football intelligence, promoted from validated research and framed so readers can move from one strong finding into deeper league context."
      />

      <section className="metric-grid compact-metrics" aria-label="Insight library summary">
        <KpiCard
          accent="green"
          label="Published insights"
          value={featuredGoalTiming ? 1 : 0}
          context="Goal Timing is the current promoted insight."
          variant="compact"
        />
        <KpiCard
          accent="gold"
          label="Peak window share"
          value={peakShare !== null ? formatPercent(peakShare) : "N/A"}
          context="Top regular-time scoring share from the featured insight scope."
          variant="compact"
        />
        <KpiCard
          label="Intervals analysed"
          value={intervalCount}
          context="Regular-time windows available for this insight."
          variant="compact"
        />
      </section>

      {featuredGoalTiming ? (
        <>
          <section className="insights-library-hero" aria-label="Featured insight">
            <article className="trends-card trends-card-featured insights-library-feature">
              <div className="trends-card-featured-content">
                <div className="insight-feature-topline">
                  <span className="eyebrow">Current promoted insight</span>
                  <span className="insight-feature-scope">{scopeLabel}</span>
                </div>
                <div className="trends-card-icon" aria-hidden="true">
                  <LineChart size={18} />
                </div>
                <strong>Goal Timing</strong>
                <p>
                  Review when goals arrive across the featured insight scope, which regular-time windows carry the heaviest
                  scoring share, and how that timing trend can guide deeper team and match questions.
                </p>
                <div className="insight-feature-stat-grid" aria-label="Goal timing highlights">
                  <div className="insight-feature-stat">
                    <span>Peak window</span>
                    <strong>{featuredGoalTiming.peak_interval ?? "Unavailable"}</strong>
                  </div>
                  <div className="insight-feature-stat">
                    <span>Peak share</span>
                    <strong>{peakShare !== null ? formatPercent(peakShare) : "N/A"}</strong>
                  </div>
                  <div className="insight-feature-stat">
                    <span>Intervals</span>
                    <strong>{intervalCount}</strong>
                  </div>
                </div>
                <div className="insight-feature-actions">
                  <Link className="text-button" to="/insights/goal-timing">
                    Open insight <ArrowRight size={14} aria-hidden="true" />
                  </Link>
                  <Link className="text-button subtle" to="/trends">
                    Compare league trends
                  </Link>
                </div>
              </div>
              <div className="trends-card-featured-graph" aria-hidden="true">
                <LineChart size={160} />
              </div>
            </article>

            <div className="insights-library-side">
              <article className="panel insight-support-card">
                <div className="insight-support-icon" aria-hidden="true">
                  <ShieldCheck size={18} />
                </div>
                <div className="insight-support-copy">
                  <strong>Why this library matters</strong>
                  <p>
                    Each entry is meant to move past match records and show a football question, the evidence behind
                    it, and the season context that shapes the finding.
                  </p>
                </div>
              </article>
              <article className="panel insight-support-card">
                <div className="insight-support-icon" aria-hidden="true">
                  <SlidersHorizontal size={18} />
                </div>
                <div className="insight-support-copy">
                  <strong>Read, then explore</strong>
                  <p>
                    The featured cards frame the key takeaway first. Open an insight to inspect the chart, method
                    notes, and selected-season context in more detail.
                  </p>
                </div>
              </article>
            </div>
          </section>

          <section className="panel">
            <div className="section-heading compact">
              <div>
                <h2>Library shelf</h2>
                <p>Start with the promoted report, then use the surrounding context cards to understand how to read it.</p>
              </div>
            </div>

            <div className="insight-library-shelf">
              <article className="surface-muted insight-library-card">
                <div className="insight-library-icon" aria-hidden="true">
                  <LineChart size={18} />
                </div>
                <div className="insight-library-copy">
                  <strong>Goal Timing</strong>
                  <p>
                    Understand when goals are scored across the current featured insight scope and which windows carry the strongest
                    scoring signal.
                  </p>
                  <div className="insight-library-meta">
                    <span>
                      <Clock3 size={13} aria-hidden="true" /> {scopeLabel}
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

              <article className="surface-muted insight-library-note">
                <div className="insight-library-note-icon" aria-hidden="true">
                  <NotebookPen size={18} />
                </div>
                <div>
                  <strong>Method and caveats</strong>
                  <p>
                    This insight uses validated goal-event windows from the API. Added-time handling and timeline
                    completeness are explained on the detail page.
                  </p>
                </div>
              </article>

              <article className="surface-muted insight-library-note">
                <div className="insight-library-note-icon" aria-hidden="true">
                  <BookOpen size={18} />
                </div>
                <div>
                  <strong>More promoted work will appear here</strong>
                  <p>
                    As more research questions graduate into product-ready analyses, this shelf will expand without
                    changing the reading pattern.
                  </p>
                </div>
              </article>
            </div>
          </section>
        </>
      ) : (
        <section className="panel">
          <div className="section-heading compact">
            <div>
              <h2>Available insights</h2>
              <p>Open each insight to review method, chart evidence, and season context.</p>
            </div>
          </div>
              <EmptyState
            message={
              loadState === "loading"
                ? "Loading insights for the current scope."
                : "No promoted insights are available for this scope yet."
            }
          />
        </section>
      )}
    </>
  );
}
