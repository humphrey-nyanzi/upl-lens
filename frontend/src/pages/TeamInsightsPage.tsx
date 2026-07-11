import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import type { TeamProfileLabel, TeamResponse } from "../api/types";
import type { PageProps } from "../app/types";
import { EmptyState } from "../components/common/EmptyState";
import { PageIntro } from "../components/common/PageIntro";
import { ReportSectionHeader } from "../components/common/ReportSectionHeader";
import { ShowMoreList } from "../components/common/ShowMoreList";
import { TeamMarker } from "../components/common/TeamMarker";
import { DataQualityNote } from "../components/intelligence/DataQualityNote";
import { MetricDelta } from "../components/intelligence/MetricDelta";
import { ScatterComparisonPlot } from "../components/intelligence/ScatterComparisonPlot";
import { SignalChip, SignalChipGroup, type SignalChipItem, type SignalTone as ComponentSignalTone } from "../components/intelligence/SignalChip";
import { formatSeason } from "../utils/format";
import { getSelectedSeasonLabel } from "../utils/seasonScope";
import { formatGoalDifference, getTeamFixtureNote, getTeamPoints, getTeamPointsNote, getTeamSlug } from "../utils/teams";

type TeamBoardSortKey =
  | "points"
  | "goal_difference"
  | "goals_per_match"
  | "conceded_per_match"
  | "win_rate"
  | "name";

type RankingSection = {
  key: string;
  title: string;
  description: string;
  teams: TeamResponse[];
  metricLabel: string;
  signalKeys: string[];
  getMetric: (team: TeamResponse) => string;
  getSupport: (team: TeamResponse) => string;
};

const sortOptions: { label: string; value: TeamBoardSortKey }[] = [
  { label: "Points", value: "points" },
  { label: "Goal difference", value: "goal_difference" },
  { label: "Goals per match", value: "goals_per_match" },
  { label: "Conceded per match", value: "conceded_per_match" },
  { label: "Win rate", value: "win_rate" },
  { label: "Team name", value: "name" },
];

function formatRate(value: number | null | undefined) {
  if (value === null || value === undefined) return "Unavailable";
  return value.toFixed(2);
}


function getTeamHref(team: TeamResponse) {
  return `/teams/${team.team_slug ?? getTeamSlug(team.team_name)}`;
}

function getLabelItems(labels: TeamProfileLabel[]): SignalChipItem[] {
  return labels.map((label) => ({
    key: label.key,
    label: label.label,
    tone: label.tone as ComponentSignalTone,
    description: label.description,
  }));
}

function hasDataCaveat(team: TeamResponse) {
  return team.administrative_matches > 0 || team.missing_matches > 0 || Boolean(team.points_note);
}

function compareNullableRate(
  left: number | null,
  right: number | null,
  direction: "asc" | "desc" = "desc",
) {
  const leftValue = left ?? (direction === "desc" ? Number.NEGATIVE_INFINITY : Number.POSITIVE_INFINITY);
  const rightValue = right ?? (direction === "desc" ? Number.NEGATIVE_INFINITY : Number.POSITIVE_INFINITY);
  return direction === "desc" ? rightValue - leftValue : leftValue - rightValue;
}

function sortTeamsForBoard(teams: TeamResponse[], sortKey: TeamBoardSortKey) {
  return teams.toSorted((left, right) => {
    if (sortKey === "name") return left.team_name.localeCompare(right.team_name);
    if (sortKey === "points") {
      return getTeamPoints(right) - getTeamPoints(left) || right.goal_difference - left.goal_difference;
    }
    if (sortKey === "conceded_per_match") {
      return compareNullableRate(left.conceded_per_match, right.conceded_per_match, "asc") || left.team_name.localeCompare(right.team_name);
    }
    if (sortKey === "goals_per_match") {
      return compareNullableRate(left.goals_per_match, right.goals_per_match) || left.team_name.localeCompare(right.team_name);
    }
    if (sortKey === "win_rate") {
      return compareNullableRate(left.win_rate, right.win_rate) || getTeamPoints(right) - getTeamPoints(left);
    }
    return right.goal_difference - left.goal_difference || getTeamPoints(right) - getTeamPoints(left);
  });
}

function getTopTeam(
  teams: TeamResponse[],
  getValue: (team: TeamResponse) => number | null,
  direction: "asc" | "desc" = "desc",
) {
  let selectedTeam: TeamResponse | null = null;
  let selectedValue = direction === "desc" ? Number.NEGATIVE_INFINITY : Number.POSITIVE_INFINITY;

  for (const team of teams) {
    const value = getValue(team);
    if (value === null) continue;
    if ((direction === "desc" && value > selectedValue) || (direction === "asc" && value < selectedValue)) {
      selectedTeam = team;
      selectedValue = value;
    }
  }

  return selectedTeam;
}

function TeamBoardSkeleton() {
  return (
    <div className="team-board-skeleton" aria-busy="true" aria-label="Loading team intelligence">
      <section className="team-intelligence-summary">
        {Array.from({ length: 5 }, (_, index) => (
          <article className="metric-delta skeleton-card" key={index}>
            <span className="skeleton-line short" />
            <span className="skeleton-line number" />
            <span className="skeleton-line medium" />
          </article>
        ))}
      </section>
      <section className="team-comparison-grid">
        <article className="panel team-board-panel skeleton-panel">
          <span className="skeleton-line medium" />
          <span className="skeleton-line" />
          <span className="trends-chart-skeleton" />
        </article>
        <article className="panel team-board-panel skeleton-panel">
          <span className="skeleton-line medium" />
          <span className="skeleton-line" />
          <span className="trends-chart-skeleton" />
        </article>
      </section>
    </div>
  );
}

function RankingRow({
  metricLabel,
  preferredSignalKeys,
  rank,
  support,
  team,
  value,
}: {
  metricLabel: string;
  preferredSignalKeys: string[];
  rank: number;
  support: string;
  team: TeamResponse;
  value: string;
}) {
  const signalItems = getLabelItems(team.profile_labels);
  const primarySignal = preferredSignalKeys
    .map((key) => signalItems.find((signal) => signal.key === key))
    .find((signal) => signal !== undefined);
  const supportingSignals = signalItems.filter((signal) => signal !== primarySignal);

  return (
    <Link className="team-ranking-row" to={getTeamHref(team)}>
      <span className="team-ranking-rank">{rank}</span>
      <TeamMarker label={team.team_name} size="small" />
      <div className="team-ranking-copy">
        <strong>{team.team_name}</strong>
        <div className="team-ranking-signal">
          {primarySignal ? <SignalChip description={primarySignal.description} label={primarySignal.label} size="small" tone={primarySignal.tone} /> : null}
          <span>{primarySignal?.description ?? support}</span>
        </div>
        {supportingSignals.length ? (
          <SignalChipGroup items={supportingSignals} maxVisible={1} overflowMode="inline-summary" size="small" />
        ) : null}
      </div>
      <div className="team-ranking-metric">
        <span>{metricLabel}</span>
        <strong>{value}</strong>
        <small>{support}</small>
      </div>
    </Link>
  );
}

function TeamBoardCard({ rank, team }: { rank: number; team: TeamResponse }) {
  const fixtureNote = getTeamFixtureNote(team);
  const pointsNote = getTeamPointsNote(team);
  const signalItems = getLabelItems(team.profile_labels);
  const primarySignal = signalItems.at(0);
  const supportingSignals = signalItems.slice(1);

  return (
    <article className="team-board-card">
      <div className="team-board-card-header">
        <div className="team-board-title">
          <span className="team-rank">{rank}</span>
          <TeamMarker label={team.team_name} size="small" />
          <div>
            <strong>{team.team_name}</strong>
          </div>
        </div>
        <Link className="text-button compact-result-link" to={getTeamHref(team)}>
          Open profile
        </Link>
      </div>

      <div className="team-board-signal">
        {primarySignal ? <SignalChip description={primarySignal.description} label={primarySignal.label} size="small" tone={primarySignal.tone} /> : null}
        <p>
          {primarySignal?.description ?? `${team.wins}W ${team.draws}D ${team.losses}L, with ${getTeamPoints(team)} official points.`}
        </p>
      </div>

      <dl className="team-board-card-stats" aria-label={`${team.team_name} supporting team facts`}>
        <div>
          <dt>Record</dt>
          <dd>{team.wins}W {team.draws}D {team.losses}L, {getTeamPoints(team)} pts</dd>
        </div>
        <div>
          <dt>Goal difference</dt>
          <dd>{formatGoalDifference(team.goal_difference)}</dd>
        </div>
        <div>
          <dt>Goals per match</dt>
          <dd>{formatRate(team.goals_per_match)}</dd>
        </div>
        <div>
          <dt>Conceded per match</dt>
          <dd>{formatRate(team.conceded_per_match)}</dd>
        </div>
      </dl>

      {supportingSignals.length ? <SignalChipGroup items={supportingSignals} maxVisible={3} size="small" /> : null}

      {fixtureNote || pointsNote ? (
        <DataQualityNote
          compact
          note={[fixtureNote, pointsNote].filter(Boolean).join(" ")}
          title="Team data note"
          tone="caution"
        />
      ) : null}
    </article>
  );
}

export function TeamInsightsPage({ data, loadState, onRefresh, selectedSeason, selectedSeasonInfo }: PageProps) {
  const [teamQuery, setTeamQuery] = useState("");
  const [sortKey, setSortKey] = useState<TeamBoardSortKey>("points");
  const seasonLabel = getSelectedSeasonLabel(selectedSeason, selectedSeasonInfo);
  const teams = data.teams;

  const filteredTeams = useMemo(() => {
    const normalizedQuery = teamQuery.trim().toLowerCase();
    const matchingTeams = normalizedQuery
      ? teams.filter((team) => team.team_name.toLowerCase().includes(normalizedQuery))
      : teams;

    return sortTeamsForBoard(matchingTeams, sortKey);
  }, [teams, sortKey, teamQuery]);

  const topAttack = getTopTeam(teams, (team) => team.goals_per_match);
  const tightestDefence = getTopTeam(teams, (team) => team.conceded_per_match, "asc");
  const bestGoalDifference = getTopTeam(teams, (team) => team.goal_difference);
  const bestPointsPerMatch = getTopTeam(teams, (team) => team.points_per_match);
  const mostOpenProfile = getTopTeam(teams, (team) =>
    team.goals_per_match !== null && team.conceded_per_match !== null
      ? team.goals_per_match + team.conceded_per_match
      : null,
  );
  const dataCaveatTeams = teams.filter(hasDataCaveat);
  const hasPointsPerMatch = teams.some((team) => team.points_per_match !== null);

  const attackDefenceData = teams.reduce<Array<{ id: string; label: string; x: number; y: number; tone: "gold" | "green"; href: string }>>((points, team) => {
    if (team.goals_per_match === null || team.conceded_per_match === null) return points;
    points.push({
      id: team.team_slug ?? team.team_name,
      label: team.team_name,
      x: team.goals_per_match,
      y: team.conceded_per_match,
      tone: hasDataCaveat(team) ? ("gold" as const) : ("green" as const),
      href: getTeamHref(team),
    });
    return points;
  }, []);

  const pointsGoalDifferenceData = teams.reduce<Array<{ id: string; label: string; x: number; y: number; tone: "gold" | "navy"; href: string }>>((points, team) => {
    if (hasPointsPerMatch && team.points_per_match === null) return points;
    points.push({
      id: team.team_slug ?? team.team_name,
      label: team.team_name,
      x: team.goal_difference,
      y: hasPointsPerMatch ? team.points_per_match ?? 0 : getTeamPoints(team),
      tone: hasDataCaveat(team) ? ("gold" as const) : ("navy" as const),
      href: getTeamHref(team),
    });
    return points;
  }, []);

  const rankingSections: RankingSection[] = [
    {
      key: "record",
      title: "Record",
      description: "Official points and results context.",
      teams: sortTeamsForBoard(teams, "points").slice(0, 5),
      metricLabel: "Points",
      signalKeys: ["results_team", "needs_results"],
      getMetric: (team) => getTeamPoints(team).toLocaleString(),
      getSupport: (team) => `${team.wins}W ${team.draws}D ${team.losses}L`,
    },
    {
      key: "attack",
      title: "Attack",
      description: "Scoring rate across available matches.",
      teams: sortTeamsForBoard(teams, "goals_per_match").slice(0, 5),
      metricLabel: "G/match",
      signalKeys: ["strong_attack"],
      getMetric: (team) => formatRate(team.goals_per_match),
      getSupport: (team) => `${team.goals_for} goals for`,
    },
    {
      key: "defence",
      title: "Defence",
      description: "Lower conceded rate is stronger here.",
      teams: sortTeamsForBoard(teams, "conceded_per_match").slice(0, 5),
      metricLabel: "Conceded/match",
      signalKeys: ["tight_defence"],
      getMetric: (team) => formatRate(team.conceded_per_match),
      getSupport: (team) => `${team.goals_against} goals against`,
    },
    {
      key: "efficiency",
      title: "Efficiency",
      description: "Points collected per played match.",
      teams: teams
        .filter((team) => team.points_per_match !== null)
        .sort((left, right) => (right.points_per_match ?? 0) - (left.points_per_match ?? 0))
        .slice(0, 5),
      metricLabel: "Pts/match",
      signalKeys: ["results_team", "needs_results"],
      getMetric: (team) => formatRate(team.points_per_match),
      getSupport: (team) => `${getTeamPoints(team)} official points`,
    },
    {
      key: "caveats",
      title: "Data caveats",
      description: "Teams with administrative, missing, or points notes.",
      teams: dataCaveatTeams.slice(0, 5),
      metricLabel: "Caveat",
      signalKeys: ["data_caveat"],
      getMetric: (team) => `${team.administrative_matches + team.missing_matches}`,
      getSupport: (team) => getTeamFixtureNote(team) || getTeamPointsNote(team) || "Review note",
    },
  ];

  const couldNotLoad = loadState === "error" && teams.length === 0;

  return (
    <div className="team-board-page">
      <PageIntro
        variant="dense"
        eyebrow="Team intelligence board"
        title="Teams"
        text={`Compare UPL teams by record, scoring profile, defensive strength, and season-level performance signals. ${seasonLabel}.`}
      />

      {couldNotLoad ? (
        <section className="error-panel" role="alert">
          <span className="eyebrow">Teams</span>
          <h2>Could not load team intelligence</h2>
          <p>The team board did not load for the current scope. The data service may be waking up.</p>
          <button className="text-button" type="button" onClick={onRefresh}>
            Retry
          </button>
        </section>
      ) : null}

      {loadState === "loading" && teams.length === 0 ? <TeamBoardSkeleton /> : null}

      {teams.length > 0 ? (
        <>
          <section className="team-intelligence-summary" aria-label="Team intelligence summary">
            <MetricDelta label="Teams tracked" value={teams.length} context={seasonLabel} tone="neutral" />
            {topAttack ? (
              <MetricDelta
                label="Top attack"
                value={formatRate(topAttack.goals_per_match)}
                context={`${topAttack.team_name}, ${topAttack.goals_for} goals scored.`}
                tone="positive"
              />
            ) : null}
            {tightestDefence ? (
              <MetricDelta
                label="Tightest defence"
                value={formatRate(tightestDefence.conceded_per_match)}
                context={`${tightestDefence.team_name}, ${tightestDefence.goals_against} conceded.`}
                tone="positive"
              />
            ) : null}
            {bestGoalDifference ? (
              <MetricDelta
                label="Best goal difference"
                value={formatGoalDifference(bestGoalDifference.goal_difference)}
                context={`${bestGoalDifference.team_name}, ${getTeamPoints(bestGoalDifference)} points.`}
                tone="neutral"
              />
            ) : null}
            {bestPointsPerMatch ? (
              <MetricDelta
                label="Highest points/match"
                value={formatRate(bestPointsPerMatch.points_per_match)}
                context={bestPointsPerMatch.team_name}
                tone="neutral"
              />
            ) : null}
            {mostOpenProfile ? (
              <MetricDelta
                label="Most open profile"
                value={formatRate((mostOpenProfile.goals_per_match ?? 0) + (mostOpenProfile.conceded_per_match ?? 0))}
                context={`${mostOpenProfile.team_name}, combined goals for and against per match.`}
                tone="warning"
              />
            ) : null}
          </section>

          <section className="team-comparison-grid" aria-label="Team comparison maps">
            <article className="panel team-board-panel">
              <ScatterComparisonPlot
                data={attackDefenceData}
                description="Goals scored and conceded per match help show whether teams are balanced, attack-led, defence-led, or open. Lower conceded per match is better."
                emptyLabel="Attack and defence rate data is not available for this season yet."
                title="Attack vs defence map"
                xFormatter={(value) => value.toFixed(2)}
                xLabel="Goals per match"
                yFormatter={(value) => value.toFixed(2)}
                yLabel="Conceded per match"
              />
            </article>
            <article className="panel team-board-panel">
              <ScatterComparisonPlot
                data={pointsGoalDifferenceData}
                description="Goal difference and points collection show how scoring balance lines up with results."
                emptyLabel="Points and goal-difference data is not available for this season yet."
                title="Points vs goal difference"
                xFormatter={(value) => formatGoalDifference(value)}
                xLabel="Goal difference"
                yFormatter={(value) => value.toFixed(2)}
                yLabel={hasPointsPerMatch ? "Points per match" : "Official points"}
              />
            </article>
          </section>

          <section className="team-rankings-grid" aria-label="Team signal rankings">
            {rankingSections.map((section) => (
              <article className="panel team-ranking-panel" key={section.key}>
                <div className="section-heading compact">
                  <div>
                    <h2>{section.title}</h2>
                    <p>{section.description}</p>
                  </div>
                </div>
                {section.teams.length > 0 ? (
                  <div className="team-ranking-list">
                    {section.teams.map((team, index) => (
                      <RankingRow
                        key={team.team_name}
                        metricLabel={section.metricLabel}
                        preferredSignalKeys={section.signalKeys}
                        rank={index + 1}
                        support={section.getSupport(team)}
                        team={team}
                        value={section.getMetric(team)}
                      />
                    ))}
                  </div>
                ) : (
                  <EmptyState message="No teams match this signal yet." />
                )}
              </article>
            ))}
          </section>

          <section className="panel team-board-panel">
            <ReportSectionHeader
              title="Team profile list"
              text="Search, sort, and open team dossiers with record, scoring profile, labels, and caveats kept visible."
            />
            <div className="filter-grid team-filter-grid" aria-label="Team filters">
              <label>
                Search teams
                <input
                  className="filter-input"
                  onChange={(event) => setTeamQuery(event.target.value)}
                  placeholder="Search by team name"
                  type="search"
                  value={teamQuery}
                />
              </label>
              <label>
                Sort by
                <select value={sortKey} onChange={(event) => setSortKey(event.target.value as TeamBoardSortKey)}>
                  {sortOptions.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            {filteredTeams.length > 0 ? (
              <ShowMoreList
                className="team-board-card-list"
                getKey={(team) => team.team_name}
                initialCount={8}
                itemNoun="team"
                items={filteredTeams}
                renderItem={(team, index) => <TeamBoardCard rank={index + 1} team={team} />}
              />
            ) : (
              <EmptyState message="No teams match the current search." />
            )}
          </section>

          {dataCaveatTeams.length > 0 ? (
            <DataQualityNote
              metrics={[
                { label: "Teams with caveats", value: dataCaveatTeams.length },
                { label: "Season", value: selectedSeason === "all" ? "All seasons" : formatSeason(selectedSeason) },
              ]}
              note="Administrative results, missing fixtures, or official points notes can affect how team comparisons should be read."
              title="Team data caveats"
              tone="caution"
            />
          ) : null}
        </>
      ) : loadState !== "loading" && !couldNotLoad ? (
        <EmptyState message="No team summaries are available for this season yet." />
      ) : null}
    </div>
  );
}
