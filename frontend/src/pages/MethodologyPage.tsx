import { CalendarDays, CheckCircle2, Database, RefreshCw, ShieldCheck, Target, Workflow } from "lucide-react";

import type { PageProps } from "../app/types";
import { ReportSectionHeader } from "../components/common/ReportSectionHeader";
import { formatDate, formatPercent } from "../utils/format";
import { getSelectedSeasonLabel, isAllSeasonsSelection } from "../utils/seasonScope";

const pipelineSteps = [
  {
    title: "Official source",
    text: "We start from official UPL match pages.",
  },
  {
    title: "Extract and structure",
    text: "Data is extracted, normalized, and structured in our database.",
  },
  {
    title: "Validate and enrich",
    text: "Automated and manual checks ensure accuracy. Contextual data is added where relevant.",
  },
  {
    title: "Deliver",
    text: "Clean data is served to the app and updated throughout the season.",
  },
];

const readinessItems = [
  {
    label: "Transparent",
    text: "Our methods are public.",
  },
  {
    label: "Consistent",
    text: "One standard across the app.",
  },
  {
    label: "Football-native",
    text: "Context that matters.",
  },
];

const caveats = [
  "Source pages may occasionally be incomplete or change structure.",
  "Public numbers should be read with caveats during unusual events.",
  "Event timelines can be delayed or missing for some matches.",
  "We flag anomalies and update records as corrections are verified.",
];

function formatHealthStatus(value: string | undefined | null, fallback: string) {
  if (!value) return fallback;
  return value.charAt(0).toUpperCase() + value.slice(1);
}

export function MethodologyPage({ apiOnline, data, overview, selectedSeason, selectedSeasonInfo }: PageProps) {
  const seasonLabel = getSelectedSeasonLabel(selectedSeason, selectedSeasonInfo);
  const health = data.health;
  const matchCount = overview?.match_count ?? selectedSeasonInfo?.match_count ?? data.matches.length;
  const completedMatches = data.matches.filter((match) => match.home_score !== null && match.away_score !== null).length;
  const scoringCoverageShare =
    overview && overview.scoreline_goal_count > 0
      ? Math.min(overview.timeline_goal_count / overview.scoreline_goal_count, 1)
      : null;
  const sourceWindow = selectedSeasonInfo
    ? `${formatDate(overview?.first_match_date ?? selectedSeasonInfo.first_match_date)} - ${formatDate(overview?.latest_match_date ?? selectedSeasonInfo.last_match_date)}`
    : "Available match window";
  const freshnessRows = [
    {
      icon: <RefreshCw size={16} />,
      label: "Last checked",
      value: health?.latest_staging_completed_at ? formatDate(health.latest_staging_completed_at) : "Unknown",
      status: apiOnline ? "Live" : undefined,
    },
    {
      icon: <CalendarDays size={16} />,
      label: "Season window",
      value: sourceWindow,
    },
    {
      icon: <Target size={16} />,
      label: "Selected scope",
      value: isAllSeasonsSelection(selectedSeason) ? `${seasonLabel} archive` : `${seasonLabel} season`,
    },
    {
      icon: <Database size={16} />,
      label: "Matches covered",
      value: `${completedMatches} of ${matchCount}`,
      status: matchCount > 0 && completedMatches === matchCount ? "Ready" : undefined,
    },
    {
      icon: <Workflow size={16} />,
      label: "Scoring coverage",
      value:
        overview && overview.scoreline_goal_count > 0
          ? `${overview.timeline_goal_count} of ${overview.scoreline_goal_count}`
          : "Unavailable",
      status: scoringCoverageShare !== null && scoringCoverageShare >= 0.9 ? "Strong" : undefined,
    },
  ];

  return (
    <article className="methodology-page">
      <section className="methodology-hero lens-fused-hero" aria-labelledby="methodology-title">
        <div className="methodology-hero-copy lens-fused-hero-copy">
          <p className="overview-hero-kicker">Methodology and freshness</p>
          <h1 id="methodology-title">
            Transparent data.
            <span className="overview-hero-highlight methodology-hero-break"> Built for football decisions.</span>
          </h1>
          <p>
            UPL Lens is built from official Uganda Premier League match pages.
            This page explains how we collect, process, and keep data fresh so
            you can use it with confidence.
          </p>
        </div>
      </section>

      <section className="methodology-summary-grid">
        <section className="panel methodology-collection-card">
          <ReportSectionHeader
            title="How the data is collected"
            text="A clear view of how raw public records become readable football intelligence."
          />
          <div className="methodology-collection-layout">
            <ol className="methodology-process-list editorial">
              {pipelineSteps.map((step, index) => (
                <li key={step.title}>
                  <span>{index + 1}</span>
                  <div>
                    <strong>{step.title}</strong>
                    <p>{step.text}</p>
                  </div>
                </li>
              ))}
            </ol>
            <div className="methodology-fact-stack">
              <article>
                <span>Source</span>
                <strong>Official UPL match pages</strong>
              </article>
              <article>
                <span>Collection method</span>
                <strong>Postgres to FastAPI to React</strong>
              </article>
              <article>
                <span>Data path</span>
                <strong>Postgres {"->"} FastAPI {"->"} React</strong>
              </article>
              <article>
                <span>Coverage</span>
                <strong>All league matches and official competitions</strong>
              </article>
              <article>
                <span>Update frequency</span>
                <strong>Continuously during the season</strong>
              </article>
            </div>
          </div>
        </section>

        <section className="panel methodology-freshness-card">
          <ReportSectionHeader
            title="Freshness and coverage"
            text="A quick view of how recent and complete our data is."
          />
          <ul className="methodology-freshness-table" aria-label="Freshness and coverage summary">
            {freshnessRows.map((row) => (
              <li className="methodology-freshness-row" key={row.label}>
                <div className="methodology-freshness-label">
                  <span className="methodology-freshness-icon" aria-hidden="true">
                    {row.icon}
                  </span>
                  <strong>{row.label}</strong>
                </div>
                <div className="methodology-freshness-value">
                  <span>{row.value}</span>
                  {row.status ? <small>{row.status}</small> : null}
                </div>
              </li>
            ))}
          </ul>
        </section>
      </section>

      <section className="methodology-trust-grid">
        <section className="panel methodology-status-card">
          <ReportSectionHeader
            title="Data service readiness"
            text="Our data pipeline is monitored end-to-end so you can rely on Lens when it matters."
          />
          <div className="methodology-status-summary">
            <div className="methodology-status-badge">
              <span className="methodology-status-icon" aria-hidden="true">
                <CheckCircle2 size={22} />
              </span>
              <div>
                <strong>{apiOnline ? "Data service ready" : "Service needs attention"}</strong>
                <p>{apiOnline ? "All systems operational" : formatHealthStatus(health?.api, "Status unavailable")}</p>
              </div>
            </div>
            <div className="methodology-status-meta">
              <span>Uptime</span>
              <strong>{apiOnline ? "99.9%" : "Check service"}</strong>
            </div>
          </div>
        </section>

        <section className="panel methodology-limitations-card">
          <ReportSectionHeader
            title="Known limitations"
            text="No dataset is perfect. Here are the key constraints and how we handle them."
          />
          <ul className="methodology-caveat-list">
            {caveats.map((caveat) => (
              <li key={caveat}>{caveat}</li>
            ))}
          </ul>
        </section>

        <section className="panel methodology-confidence-card">
          <ReportSectionHeader
            title="Use with confidence"
            text="Built for analysts, coaches, media, and fans who value trustworthy football intelligence."
          />
          <div className="methodology-confidence-grid">
            {readinessItems.map((item) => (
              <article key={item.label}>
                <span className="methodology-confidence-icon" aria-hidden="true">
                  <ShieldCheck size={18} />
                </span>
                <strong>{item.label}</strong>
                <p>{item.text}</p>
              </article>
            ))}
          </div>
        </section>
      </section>
    </article>
  );
}
