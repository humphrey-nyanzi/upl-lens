import type { ReactNode } from "react";
import {
  Github,
  Newspaper,
  ShieldCheck,
  Twitter,
} from "lucide-react";

import { ReportSectionHeader } from "../common/ReportSectionHeader";

export type MethodologyFreshnessRow = {
  icon: ReactNode;
  label: string;
  value: string;
  status?: string;
};

export type MethodologyServiceStatus = {
  detail: string;
  icon: ReactNode;
  label: string;
  meta: string;
};

const pipelineSteps = [
  {
    title: "Official source",
    text: "Public UPL match pages provide the source records. The official website remains the archive.",
  },
  {
    title: "Extract and structure",
    text: "Collected records are normalized and stored so the same fields can be compared consistently.",
  },
  {
    title: "Validate and enrich",
    text: "Checks flag mismatches, missing coverage, administrative results, and source anomalies before interpretation.",
  },
  {
    title: "Deliver",
    text: "FastAPI serves the checked data to React as football summaries, signals, comparisons, and caveats.",
  },
];

const interpretationModes = [
  {
    title: "Transform",
    text: "UPL Lens turns records into timing patterns, match signals, team comparisons, trends, and promoted insights.",
  },
  {
    title: "Summarize",
    text: "Scorelines, dates, and key events stay compact when they support an analytical explanation.",
  },
  {
    title: "Link out",
    text: "Full archive detail remains on the official source when UPL Lens has not added analytical meaning.",
  },
];

const readinessItems = [
  {
    label: "Traceable",
    text: "Findings begin with collected source records.",
  },
  {
    label: "Consistent",
    text: "The same definitions are used across the app.",
  },
  {
    label: "Caveated",
    text: "Coverage limits stay visible near affected analysis.",
  },
];

const caveats = [
  "Source pages may occasionally be incomplete or change structure.",
  "Public numbers should be read with caveats during unusual events.",
  "Event timelines can be delayed, partial, or unavailable for some matches.",
  "Administrative results and source anomalies require additional context.",
  "Player summaries depend on available lineups, events, and stable source naming.",
];

const contactLinks = [
  {
    href: "https://github.com/humphrey-nyanzi",
    icon: <Github size={16} />,
    label: "GitHub",
  },
  {
    href: "https://humphreyn-substack.com",
    icon: <Newspaper size={16} />,
    label: "Substack",
  },
  {
    href: "https://x.com/phreyn",
    icon: <Twitter size={16} />,
    label: "X",
  },
];

export function MethodologyHero() {
  return (
    <section
      className="methodology-hero lens-fused-hero"
      aria-labelledby="methodology-title"
    >
      <div className="methodology-hero-copy lens-fused-hero-copy">
        <p className="overview-hero-kicker">Methodology and freshness</p>
        <h1 id="methodology-title">
          Transparent data.
          <span className="overview-hero-highlight methodology-hero-break">
            {" "}
            Built for football decisions.
          </span>
        </h1>
        <p>
          UPL Lens is an independent football intelligence product. It uses
          official Uganda Premier League match pages as source records, but it
          is not the official UPL website.
        </p>
      </div>
    </section>
  );
}

export function MethodologyBoundary() {
  return (
    <section className="methodology-boundary-section">
      <ReportSectionHeader
        title="Source record vs intelligence layer"
        text="The official website preserves the source record. UPL Lens adds analytical meaning without claiming to replace that archive."
      />
      <div className="methodology-boundary-grid">
        <article>
          <span>Official UPL website</span>
          <strong>Source record</strong>
          <p>
            Fixtures, results, match pages, and full archive details remain
            official-source material.
          </p>
        </article>
        <article>
          <span>UPL Lens</span>
          <strong>Analytical meaning</strong>
          <p>
            Signals, comparisons, trends, and caveats explain what the
            collected records may mean.
          </p>
        </article>
      </div>
    </section>
  );
}

export function MethodologyCollection({
  freshnessRows,
}: {
  freshnessRows: MethodologyFreshnessRow[];
}) {
  return (
    <section className="methodology-summary-grid">
      <section className="methodology-collection-card methodology-collection-section">
        <ReportSectionHeader
          title="How the data is collected"
          text="A clear view of how public source records become readable football intelligence."
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
              <strong>Structured source extraction</strong>
            </article>
            <article>
              <span>Data path</span>
              <strong>Postgres {"->"} FastAPI {"->"} React</strong>
            </article>
            <article>
              <span>Coverage</span>
              <strong>Available collected UPL records</strong>
            </article>
            <article>
              <span>Update rhythm</span>
              <strong>Scheduled and manual refreshes</strong>
            </article>
          </div>
        </div>
      </section>

      <section className="panel methodology-freshness-card">
        <ReportSectionHeader
          title="Freshness and coverage"
          text="A point-in-time view of recency and the records supporting this scope."
        />
        <ul
          className="methodology-freshness-table"
          aria-label="Freshness and coverage summary"
        >
          {freshnessRows.map((row) => (
            <li className="methodology-freshness-row" key={row.label}>
              <div className="methodology-freshness-label">
                <span
                  className="methodology-freshness-icon"
                  aria-hidden="true"
                >
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
  );
}

export function MethodologyInterpretation() {
  return (
    <>
      <section className="methodology-interpretation-section">
        <ReportSectionHeader
          title="How UPL Lens uses source material"
          text="Every source detail is transformed, summarized, or left with the official archive."
        />
        <div className="methodology-transform-grid">
          {interpretationModes.map((mode) => (
            <article key={mode.title}>
              <strong>{mode.title}</strong>
              <p>{mode.text}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="methodology-inline-panel methodology-comparison-section">
        <ReportSectionHeader
          title="Scoreline goals and timeline goals"
          text="These counts answer different questions, so they can differ without the final result being wrong."
        />
        <div className="methodology-boundary-grid">
          <article>
            <span>Scoreline goals</span>
            <strong>The final recorded result</strong>
            <p>
              This count comes from the match scoreline and is used for result
              and scoring-rate summaries.
            </p>
          </article>
          <article>
            <span>Timeline goals</span>
            <strong>Goals found in event records</strong>
            <p>
              This count powers timing analysis. It may be lower when a source
              timeline is partial, delayed, or unavailable.
            </p>
          </article>
        </div>
      </section>
    </>
  );
}

export function MethodologyTrust({
  serviceStatus,
}: {
  serviceStatus: MethodologyServiceStatus;
}) {
  return (
    <section className="methodology-trust-grid">
      <section className="methodology-status-card methodology-status-section">
        <ReportSectionHeader
          title="Current service status"
          text="This is the latest available API health response, not an uptime percentage or availability guarantee."
        />
        <div className="methodology-status-summary">
          <div className="methodology-status-badge">
            <span className="methodology-status-icon" aria-hidden="true">
              {serviceStatus.icon}
            </span>
            <div>
              <strong>{serviceStatus.label}</strong>
              <p>{serviceStatus.detail}</p>
            </div>
          </div>
          <div className="methodology-status-meta">
            <span>Health check</span>
            <strong>{serviceStatus.meta}</strong>
          </div>
        </div>
      </section>

      <section className="methodology-limitations-card methodology-limitations-section">
        <ReportSectionHeader
          title="Known limitations"
          text="These constraints affect interpretation and remain visible throughout the product."
        />
        <ul className="methodology-caveat-list">
          {caveats.map((caveat) => (
            <li key={caveat}>{caveat}</li>
          ))}
        </ul>
      </section>

      <section className="methodology-confidence-card methodology-confidence-section">
        <ReportSectionHeader
          title="How to read UPL Lens"
          text="Trust comes from traceability, consistent definitions, and visible limits."
        />
        <div className="methodology-confidence-grid">
          {readinessItems.map((item) => (
            <article key={item.label}>
              <span
                className="methodology-confidence-icon"
                aria-hidden="true"
              >
                <ShieldCheck size={18} />
              </span>
              <strong>{item.label}</strong>
              <p>{item.text}</p>
            </article>
          ))}
        </div>
      </section>
    </section>
  );
}

export function MethodologyContact() {
  return (
    <section className="methodology-two-column">
      <section className="methodology-contact-section">
        <ReportSectionHeader
          title="Maintainer"
          text="The football questions lead the product; the technical system supports their public presentation."
        />
        <div className="methodology-maintainer">
          <strong>Built and maintained by Humphrey Nyanzi.</strong>
          <p>
            UPL Lens combines Uganda Premier League research, data engineering,
            and public sports analysis.
          </p>
        </div>
      </section>

      <section className="methodology-contact-section">
        <ReportSectionHeader
          title="Contact and follow"
          text="Use the same public project links available from the app navigation."
        />
        <div className="methodology-contact-list">
          {contactLinks.map((link) => (
            <a
              href={link.href}
              key={link.label}
              rel="noreferrer"
              target="_blank"
            >
              {link.icon}
              <span>{link.label}</span>
            </a>
          ))}
        </div>
      </section>
    </section>
  );
}
