import type { SeasonOverviewResponse, SeasonResponse } from "../../api/types";
import type { LoadState, PageKey } from "../../app/types";
import { StatusItem } from "../common/StatusItem";
import { SeasonControls } from "../season/SeasonControls";
import { formatDate, formatSeason } from "../../utils/format";

type HeroSectionProps = {
  apiOnline: boolean;
  seasons: SeasonResponse[];
  selectedSeason: string;
  selectedSeasonInfo: SeasonResponse | undefined;
  overview: SeasonOverviewResponse | null;
  loadState: LoadState;
  onSeasonChange: (season: string) => void;
  onRefresh: () => void;
  onPageChange: (page: PageKey) => void;
};

export function HeroSection({
  apiOnline,
  seasons,
  selectedSeason,
  selectedSeasonInfo,
  overview,
  loadState,
  onSeasonChange,
  onRefresh,
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
        <p className="eyebrow">Uganda Premier League data, made analytical</p>
        <h1 id="page-title">UPL Match Intelligence</h1>
        <p className="hero-text">
          Understand the league through statistical signals from official match data, beyond ordinary fixtures,
          results, and tables.
        </p>
      </div>

      <SeasonControls
        seasons={seasons}
        selectedSeason={selectedSeason}
        loadState={loadState}
        onRefresh={onRefresh}
        onSeasonChange={onSeasonChange}
        variant="hero"
      />

      <div className="status-strip" aria-label="Data freshness and availability">
        <StatusItem label="Selected season" value={selectedSeason ? formatSeason(selectedSeason) : "No season loaded"} />
        <StatusItem label="Coverage window" value={dateRange} />
        <div>
          <span>Data status</span>
          <strong>{apiOnline ? "Ready for analysis" : "Loading latest data"}</strong>
          <button className="text-link inverse" type="button" onClick={() => onPageChange("methodology")}>
            How this data is collected
          </button>
        </div>
      </div>
    </section>
  );
}
