import type { MatchDetailResponse, MatchSummary } from "../api/types";

type MatchBriefSource = Pick<
  MatchSummary,
  | "administrative_note"
  | "away_score"
  | "home_score"
  | "is_administrative_result"
  | "is_source_anomaly"
  | "result"
  | "source_anomaly_reason"
  | "stats_red_card_count"
  | "stats_yellow_card_count"
  | "timeline_goal_count"
  | "timeline_note"
  | "timeline_red_card_count"
  | "timeline_status"
  | "timeline_yellow_card_count"
  | "total_goals"
> &
  Partial<Pick<MatchDetailResponse, "events" | "has_timeline">>;

export type MatchBriefSignalKey =
  | "timeline_backed"
  | "partial_evidence"
  | "goal_heavy"
  | "decisive_margin"
  | "level_contest"
  | "discipline"
  | "result_note";

export type MatchBriefSignal = {
  key: MatchBriefSignalKey;
  label: string;
  tone: "default" | "muted" | "success" | "warning";
};

export type MatchBriefCard = {
  label: string;
  value: string;
  tone?: "default" | "muted" | "success" | "warning";
  text: string;
};

function getTotalGoals(match: MatchBriefSource) {
  if (match.total_goals !== null && match.total_goals !== undefined) return match.total_goals;
  if (match.home_score !== null && match.away_score !== null) return match.home_score + match.away_score;
  return null;
}

function getGoalDifference(match: MatchBriefSource) {
  if (match.home_score === null || match.away_score === null) return null;
  return Math.abs(match.home_score - match.away_score);
}

function getCardCounts(match: MatchBriefSource) {
  const yellowCards = match.timeline_yellow_card_count ?? match.stats_yellow_card_count ?? 0;
  const redCards = match.timeline_red_card_count ?? match.stats_red_card_count ?? 0;
  return { redCards, totalCards: yellowCards + redCards, yellowCards };
}

function hasTimelineEvidence(match: MatchBriefSource) {
  return match.timeline_status === "complete" || Boolean(match.has_timeline) || (match.events?.length ?? 0) > 0;
}

export function getMatchBriefSignals(match: MatchBriefSource) {
  const signals: MatchBriefSignal[] = [];
  const totalGoals = getTotalGoals(match);
  const goalDifference = getGoalDifference(match);
  const { redCards, totalCards } = getCardCounts(match);

  if (match.is_administrative_result || match.is_source_anomaly) {
    signals.push({ key: "result_note", label: "Result note", tone: "warning" });
  }

  if (match.timeline_status === "complete" || hasTimelineEvidence(match)) {
    signals.push({ key: "timeline_backed", label: "Timeline backed", tone: "success" });
  } else if (match.timeline_status === "partial") {
    signals.push({ key: "partial_evidence", label: "Partial evidence", tone: "warning" });
  }

  if (totalGoals !== null && totalGoals >= 5) {
    signals.push({ key: "goal_heavy", label: `${totalGoals}-goal game`, tone: "success" });
  }

  if (goalDifference !== null && goalDifference >= 3) {
    signals.push({ key: "decisive_margin", label: "Clear margin", tone: "default" });
  } else if (match.result === "draw") {
    signals.push({ key: "level_contest", label: "Level contest", tone: "default" });
  }

  if (redCards > 0) {
    signals.push({
      key: "discipline",
      label: redCards === 1 ? "Red card recorded" : `${redCards} red cards recorded`,
      tone: "warning",
    });
  } else if (totalCards >= 6) {
    signals.push({ key: "discipline", label: `${totalCards} cards recorded`, tone: "warning" });
  }

  return signals;
}

export function hasMatchBriefSignal(match: MatchBriefSource, signalKey: MatchBriefSignalKey) {
  return getMatchBriefSignals(match).some((signal) => signal.key === signalKey);
}

export function buildMatchBriefLead(match: MatchBriefSource) {
  const totalGoals = getTotalGoals(match);
  const goalDifference = getGoalDifference(match);
  const { redCards, totalCards } = getCardCounts(match);

  if (match.is_administrative_result) {
    return match.administrative_note ?? "Recorded as an administrative result rather than a normal full-time outcome.";
  }

  if (match.is_source_anomaly) {
    return match.source_anomaly_reason ?? "This fixture carries a source note, so the brief should be read with care.";
  }

  if (redCards > 0) {
    return "Discipline likely shaped this fixture, with at least one red card recorded in the available evidence.";
  }

  if (totalGoals !== null && totalGoals >= 5 && goalDifference !== null && goalDifference <= 1) {
    return "High-scoring contest with both clubs kept alive in the scoreline deep into the brief.";
  }

  if (totalGoals !== null && totalGoals >= 5) {
    return "Goal-heavy result that stands out from the surrounding fixture list.";
  }

  if (goalDifference !== null && goalDifference >= 3) {
    return "Clear-margin result with a decisive scoreline before the deeper context begins.";
  }

  if (match.result === "draw") {
    return "Level scoreline that needs event or stat context to explain how the points were shared.";
  }

  if (match.timeline_status === "partial") {
    return match.timeline_note ?? "The source record is only partially captured, so this brief stays compact and cautious.";
  }

  if (hasTimelineEvidence(match)) {
    return "Timeline-backed fixture with enough event evidence for a fuller intelligence brief.";
  }

  if (totalCards >= 4) {
    return "Moderate card count suggests a more physical match than the scoreline alone may imply.";
  }

  return "Compact scoreline brief with supporting source context where available.";
}

export function buildMatchBriefCards(match: MatchBriefSource) {
  const totalGoals = getTotalGoals(match);
  const goalDifference = getGoalDifference(match);
  const { redCards, totalCards, yellowCards } = getCardCounts(match);
  const evidenceValue =
    match.is_administrative_result || match.is_source_anomaly
      ? "Result note"
      : match.timeline_status === "complete" || hasTimelineEvidence(match)
        ? "Timeline backed"
        : match.timeline_status === "partial"
          ? "Partial evidence"
          : "Scoreline only";

  const evidenceText =
    match.is_administrative_result || match.is_source_anomaly
      ? "The source record needs explicit context before treating the result as an ordinary played match."
      : match.timeline_status === "complete" || hasTimelineEvidence(match)
        ? "UPL Lens has enough timeline evidence here to move beyond the source result line."
        : match.timeline_status === "partial"
          ? match.timeline_note ?? "Only part of the event record is available for this brief."
          : "This brief leans more heavily on the scoreline and source metadata than a full event record.";

  const resultShapeValue = match.is_administrative_result
    ? "Administrative outcome"
    : totalGoals !== null && totalGoals >= 5
      ? "Goal-heavy result"
      : goalDifference !== null && goalDifference >= 3
        ? "Clear-margin win"
        : match.result === "draw"
          ? "Shared points"
          : "Narrow result";

  const resultShapeText = match.is_administrative_result
    ? "The scoreline is paired with an administrative ruling, so the brief treats it as a recorded decision first."
    : totalGoals !== null && totalGoals >= 5
      ? `The match produced ${totalGoals} total goals, making the scoreline itself part of the story.`
      : goalDifference !== null && goalDifference >= 3
        ? "A multi-goal margin makes the result look decisive before the supporting evidence is read."
        : match.result === "draw"
          ? "The points were shared, so the timeline and stat context matter more than the result label alone."
          : "The final margin stayed tight enough that small moments likely mattered.";

  const disciplineValue =
    redCards > 0
      ? redCards === 1
        ? "Red card recorded"
        : `${redCards} red cards`
      : totalCards > 0
        ? `${totalCards} cards logged`
        : "No card signal";

  const disciplineText =
    redCards > 0
      ? "A dismissal is part of the available evidence and may have changed the balance of the match."
      : totalCards > 0
        ? `${yellowCards} yellow and ${redCards} red cards are captured in the available record.`
        : "No meaningful card signal is captured in the available event or stat record.";

  const sourceValue = match.is_source_anomaly
    ? "Source issue"
    : match.is_administrative_result
      ? "Administrative note"
      : "Official source linked";

  const sourceText = match.is_source_anomaly
    ? match.source_anomaly_reason ?? "A source anomaly is recorded against this fixture."
    : match.is_administrative_result
      ? match.administrative_note ?? "The result comes with an administrative note from the source record."
      : "The official match page remains available as the underlying source record for this brief.";

  return [
    { label: "Result shape", value: resultShapeValue, text: resultShapeText },
    {
      label: "Evidence quality",
      value: evidenceValue,
      tone: evidenceValue === "Timeline backed" ? "success" : evidenceValue === "Scoreline only" ? "muted" : "warning",
      text: evidenceText,
    },
    {
      label: "Discipline signal",
      value: disciplineValue,
      tone: redCards > 0 || totalCards >= 6 ? "warning" : totalCards > 0 ? "default" : "muted",
      text: disciplineText,
    },
    {
      label: "Source handoff",
      value: sourceValue,
      tone: match.is_source_anomaly || match.is_administrative_result ? "warning" : "default",
      text: sourceText,
    },
  ] satisfies MatchBriefCard[];
}
