import type { PageProps } from "../app/types";
import { PageIntro } from "../components/common/PageIntro";
import { StatusItem } from "../components/common/StatusItem";
import { formatDate } from "../utils/format";

export function MethodologyPage({ apiOnline, data, overview, selectedSeasonInfo }: PageProps) {
  return (
    <>
      <PageIntro
        eyebrow="Data notes"
        title="Methodology and freshness"
        text="The app is built from official UPL match pages. This page keeps source, freshness, and limitations visible without crowding the football overview."
      />
      <section className="overview-grid">
        <section className="panel">
          <div className="section-heading compact">
            <div>
              <h2>How the data is collected</h2>
              <p>
                Official UPL match pages are collected, cleaned into Postgres, checked for structural issues, then served
                through FastAPI to the React app.
              </p>
            </div>
          </div>
          <div className="trust-list">
            <StatusItem label="Source" value="Official UPL match pages" />
            <StatusItem label="App data path" value="Postgres to FastAPI to React" />
            <StatusItem label="Current status" value={apiOnline ? "Data service ready" : "Data service loading"} />
          </div>
        </section>

        <section className="panel">
          <div className="section-heading compact">
            <div>
              <h2>Freshness and coverage</h2>
              <p>These details help readers judge how recent and complete the current season view is.</p>
            </div>
          </div>
          <div className="trust-list">
            <StatusItem
              label="Last checked"
              value={data.health?.latest_staging_completed_at ? formatDate(data.health.latest_staging_completed_at) : "Unknown"}
            />
            <StatusItem
              label="Season window"
              value={
                selectedSeasonInfo
                  ? `${formatDate(overview?.first_match_date ?? selectedSeasonInfo.first_match_date)} to ${formatDate(
                      overview?.latest_match_date ?? selectedSeasonInfo.last_match_date,
                    )}`
                  : "Unavailable"
              }
            />
            <StatusItem
              label="Scoreline goals"
              value={overview?.scoreline_goal_count != null ? overview.scoreline_goal_count.toLocaleString() : "Unavailable"}
            />
          </div>
        </section>
      </section>

      <section className="panel">
        <div className="section-heading compact">
          <div>
            <h2>Known limitations</h2>
            <p>
              Scraped source data can be incomplete or change structure. Public numbers should be read with caveats when
              event timelines are missing, seasons are unusual, or validation finds a source anomaly.
            </p>
          </div>
        </div>
      </section>
    </>
  );
}
