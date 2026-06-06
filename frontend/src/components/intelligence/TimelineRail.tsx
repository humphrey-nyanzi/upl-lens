import { ChartEmptyState } from "../charts/ChartPrimitives";

export type TimelineRailEvent = {
  id: string;
  minute: number | null;
  minuteText?: string | null;
  label: string;
  eventType?: string | null;
  teamName?: string | null;
  tone?: "goal" | "card" | "red" | "substitution" | "neutral" | "warning";
};

export type TimelineRailProps = {
  events: TimelineRailEvent[];
  title?: string;
  description?: string;
  maxMinute?: number;
  emptyLabel?: string;
};

export function TimelineRail({
  description,
  emptyLabel = "No key timeline moments available yet.",
  events,
  maxMinute,
  title,
}: TimelineRailProps) {
  const timedEvents = events.filter((event) => typeof event.minute === "number");
  const untimedEvents = events.filter((event) => event.minute === null);
  const safeMaxMinute = maxMinute ?? (timedEvents.some((event) => (event.minute ?? 0) > 90) ? 100 : 90);

  return (
    <section className="timeline-rail" aria-label={title}>
      {title || description ? (
        <div className="intelligence-chart-heading">
          {title ? <h3>{title}</h3> : null}
          {description ? <p>{description}</p> : null}
        </div>
      ) : null}
      {events.length ? (
        <>
          <div className="timeline-rail-track" aria-hidden="true">
            <span>0'</span>
            <i />
            <span>{safeMaxMinute}'</span>
            {timedEvents.map((event) => {
              const left = Math.min(Math.max(((event.minute ?? 0) / safeMaxMinute) * 100, 0), 100);
              return (
                <b
                  className={`timeline-rail-marker tone-${event.tone ?? "neutral"}`}
                  key={event.id}
                  style={{ left: `${left}%` }}
                  title={`${event.minuteText ?? `${event.minute}'`} ${event.label}`}
                />
              );
            })}
          </div>
          <ol className="timeline-rail-events">
            {timedEvents.map((event) => (
              <li className={`tone-${event.tone ?? "neutral"}`} key={event.id}>
                <strong>{event.minuteText ?? `${event.minute}'`}</strong>
                <span>{event.label}</span>
                {event.teamName ? <small>{event.teamName}</small> : null}
              </li>
            ))}
          </ol>
          {untimedEvents.length ? (
            <div className="timeline-rail-untimed">
              <strong>Minute TBC</strong>
              {untimedEvents.map((event) => (
                <span key={event.id}>{event.label}</span>
              ))}
            </div>
          ) : null}
        </>
      ) : (
        <ChartEmptyState message={emptyLabel} />
      )}
    </section>
  );
}
