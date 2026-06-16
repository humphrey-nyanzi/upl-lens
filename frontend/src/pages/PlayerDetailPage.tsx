import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { apiClient, ApiRequestError } from "../api/client";
import type { PlayerDetailResponse, PlayerProfileLabel } from "../api/types";
import type { PageProps } from "../app/types";
import { DisclosureSection } from "../components/common/DisclosureSection";
import { EmptyState } from "../components/common/EmptyState";
import { ReportSectionHeader } from "../components/common/ReportSectionHeader";
import { ShowMoreList } from "../components/common/ShowMoreList";
import { DataQualityNote } from "../components/intelligence/DataQualityNote";
import { HorizontalComparisonBar, StackedShareBar } from "../components/intelligence/ComparisonBars";
import { MetricDelta } from "../components/intelligence/MetricDelta";
import { MiniBarChart } from "../components/intelligence/MiniBarChart";
import { SignalChip, SignalChipGroup, type SignalTone } from "../components/intelligence/SignalChip";
import { formatDate, formatPercent, formatScoreline, formatSeason } from "../utils/format";
import { getSelectedSeasonLabel, toApiSeason } from "../utils/seasonScope";
import { getTeamSlug } from "../utils/teams";

type PlayerDetailViewState = {
  errorMessage: string;
  player: PlayerDetailResponse | null;
  requestKey: string;
  status: "success" | "error";
};

function formatRole(role: string | null) {
  if (!role) return "Listed";
  return role.replace(/_/g, " ").replace(/\b\w/g, (character) => character.toUpperCase());
}

function formatRate(value: number | null | undefined, decimals = 2) {
  if (value === null || value === undefined) return "Unavailable";
  return value.toFixed(decimals);
}

function formatStartsShare(value: number | null | undefined) {
  if (value === null || value === undefined) return "Unavailable";
  return formatPercent(value);
}

function buildPlayerStandfirst(player: PlayerDetailResponse, teams: string, seasonLabel: string) {
  return `${player.player_name}'s ${seasonLabel.toLowerCase()} contribution profile brings together output, squad role, discipline, and recent match evidence for ${teams}.`;
}

function getLabelItems(labels: PlayerProfileLabel[]) {
  return labels.map((label) => ({
    key: label.key,
    label: label.label,
    tone: label.tone as SignalTone,
  }));
}

function getPlayerDataTone(player: PlayerDetailResponse) {
  if (player.data_quality_note) return "caution" as const;
  if (player.appearances <= 3) return "limited" as const;
  return "neutral" as const;
}

function PlayerProfileSkeleton() {
  return (
    <div className="player-profile-page" aria-busy="true" aria-label="Loading player contribution profile">
      <section className="player-profile-hero skeleton-panel">
        <span className="skeleton-line short" />
        <span className="skeleton-line title" />
        <span className="skeleton-line" />
      </section>
      <section className="player-contribution-summary-grid">
        {Array.from({ length: 8 }, (_, index) => (
          <article className="metric-delta skeleton-card" key={index}>
            <span className="skeleton-line short" />
            <span className="skeleton-line number" />
            <span className="skeleton-line medium" />
          </article>
        ))}
      </section>
      <section className="player-profile-grid">
        <article className="panel player-profile-panel skeleton-panel">
          <span className="skeleton-line medium" />
          <span className="skeleton-line" />
          <span className="trends-chart-skeleton" />
        </article>
        <article className="panel player-profile-panel skeleton-panel">
          <span className="skeleton-line medium" />
          <span className="skeleton-line" />
          <span className="trends-chart-skeleton" />
        </article>
      </section>
    </div>
  );
}

function PlayerIdentityPanel({ player }: { player: PlayerDetailResponse }) {
  if (player.profile_labels.length === 0) {
    return (
      <section className="panel player-profile-panel">
        <ReportSectionHeader
          eyebrow="Contribution identity"
          title="What does the available data say about this player?"
          text="These profile labels describe the player's visible contribution shape in the selected scope, not a scouting verdict."
        />
        <EmptyState message="No contribution labels are available for this player in the selected scope." />
      </section>
    );
  }

  return (
    <section className="panel player-profile-panel">
      <ReportSectionHeader
        eyebrow="Contribution identity"
        title="What does the available data say about this player?"
        text="These profile labels describe the player's visible contribution shape in the selected scope, not a scouting verdict."
      />
      <div className="player-identity-list">
        {player.profile_labels.map((label) => (
          <article key={label.key}>
            <SignalChip label={label.label} tone={label.tone as SignalTone} />
            <p>{label.label} is one of the contribution categories surfaced from the available lineup and event data.</p>
          </article>
        ))}
      </div>
    </section>
  );
}

function PlayerContributionSummary({ player }: { player: PlayerDetailResponse }) {
  return (
    <section className="player-contribution-summary-grid" aria-label="Player contribution summary">
      <MetricDelta label="Appearances" value={player.appearances} context="Available lineup listings in the selected scope." tone="neutral" />
      <MetricDelta label="Starts" value={player.starts} context={`${formatStartsShare(player.starts_share)} of appearances.`} tone="positive" />
      <MetricDelta label="Goals" value={player.goals} context={`${formatRate(player.goals_per_appearance)} per appearance.`} tone="positive" />
      <MetricDelta label="Assists" value={player.assists} context={`${formatRate(player.assists_per_appearance)} per appearance.`} tone="warning" />
      <MetricDelta label="Goal contributions" value={player.goal_contributions} context={`${formatRate(player.goal_contributions_per_appearance)} per appearance.`} tone="positive" />
      <MetricDelta label="Yellow cards" value={player.yellow_cards} context="Booked events credited in available match timelines." tone="risk" />
      <MetricDelta label="Red cards" value={player.red_cards} context="Dismissals credited in available match timelines." tone="risk" />
      <MetricDelta
        label="Cards per appearance"
        value={formatRate(player.cards_per_appearance)}
        context={player.player_of_match_awards > 0 ? `${player.player_of_match_awards} player-of-match awards.` : "No player-of-match awards recorded."}
        tone="risk"
      />
    </section>
  );
}

function PlayerContributionProfile({ cards, player }: { cards: number; player: PlayerDetailResponse }) {
  return (
    <section className="player-profile-grid">
      <article className="panel player-profile-panel">
        <ReportSectionHeader eyebrow="Output profile" title="Contribution mix" text="Goals and assists are shown together, with cards kept visible as a separate risk signal rather than folded into positive output." />
        <HorizontalComparisonBar
          label="Goals and assists"
          segments={[
            { label: "Goals", value: player.goals, tone: "green" },
            { label: "Assists", value: player.assists, tone: "gold" },
          ]}
          valueFormatter={(value) => value.toLocaleString()}
        />
        {cards > 0 ? (
          <HorizontalComparisonBar
            label="Discipline signal"
            segments={[
              { label: "Yellow cards", value: player.yellow_cards, tone: "gold" },
              { label: "Red cards", value: player.red_cards, tone: "risk" },
            ]}
            valueFormatter={(value) => value.toLocaleString()}
          />
        ) : null}
        <div className="player-profile-mini-metrics">
          <MetricDelta label="Goals per app" value={formatRate(player.goals_per_appearance)} context="Scoring rate from available appearances." tone="positive" />
          <MetricDelta label="G+A per app" value={formatRate(player.goal_contributions_per_appearance)} context="Combined output rate from available appearances." tone="positive" />
        </div>
      </article>

      <article className="panel player-profile-panel">
        <ReportSectionHeader eyebrow="Squad role" title="Starts and bench role" text="Starts, bench listings, and substitution patterns help separate regular starters from players whose main impact comes later in matches." />
        <StackedShareBar
          label="Starts versus bench listings"
          segments={[
            { label: "Starts", value: player.starts, tone: "green" },
            { label: "Bench listings", value: player.bench_listings, tone: "muted" },
          ]}
          valueFormatter={(value, share) => `${value.toLocaleString()} (${formatPercent(share)})`}
        />
        <div className="player-profile-mini-metrics">
          <MetricDelta label="Bench listings" value={player.bench_listings} context="Times listed without starting in available lineup records." tone="neutral" />
          <MetricDelta label="Sub on" value={player.substitutions_on} context="Recorded substitute appearances from the bench." tone="warning" />
          <MetricDelta label="Sub off" value={player.substitutions_off} context="Starts or appearances ending before full time." tone="neutral" />
          <MetricDelta label="Starts share" value={formatStartsShare(player.starts_share)} context="Share of appearances that were starts." tone="positive" />
        </div>
      </article>
    </section>
  );
}

function PlayerSeasonEvidence({
  player,
  seasonTrendData,
}: {
  player: PlayerDetailResponse;
  seasonTrendData: Array<{ key: string; label: string; secondaryValue: number; tone: "green" | "muted"; value: number }>;
}) {
  return (
    <section className="player-profile-grid">
      <article className="panel player-profile-panel">
        <ReportSectionHeader eyebrow="Season trend" title="How output changes by season" text="Goal contribution totals by season keep the trend easy to scan while still staying anchored to the available player records." />
        {seasonTrendData.length > 0 ? (
          <MiniBarChart data={seasonTrendData} description="Bars show goal contributions in each season. Appearance totals remain important context when comparing seasons." emptyLabel="No season trend data is available yet." title="Goal contributions by season" valueFormatter={(value) => value.toLocaleString()} />
        ) : (
          <EmptyState message="No season trend is available for this player yet." />
        )}
      </article>

      <article className="panel player-profile-panel">
        <ReportSectionHeader eyebrow="Season totals" title="Output by season" text="Lineup and event totals are grouped by season so longer-term contribution stays easy to compare without turning into a source-record archive." />
        {player.season_breakdown.length > 0 ? (
          <ShowMoreList
            as="ul"
            className="player-list compact"
            getKey={(season) => season.season}
            initialCount={4}
            itemNoun="season"
            items={player.season_breakdown}
            renderItem={(season) => (
              <li className="player-list-row static player-season-row">
                <div>
                  <strong>{formatSeason(season.season)}</strong>
                  <span>{season.teams.join(", ") || "Team TBC"}</span>
                </div>
                <dl>
                  <div><dt>Apps</dt><dd>{season.appearances}</dd></div>
                  <div><dt>Starts</dt><dd>{season.starts}</dd></div>
                  <div><dt>G+A</dt><dd>{season.goals + season.assists}</dd></div>
                  <div><dt>Cards</dt><dd>{season.yellow_cards + season.red_cards}</dd></div>
                </dl>
              </li>
            )}
          />
        ) : (
          <EmptyState message="No season breakdown is available for this player yet." />
        )}
      </article>
    </section>
  );
}

function RecentInvolvementPanel({ player }: { player: PlayerDetailResponse }) {
  return (
    <section className="panel player-profile-panel">
      <ReportSectionHeader eyebrow="Recent involvement" title="Latest match evidence" text="These match rows show how the recent evidence lines up with the wider contribution profile." />
      {player.recent_matches.length > 0 ? (
        <ShowMoreList
          className="player-match-list"
          getKey={(match) => match.match_id}
          initialCount={5}
          itemNoun="match"
          items={player.recent_matches}
          renderItem={(match) => (
            <Link className="player-match-row" to={`/matches/${match.match_id}`}>
              <div>
                <strong>{match.home_team ?? "Home"} {formatScoreline(match.home_score, match.away_score)} {match.away_team ?? "Away"}</strong>
                <span>{formatDate(match.match_date)} · {formatRole(match.squad_role)} · {match.team_name ?? "Team TBC"}</span>
              </div>
              <small>{match.goals} G · {match.assists} A · {match.yellow_cards + match.red_cards} cards</small>
            </Link>
          )}
        />
      ) : (
        <EmptyState message="No recent match records are available for this player yet." />
      )}
    </section>
  );
}

export default function PlayerDetailPage({ selectedSeason }: Pick<PageProps, "selectedSeason">) {
  const { playerSlug } = useParams();
  const requestKey = `${selectedSeason}|${playerSlug ?? ""}`;
  const [viewState, setViewState] = useState<PlayerDetailViewState>({
    errorMessage: "",
    player: null,
    requestKey: "",
    status: "success",
  });
  const seasonLabel = getSelectedSeasonLabel(selectedSeason);

  useEffect(() => {
    if (!playerSlug) return;

    let ignore = false;

    apiClient
      .getPlayerDetail(playerSlug, toApiSeason(selectedSeason))
      .then((response) => {
        if (!ignore) {
          setViewState({ errorMessage: "", player: response, requestKey, status: "success" });
        }
      })
      .catch((error) => {
        if (!ignore) {
          const errorMessage =
            error instanceof ApiRequestError && error.status === 404
              ? "Player not found in the current scope."
              : error instanceof Error
                ? error.message
                : "Could not load player contribution profile.";
          setViewState({ errorMessage, player: null, requestKey, status: "error" });
        }
      });

    return () => {
      ignore = true;
    };
  }, [playerSlug, requestKey, selectedSeason]);

  const loadState = viewState.requestKey === requestKey ? viewState.status : "loading";
  const player = viewState.requestKey === requestKey ? viewState.player : null;
  const errorMessage = viewState.requestKey === requestKey ? viewState.errorMessage : "";

  const seasonTrendData = useMemo(() => {
    return (player?.season_trend ?? []).map((point) => ({
      key: point.season,
      label: formatSeason(point.season),
      secondaryValue: point.appearances,
      tone: point.goal_contributions > 0 ? ("green" as const) : ("muted" as const),
      value: point.goal_contributions,
    }));
  }, [player]);

  if (loadState === "loading") {
    return <PlayerProfileSkeleton />;
  }

  if (!player) {
    return (
      <section className="error-panel player-profile-error" role="alert">
        <p className="eyebrow">Player contribution profile</p>
        <h1>{errorMessage || "Could not load player contribution profile."}</h1>
        <div className="match-detail-actions">
          <Link className="text-button" to="/players">
            Back to Players
          </Link>
        </div>
      </section>
    );
  }

  const teams = player.teams.length > 0 ? player.teams.join(", ") : "Team TBC";
  const cards = player.yellow_cards + player.red_cards;
  const standfirst = buildPlayerStandfirst(player, teams, seasonLabel);
  const primaryTeam = player.primary_team ?? player.teams[0] ?? null;
  const dataTone = getPlayerDataTone(player);
  const contributionLabels = getLabelItems(player.profile_labels);

  return (
    <article className="player-profile-page">
      <Link className="text-button back-link" to="/players">
        Back to Players
      </Link>

      <header className="player-profile-hero player-profile-header lens-fused-hero">
        <div className="player-profile-hero-copy lens-fused-hero-copy">
          <span className="eyebrow">Player contribution profile</span>
          <h1>{player.player_name}</h1>
          <p>
            {seasonLabel} · {teams}
          </p>
          <p className="report-standfirst">{standfirst}</p>
          <SignalChipGroup emptyLabel="No contribution labels yet" items={contributionLabels} maxVisible={5} />
        </div>
        <SignalChip
          label={dataTone === "limited" ? "Limited player data" : dataTone === "caution" ? "Read with context" : "Available data"}
          tone={dataTone === "limited" ? "muted" : dataTone === "caution" ? "warning" : "neutral"}
        />
      </header>

      <DataQualityNote
        compact
        note={
          player.data_quality_note ??
          "This player profile is built from available lineups and event timelines, so treat it as a source-backed contribution summary rather than an official ranking."
        }
        title="Player data caveat"
        tone={dataTone}
      />

      <PlayerIdentityPanel player={player} />
      <PlayerContributionSummary player={player} />
      <PlayerContributionProfile cards={cards} player={player} />
      <PlayerSeasonEvidence player={player} seasonTrendData={seasonTrendData} />
      <RecentInvolvementPanel player={player} />

      <DisclosureSection
        description="Open the detailed player-data caveat and coverage metrics."
        eyebrow="Evidence quality"
        title="How reliable is this profile?"
      >
        <DataQualityNote
          metrics={[
            { detail: "Available lineup records in the selected scope.", label: "Appearances", value: player.appearances },
            { detail: "Starts as a share of appearances.", label: "Starts share", value: formatStartsShare(player.starts_share) },
            { detail: "Cards divided by appearances when possible.", label: "Cards/app", value: formatRate(player.cards_per_appearance) },
          ]}
          note="Player data depends on lineup availability and event parsing. Strong totals are still useful, but quieter profiles can reflect missing coverage as well as lower contribution."
          title="Player data detail"
          tone={dataTone}
        />
      </DisclosureSection>

      <section className="panel related-actions-panel">
        <ReportSectionHeader
          eyebrow="Next step"
          title="Follow the contribution signal"
          text="Move from this profile back into the player board, team context, or supporting match evidence."
        />
        <div className="match-detail-actions">
          <Link className="text-button" to="/players">
            Back to Players
          </Link>
          {primaryTeam ? (
            <Link className="text-button" to={`/teams/${getTeamSlug(primaryTeam)}`}>
              View {primaryTeam}
            </Link>
          ) : null}
          <Link className="text-button" to="/matches">
            View match briefs
          </Link>
        </div>
      </section>
    </article>
  );
}
