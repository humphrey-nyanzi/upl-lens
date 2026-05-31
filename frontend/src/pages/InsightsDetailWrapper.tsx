import React from "react";
import { useParams } from "react-router-dom";
import type { PageProps } from "../app/types";
import { GoalTimingPage } from "./GoalTimingPage";

export function InsightsDetailWrapper(props: PageProps) {
  const { insightSlug } = useParams();
  if (insightSlug === "goal-timing") {
    return <GoalTimingPage {...props} />;
  }

  return (
    <section className="panel">
      <h2>Insight unavailable</h2>
      <p>The requested insight is not available in this release: {insightSlug ?? "unknown"}.</p>
    </section>
  );
}
