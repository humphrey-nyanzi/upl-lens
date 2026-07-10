import { useState } from "react";

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

type TimelineMarkerGroup = {
  id: string;
  minute: number;
  minuteLabel: string;
  events: TimelineRailEvent[];
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
  const markerGroups = timedEvents.reduce<TimelineMarkerGroup[]>((groups, event) => {
    const minute = event.minute ?? 0;
    const group = groups.find((candidate) => candidate.minute === minute);

    if (group) {
      group.events.push(event);
      return groups;
    }

    groups.push({
      id: `minute-${minute}`,
      minute,
      minuteLabel: event.minuteText ?? `${minute}'`,
      events: [event],
    });
    return groups;
  }, []);
  const [selectedMarkerId, setSelectedMarkerId] = useState<string | null>(() => markerGroups.at(0)?.id ?? null);
  const selectedMarkerGroup = markerGroups.find((group) => group.id === selectedMarkerId) ?? markerGroups.at(0);
  const scaleMarks = [0, 45, 90, ...(safeMaxMinute > 90 ? [safeMaxMinute] : [])].filter((minute) => minute <= safeMaxMinute);

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
          <div aria-label={`Match timeline from 0 to ${safeMaxMinute} minutes`} className="timeline-rail-track" role="group">
            <div aria-hidden="true" className="timeline-rail-scale">
              {scaleMarks.map((minute) => (
                <span className={minute > 90 ? "timeline-rail-scale-extra" : undefined} key={minute} style={{ left: `${(minute / safeMaxMinute) * 100}%` }}>
                  {minute}'
                </span>
              ))}
            </div>
            <div className="timeline-rail-line">
              <i />
              {markerGroups.map((group) => {
                const left = Math.min(Math.max((group.minute / safeMaxMinute) * 100, 0), 100);
                const eventSummary = group.events
                  .map((event) => [event.label, event.teamName].filter(Boolean).join(", "))
                  .join("; ");
                const markerLabel = group.events.length === 1 ? `Show event at ${group.minuteLabel}: ${eventSummary}` : `Show ${group.events.length} events at ${group.minuteLabel}: ${eventSummary}`;
                const tone = group.events.at(0)?.tone ?? "neutral";
                return (
                  <button
                    aria-controls={`timeline-rail-marker-detail-${group.id}`}
                    aria-label={markerLabel}
                    aria-pressed={selectedMarkerGroup?.id === group.id}
                    className={`timeline-rail-marker tone-${tone}`}
                    key={group.id}
                    onClick={() => setSelectedMarkerId(group.id)}
                    style={{ left: `${left}%` }}
                    type="button"
                  />
                );
              })}
            </div>
          </div>
          {selectedMarkerGroup ? (
            <div aria-live="polite" className={`timeline-rail-marker-detail tone-${selectedMarkerGroup.events.at(0)?.tone ?? "neutral"}`} id={`timeline-rail-marker-detail-${selectedMarkerGroup.id}`}>
              <strong>{selectedMarkerGroup.minuteLabel}</strong>
              <ul>
                {selectedMarkerGroup.events.map((event) => (
                  <li key={event.id}>
                    <span>{event.label}</span>
                    {event.teamName ? <small>{event.teamName}</small> : null}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
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
