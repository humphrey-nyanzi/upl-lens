export function OverviewSkeleton() {
  return (
    <>
      <section className="hero-panel skeleton-panel" aria-busy="true" aria-label="Loading league overview">
        <div className="skeleton-line short" />
        <div className="skeleton-line title" />
        <div className="skeleton-line" />
        <div className="skeleton-line medium" />
      </section>
      <section className="metric-grid" aria-label="Loading summary cards">
        {[0, 1, 2, 3].map((item) => (
          <article className="metric-card skeleton-card" key={item}>
            <div className="skeleton-line short" />
            <div className="skeleton-line number" />
            <div className="skeleton-line" />
          </article>
        ))}
      </section>
      <section className="featured-insight skeleton-card">
        <div className="skeleton-line short" />
        <div className="skeleton-line title" />
        <div className="skeleton-line" />
        <p className="empty-state">Loading the latest league data. The service may be waking up.</p>
      </section>
    </>
  );
}

export function GoalTimingSkeleton() {
  return (
    <section className="featured-insight skeleton-card" aria-busy="true" aria-label="Loading goal timing">
      <div className="skeleton-line short" />
      <div className="skeleton-line title" />
      <div className="skeleton-line" />
      <div className="skeleton-line medium" />
    </section>
  );
}
