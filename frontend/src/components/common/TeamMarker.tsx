type TeamMarkerProps = {
  className?: string;
  initials?: string;
  label: string | null | undefined;
  size?: "small" | "medium";
};

function getSafeTeamLabel(label: string | null | undefined) {
  return label?.trim() || "Team TBC";
}

export function getTeamInitials(label: string | null | undefined) {
  return getSafeTeamLabel(label)
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0])
    .join("")
    .toUpperCase();
}

export function getStableTeamTone(label: string | null | undefined) {
  const toneCount = 5;
  const safeLabel = getSafeTeamLabel(label);
  const hash = Array.from(safeLabel).reduce((total, character) => total + character.charCodeAt(0), 0);

  return (hash % toneCount) + 1;
}

export function TeamMarker({ className, initials, label, size = "medium" }: TeamMarkerProps) {
  const classes = ["team-marker", `team-marker-${size}`, className].filter(Boolean).join(" ");

  return (
    <span className={classes} data-tone={getStableTeamTone(label)} aria-hidden="true">
      {initials || getTeamInitials(label)}
    </span>
  );
}
