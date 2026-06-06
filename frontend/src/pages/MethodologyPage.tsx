import { Github, Newspaper, Twitter } from "lucide-react";

import type { PageProps } from "../app/types";
import { PageIntro } from "../components/common/PageIntro";
import { ReportSectionHeader } from "../components/common/ReportSectionHeader";
import { DataQualityNote, MetricDelta, SignalChipGroup, type SignalChipItem } from "../components/intelligence";
import { formatDate } from "../utils/format";
import { getSelectedSeasonLabel, isAllSeasonsSelection } from "../utils/seasonScope";

const boundaryChips: SignalChipItem[] = [
  { key: "source-record", label: "Official site: source record", tone: "neutral" },
  { key: "meaning-layer", label: "UPL Lens: analytical layer", tone: "positive" },
  { key: "independent", label: "Independent product", tone: "warning" },
];

const pipelineSteps = [
  {
    title: "Official UPL match pages",
    text: "Public match records provide the source material. The official website remains the archive.",
  },
  {
    title: "Cleaned data store",
    text: "Collected records are stored, cleaned, normalized, and checked before they become public-facing summaries.",
  },
  {
    title: "Analytical summaries",
    text: "Reusable football questions are shaped into match, team, player, season, and data-quality signals.",
  },
  {
    title: "FastAPI and React",
    text: "The frontend consumes typed API responses, then presents the evidence as briefs, profiles, trends, and insights.",
  },
];

const transforms = [
  {
    title: "Match results",
    text: "become match intelligence briefs with scoring, late-goal, discipline, and evidence-quality signals.",
  },
  {
    title: "Team records",
    text: "become attack, defence, points, form, home-away, and caveat profiles.",
  },
  {
    title: "Event timelines",
    text: "become key moments, score progression, scoring timing, and phase summaries where coverage allows.",
  },
  {
    title: "Season records",
    text: "become trends for scoring, cards, result balance, and data coverage across available seasons.",
  },
  {
    title: "Player records",
    text: "become contribution summaries across goals, assists, appearances, starts, and discipline.",
  },
];

const qualityStates: SignalChipItem[] = [
  { key: "publishable", label: "Publishable", tone: "positive", description: "The record is usable in public summaries." },
  {
    key: "publishable-caveat",
    label: "Publishable with caveat",
    tone: "warning",
    description: "The record is useful, but source or coverage limitations should stay visible.",
  },
  {
    key: "blocked",
    label: "Blocked from public display",
    tone: "risk",
    description: "The record should not be promoted until the source issue is resolved.",
  },
];

const caveats = [
  "Source pages can change after they are first collected.",
  "Some match timelines may be incomplete or unavailable.",
  "Timeline goals and final scoreline goals can differ when event coverage is partial.",
  "Player data depends on available lineups, events, and source naming consistency.",
  "Administrative results and source anomalies are treated as caveated records.",
  "Event-based charts should be read with coverage in mind.",
];

const contactLinks = [
  { href: "https://github.com/humphrey-nyanzi", icon: <Github size={16} />, label: "GitHub" },
  { href: "https://humphreyn-substack.com", icon: <Newspaper size={16} />, label: "Substack" },
  { href: "https://x.com/phreyn", icon: <Twitter size={16} />, label: "X" },
];

function formatHealthStatus(value: string | undefined | null, fallback: string) {
  if (!value) return fallback;
  return value.charAt(0).toUpperCase() + value.slice(1);
}

export function MethodologyPage({ apiOnline, data, overview, selectedSeason, selectedSeasonInfo }: PageProps) {
  const seasonLabel = getSelectedSeasonLabel(selectedSeason, selectedSeasonInfo);
  const scopeNoun = isAllSeasonsSelection(selectedSeason) ? "archive view" : "season view";
  const health = data.health;

  return (
    <article className="methodology-page">
      <PageIntro
        eyebrow="Trust and methodology"
        title="About UPL Lens"
        text="UPL Lens is an independent football intelligence product that turns publicly available Uganda Premier League match records into statistical summaries, visual comparisons, and analytical features."
      >
        <SignalChipGroup items={boundaryChips} maxVisible={3} />
      </PageIntro>

      <section className="panel methodology-boundary-panel">
        <ReportSectionHeader
          title="Source record vs intelligence layer"
          text="UPL Lens is not the official UPL website. It uses public source pages as evidence, then adds patterns, comparisons, signals, and caveats that are harder to see from source pages alone."
        />
        <div className="methodology-boundary-grid">
          <article>
            <span>Official UPL website</span>
            <strong>Source record</strong>
            <p>The official site remains the archive for fixtures, match records, and source pages.</p>
          </article>
          <article>
            <span>UPL Lens</span>
            <strong>Analytical meaning layer</strong>
            <p>This app focuses on football intelligence, comparisons, trends, and transparent data caveats.</p>
          </article>
        </div>
      </section>

      <section className="panel">
        <ReportSectionHeader title="How source data becomes public intelligence" text="The process is deliberately simple to read, even though the underlying checks are more detailed." />
        <ol className="methodology-process-list">
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
      </section>

      <section className="panel">
        <ReportSectionHeader title="What the app transforms" text="The product is designed to add analytical meaning, not to recreate the official archive." />
        <div className="methodology-transform-grid">
          {transforms.map((item) => (
            <article key={item.title}>
              <strong>{item.title}</strong>
              <p>{item.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="methodology-two-column">
        <section className="panel">
          <ReportSectionHeader title="Data quality states" text="Public-facing data is treated according to whether it is safe to interpret." />
          <SignalChipGroup items={qualityStates} />
          <DataQualityNote
            tone="caution"
            note="UPL Lens shows caveats because they affect interpretation. A caveat does not always make a record unusable, but it should change how confidently event-based patterns are read."
          />
        </section>

        <section className="panel">
          <ReportSectionHeader title="Known caveats" text="These limitations are part of the public method, not hidden fine print." />
          <ul className="methodology-caveat-list">
            {caveats.map((caveat) => (
              <li key={caveat}>{caveat}</li>
            ))}
          </ul>
        </section>
      </section>

      <section className="panel">
        <ReportSectionHeader title="Freshness and status" text={`These details help readers judge the current ${scopeNoun}.`} />
        <div className="methodology-freshness-grid">
          <MetricDelta label="Data service" value={apiOnline ? "Available" : "Unavailable"} context={formatHealthStatus(health?.api, "API status")} tone={apiOnline ? "positive" : "warning"} />
          <MetricDelta label="Data store" value={formatHealthStatus(health?.database, "Unknown")} context={health?.database_name ?? "Data store name unavailable"} />
          <MetricDelta
            label="Latest staging run"
            value={health?.latest_staging_completed_at ? formatDate(health.latest_staging_completed_at) : "Unknown"}
            context={health?.latest_staging_run_id ? `Run ${health.latest_staging_run_id}` : "No run id reported"}
          />
          <MetricDelta label="Selected scope" value={seasonLabel} context={`${overview?.match_count ?? selectedSeasonInfo?.match_count ?? data.matches.length} matches in view`} />
        </div>
      </section>

      <section className="methodology-two-column">
        <section className="panel">
          <ReportSectionHeader title="Maintainer" text="The project is maintained as a public football analytics product, with the technical system supporting the football questions." />
          <div className="methodology-maintainer">
            <strong>Built and maintained by Humphrey.</strong>
            <p>The project combines football research, data engineering, and public sports analytics.</p>
          </div>
        </section>

        <section className="panel">
          <ReportSectionHeader title="Find more" text="Follow the project, read longer notes, or inspect the public repository." />
          <div className="methodology-contact-list">
            {contactLinks.map((link) => (
              <a href={link.href} key={link.label} rel="noreferrer" target="_blank">
                {link.icon}
                <span>{link.label}</span>
              </a>
            ))}
          </div>
        </section>
      </section>

      <DataQualityNote
        title="Public interpretation"
        tone="neutral"
        note="UPL Lens is based on official source pages, but it is independently built and maintained. The official site remains the source record."
        metrics={[
          { label: "Source", value: "Official UPL pages" },
          { label: "Product role", value: "Independent intelligence" },
          { label: "Coverage", value: "Caveated where needed" },
        ]}
      />
    </article>
  );
}
