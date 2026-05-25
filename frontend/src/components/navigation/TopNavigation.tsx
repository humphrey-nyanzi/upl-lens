import { useState } from "react";

import { pages } from "../../app/pages";
import type { PageKey } from "../../app/types";

type TopNavigationProps = {
  apiOnline: boolean;
  currentPage: PageKey;
  onPageChange: (page: PageKey) => void;
};

export function TopNavigation({ apiOnline, currentPage, onPageChange }: TopNavigationProps) {
  const [menuOpen, setMenuOpen] = useState(false);

  function choosePage(page: PageKey) {
    onPageChange(page);
    setMenuOpen(false);
  }

  return (
    <header className="top-nav">
      <button className="brand-lockup" type="button" onClick={() => choosePage("overview")} aria-label="UPL Match Intelligence home">
        <span className="brand-mark">UPL</span>
        <span>
          <span className="brand-title">Match Intelligence</span>
          <span className="brand-subtitle">Football data observatory</span>
        </span>
      </button>

      <button
        className="menu-button"
        type="button"
        aria-controls="primary-navigation"
        aria-expanded={menuOpen}
        onClick={() => setMenuOpen((open) => !open)}
      >
        <span className="menu-icon" aria-hidden="true" />
        Menu
      </button>

      <nav className={menuOpen ? "nav-list open" : "nav-list"} id="primary-navigation" aria-label="Product sections">
        {pages.map((page) => (
          <button
            className={page.key === currentPage ? "nav-item active" : "nav-item"}
            key={page.key}
            type="button"
            aria-current={page.key === currentPage ? "page" : undefined}
            onClick={() => choosePage(page.key)}
          >
            {page.label}
          </button>
        ))}
      </nav>

      <div className="api-pill" aria-label={apiOnline ? "Data is ready" : "Data is still loading"}>
        <span className={apiOnline ? "status-dot online" : "status-dot offline"} />
        <span>{apiOnline ? "Data ready" : "Loading data"}</span>
      </div>
    </header>
  );
}
