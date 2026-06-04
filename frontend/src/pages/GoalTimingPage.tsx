import type { PageProps } from "../app/types";
import { GoalTimingChart } from "../components/charts/GoalTimingChart";
import { PageIntro } from "../components/common/PageIntro";
import { formatPercent, formatSeasonScope } from "../utils/format";

function GoalTimingSkeleton() {
  return (
    <section className="featured-insight skeleton-card" aria-busy="true" aria-label="Loading goal timing">
      <div className="skeleton-line short" />
      <div className="skeleton-line title" />
      <div className="skeleton-line" />
      <div className="skeleton-line medium" />
    </section>
  );
}

export function GoalTimingPage({
  goalTiming,
  loadState,
}: PageProps) {
  const peakInterval = goalTiming?.intervals.find((interval) => interval.rank === 1);
  const secondHalfGoals =
    goalTiming?.intervals
      .filter((interval) => interval.start_minute >= 46)
      .reduce((total, interval) => total + interval.goals, 0) ?? 0;
  const secondHalfShare = goalTiming && goalTiming.total_regular_time_goals > 0 ? secondHalfGoals / goalTiming.total_regular_time_goals : 0;
  const scopeLabel = goalTiming ? formatSeasonScope(goalTiming.scope_key, goalTiming.season_count) : "the selected scope";

  return (
    <>
      <PageIntro
        eyebrow="Featured insight"
        title="Goal Timing"
        text="A fan-facing look at when UPL goals arrive, built from the first validated notebook insight promoted into the app."
      />

      {loadState === "loading" && !goalTiming ? <GoalTimingSkeleton /> : null}

      {goalTiming ? (
        <>
          <section className="feature-story goal-timing-summary">
            <div>
              <p className="eyebrow">Main finding</p>
              <h2>Goals cluster most in the {goalTiming.peak_interval ?? "available"} window.</h2>
              <p>
                The available regular-time event data shows {goalTiming.total_regular_time_goals.toLocaleString()} goals for{" "}
                {scopeLabel.toLowerCase()}. The strongest period accounts for{" "}
                {peakInterval ? `${peakInterval.goals.toLocaleString()} goals (${formatPercent(peakInterval.share)})` : "the clearest share"}.
              </p>
            </div>
            <div className="insight-stat">
              <span>Second-half share</span>
              <strong>{formatPercent(secondHalfShare)}</strong>
              <p>{secondHalfGoals.toLocaleString()} regular-time goals came after halftime.</p>
            </div>
          </section>

          <GoalTimingChart goalTiming={goalTiming} />

          <section className="overview-grid goal-timing-notes">
            <section className="panel">
              <div className="section-heading compact">
                <div>
                  <h2>How to read this</h2>
                  <p>
                    This is a period trend, not a tactical claim. It helps show when goals appear in the available match
                    timelines, then gives us a base for deeper team and match questions later.
                  </p>
                </div>
              </div>
            </section>
            <section className="panel">
              <div className="section-heading compact">
                <div>
                  <h2>Worth noting</h2>
                  <p>
                    Added-time goals are excluded from this comparison, and the chart only uses goals available in the
                    cleaned event timeline.
                  </p>
                </div>
              </div>
            </section>
          </section>
        </>
      ) : null}
    </>
  );
}
