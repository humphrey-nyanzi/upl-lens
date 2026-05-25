"""Normalization helpers used while turning raw rows into staging rows."""

from __future__ import annotations

import re
from datetime import date
from typing import Any

import pandas as pd

from src import config
from src.cleaning import normalize_team_name


def _season_key_series(series: pd.Series) -> pd.Series:
    """Normalize season text so `2025/26`, `2025-26`, and `2025_26` compare equally."""

    return (
        series.astype("string")
        .str.strip()
        .str.replace("-", "_", regex=False)
        .str.replace("/", "_", regex=False)
    )


def _clean_text(value: Any) -> str | None:
    """Return stripped text or None for empty/null values."""

    if pd.isna(value):
        return None
    text_value = str(value).strip()
    return text_value or None


def _standardize_label(value: Any) -> str | None:
    """Normalize low-cardinality labels such as event types and squad roles."""

    text_value = _clean_text(value)
    if text_value is None:
        return None
    return re.sub(r"\s+", "_", text_value.lower())


def _normalize_team(value: Any) -> str | None:
    """Normalize team names with the shared project corrections."""

    text_value = _clean_text(value)
    if text_value is None:
        return None
    corrected = config.CLUB_NAME_CORRECTIONS.get(text_value, text_value)
    corrected = config.CLUB_NAME_CORRECTIONS.get(corrected.title(), corrected)
    normalized = normalize_team_name(corrected.lower())
    return config.CLUB_NAME_CORRECTIONS.get(normalized, normalized)


def _normalize_person(value: Any) -> str | None:
    """Trim person names while preserving the source spelling."""

    return _clean_text(value)


def _clean_person_name(value: Any) -> str | None:
    """Return a stricter person-name value for fields such as Man of the Match."""

    text_value = _clean_text(value)
    if text_value is None:
        return None
    cleaned = re.sub(r"^\(?\s*(?:gk|captain|capt)\s*\)?\s*", "", text_value, flags=re.IGNORECASE)
    cleaned = cleaned.replace("(", "").replace(")", "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .:-|")
    if not cleaned:
        return None
    if re.search(
        r"\b(match|coach|yellow|red|card|live|televised|turn up|circumstances|decision|forfeiture|fixture|notice)\b",
        cleaned,
        flags=re.IGNORECASE,
    ):
        return None
    return cleaned


def _team_matches_match(row: pd.Series, team_name: str | None) -> bool:
    """Return whether a team belongs to the match's home/away pair."""

    if team_name is None:
        return False
    return team_name in {row.get("home_team"), row.get("away_team")}


def _extract_man_of_match(row: pd.Series) -> tuple[str | None, str | None]:
    """Extract a strict Man of the Match name/team pair from raw match text.

    The UPL page excerpt often mixes broadcast notes, coach cards, forfeiture
    explanations, and the actual award. Staging keeps only the award when it can
    identify a likely person name and a team that played in the match.
    """

    raw_name = _clean_text(row.get("man_of_the_match"))
    raw_team = _normalize_team(row.get("man_of_the_match_team"))
    if raw_name is None:
        return None, None

    label_match = re.search(
        r"(?:pilsner\s+)?m\s*<?an\s*of\s*(?:the\s*)?(?:match|math)\s*:\s*(?P<body>.+)",
        raw_name,
        flags=re.IGNORECASE,
    )
    if label_match:
        body = label_match.group("body")
        parenthetical_teams = list(re.finditer(r"\((?P<team>[^()]*)\)", body))
        for team_match in reversed(parenthetical_teams):
            parsed_team = _normalize_team(team_match.group("team"))
            if not _team_matches_match(row, parsed_team):
                continue
            parsed_name = _clean_person_name(body[: team_match.start()])
            if parsed_name:
                return parsed_name, parsed_team

        # A few source rows omit the opening parenthesis before the team, e.g.
        # `Name Team FC)`. Use the home/away team names as anchors instead of
        # guessing arbitrary trailing words.
        for candidate_team in (row.get("home_team"), row.get("away_team")):
            if candidate_team and re.search(re.escape(str(candidate_team)), body, flags=re.IGNORECASE):
                parsed_name = _clean_person_name(
                    re.split(re.escape(str(candidate_team)), body, maxsplit=1, flags=re.IGNORECASE)[0]
                )
                if parsed_name:
                    return parsed_name, str(candidate_team)

    clean_name = _clean_person_name(raw_name)
    if clean_name and len(clean_name) <= 80:
        if _team_matches_match(row, raw_team):
            return clean_name, raw_team
        if raw_team is None:
            return clean_name, None

    return None, None


def _parse_dates(series: pd.Series) -> pd.Series:
    """Parse UPL dates with day-first ordering.

    Historical source files use day-first dates. Invalid dates become null and
    are logged by validation instead of crashing the whole build.
    """

    return pd.to_datetime(series, dayfirst=True, errors="coerce").dt.date


def _is_forfeit_text(value: Any) -> bool:
    """Return whether source text clearly describes a forfeited match."""

    text_value = _clean_text(value)
    if text_value is None:
        return False
    return bool(
        re.search(
            r"\b(forfeit|forfeiture|failed to turn up|failure to honour|walkover|walk over)\b",
            text_value,
            flags=re.IGNORECASE,
        )
    )


def _season_date_window(season: Any) -> tuple[date, date] | None:
    """Return a broad plausible match-date window for a UPL season key.

    UPL seasons normally start around August/September and end by June. The
    window stays intentionally generous through late August of the second season
    year so legitimate delayed fixtures do not become hard failures.
    """

    season_text = _clean_text(season)
    if season_text is None:
        return None
    match = re.fullmatch(r"(?P<start>\d{4})[_/-](?P<end>\d{2})", season_text)
    if match is None:
        return None

    start_year = int(match.group("start"))
    end_year = int(f"{str(start_year)[:2]}{match.group('end')}")
    if end_year < start_year:
        end_year += 100
    return date(start_year, 8, 1), date(end_year, 8, 31)


def _season_date_anomaly_reason(season: Any, match_date: Any) -> str | None:
    """Return an anomaly reason when a match date falls outside its season."""

    if pd.isna(match_date):
        return None
    window = _season_date_window(season)
    if window is None:
        return None
    start_date, end_date = window
    if match_date < start_date or match_date > end_date:
        return (
            "match_date_outside_season_window:"
            f" expected {start_date.isoformat()}..{end_date.isoformat()},"
            f" got {match_date.isoformat()}"
        )
    return None


def _minute_period(minute_total: int | None) -> str | None:
    """Bucket a match minute into a simple analysis interval."""

    if minute_total is None:
        return None
    if minute_total <= 15:
        return "0-15"
    if minute_total <= 30:
        return "16-30"
    if minute_total <= 45:
        return "31-45"
    if minute_total <= 60:
        return "46-60"
    if minute_total <= 75:
        return "61-75"
    if minute_total <= 90:
        return "76-90"
    return "90+"


def _parse_minute(value: Any) -> dict[str, Any]:
    """Parse event minute text into numeric pieces.

    Handles normal minutes (`56`), added time (`45+2`), apostrophes, empty
    strings, and inline annotations such as `56 (P)` or `90 OG`.
    """

    text_value = _clean_text(value)
    if text_value is None:
        return {
            "event_minute_text": None,
            "minute_base": None,
            "minute_added": None,
            "minute_total": None,
            "is_added_time": False,
            "minute_period": None,
            "minute_annotation": None,
            "minute_parse_failed": False,
        }

    annotation_parts: list[str] = []
    normalized = text_value.replace("'", "").strip()
    if re.search(r"\(\s*p\s*\)|\bpen\b", normalized, flags=re.IGNORECASE):
        annotation_parts.append("penalty")
    if re.search(r"\bog\b", normalized, flags=re.IGNORECASE):
        annotation_parts.append("own_goal")

    minute_text = re.sub(r"\(\s*p\s*\)", "", normalized, flags=re.IGNORECASE)
    minute_text = re.sub(r"\bpen\b", "", minute_text, flags=re.IGNORECASE)
    minute_text = re.sub(r"\bog\b", "", minute_text, flags=re.IGNORECASE).strip()
    match = re.search(r"(?P<base>\d{1,3})(?:\s*\+\s*(?P<added>\d{1,2}))?", minute_text)
    if match is None:
        return {
            "event_minute_text": text_value,
            "minute_base": None,
            "minute_added": None,
            "minute_total": None,
            "is_added_time": False,
            "minute_period": None,
            "minute_annotation": ",".join(annotation_parts) or None,
            "minute_parse_failed": True,
        }

    base_minute = int(match.group("base"))
    added_minute = int(match.group("added") or 0)
    total_minute = base_minute + added_minute
    return {
        "event_minute_text": text_value,
        "minute_base": base_minute,
        "minute_added": added_minute,
        "minute_total": total_minute,
        "is_added_time": added_minute > 0,
        "minute_period": _minute_period(total_minute),
        "minute_annotation": ",".join(annotation_parts) or None,
        "minute_parse_failed": False,
    }


def _normalize_goal_type(raw_goal_type: Any, minute_annotation: Any) -> str | None:
    """Standardize goal type and preserve penalty/own-goal hints from minute text."""

    goal_type = _clean_text(raw_goal_type)
    annotation = _clean_text(minute_annotation)
    if annotation == "penalty":
        return config.GOAL_TYPE_PENALTY
    if annotation == "own_goal":
        return config.GOAL_TYPE_OWN_GOAL
    if annotation == "penalty,own_goal":
        return config.GOAL_TYPE_PENALTY
    if goal_type is None:
        return None
    normalized = goal_type.replace("_", " ").title()
    if normalized.lower() == "own goal":
        return config.GOAL_TYPE_OWN_GOAL
    if normalized.lower() == "penalty":
        return config.GOAL_TYPE_PENALTY
    return normalized


def _team_from_side(row: pd.Series) -> str | None:
    """Resolve the actual team name for an event from its home/away side."""

    if row.get("team_side") == config.SIDE_HOME:
        return row.get("home_team")
    if row.get("team_side") == config.SIDE_AWAY:
        return row.get("away_team")
    return None

