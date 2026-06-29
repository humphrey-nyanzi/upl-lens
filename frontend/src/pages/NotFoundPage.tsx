import { Link, useLocation } from "react-router-dom";
import { ArrowRight, Compass, Home } from "lucide-react";

import { pages } from "../app/pages";
import { PageIntro } from "../components/common/PageIntro";

const recoveryRoutes = pages.map((page) => ({
  ...page,
  path: page.key === "overview" ? "/" : `/${page.key}`,
}));

export function NotFoundPage() {
  const location = useLocation();

  return (
    <div className="not-found-page">
      <PageIntro
        variant="dense"
        eyebrow="Page not found"
        title="That UPL Lens route is not available"
        text="The page may have moved, or the link may not match a current product surface. Use one of the main football intelligence routes below to keep exploring."
      >
        <div className="not-found-current-route" aria-label="Unavailable path">
          <Compass size={18} aria-hidden="true" />
          <span>{location.pathname}</span>
        </div>
      </PageIntro>

      <section className="not-found-panel" aria-labelledby="not-found-recovery-title">
        <div>
          <h2 id="not-found-recovery-title">Return to a known section</h2>
          <p>
            UPL Lens keeps official match data separate from its intelligence layer, so unknown routes should land on a clear recovery page instead of silently showing another surface.
          </p>
        </div>

        <div className="not-found-route-grid">
          {recoveryRoutes.map((route) => (
            <Link key={route.key} to={route.path}>
              <span>{route.label}</span>
              <ArrowRight size={15} aria-hidden="true" />
            </Link>
          ))}
        </div>

        <Link className="text-button not-found-home-link" to="/">
          <Home size={15} aria-hidden="true" />
          Back to Overview
        </Link>
      </section>
    </div>
  );
}