import type {
  EventResponse,
  GoalTimingInsightResponse,
  HealthResponse,
  MatchDetailResponse,
  MatchSummary,
  PlayerDetailResponse,
  PlayerSummary,
  SeasonOverviewResponse,
  SeasonResponse,
  TeamResponse,
} from "./types";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

type QueryValue = string | number | null | undefined;

export class ApiRequestError extends Error {
  status: number;
  statusText: string;

  constructor(status: number, statusText: string) {
    super(`API request failed: ${status} ${statusText}`);
    this.name = "ApiRequestError";
    this.status = status;
    this.statusText = statusText;
  }
}

function buildUrl(path: string, params: Record<string, QueryValue> = {}) {
  const url = new URL(path, API_BASE_URL);

  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      url.searchParams.set(key, String(value));
    }
  });

  return url;
}

async function getJson<T>(path: string, params?: Record<string, QueryValue>): Promise<T> {
  const response = await fetch(buildUrl(path, params));

  if (!response.ok) {
    throw new ApiRequestError(response.status, response.statusText);
  }

  return response.json() as Promise<T>;
}

export const apiClient = {
  getHealth: () => getJson<HealthResponse>("/health"),
  getSeasons: () => getJson<SeasonResponse[]>("/seasons"),
  getSeasonOverview: (season?: string) =>
    getJson<SeasonOverviewResponse>("/seasons/overview", { season }),
  getGoalTimingInsight: (season?: string) =>
    getJson<GoalTimingInsightResponse>("/insights/goal-timing", { season }),
  getMatches: (season?: string, limit = 500) =>
    getJson<MatchSummary[]>("/matches", { season, limit }),
  getTeamMatches: (season: string | undefined, team: string, limit = 500) =>
    getJson<MatchSummary[]>("/matches", { season, team, limit }),
  getMatchDetail: (matchId: number) => getJson<MatchDetailResponse>(`/matches/${matchId}`),
  getTeams: (season?: string, limit = 500) => getJson<TeamResponse[]>("/teams", { season, limit }),
  getPlayers: (season: string | undefined, limit = 200, sort = "goals") =>
    getJson<PlayerSummary[]>("/players", { season, limit, sort }),
  getPlayerDetail: (playerSlug: string, season?: string) =>
    getJson<PlayerDetailResponse>(`/players/${playerSlug}`, { season }),
  getEvents: (season: string | undefined, limit = 200, offset = 0) =>
    getJson<EventResponse[]>("/events", { season, limit, offset }),
  getTeamEvents: (season: string | undefined, team: string, limit = 200, offset = 0) =>
    getJson<EventResponse[]>("/events", { season, team, limit, offset }),
  getRecentEvents: (season: string | undefined, limit = 200) =>
    getJson<EventResponse[]>("/events", { season, limit }),
};
