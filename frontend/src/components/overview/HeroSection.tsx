import heroImage from "../../assets/upl-lens-overview-hero.jpg";

export function HeroSection() {
  const heroStyle = {
    backgroundImage: `linear-gradient(to right, rgba(245, 247, 241, 0.95) 0%, rgba(245, 247, 241, 0.85) 40%, rgba(245, 247, 241, 0.4) 70%, transparent 100%), url(${heroImage})`,
    backgroundSize: 'cover',
    backgroundPosition: 'right center',
    backgroundRepeat: 'no-repeat',
  };

  return (
    <section className="overview-dashboard-header" style={heroStyle} aria-labelledby="page-title">
      <div className="overview-dashboard-header-copy">
        <h1 id="page-title">Understand the Uganda Premier League</h1>
        <p>
          UPL Lens helps fans, analysts, and football professionals understand
          the Uganda Premier League through trusted match data, statistical
          insights, and team-level exploration.
        </p>
      </div>
    </section>
  );
}
