import type { PageProps } from "../app/types";
import { GoalTimingChart } from "../components/charts/GoalTimingChart";
import { PageIntro } from "../components/common/PageIntro";
import { GoalTimingSkeleton } from "../components/common/Skeletons";
import { SeasonControls } from "../components/season/SeasonControls";
import { formatPercent } from "../utils/format";

export function GoalTimingPage({
  data,
  goalTiming,
  loadState,
  onRefresh,
  onSeasonChange,
  selectedSeason,
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
        text="A fan-facing look at when UPL goals arrive, built from the first validated notebook insight promoted into the app."
      >
        <SeasonControls
          seasons={data.seasons}
          selectedSeason={selectedSeason}
          loadState={loadState}
          onRefresh={onRefresh}
          onSeasonChange={onSeasonChange}
        />
      </PageIntro>

      {loadState === "loading" && !goalTiming ? <GoalTimingSkeleton /> : null}

      {goalTiming ? (
        <>
          <section className="feature-story">
            <div>
              <p className="eyebrow">Main finding</p>
              <h2>Goals cluster most in the {goalTiming.peak_interval ?? "available"} window.</h2>
              <p>
                The available regular-time event data shows {goalTiming.total_regular_time_goals.toLocaleString()} goals for
                this season. The strongest period accounts for{" "}
                {peakInterval ? `${peakInterval.goals.toLocaleString()} goals (${formatPercent(peakInterval.share)})` : "the clearest share"}.
              </p>
            </div>
            <div className="insight-stat">
              <span>Second-half share</span>
              <strong>{formatPercent(secondHalfShare)}</strong>
              <p>{secondHalfGoals.toLocaleString()} regular-time goals came after halftime.</p>
            </div>
          </section>

          <section className="featured-insight">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Explore the timing</p>
                <h2>Regular-time goals by 15-minute period</h2>
                <p>Each bar shows a readable period comparison. The peak period is highlighted and also labelled in text.</p>
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
