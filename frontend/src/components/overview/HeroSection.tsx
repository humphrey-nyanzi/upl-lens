import type { SeasonOverviewResponse, SeasonResponse } from "../../api/types";
import type { LoadState, PageKey } from "../../app/types";
import { StatusItem } from "../common/StatusItem";
import { formatDate, formatSeason } from "../../utils/format";

type HeroSectionProps = {
  apiOnline: boolean;
  selectedSeason: string;
  selectedSeasonInfo: SeasonResponse | undefined;
  overview: SeasonOverviewResponse | null;
  loadState: LoadState;
  onPageChange: (page: PageKey) => void;
};

export function HeroSection({
  apiOnline,
  selectedSeason,
  selectedSeasonInfo,
  overview,
  loadState,
  onPageChange,
}: HeroSectionProps) {
  const dateRange = selectedSeasonInfo
    ? `${formatDate(overview?.first_match_date ?? selectedSeasonInfo.first_match_date)} to ${formatDate(
        overview?.latest_match_date ?? selectedSeasonInfo.last_match_date,
      )}`
    : "Date range unavailable";

  return (
    <section className="hero-panel" aria-labelledby="page-title">
      <div className="hero-copy">
        <p className="eyebrow">League intelligence workspace</p>
        <h1 id="page-title">League Overview</h1>
        <p className="hero-text">
          Real-time intelligence from official Uganda Premier League match data: season signals, team trends,
          scoring windows, and recent evidence in one scan.
        </p>
      </div>

      <div className="status-strip" aria-label="Data freshness and availability">
        <StatusItem label="Selected season" value={selectedSeason ? formatSeason(selectedSeason) : "No season loaded"} />
        <StatusItem label="Coverage window" value={dateRange} />
        <div>
          <span>Data status</span>
          <strong>{apiOnline ? "Ready for analysis" : loadState === "error" ? "Needs attention" : "Loading latest data"}</strong>
          <button className="text-link inverse" type="button" onClick={() => onPageChange("methodology")}>
            How this data is collected
          </button>
        </div>
      </div>
    </section>
  );
}
