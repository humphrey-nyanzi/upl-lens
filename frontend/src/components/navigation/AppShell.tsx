import type { ReactNode } from "react";

import { pages } from "../../app/pages";
import type { LoadState, PageKey } from "../../app/types";
import type { SeasonResponse } from "../../api/types";
import { SeasonControls } from "../season/SeasonControls";

type AppShellProps = {
  apiOnline: boolean;
  children: ReactNode;
  currentPage: PageKey;
  loadState: LoadState;
  onPageChange: (page: PageKey) => void;
  onRefresh: () => void;
  onSeasonChange: (season: string) => void;
  seasons: SeasonResponse[];
  selectedSeason: string;
};

const navIcons: Record<PageKey, string> = {
  overview: "O",
  "goal-timing": "G",
  matches: "M",
  teams: "T",
  methodology: "i",
};

export function AppShell({
  apiOnline,
  children,
  currentPage,
  loadState,
  onPageChange,
  onRefresh,
  onSeasonChange,
  seasons,
  selectedSeason,
}: AppShellProps) {
  return (
    <main className="app-shell">
      <aside className="sidebar" aria-label="Primary">
        <button className="brand-lockup" type="button" onClick={() => onPageChange("overview")} aria-label="UPL Match Intelligence home">
          <span className="brand-mark">UPL</span>
          <span>
            <span className="brand-title">Match Intelligence</span>
            <span className="brand-subtitle">Football intelligence workspace</span>
          </span>
        </button>

        <nav className="side-nav" aria-label="Product sections">
          {pages.map((page) => (
            <button
              className={page.key === currentPage ? "nav-item active" : "nav-item"}
              key={page.key}
              type="button"
              aria-current={page.key === currentPage ? "page" : undefined}
              onClick={() => onPageChange(page.key)}
            >
              <span aria-hidden="true">{navIcons[page.key]}</span>
              {page.label}
            </button>
          ))}
        </nav>

        <div className="sidebar-status">
          <span>Data status</span>
          <strong>{apiOnline ? "Live" : loadState === "error" ? "Offline" : "Waking up"}</strong>
          <p>{apiOnline ? "Ready for analysis" : "The hosted API may be starting."}</p>
        </div>
      </aside>

      <div className="app-main">
        <header className="top-bar">
          <div className="mobile-brand">
            <button className="brand-lockup" type="button" onClick={() => onPageChange("overview")} aria-label="UPL Match Intelligence home">
              <span className="brand-mark">UPL</span>
              <span>
                <span className="brand-title">Match Intelligence</span>
              </span>
            </button>
          </div>
          <nav className="mobile-nav" aria-label="Mobile product sections">
            {pages.map((page) => (
              <button
                className={page.key === currentPage ? "mobile-nav-item active" : "mobile-nav-item"}
                key={page.key}
                type="button"
                aria-current={page.key === currentPage ? "page" : undefined}
                onClick={() => onPageChange(page.key)}
              >
                {page.shortLabel}
              </button>
            ))}
          </nav>
          <SeasonControls
            seasons={seasons}
            selectedSeason={selectedSeason}
            loadState={loadState}
            onRefresh={onRefresh}
            onSeasonChange={onSeasonChange}
            variant="shell"
          />
          <div className="top-search" aria-label="Search placeholder">
            <span aria-hidden="true">S</span>
            <span>Search teams, matches, insights...</span>
          </div>
          <button className="export-button" type="button" onClick={() => window.print()}>
            Export report
          </button>
        </header>

        <section className="workspace" aria-live={loadState === "loading" ? "polite" : "off"}>
          {children}
        </section>
      </div>
    </main>
  );
}
