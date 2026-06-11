import { ChartEmptyState } from "../charts/ChartPrimitives";

export type ScoreProgressionPoint = {
  minute: number | null;
  minuteText?: string | null;
  homeScore: number;
  awayScore: number;
  scoringTeam?: string | null;
  eventType?: string | null;
};

export type ScoreProgressionProps = {
  homeTeam: string;
  awayTeam: string;
  points: ScoreProgressionPoint[];
  emptyLabel?: string;
};

export function ScoreProgression({
  awayTeam,
  emptyLabel = "No scoring progression is available for this match.",
  homeTeam,
  points,
}: ScoreProgressionProps) {
  if (points.length === 0) return <ChartEmptyState message={emptyLabel} />;

  return (
    <section className="score-progression" aria-label="Score progression">
      <div className="score-progression-teams">
        <span>{homeTeam}</span>
        <span>{awayTeam}</span>
      </div>
      <ol>
        {points.map((point, index) => (
          <li key={`${point.minuteText ?? point.minute ?? "tbc"}-${point.homeScore}-${point.awayScore}-${point.scoringTeam ?? "team-tbc"}-${point.eventType ?? "event"}`}>
            <span>{point.minuteText ?? (point.minute === null ? "Minute TBC" : `${point.minute}'`)}</span>
            <strong>
              {point.homeScore} - {point.awayScore}
            </strong>
            <em>{point.scoringTeam ?? "Scoring team TBC"}</em>
          </li>
        ))}
      </ol>
    </section>
  );
}
