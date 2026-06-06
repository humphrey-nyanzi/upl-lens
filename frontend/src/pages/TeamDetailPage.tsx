import { useCallback, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

import { apiClient } from "../api/client";
import type {
  DataQualityStatus,
  TeamFormMatch,
  TeamProfileLabel,
  TeamProfileMatch,
  TeamProfileResponse,
  TeamSplitRecord,
} from "../api/types";
import type { PageProps } from "../app/types";
import { EmptyState } from "../components/common/EmptyState";
import { ReportSectionHeader } from "../components/common/ReportSectionHeader";
import { TeamMarker } from "../components/common/TeamMarker";
import {
  DataQualityNote,
  FormStrip,
  HorizontalComparisonBar,
  MetricDelta,
  MiniBarChart,
  SignalChip,
  SignalChipGroup,
  StackedShareBar,
} from "../components/intelligence";
import type { DataQualityTone } from "../components/intelligence/DataQualityNote";
import type { FormStripItem } from "../components/intelligence/FormStrip";
import type { SignalChipItem, SignalTone as ComponentSignalTone } from "../components/intelligence/SignalChip";
import { formatDate, formatPercent, formatSeason } from "../utils/format";
import { getSelectedSeasonLabel, toApiSeason } from "../utils/seasonScope";
import { formatGoalDifference } from "../utils/teams";

type TeamProfileState = "loading" | "success" | "error";

function formatRate(value: number | null | undefined) {
  if (value === null || value === undefined) return "Unavailable";
  return value.toFixed(2);
}

function formatNullablePercent(value: number | null | undefined) {
  if (value === null || value === undefined) return "Unavailable";
  return formatPercent(value);
}

function getLabelItems(labels: TeamProfileLabel[]): SignalChipItem[] {
  return labels.map((label) => ({
    key: label.key,
    label: label.label,
    tone: label.tone as ComponentSignalTone,
    description: label.description,
  }));
}

function getDataQualityStatus(profile: TeamProfileResponse): DataQualityStatus {
  const coverageShare = profile.data_quality.timeline_coverage_share;
  if (coverageShare !== null && coverageShare < 0.5) return "limited";
  if (
    profile.data_quality.administrative_matches > 0 ||
    profile.data_quality.missing_matches > 0 ||
    profile.data_quality.note ||
    (coverageShare !== null && coverageShare < 0.85)
  ) {
    return "caution";
  }
  return "good";
}

function signalToneForStatus(status: DataQualityStatus): ComponentSignalTone {
  if (status === "good") return "positive";
  if (status === "caution") return "warning";
  return "muted";
}

function qualityToneForStatus(status: DataQualityStatus): DataQualityTone {
  if (status === "good") return "good";
  if (status === "caution") return "caution";
  return "limited";
}

function pointsPerMatch(profile: TeamProfileResponse) {
  return profile.played_matches > 0 ? profile.official_points / profile.played_matches : null;
}

function getSplitLabel(label: "Home" | "Away", record: TeamSplitRecord | null) {
  if (!record) return `${label} record unavailable`;
  return `${record.wins}W ${record.draws}D ${record.losses}L · ${record.points} pts`;
}

function getRecentTeamGoals(match: TeamProfileMatch) {
  const teamIsHome = match.home_away === "home";
  return {
    for: teamIsHome ? match.home_score : match.away_score,
    against: teamIsHome ? match.away_score : match.home_score,
  };
}

function formStripItems(form: TeamFormMatch[]): FormStripItem[] {
  return form.slice(0, 10).map((match) => ({
    id: String(match.match_id),
    href: `/matches/${match.match_id}`,
    label: match.opponent ?? (match.match_date ? formatDate(match.match_date) : "Match"),
    result: match.result,
  }));
}

function TeamProfileSkeleton() {
  return (
    <div className="team-dossier-page" aria-busy="true" aria-label="Loading team dossier">
      <section className="team-dossier-hero skeleton-panel">
        <span className="skeleton-line short" />
        <span className="skeleton-line title" />
        <span className="skeleton-line" />
      </section>
      <section className="team-dossier-summary-grid">
        {Array.from({ length: 6 }, (_, index) => (
          <article className="metric-delta skeleton-card" key={index}>
            <span className="skeleton-line short" />
            <span className="skeleton-line number" />
            <span className="skeleton-line medium" />
          </article>
        ))}
      </section>
      <section className="team-dossier-grid">
        <article className="panel team-dossier-panel skeleton-panel">
          <span className="skeleton-line medium" />
          <span className="skeleton-line" />
          <span className="trends-chart-skeleton" />
        </article>
        <article className="panel team-dossier-panel skeleton-panel">
          <span className="skeleton-line medium" />
          <span className="skeleton-line" />
          <span className="trends-chart-skeleton" />
        </article>
      </section>
    </div>
  );
}

function TeamIdentityPanel({ profile }: { profile: TeamProfileResponse }) {
  if (profile.profile_labels.length === 0) {
    return <EmptyState message="No team identity labels are available for this team in the selected season." />;
  }

  return (
    <div className="team-identity-list">
      {profile.profile_labels.map((label) => (
        <article key={label.key}>
          <SignalChip label={label.label} tone={label.tone as ComponentSignalTone} />
          <p>{label.description}</p>
        </article>
      ))}
    </div>
  );
}

function HomeAwaySplit({ awayRecord, homeRecord }: { awayRecord: TeamSplitRecord | null; homeRecord: TeamSplitRecord | null }) {
  if (!homeRecord && !awayRecord) {
    return <EmptyState message="Home and away split is not available for this team in the selected season." />;
  }

  return (
    <div className="team-split-grid">
      {[
        { label: "Home", record: homeRecord },
        { label: "Away", record: awayRecord },
      ].map(({ label, record }) => (
        <article className="team-split-card" key={label}>
          <div>
            <strong>{label}</strong>
            <span>{getSplitLabel(label as "Home" | "Away", record)}</span>
          </div>
          {record ? (
            <>
              <StackedShareBar
                segments={[
                  { label: "Wins", value: record.wins, tone: "green" },
                  { label: "Draws", value: record.draws, tone: "muted" },
                  { label: "Losses", value: record.losses, tone: "risk" },
                ]}
                valueFormatter={(value, share) => `${value.toLocaleString()} (${formatPercent(share)})`}
              />
              <div className="team-split-stats">
                <span>{record.matches} matches</span>
                <span>
                  {record.goals_for} / {record.goals_against} GF/GA
                </span>
              </div>
            </>
          ) : null}
        </article>
      ))}
    </div>
  );
}

function RecentMatchList({ matches }: { matches: TeamProfileMatch[] }) {
  if (matches.length === 0) {
    return <EmptyState message="No recent matches are available for this team in the selected season." />;
  }

  return (
    <div className="team-dossier-match-list">
      {matches.slice(0, 8).map((match) => (
        <Link className="team-dossier-match-row" key={match.match_id} to={`/matches/${match.match_id}`}>
          <div>
            <span>{match.match_date ? formatDate(match.match_date) : `Matchday ${match.match_day ?? "TBC"}`}</span>
            <strong>{match.opponent ?? "Opponent TBC"}</strong>
            <small>
              {match.home_away === "home" ? "Home" : "Away"}
              {match.signal_labels.length ? ` · ${match.signal_labels.slice(0, 2).join(", ")}` : ""}
            </small>
          </div>
          <div>
            <strong>
              {match.home_score ?? "-"} - {match.away_score ?? "-"}
            </strong>
            <SignalChip
              label={match.result_for_team}
              size="small"
              tone={match.result_for_team === "W" ? "positive" : match.result_for_team === "L" ? "risk" : "neutral"}
            />
          </div>
        </Link>
      ))}
    </div>
  );
}

export default function TeamDetailPage({ onRefresh, selectedSeason, selectedSeasonInfo }: PageProps) {
  const { teamSlug } = useParams();
  const [profile, setProfile] = useState<TeamProfileResponse | null>(null);
  const [profileState, setProfileState] = useState<TeamProfileState>("loading");
  const [profileError, setProfileError] = useState("");
  const seasonLabel = getSelectedSeasonLabel(selectedSeason, selectedSeasonInfo);

  const loadProfile = useCallback(async () => {
    if (!teamSlug) {
      setProfile(null);
      setProfileState("error");
      setProfileError("Team profile unavailable.");
      return;
    }

    setProfileState("loading");
    setProfileError("");
    try {
      const response = await apiClient.getTeamProfile(teamSlug, toApiSeason(selectedSeason));
      setProfile(response);
      setProfileState("success");
    } catch (error) {
      setProfile(null);
      setProfileState("error");
      setProfileError(error instanceof Error ? error.message : "Team profile unavailable.");
    }
  }, [selectedSeason, teamSlug]);

  useEffect(() => {
    void loadProfile();
  }, [loadProfile]);

  const recentGoalRows = useMemo(() => {
    return (profile?.recent_matches ?? []).slice(0, 6).map((match) => ({
      match,
      goals: getRecentTeamGoals(match),
    }));
  }, [profile]);

  const handleRetry = () => {
    onRefresh();
    void loadProfile();
  };

  if (profileState === "loading") {
    return <TeamProfileSkeleton />;
  }

  if (profileState === "error" || !profile) {
    return (
      <section className="error-panel team-dossier-error" role="alert">
        <span className="eyebrow">Team dossier</span>
        <h2>Team profile unavailable.</h2>
        <p>{profileError || "Team profile data is unavailable for this team and season."}</p>
        <div className="match-detail-actions">
          <Link className="text-button" to="/teams">
            Back to Teams
          </Link>
          <button className="text-button" type="button" onClick={handleRetry}>
            Retry profile
          </button>
        </div>
      </section>
    );
  }

  const dataStatus = getDataQualityStatus(profile);
  const ppm = pointsPerMatch(profile);
  const goalTimingData = profile.goal_timing
    .filter((interval) => interval.goals > 0 || interval.share !== null)
    .map((interval) => ({
      key: interval.interval,
      label: interval.interval,
      value: interval.goals,
      secondaryValue: interval.share,
      tone: "green" as const,
    }));

  return (
    <article className="team-dossier-page">
      <Link className="text-button back-link" to="/teams">
        Back to Teams
      </Link>

      <header className="team-dossier-hero">
        <TeamMarker label={profile.team_name} size="medium" />
        <div className="team-dossier-hero-copy">
          <span className="eyebrow">Team dossier</span>
          <h1>{profile.team_name}</h1>
          <p>
            {seasonLabel} · {profile.wins}W {profile.draws}D {profile.losses}L · {profile.official_points} points ·{" "}
            {formatGoalDifference(profile.goal_difference)} GD
          </p>
          <SignalChipGroup emptyLabel="No profile labels yet" items={getLabelItems(profile.profile_labels)} maxVisible={5} />
        </div>
        <SignalChip label={dataStatus === "good" ? "Good data" : dataStatus === "caution" ? "Read with context" : "Limited data"} tone={signalToneForStatus(dataStatus)} />
      </header>

      <section className="panel team-dossier-panel">
        <ReportSectionHeader
          eyebrow="Team identity"
          title="What kind of team is this?"
          text="These labels are guideposts for reading the data, not tactical claims."
        />
        <TeamIdentityPanel profile={profile} />
      </section>

      <section className="team-dossier-summary-grid" aria-label="Record summary">
        <MetricDelta label="Matches" value={profile.matches_played} context={`${profile.played_matches} played on pitch.`} tone="neutral" />
        <MetricDelta label="Wins" value={profile.wins} context={`${formatNullablePercent(profile.win_rate)} win rate.`} tone="positive" />
        <MetricDelta label="Draws" value={profile.draws} context="Drawn matches in available results." tone="neutral" />
        <MetricDelta label="Losses" value={profile.losses} context="Recorded losses in available results." tone="risk" />
        <MetricDelta label="Official points" value={profile.official_points} context={profile.points_note ?? "Official table points."} tone="neutral" />
        {ppm !== null ? <MetricDelta label="Points/match" value={formatRate(ppm)} context="Official points divided by played matches." tone="neutral" /> : null}
      </section>

      <section className="team-dossier-grid">
        <article className="panel team-dossier-panel">
          <ReportSectionHeader
            eyebrow="Attack and defence"
            title="Scoring profile"
            text="Goals for, goals against, and goal difference show the team balance in the selected scope."
          />
          <div className="team-profile-bars">
            <HorizontalComparisonBar
              label="Goals balance"
              segments={[
                { label: "Goals for", value: profile.goals_for, tone: "green" },
                { label: "Goals against", value: profile.goals_against, tone: "gold" },
              ]}
              valueFormatter={(value) => value.toLocaleString()}
            />
          </div>
          <div className="team-dossier-mini-metrics">
            <MetricDelta label="Goals for" value={profile.goals_for} context={`${formatRate(profile.goals_per_match)} per match.`} />
            <MetricDelta label="Goals against" value={profile.goals_against} context={`${formatRate(profile.conceded_per_match)} conceded per match.`} />
            <MetricDelta label="Goal difference" value={formatGoalDifference(profile.goal_difference)} context="Goals for minus goals against." />
          </div>
        </article>

        <article className="panel team-dossier-panel">
          <ReportSectionHeader
            eyebrow="Venue split"
            title="Home vs away"
            text="Record and goal balance by home and away matches where split data is available."
          />
          <HomeAwaySplit awayRecord={profile.away_record} homeRecord={profile.home_record} />
        </article>
      </section>

      <section className="team-dossier-grid">
        <article className="panel team-dossier-panel">
          <ReportSectionHeader
            eyebrow="Recent form"
            title="Latest results"
            text="Recent form is shown as a compact result strip before the match list."
          />
          <FormStrip items={formStripItems(profile.form)} />
          <RecentMatchList matches={profile.recent_matches} />
        </article>

        <article className="panel team-dossier-panel">
          <ReportSectionHeader
            eyebrow="Recent scoring"
            title="Goals for and against"
            text="Recent scorelines show match-by-match scoring balance. Avoid overclaiming from short runs."
          />
          {recentGoalRows.length > 0 ? (
            <div className="team-recent-goals-list">
              {recentGoalRows.map(({ goals, match }) => (
                <HorizontalComparisonBar
                  key={match.match_id}
                  label={match.opponent ?? `Match ${match.match_id}`}
                  segments={[
                    { label: "For", value: goals.for ?? 0, tone: "green" },
                    { label: "Against", value: goals.against ?? 0, tone: "gold" },
                  ]}
                  valueFormatter={(value) => value.toLocaleString()}
                />
              ))}
            </div>
          ) : (
            <EmptyState message="No recent scoreline profile is available for this team in the selected season." />
          )}
        </article>
      </section>

      <section className="team-dossier-grid">
        <article className="panel team-dossier-panel">
          <MiniBarChart
            data={goalTimingData}
            description="Distribution of available timeline goals for the selected season."
            emptyLabel="No goal timing profile is available for this team in the selected season."
            height="compact"
            title="When this team scores"
            valueFormatter={(value) => value.toLocaleString()}
          />
          <DataQualityNote
            compact
            note="Timeline-based goal timing depends on event coverage."
            title="Goal timing caveat"
            tone={qualityToneForStatus(dataStatus)}
          />
        </article>

        <article className="panel team-dossier-panel">
          <ReportSectionHeader
            eyebrow="Event evidence"
            title="Discipline and events"
            text="Event totals summarize available timeline evidence for this team."
          />
          <div className="team-event-summary-grid">
            <MetricDelta label="Goals" value={profile.event_summary.goals} context="Timeline event goals." tone="positive" />
            <MetricDelta label="Assists" value={profile.event_summary.assists} context="Timeline event assists." />
            <MetricDelta label="Yellow cards" value={profile.event_summary.yellow_cards} context="Discipline events." tone="warning" />
            <MetricDelta label="Red cards" value={profile.event_summary.red_cards} context="Discipline events." tone={profile.event_summary.red_cards > 0 ? "risk" : "neutral"} />
            <MetricDelta label="Substitutions" value={profile.event_summary.substitutions} context="Timeline substitutions." />
            <MetricDelta label="Cards/match" value={formatRate(profile.discipline_summary.cards_per_match)} context="Yellow and red cards per match." tone="warning" />
          </div>
        </article>
      </section>

      <DataQualityNote
        metrics={[
          { label: "Timeline coverage", value: formatNullablePercent(profile.data_quality.timeline_coverage_share) },
          { label: "Covered matches", value: profile.data_quality.timeline_coverage_matches.toLocaleString(), detail: `${profile.data_quality.total_matches} total` },
          { label: "Admin matches", value: profile.data_quality.administrative_matches.toLocaleString() },
          { label: "Missing matches", value: profile.data_quality.missing_matches.toLocaleString() },
        ]}
        note={
          profile.data_quality.note ??
          "This profile is based on available match and event data. Timeline-dependent sections should be read with coverage in mind."
        }
        title="Team data quality"
        tone={qualityToneForStatus(dataStatus)}
      />

      <section className="panel related-actions-panel">
        <ReportSectionHeader
          eyebrow="Next step"
          title="Continue the team read"
          text="Move between the team board, this team's matches, and league-wide trend context."
        />
        <div className="match-detail-actions">
          <Link className="text-button" to="/teams">
            Back to Teams
          </Link>
          <Link className="text-button" to={`/matches?team=${encodeURIComponent(profile.team_name)}`}>
            View this team's match briefs
          </Link>
          <Link className="text-button" to="/matches">
            View related matches
          </Link>
          <Link className="text-button" to="/trends">
            View Trends
          </Link>
        </div>
      </section>
    </article>
  );
}
