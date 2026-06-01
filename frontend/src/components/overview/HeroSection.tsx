import heroImage from "../../assets/upl-lens-overview-hero.jpg";

export function HeroSection() {
  const heroStyle = {
    backgroundImage: `linear-gradient(90deg, rgba(245, 243, 238, 0.98) 0%, rgba(245, 243, 238, 0.88) 38%, rgba(245, 243, 238, 0.34) 68%, rgba(245, 243, 238, 0.06) 100%), url(${heroImage})`,
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
