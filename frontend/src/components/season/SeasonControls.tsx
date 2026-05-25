import type { SeasonResponse } from "../../api/types";
import type { LoadState } from "../../app/types";
import { formatSeason } from "../../utils/format";

type SeasonControlsProps = {
  seasons: SeasonResponse[];
  selectedSeason: string;
  loadState: LoadState;
  onRefresh: () => void;
  onSeasonChange: (season: string) => void;
  variant?: "default" | "hero";
};

export function SeasonControls({
  seasons,
  selectedSeason,
  loadState,
  onRefresh,
  onSeasonChange,
  variant = "default",
}: SeasonControlsProps) {
  return (
    <div className={variant === "hero" ? "season-controls hero-controls" : "season-controls"} aria-label="Season controls">
      <label>
        Season
        <select value={selectedSeason} onChange={(event) => onSeasonChange(event.target.value)} disabled={seasons.length === 0}>
          {seasons.map((season) => (
            <option value={season.season} key={season.season}>
              {formatSeason(season.season)}
            </option>
          ))}
        </select>
      </label>
      <button type="button" onClick={onRefresh} disabled={!selectedSeason || loadState === "loading"}>
        {loadState === "loading" ? "Refreshing" : "Refresh"}
      </button>
    </div>
  );
}
