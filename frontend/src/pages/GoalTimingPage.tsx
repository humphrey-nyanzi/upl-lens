import type { PageProps } from "../app/types";
import { GoalTimingChart } from "../components/charts/GoalTimingChart";
import { KpiCard } from "../components/common/KpiCard";
import { PageIntro } from "../components/common/PageIntro";
import { GoalTimingSkeleton } from "../components/common/Skeletons";
import { formatPercent } from "../utils/format";

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

  return (
    <>
      <PageIntro
        eyebrow="Featured insight"
        title="Goal Timing"
        text="The flagship insight: when regular-time UPL goals arrive, where the scoring pressure rises, and what to read with caution."
      />

      {loadState === "loading" && !goalTiming ? <GoalTimingSkeleton /> : null}

      {goalTiming ? (
        <>
          <section className="feature-story insight-hero">
            <div>
              <p className="eyebrow">Main finding</p>
              <h2>Goals cluster most in the {goalTiming.peak_interval ?? "available"} window.</h2>
              <p>
                The available regular-time event data shows {goalTiming.total_regular_time_goals.toLocaleString()} goals for this season.
                The strongest period accounts for{" "}
                {peakInterval ? `${peakInterval.goals.toLocaleString()} goals (${formatPercent(peakInterval.share)})` : "the clearest share"}.
              </p>
            </div>
            <KpiCard
              accent="gold"
              label="Second-half share"
              value={formatPercent(secondHalfShare)}
              detail={`${secondHalfGoals.toLocaleString()} regular-time goals came after halftime.`}
            />
          </section>

          <section className="featured-insight chart-panel">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Explore the timing</p>
                <h2>Goal timing heatmap</h2>
                <p>Each tile shows a 15-minute scoring window. The peak period is highlighted and also labelled in text.</p>
              </div>
            </div>
            <GoalTimingChart goalTiming={goalTiming} />
          </section>

          <section className="overview-grid">
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
