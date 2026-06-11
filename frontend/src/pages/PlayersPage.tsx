import { useDeferredValue, useEffect, useMemo, useReducer, useState } from "react";
import { Link } from "react-router-dom";

import { apiClient } from "../api/client";
import type { PlayerLeaderboardsResponse, PlayerProfileLabel, PlayerSummary } from "../api/types";
import type { PageProps } from "../app/types";
import { EditorialTable, EditorialTableHeader } from "../components/common/EditorialTable";
import { EmptyState } from "../components/common/EmptyState";
import { KpiCard } from "../components/common/KpiCard";
import { PageIntro } from "../components/common/PageIntro";
import { ReportSectionHeader } from "../components/common/ReportSectionHeader";
import { ShowMoreList } from "../components/common/ShowMoreList";
import { TeamName } from "../components/common/EditorialRows";
import { DataQualityNote } from "../components/intelligence/DataQualityNote";
import { HorizontalComparisonBar, type IntelligenceTone } from "../components/intelligence/ComparisonBars";
import { MetricDelta } from "../components/intelligence/MetricDelta";
import { ScatterComparisonPlot } from "../components/intelligence/ScatterComparisonPlot";
import { SignalChipGroup, type SignalTone } from "../components/intelligence/SignalChip";
import { PlayerRow } from "../components/players/PlayerRow";
import { formatPercent } from "../utils/format";
import { getSelectedSeasonLabel, toApiSeason } from "../utils/seasonScope";

type LeaderboardKey =
  | "goals"
  | "assists"
  | "goal_contributions"
  | "appearances"
  | "starts"
  | "cards"
  | "bench_impact";
type SortKey = "goals" | "assists" | "goal_contributions" | "appearances" | "starts" | "cards" | "name";
type LeaderboardState = "loading" | "success" | "error";

type LeaderboardsViewState = {
  requestKey: string;
  leaderboards: PlayerLeaderboardsResponse | null;
  status: Exclude<LeaderboardState, "loading">;
};

type PlayerBoardFilters = {
  minimumAppearances: string;
  searchTerm: string;
  sortKey: SortKey;
  teamFilter: string;
};

type PlayerBoardFilterAction =
  | { type: "minimumAppearances"; value: string }
  | { type: "search"; value: string }
  | { type: "sort"; value: SortKey }
  | { type: "team"; value: string };

const sortOptions: Array<{ label: string; value: SortKey }> = [
  { label: "Goals", value: "goals" },
  { label: "Assists", value: "assists" },
  { label: "Goal contributions", value: "goal_contributions" },
  { label: "Appearances", value: "appearances" },
  { label: "Starts", value: "starts" },
  { label: "Cards", value: "cards" },
  { label: "Name", value: "name" },
];

const leaderboardSections: Array<{
  key: LeaderboardKey;
  title: string;
  text: string;
  primaryLabel: string;
  secondaryLabel: string;
}> = [
  {
    key: "goals",
    title: "Leading goal totals",
    text: "Available event data highlights the players finishing moves most often in this scope.",
    primaryLabel: "Goals",
    secondaryLabel: "Assists",
  },
  {
    key: "assists",
    title: "Chance creators",
    text: "Assist leaders help separate finishers from the players supplying the final pass when the source timeline credits it.",
    primaryLabel: "Assists",
    secondaryLabel: "Goals",
  },
  {
    key: "goal_contributions",
    title: "Combined output",
    text: "Goal plus assist totals give a broader view of attacking involvement in the available records.",
    primaryLabel: "G+A",
    secondaryLabel: "Apps",
  },
  {
    key: "appearances",
    title: "Most involved",
    text: "Appearance totals point to squad regulars who keep showing up in available lineup data.",
    primaryLabel: "Apps",
    secondaryLabel: "Starts",
  },
  {
    key: "starts",
    title: "Regular starters",
    text: "Start counts help distinguish core starters from wider squad options.",
    primaryLabel: "Starts",
    secondaryLabel: "Starts share",
  },
  {
    key: "cards",
    title: "Discipline signals",
    text: "Card totals surface the players carrying the clearest discipline flags in available data.",
    primaryLabel: "Cards",
    secondaryLabel: "Apps",
  },
  {
    key: "bench_impact",
    title: "Bench impact",
    text: "Substitute appearances and output point to players influencing matches without always starting.",
    primaryLabel: "Sub on",
    secondaryLabel: "G+A",
  },
];

function playerBoardFilterReducer(
  filters: PlayerBoardFilters,
  action: PlayerBoardFilterAction,
): PlayerBoardFilters {
  if (action.type === "minimumAppearances") return { ...filters, minimumAppearances: action.value };
  if (action.type === "search") return { ...filters, searchTerm: action.value };
  if (action.type === "sort") return { ...filters, sortKey: action.value };
  return { ...filters, teamFilter: action.value };
}

function formatStartsShare(value: number | null) {
  if (value === null || value === undefined) return "Starts share unavailable";
  return formatPercent(value);
}

function getPlayerLabels(labels: PlayerProfileLabel[]) {
  return labels.map((label) => ({
    key: label.key,
    label: label.label,
    tone: label.tone as SignalTone,
  }));
}

function getSortValue(player: PlayerSummary, sortKey: SortKey) {
  if (sortKey === "name") return player.player_name.toLowerCase();
  if (sortKey === "cards") return player.cards;
  return player[sortKey];
}

function sortPlayers(players: PlayerSummary[], sortKey: SortKey) {
  return players.toSorted((left, right) => {
    const leftValue = getSortValue(left, sortKey);
    const rightValue = getSortValue(right, sortKey);

    if (typeof leftValue === "string" && typeof rightValue === "string") {
      return leftValue.localeCompare(rightValue);
    }

    return Number(rightValue) - Number(leftValue) || left.player_name.localeCompare(right.player_name);
  });
}

function formatLeaderboardSecondary(player: PlayerSummary, key: LeaderboardKey) {
  if (key === "goals") return `${player.assists} assists`;
  if (key === "assists") return `${player.goals} goals`;
  if (key === "goal_contributions") return `${player.appearances} appearances`;
  if (key === "appearances") return `${player.starts} starts`;
  if (key === "starts") return formatStartsShare(player.starts_share);
  if (key === "cards") return `${player.appearances} appearances`;
  return `${player.goal_contributions} goal contributions`;
}

function formatLeaderboardPrimary(player: PlayerSummary, key: LeaderboardKey) {
  if (key === "goals") return player.goals.toLocaleString();
  if (key === "assists") return player.assists.toLocaleString();
  if (key === "goal_contributions") return player.goal_contributions.toLocaleString();
  if (key === "appearances") return player.appearances.toLocaleString();
  if (key === "starts") return player.starts.toLocaleString();
  if (key === "cards") return player.cards.toLocaleString();
  return player.substitutions_on.toLocaleString();
}

function LeaderboardRow({
  player,
  leaderboardKey,
  primaryLabel,
  secondaryLabel,
}: {
  player: PlayerSummary;
  leaderboardKey: LeaderboardKey;
  primaryLabel: string;
  secondaryLabel: string;
}) {
  const teamLabel = player.primary_team ?? player.teams[0] ?? "Team TBC";

  return (
    <Link className="player-board-row" to={`/players/${player.player_slug}`}>
      <div className="player-board-row-copy">
        <div className="player-board-row-heading">
          <strong>{player.player_name}</strong>
          <TeamName className="player-row-team" label={teamLabel} size="small" />
        </div>
        <span>{player.teams.length > 1 ? player.teams.join(", ") : formatLeaderboardSecondary(player, leaderboardKey)}</span>
        <SignalChipGroup emptyLabel="No contribution labels yet" items={getPlayerLabels(player.profile_labels)} maxVisible={3} size="small" />
      </div>
      <div className="player-board-row-metrics">
        <MetricDelta
          label={primaryLabel}
          value={formatLeaderboardPrimary(player, leaderboardKey)}
          context={`${secondaryLabel}: ${formatLeaderboardSecondary(player, leaderboardKey)}`}
          tone={leaderboardKey === "cards" ? "risk" : leaderboardKey === "assists" ? "warning" : "positive"}
        />
        <HorizontalComparisonBar
          label={leaderboardKey === "cards" ? "Discipline split" : "Output mix"}
          segments={
            leaderboardKey === "cards"
              ? [
                  { label: "Yellow", value: player.yellow_cards, tone: "gold" },
                  { label: "Red", value: player.red_cards, tone: "risk" },
                ]
              : [
                  { label: "Goals", value: player.goals, tone: "green" },
                  { label: "Assists", value: player.assists, tone: "gold" },
                ]
          }
          valueFormatter={(value) => value.toLocaleString()}
        />
      </div>
    </Link>
  );
}

function LeaderboardSection({
  keyName,
  leaderboard,
  primaryLabel,
  secondaryLabel,
  text,
  title,
}: {
  keyName: LeaderboardKey;
  leaderboard: PlayerSummary[];
  primaryLabel: string;
  secondaryLabel: string;
  text: string;
  title: string;
}) {
  if (!leaderboard.length) {
    return (
      <article className="panel player-board-panel">
        <ReportSectionHeader title={title} text={text} />
        <EmptyState message="No leaderboard data is available for this module yet." />
      </article>
    );
  }

  return (
    <article className="panel player-board-panel">
      <ReportSectionHeader title={title} text={text} />
      <ShowMoreList
        className="player-board-list"
        getKey={(player) => player.player_slug}
        initialCount={3}
        itemNoun="player"
        items={leaderboard}
        renderItem={(player) => (
          <LeaderboardRow
            leaderboardKey={keyName}
            player={player}
            primaryLabel={primaryLabel}
            secondaryLabel={secondaryLabel}
          />
        )}
      />
    </article>
  );
}

export function PlayersPage({ data, loadState, selectedSeason, selectedSeasonInfo }: PageProps) {
  const [leaderboardsView, setLeaderboardsView] = useState<LeaderboardsViewState>({
    leaderboards: null,
    requestKey: "",
    status: "success",
  });
  const [{ minimumAppearances, searchTerm, sortKey, teamFilter }, updateFilters] = useReducer(playerBoardFilterReducer, {
    minimumAppearances: "0",
    searchTerm: "",
    sortKey: "goal_contributions",
    teamFilter: "all",
  });
  const deferredSearchTerm = useDeferredValue(searchTerm);

  const players = data.players;
  const seasonLabel = getSelectedSeasonLabel(selectedSeason, selectedSeasonInfo);

  useEffect(() => {
    let ignore = false;

    apiClient
      .getPlayerLeaderboards(toApiSeason(selectedSeason), 8)
      .then((response) => {
        if (!ignore) {
          setLeaderboardsView({ leaderboards: response, requestKey: selectedSeason, status: "success" });
        }
      })
      .catch(() => {
        if (!ignore) {
          setLeaderboardsView({ leaderboards: null, requestKey: selectedSeason, status: "error" });
        }
      });

    return () => {
      ignore = true;
    };
  }, [selectedSeason]);

  const leaderboardState: LeaderboardState = leaderboardsView.requestKey === selectedSeason ? leaderboardsView.status : "loading";
  const leaderboards = leaderboardsView.requestKey === selectedSeason ? leaderboardsView.leaderboards : null;

  const teamOptions = useMemo(() => {
    const names = new Set<string>();
    players.forEach((player) => {
      player.teams.forEach((team) => names.add(team));
      if (player.primary_team) names.add(player.primary_team);
    });
    return Array.from(names).toSorted((left, right) => left.localeCompare(right));
  }, [players]);

  const filteredPlayers = useMemo(() => {
    const minAppearances = Number(minimumAppearances) || 0;
    const normalizedSearch = deferredSearchTerm.trim().toLowerCase();

    return sortPlayers(
      players.filter((player) => {
        const matchesSearch =
          normalizedSearch.length === 0 ||
          player.player_name.toLowerCase().includes(normalizedSearch) ||
          player.teams.some((team) => team.toLowerCase().includes(normalizedSearch));
        const matchesTeam =
          teamFilter === "all" || player.primary_team === teamFilter || player.teams.includes(teamFilter);
        return matchesSearch && matchesTeam && player.appearances >= minAppearances;
      }),
      sortKey,
    );
  }, [deferredSearchTerm, minimumAppearances, players, sortKey, teamFilter]);

  const contributionSummary = useMemo(() => {
    const goalContributors = players.filter((player) => player.goals > 0).length;
    const assistContributors = players.filter((player) => player.assists > 0).length;
    const regularStarters = players.filter((player) => (player.starts_share ?? 0) >= 0.6).length;
    const playersWithCards = players.filter((player) => player.cards > 0).length;
    const multiTeamPlayers = players.filter((player) => player.teams.length > 1).length;

    return {
      assistContributors,
      goalContributors,
      multiTeamPlayers,
      playersWithCards,
      regularStarters,
    };
  }, [players]);

  const scatterData = useMemo(() => {
    return filteredPlayers
      .filter((player) => player.starts > 0 || player.goals > 0)
      .slice(0, 24)
      .map((player) => ({
        group: player.primary_team,
        href: `/players/${player.player_slug}`,
        id: player.player_slug,
        label: player.player_name,
        tone: (player.goal_contributions > 0 ? "green" : player.cards > 0 ? "gold" : "muted") as IntelligenceTone,
        x: player.starts,
        y: player.goals,
      }));
  }, [filteredPlayers]);

  const qualityNote =
    leaderboards?.data_quality_note ??
    "Player summaries depend on available lineups and event timelines, so read them as source-backed indicators rather than official awards.";

  return (
    <article className="player-board-page">
      <PageIntro
        eyebrow="Player contribution board"
        title="Players"
        text={`Explore player contribution through available UPL lineup and event data in ${seasonLabel.toLowerCase()} — goals, assists, appearances, starts, discipline, and involvement patterns.`}
      />

      <DataQualityNote compact note={qualityNote} title="Source-backed player summaries" tone="caution" />

      <section className="metric-grid compact-metrics" aria-label="Player contribution summary">
        <KpiCard label="Players tracked" value={players.length} context={`Distinct player profiles in ${seasonLabel.toLowerCase()}.`} variant="compact" />
        <KpiCard accent="green" label="Goal contributors" value={contributionSummary.goalContributors} context="Players with at least one recorded goal in available data." variant="compact" />
        <KpiCard accent="gold" label="Assist contributors" value={contributionSummary.assistContributors} context="Players credited with at least one assist in the source timeline." variant="compact" />
        <KpiCard label="Regular starters" value={contributionSummary.regularStarters} context="Starts share of 60% or higher in available lineup records." variant="compact" />
        <KpiCard label="Players with cards" value={contributionSummary.playersWithCards} context="Visible discipline signals from recorded yellow and red cards." variant="compact" />
        {contributionSummary.multiTeamPlayers > 0 ? (
          <KpiCard label="Multi-team profiles" value={contributionSummary.multiTeamPlayers} context="Players whose selected-season summary spans more than one listed team." variant="compact" />
        ) : null}
      </section>

      <section className="player-board-grid" aria-label="Grouped player leaderboards">
        {leaderboardSections.map((section) => (
          <LeaderboardSection
            key={section.key}
            keyName={section.key}
            leaderboard={leaderboards?.[section.key] ?? []}
            primaryLabel={section.primaryLabel}
            secondaryLabel={section.secondaryLabel}
            text={section.text}
            title={section.title}
          />
        ))}
      </section>

      <section className="panel player-board-panel">
        <ReportSectionHeader
          title="Goals versus starts"
          text="This comparison helps separate regular starters from players with visible scoring output in available data. It is a contribution view, not a quality verdict."
        />
        <ScatterComparisonPlot
          data={scatterData}
          description="Higher starts often signal a stable role. Higher goals signal recorded finishing output. Some players appear in one dimension more than the other."
          emptyLabel="No player comparison points fit the current filters yet."
          title="Starts on one axis, goals on the other"
          xLabel="Starts"
          yLabel="Goals"
        />
      </section>

      <section className="panel player-board-panel">
        <ReportSectionHeader
          title="Filter the player pool"
          text="Narrow the board by name, team, contribution sort, or a minimum appearance floor before opening an individual profile."
        />
        <div className="filter-grid player-filter-grid" aria-label="Player filters">
          <label>
            Search player
            <input
              onChange={(event) => updateFilters({ type: "search", value: event.target.value })}
              placeholder="Search by player or team"
              type="search"
              value={searchTerm}
            />
          </label>
          <label>
            Team
            <select onChange={(event) => updateFilters({ type: "team", value: event.target.value })} value={teamFilter}>
              <option value="all">All teams</option>
              {teamOptions.map((team) => (
                <option key={team} value={team}>
                  {team}
                </option>
              ))}
            </select>
          </label>
          <label>
            Sort by
            <select onChange={(event) => updateFilters({ type: "sort", value: event.target.value as SortKey })} value={sortKey}>
              {sortOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Minimum appearances
            <select onChange={(event) => updateFilters({ type: "minimumAppearances", value: event.target.value })} value={minimumAppearances}>
              <option value="0">Any</option>
              <option value="3">3+</option>
              <option value="5">5+</option>
              <option value="8">8+</option>
              <option value="10">10+</option>
            </select>
          </label>
        </div>
      </section>

      <section className="panel">
        <ReportSectionHeader
          title="Contribution list"
          text="This list keeps goals and assists in view, but it also shows appearances, starts, cards, and profile labels so the page reads as a contribution board rather than a scorers archive."
        />
        {filteredPlayers.length > 0 ? (
          <EditorialTable className="player-table-shell">
            <EditorialTableHeader
              className="player-table-header player-contribution-table-header"
              columns={[
                { label: "Player contribution profile" },
                { align: "right", label: "Goals" },
                { align: "right", label: "Assists" },
                { align: "right", label: "Apps" },
                { align: "right", label: "Starts" },
                { align: "right", label: "G+A" },
                { align: "right", label: "Cards" },
              ]}
            />
            <ShowMoreList
              as="ul"
              className="player-list player-table-list"
              getKey={(player) => player.player_slug}
              initialCount={18}
              itemNoun="player"
              items={filteredPlayers}
              renderItem={(player) => (
                <li>
                  <PlayerRow player={player} />
                </li>
              )}
            />
          </EditorialTable>
        ) : (
          <EmptyState message={loadState === "loading" ? "Loading player summaries." : "No players fit the current contribution filters."} />
        )}
      </section>

      <section className="panel player-board-panel">
        <ReportSectionHeader
          title="How to read this board"
          text="Use goals, assists, starts, bench listings, and cards together. A high placement in one list does not make this an official ranking or award."
        />
        <div className="player-board-reading-grid">
          <article>
            <strong>Regular starters</strong>
            <p>Look for high starts and strong starts share, not only appearance totals.</p>
          </article>
          <article>
            <strong>Bench impact</strong>
            <p>Substitution-on counts and goal contributions can highlight players who influence matches without starting often.</p>
          </article>
          <article>
            <strong>Discipline signals</strong>
            <p>Cards belong in the reading, especially when they show up alongside lower appearance totals.</p>
          </article>
        </div>
      </section>

      <DataQualityNote
        metrics={[
          { detail: "Available lineup and event summaries in the selected season.", label: "Profiles", value: players.length },
          { detail: "Grouped contribution modules for the selected season.", label: "Board source", value: leaderboards ? "Live" : leaderboardState === "error" ? "Unavailable" : "Loading" },
        ]}
        note="Player data comes from available lineup and event records. Some seasons or matches may have incomplete player-level coverage, so use these totals as indicators rather than official awards."
        title="Player data caveat"
        tone={leaderboardState === "error" ? "risk" : "caution"}
      />

      {leaderboardState === "error" ? (
        <p className="player-board-footnote">
          Grouped leaderboards could not be loaded, so the page is relying on the season player summaries that were already available.
        </p>
      ) : null}

      {players.length === 0 && loadState !== "loading" ? (
        <section className="panel player-board-panel">
          <EmptyState message="No player contribution summaries are available in the selected season yet." />
          <Link className="text-button" to="/matches">
            View match briefs
          </Link>
        </section>
      ) : null}
    </article>
  );
}
