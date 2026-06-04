export function HeroSection() {
  return (
    <section className="overview-dashboard-header" aria-labelledby="page-title">
      <div className="overview-dashboard-header-copy">
        <p className="overview-hero-kicker">Public football intelligence</p>
        <h1 id="page-title">
          Understand the <span className="overview-hero-highlight">Uganda Premier League</span>
        </h1>
        <p>
          UPL Lens helps fans, analysts, and football professionals understand
          the Uganda Premier League through trusted match data, statistical
          insights, and team-level exploration.
        </p>
        <p className="overview-hero-note">Scorelines, timing patterns, and team signals, presented as one readable match intelligence surface.</p>
      </div>
    </section>
  );
}
