import type {
  GoalTimingInsightResponse,
  HealthResponse,
  MatchSummary,
  SeasonOverviewResponse,
  SeasonResponse,
  TeamResponse,
} from "../api/types";

export type LoadState = "idle" | "loading" | "success" | "error";
export type PageKey = "overview" | "goal-timing" | "matches" | "teams" | "methodology";

export type DashboardData = {
  health: HealthResponse | null;
  seasons: SeasonResponse[];
  overview: SeasonOverviewResponse | null;
  goalTiming: GoalTimingInsightResponse | null;
  matches: MatchSummary[];
  teams: TeamResponse[];
};

export type PageDefinition = {
  key: PageKey;
  label: string;
  shortLabel: string;
};

export type PageProps = {
  apiOnline: boolean;
  data: DashboardData;
  errorMessage: string;
  loadState: LoadState;
  onPageChange: (page: PageKey) => void;
  onRefresh: () => void;
  onSeasonChange: (season: string) => void;
  overview: SeasonOverviewResponse | null;
  selectedSeason: string;
  selectedSeasonInfo: SeasonResponse | undefined;
  goalTiming: GoalTimingInsightResponse | null;
};
