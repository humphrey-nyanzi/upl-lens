import { Link, NavLink, useLocation, useNavigate } from "react-router-dom";
import type { KeyboardEvent as ReactKeyboardEvent, ReactNode } from "react";
import { pages } from "../../app/pages";
import type { LoadState } from "../../app/types";
import type { HealthResponse, MatchSummary, PlayerSummary, SeasonResponse, TeamResponse } from "../../api/types";
import { SeasonControls } from "../season/SeasonControls";
import { BrandLockup } from "./BrandLockup";
import { Home, List, Users, BarChart2, TrendingUp, Info, Search, User, Menu, Github, Linkedin, Newspaper, Twitter } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { formatDate, formatScoreline } from "../../utils/format";
import { MatchStatusPill, TeamName } from "../common/EditorialRows";
import { slugify } from "../../utils/slugs";

type AppShellProps = {
  apiOnline: boolean;
  children: ReactNode;
  health: HealthResponse | null;
  loadState: LoadState;
  onRefresh: () => void;
  onSeasonChange: (season: string) => void;
  seasons: SeasonResponse[];
  selectedSeason: string;
  matches: MatchSummary[];
  teams: TeamResponse[];
  players: PlayerSummary[];
};

type SearchResult =
  | { id: string; type: "team"; teamName: string }
  | { id: string; type: "player"; playerSlug: string; playerName: string }
  | { id: string; type: "match"; matchId: number };

const navIcons: Record<string, ReactNode> = {
  overview: <Home size={16} />,
  matches: <List size={16} />,
  teams: <Users size={16} />,
  players: <User size={16} />,
  insights: <BarChart2 size={16} />,
  trends: <TrendingUp size={16} />,
  about: <Info size={16} />,
};

const primaryMobilePages = ["overview", "insights", "trends"] as const;
const secondaryPages = ["matches", "teams", "players", "about"] as const;

const socialLinks = [
  { href: "https://x.com", icon: <Twitter size={15} />, label: "X" },
  { href: "https://github.com", icon: <Github size={15} />, label: "GitHub" },
  { href: "https://humphreyn-substack.com", icon: <Newspaper size={15} />, label: "Substack" },
  { href: "https://www.linkedin.com", icon: <Linkedin size={15} />, label: "LinkedIn" },
];

function formatFreshness(health: HealthResponse | null, apiOnline: boolean) {
  if (!apiOnline) return "Data status unavailable";
  const latestUpdate = health?.latest_staging_completed_at;
  if (!latestUpdate) return "Data live";

  const date = new Date(latestUpdate);
  if (Number.isNaN(date.getTime())) return "Data live";

  return `Updated ${new Intl.DateTimeFormat("en", { day: "2-digit", month: "short", year: "numeric" }).format(date)}`;
}

export function AppShell({
  apiOnline,
  children,
  health,
  loadState,
  onRefresh,
  onSeasonChange,
  seasons,
  selectedSeason,
  matches,
  teams,
  players,
}: AppShellProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const path = location.pathname.replace(/^\//, "") || "overview";
  const [moreOpen, setMoreOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchOpen, setSearchOpen] = useState(false);
  const [activeSearchIndex, setActiveSearchIndex] = useState(-1);
  const searchRegionRef = useRef<HTMLDivElement | null>(null);
  const searchInputRef = useRef<HTMLInputElement | null>(null);
  const freshnessLabel = formatFreshness(health, apiOnline);
  const normalizedSearch = searchQuery.trim().toLowerCase();
  const hasSearchQuery = normalizedSearch.length >= 2;

  const teamResults = useMemo(() => {
    if (!hasSearchQuery) return [];
    return teams
      .filter((team) => team.team_name.toLowerCase().includes(normalizedSearch))
      .sort((left, right) => left.team_name.localeCompare(right.team_name))
      .slice(0, 5);
  }, [hasSearchQuery, normalizedSearch, teams]);

  const matchResults = useMemo(() => {
    if (!hasSearchQuery) return [];

    return matches
      .filter((match) => {
        const home = match.home_team?.toLowerCase() ?? "";
        const away = match.away_team?.toLowerCase() ?? "";
        return home.includes(normalizedSearch) || away.includes(normalizedSearch);
      })
      .sort((left, right) => (right.match_date ?? "").localeCompare(left.match_date ?? "") || right.match_id - left.match_id)
      .slice(0, 5);
  }, [hasSearchQuery, matches, normalizedSearch]);

  const playerResults = useMemo(() => {
    if (!hasSearchQuery) return [];

    return players
      .filter((player) => {
        const teamNames = player.teams.join(" ").toLowerCase();
        return player.player_name.toLowerCase().includes(normalizedSearch) || teamNames.includes(normalizedSearch);
      })
      .sort((left, right) => right.goals - left.goals || right.appearances - left.appearances || left.player_name.localeCompare(right.player_name))
      .slice(0, 5);
  }, [hasSearchQuery, normalizedSearch, players]);

  const combinedSearchResults = useMemo<SearchResult[]>(
    () => [
      ...teamResults.map((team) => ({ id: `team-${slugify(team.team_name)}`, type: "team" as const, teamName: team.team_name })),
      ...playerResults.map((player) => ({
        id: `player-${player.player_slug}`,
        type: "player" as const,
        playerSlug: player.player_slug,
        playerName: player.player_name,
      })),
      ...matchResults.map((match) => ({ id: `match-${match.match_id}`, type: "match" as const, matchId: match.match_id })),
    ],
    [matchResults, playerResults, teamResults],
  );

  const showSearchResults = searchOpen && hasSearchQuery;
  const activeSearchResult = showSearchResults ? combinedSearchResults[activeSearchIndex] : undefined;
  const activeSearchOptionId = activeSearchResult ? `search-result-${activeSearchResult.id}` : undefined;

  useEffect(() => {
    if (!showSearchResults || combinedSearchResults.length === 0) {
      setActiveSearchIndex(-1);
      return;
    }

    setActiveSearchIndex((currentIndex) => (currentIndex >= 0 && currentIndex < combinedSearchResults.length ? currentIndex : 0));
  }, [combinedSearchResults.length, showSearchResults]);

  useEffect(() => {
    function handlePointerDown(event: PointerEvent) {
      if (searchRegionRef.current && !searchRegionRef.current.contains(event.target as Node)) {
        setSearchOpen(false);
        setActiveSearchIndex(-1);
      }
    }

    function handlePageKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setSearchOpen(false);
        setMoreOpen(false);
        setActiveSearchIndex(-1);
      }
    }

    document.addEventListener("pointerdown", handlePointerDown);
    document.addEventListener("keydown", handlePageKeyDown);

    return () => {
      document.removeEventListener("pointerdown", handlePointerDown);
      document.removeEventListener("keydown", handlePageKeyDown);
    };
  }, []);

  useEffect(() => {
    if (searchOpen) {
      searchInputRef.current?.focus();
    }
  }, [searchOpen]);

  function handleTeamSelect(teamName: string) {
    setSearchOpen(false);
    setSearchQuery("");
    navigate(`/teams/${slugify(teamName)}`);
  }

  function handleMatchSelect(matchId: number) {
    setSearchOpen(false);
    setSearchQuery("");
    navigate(`/matches/${matchId}`);
  }

  function handlePlayerSelect(playerSlug: string) {
    setSearchOpen(false);
    setSearchQuery("");
    navigate(`/players/${playerSlug}`);
  }

  function handleSearchResultSelect(result: SearchResult) {
    if (result.type === "team") {
      handleTeamSelect(result.teamName);
      return;
    }

    if (result.type === "player") {
      handlePlayerSelect(result.playerSlug);
      return;
    }

    handleMatchSelect(result.matchId);
  }

  function closeMoreMenu() {
    setMoreOpen(false);
  }

  function getSearchResultIndex(groupOffset: number, index: number) {
    return groupOffset + index;
  }

  function handleSearchKeyDown(event: ReactKeyboardEvent<HTMLInputElement>) {
    if (event.key === "Escape") {
      setSearchOpen(false);
      setActiveSearchIndex(-1);
      return;
    }

    if (event.key !== "ArrowDown" && event.key !== "ArrowUp" && event.key !== "Enter") {
      return;
    }

    if (!hasSearchQuery) {
      return;
    }

    if (event.key === "Enter") {
      if (showSearchResults && activeSearchResult) {
        event.preventDefault();
        handleSearchResultSelect(activeSearchResult);
      }
      return;
    }

    event.preventDefault();
    setSearchOpen(true);

    if (combinedSearchResults.length === 0) {
      return;
    }

    setActiveSearchIndex((currentIndex) => {
      if (event.key === "ArrowDown") {
        return currentIndex < combinedSearchResults.length - 1 ? currentIndex + 1 : 0;
      }

      return currentIndex > 0 ? currentIndex - 1 : combinedSearchResults.length - 1;
    });
  }

  return (
    <main className="app-shell">
      <aside className="sidebar" aria-label="Primary">
        <Link className="brand-lockup" to="/" aria-label="UPL Lens home">
          <BrandLockup />
          <span className="brand-subtitle">Football intelligence workspace</span>
        </Link>

        <nav className="side-nav" aria-label="Product sections">
          {pages.map((page) => (
            <NavLink
              key={page.key}
              to={page.key === "overview" ? "/" : `/${page.key}`}
              className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}
              aria-current={path === page.key ? "page" : undefined}
              title={page.label}
            >
              <span aria-hidden="true" className="nav-icon">
                {navIcons[page.key]}
              </span>
              <span className="nav-label">{page.label}</span>
            </NavLink>
          ))}
        </nav>

        <nav className="sidebar-footer-social" aria-label="Social links">
          {socialLinks.map((link) => (
            <a
              key={link.label}
              aria-label={link.label}
              className="social-link icon-only"
              href={link.href}
              rel="noreferrer"
              target="_blank"
              title={link.label}
            >
              {link.icon}
            </a>
          ))}
        </nav>
      </aside>

      <div className="app-main">
        <header className="top-bar">
          <div className="mobile-brand">
            <Link className="brand-lockup" to="/" aria-label="UPL Lens home">
              <BrandLockup compact />
            </Link>
          </div>
          <div className="top-search-area">
            <SeasonControls
              seasons={seasons}
              selectedSeason={selectedSeason}
              loadState={loadState}
              onRefresh={onRefresh}
              onSeasonChange={onSeasonChange}
              variant="shell"
            />
            <button
              className="mobile-search-trigger"
              type="button"
              aria-expanded={searchOpen}
              aria-controls="global-search-results"
              aria-label="Search teams, players, and matches"
              onClick={() => setSearchOpen((isOpen) => !isOpen)}
            >
              <Search size={18} aria-hidden="true" />
            </button>
            <div
              ref={searchRegionRef}
              className={`shell-search-group${searchOpen ? " is-open" : ""}`}
              onBlurCapture={(event) => {
                const nextFocusTarget = event.relatedTarget;
                if (nextFocusTarget instanceof Node && searchRegionRef.current?.contains(nextFocusTarget)) {
                  return;
                }
                setSearchOpen(false);
                setActiveSearchIndex(-1);
              }}
            >
              <div className="search-bar-container">
                <Search size={14} className="search-icon" aria-hidden />
                <input
                  ref={searchInputRef}
                  aria-activedescendant={activeSearchOptionId}
                  aria-label="Search teams, players, and matches"
                  aria-controls="global-search-results"
                  aria-expanded={showSearchResults}
                  aria-haspopup="listbox"
                  className="search-input"
                  onChange={(event) => {
                    setSearchQuery(event.target.value);
                    setSearchOpen(true);
                  }}
                  onFocus={() => setSearchOpen(true)}
                  onKeyDown={handleSearchKeyDown}
                  placeholder="Search teams, players, and matches"
                  role="combobox"
                  type="text"
                  value={searchQuery}
                />
              </div>
              {showSearchResults ? (
                <div className="search-results-panel" id="global-search-results" role="listbox" aria-label="Search results">
                  {teamResults.length > 0 ? (
                    <div className="search-results-group">
                      <span>Teams</span>
                      {teamResults.map((team, index) => {
                        const result: SearchResult = { id: `team-${slugify(team.team_name)}`, type: "team", teamName: team.team_name };
                        const isActive = activeSearchIndex === getSearchResultIndex(0, index);

                        return (
                          <button
                            aria-selected={isActive}
                            className={isActive ? "active" : undefined}
                            id={`search-result-${result.id}`}
                            key={team.team_name}
                            onMouseDown={(event) => {
                              event.preventDefault();
                              handleSearchResultSelect(result);
                            }}
                            onMouseEnter={() => setActiveSearchIndex(getSearchResultIndex(0, index))}
                            role="option"
                            type="button"
                          >
                            <span className="search-result-topline">
                              <TeamName className="search-team-name" label={team.team_name} size="small" />
                              <span className="search-result-chip">Team</span>
                            </span>
                            <small>
                              {team.wins}W {team.draws}D {team.losses}L · {team.goals_for} GF
                            </small>
                          </button>
                        );
                      })}
                    </div>
                  ) : null}
                  {playerResults.length > 0 ? (
                    <div className="search-results-group">
                      <span>Players</span>
                      {playerResults.map((player, index) => {
                        const resultIndex = getSearchResultIndex(teamResults.length, index);
                        const result: SearchResult = {
                          id: `player-${player.player_slug}`,
                          type: "player",
                          playerSlug: player.player_slug,
                          playerName: player.player_name,
                        };
                        const isActive = activeSearchIndex === resultIndex;

                        return (
                          <button
                            aria-selected={isActive}
                            className={isActive ? "active" : undefined}
                            id={`search-result-${result.id}`}
                            key={player.player_slug}
                            onMouseDown={(event) => {
                              event.preventDefault();
                              handleSearchResultSelect(result);
                            }}
                            onMouseEnter={() => setActiveSearchIndex(resultIndex)}
                            role="option"
                            type="button"
                          >
                            <span className="search-result-topline">
                              <strong>{player.player_name}</strong>
                              <span className="search-result-chip">Player</span>
                            </span>
                            <small>
                              <TeamName className="search-team-name" label={player.primary_team ?? "Team TBC"} size="small" /> · {player.goals} G · {player.assists} A · {player.appearances} apps
                            </small>
                          </button>
                        );
                      })}
                    </div>
                  ) : null}
                  {matchResults.length > 0 ? (
                    <div className="search-results-group">
                      <span>Matches</span>
                      {matchResults.map((match, index) => {
                        const resultIndex = getSearchResultIndex(teamResults.length + playerResults.length, index);
                        const result: SearchResult = { id: `match-${match.match_id}`, type: "match", matchId: match.match_id };
                        const isActive = activeSearchIndex === resultIndex;

                        return (
                          <button
                            aria-selected={isActive}
                            className={isActive ? "active" : undefined}
                            id={`search-result-${result.id}`}
                            key={match.match_id}
                            onMouseDown={(event) => {
                              event.preventDefault();
                              handleSearchResultSelect(result);
                            }}
                            onMouseEnter={() => setActiveSearchIndex(resultIndex)}
                            role="option"
                            type="button"
                          >
                            <span className="search-result-topline">
                              <strong>
                                {match.home_team ?? "Home"} {formatScoreline(match.home_score, match.away_score)} {match.away_team ?? "Away"}
                              </strong>
                              <MatchStatusPill match={match} />
                            </span>
                            <small>{formatDate(match.match_date)} · Match brief</small>
                          </button>
                        );
                      })}
                    </div>
                  ) : null}
                  {teamResults.length === 0 && playerResults.length === 0 && matchResults.length === 0 ? (
                    <div className="search-results-empty">No teams, players, or matches found.</div>
                  ) : null}
                </div>
              ) : null}
            </div>
            <div className={`data-status-indicator${apiOnline ? " is-live" : " is-waking"}`} title={freshnessLabel}>
              <span className="status-dot" aria-hidden="true"></span>
              <span className="status-text">{freshnessLabel}</span>
            </div>
          </div>
        </header>

        <nav className="mobile-nav" aria-label="Mobile product sections">
          {primaryMobilePages.map((pageKey) => {
            const page = pages.find((item) => item.key === pageKey)!;

            return (
              <NavLink
                key={page.key}
                to={page.key === "overview" ? "/" : `/${page.key}`}
                className={({ isActive }) => (isActive ? "mobile-nav-item active" : "mobile-nav-item")}
                aria-label={page.label}
                title={page.label}
              >
                <span className="mobile-nav-icon" aria-hidden="true">{navIcons[page.key]}</span>
                <span className="visually-hidden">{page.shortLabel}</span>
              </NavLink>
            );
          })}

          <button
            className={`mobile-nav-item${moreOpen || secondaryPages.includes(path as (typeof secondaryPages)[number]) ? " active" : ""}`}
            type="button"
            onClick={() => setMoreOpen((s) => !s)}
            aria-expanded={moreOpen}
            aria-controls="mobile-more-menu"
            aria-label="More"
            title="More"
          >
            <span className="mobile-nav-icon" aria-hidden="true"><Menu size={16} /></span>
            <span className="visually-hidden">More</span>
          </button>
        </nav>

        {moreOpen ? (
          <div id="mobile-more-menu" className="mobile-more-menu">
            <nav>
              {secondaryPages.map((pageKey) => {
                const page = pages.find((item) => item.key === pageKey)!;
                return (
                  <Link key={page.key} to={page.key === "overview" ? "/" : `/${page.key}`} onClick={closeMoreMenu}>
                    <span className="mobile-more-link-icon" aria-hidden="true">{navIcons[page.key]}</span>
                    <span>{page.label}</span>
                  </Link>
                );
              })}
            </nav>
            <div className="mobile-more-social">
              {socialLinks.map((link) => (
                <a
                  key={link.label}
                  aria-label={link.label}
                  className="social-link icon-only"
                  href={link.href}
                  rel="noreferrer"
                  target="_blank"
                  title={link.label}
                >
                  {link.icon}
                </a>
              ))}
            </div>
          </div>
        ) : null}

        <section className="workspace" aria-live={loadState === "loading" ? "polite" : "off"}>
          {children}
        </section>

        <footer className="app-footer">
          <div className="footer-strip">© UPL Lens</div>
        </footer>
      </div>
    </main>
  );
}
