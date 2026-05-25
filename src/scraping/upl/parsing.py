"""HTML parsing for one official UPL match page.

Parsing stays isolated from network and file-output concerns so source-site
layout changes can be repaired and tested without touching the pipeline runner.
"""

from __future__ import annotations

import re
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag

from src.scraping.upl.constants import EVENT_COLUMNS, MATCH_COLUMNS


def _normalize_whitespace(value: str | None) -> str | None:
    """Collapse repeated whitespace and strip surrounding spaces."""
    if value is None:
        return None

    normalized = re.sub(r"\s+", " ", value).strip()
    return normalized or None


def _normalize_key(value: str) -> str:
    """Convert header text into a snake_case key."""
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")


def _safe_text(node: Tag | None) -> str | None:
    """Safely return stripped text from a tag."""
    if node is None:
        return None
    return _normalize_whitespace(node.get_text(" ", strip=True))


def _first_anchor_info(node: Tag | None) -> tuple[str | None, str | None]:
    """Extract the first anchor's text and href from a tag."""
    if node is None:
        return None, None

    anchor = node.select_one("a")
    if anchor is None:
        return None, None

    return _normalize_whitespace(anchor.get_text(" ", strip=True)), anchor.get("href")


def _split_node_segments(node: Tag) -> list[list[Any]]:
    """
    Split a tag's children into <br>-separated segments.

    The UPL timeline uses the same content arranged in different orders
    on the home and away side. Segmenting by <br> lets us map each player
    to the matching icon regardless of that ordering.
    """
    segments: list[list[Any]] = [[]]

    for child in node.children:
        if isinstance(child, NavigableString):
            if child.strip():
                segments[-1].append(child)
            continue

        if getattr(child, "name", None) == "br":
            if segments[-1]:
                segments.append([])
            continue

        segments[-1].append(child)

    return [segment for segment in segments if _segment_text(segment)]


def _segment_text(segment: list[Any]) -> str:
    """Return the normalized text content of a segment."""
    parts = []
    for item in segment:
        if isinstance(item, NavigableString):
            text = _normalize_whitespace(str(item))
        elif isinstance(item, Tag):
            text = _normalize_whitespace(item.get_text(" ", strip=True))
        else:
            text = None

        if text:
            parts.append(text)

    return _normalize_whitespace(" ".join(parts)) or ""


def _clean_player_name(player_name: str | None) -> str | None:
    """Normalize player text scraped from the timeline."""
    if not player_name:
        return None

    cleaned_player_name = re.sub(r"^\s*\d+\.*\s*", "", player_name).strip()
    return cleaned_player_name or None


def _extract_player_from_segment(segment: list[Any]) -> tuple[str | None, str | None]:
    """Extract player name and URL from one segment."""
    for item in segment:
        if isinstance(item, Tag) and item.name == "a":
            return _clean_player_name(_safe_text(item)), item.get("href")

    return _clean_player_name(_segment_text(segment)), None


def _extract_player_from_icon(icon: Tag) -> tuple[str | None, str | None]:
    """Extract the player attached to a specific timeline icon."""
    icon_td = icon.find_parent("td")
    if icon_td is None:
        return None, None

    for segment in _split_node_segments(icon_td):
        if any(item is icon for item in segment):
            return _extract_player_from_segment(segment)

    return None, None


def _extract_substitution_players(cell: Tag) -> tuple[str | None, str | None, str | None, str | None]:
    """
    Extract outgoing and incoming players from a substitution cell.

    Home and away timeline cells arrange anchors and icons differently, so
    this parser looks at each <br>-separated segment independently instead
    of assuming a fixed icon-before-name order.
    """
    sub_out_player_name = None
    sub_out_player_url = None
    sub_in_player_name = None
    sub_in_player_url = None

    for segment in _split_node_segments(cell):
        titles = [
            (item.get("title") or "").strip().lower()
            for item in segment
            if isinstance(item, Tag) and item.name == "i"
        ]
        player_name, player_url = _extract_player_from_segment(segment)

        if any("sub out" in title for title in titles):
            sub_out_player_name = player_name
            sub_out_player_url = player_url
        elif any("sub in" in title for title in titles):
            sub_in_player_name = player_name
            sub_in_player_url = player_url

    return sub_out_player_name, sub_out_player_url, sub_in_player_name, sub_in_player_url


def _build_event_row(
    match_row: dict[str, Any],
    event_index: int,
    event_type: str,
    minute: str | None,
    team_side: str,
    player_name: str | None,
    player_url: str | None = None,
    goal_type: str | None = None,
    sub_out_player_name: str | None = None,
    sub_out_player_url: str | None = None,
    sub_in_player_name: str | None = None,
    sub_in_player_url: str | None = None,
) -> dict[str, Any]:
    """Create one normalized event row."""
    cleaned_minute = None
    if isinstance(minute, str) and minute.strip():
        cleaned_minute = minute.replace("'", "").strip()

    return {
        "match_id": match_row.get("match_id"),
        "match_url": match_row.get("match_url"),
        "date": match_row.get("date"),
        "time": match_row.get("time"),
        "league": match_row.get("league"),
        "season": match_row.get("season"),
        "match_day": match_row.get("match_day"),
        "home_team": match_row.get("home_team"),
        "away_team": match_row.get("away_team"),
        "event_index": event_index,
        "event_type": event_type,
        "event_minute": cleaned_minute,
        "team_side": team_side,
        "player_name": player_name,
        "player_url": player_url,
        "goal_type": goal_type,
        "sub_out_player_name": sub_out_player_name,
        "sub_out_player_url": sub_out_player_url,
        "sub_in_player_name": sub_in_player_name,
        "sub_in_player_url": sub_in_player_url,
    }


def _parse_goal_type(icon_title: str, minute: str | None) -> str:
    """Infer the goal subtype from icon metadata and minute text."""
    normalized_title = icon_title.strip().lower()
    minute_text = (minute or "").upper()

    if normalized_title == "own goals" or "own goal" in normalized_title or "OG" in minute_text:
        return "Own Goal"
    if "(P)" in minute_text or minute_text.endswith("P"):
        return "Penalty"
    return "Regular"


def _extract_timeline_events(soup: BeautifulSoup, match_row: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract timeline events from a match page."""
    timeline = soup.select_one("div.sp-template-event-timeline")
    if timeline is None:
        return []

    events: list[dict[str, Any]] = []
    event_index = 0

    for row in timeline.select("tr"):
        cells = row.find_all("td")
        if len(cells) < 3:
            continue

        minute = _normalize_whitespace(cells[1].get_text(strip=True))
        row_cells = [
            ("home", cells[0]),
            ("away", cells[2]),
        ]

        for team_side, cell in row_cells:
            if not _normalize_whitespace(cell.get_text(" ", strip=True)):
                continue

            icons = cell.find_all("i")
            for icon in icons:
                class_names = set(icon.get("class", []))
                icon_title = (icon.get("title") or "").strip()

                if "sp-icon-soccerball" in class_names:
                    player_name, player_url = _extract_player_from_icon(icon)
                    event_index += 1
                    events.append(
                        _build_event_row(
                            match_row=match_row,
                            event_index=event_index,
                            event_type="goal",
                            minute=minute,
                            team_side=team_side,
                            player_name=player_name,
                            player_url=player_url,
                            goal_type=_parse_goal_type(icon_title, minute),
                        )
                    )
                elif "sp-icon-shoe" in class_names:
                    player_name, player_url = _extract_player_from_icon(icon)
                    event_index += 1
                    events.append(
                        _build_event_row(
                            match_row=match_row,
                            event_index=event_index,
                            event_type="assist",
                            minute=minute,
                            team_side=team_side,
                            player_name=player_name,
                            player_url=player_url,
                        )
                    )
                elif "sp-icon-card" in class_names:
                    lower_title = icon_title.lower()
                    if "yellow" in lower_title:
                        event_type = "yellow_card"
                    elif "red" in lower_title:
                        event_type = "red_card"
                    else:
                        continue

                    player_name, player_url = _extract_player_from_icon(icon)
                    event_index += 1
                    events.append(
                        _build_event_row(
                            match_row=match_row,
                            event_index=event_index,
                            event_type=event_type,
                            minute=minute,
                            team_side=team_side,
                            player_name=player_name,
                            player_url=player_url,
                        )
                    )
                elif "dashicons" in class_names and "sub out" in icon_title.lower():
                    sub_out_player_name, sub_out_player_url, sub_in_player_name, sub_in_player_url = _extract_substitution_players(cell)
                    event_index += 1
                    events.append(
                        _build_event_row(
                            match_row=match_row,
                            event_index=event_index,
                            event_type="substitution",
                            minute=minute,
                            team_side=team_side,
                            player_name=None,
                            sub_out_player_name=sub_out_player_name,
                            sub_out_player_url=sub_out_player_url,
                            sub_in_player_name=sub_in_player_name,
                            sub_in_player_url=sub_in_player_url,
                        )
                    )

    return events


def _extract_match_post_id(soup: BeautifulSoup) -> str | None:
    """Extract the WordPress post ID from the article or body classes."""
    article = soup.select_one("article[id^='post-']")
    if article and article.get("id"):
        return article["id"].replace("post-", "")

    body = soup.select_one("body")
    if body:
        for class_name in body.get("class", []):
            match = re.match(r"postid-(\d+)", class_name)
            if match:
                return match.group(1)

    return None


def _extract_team_links(soup: BeautifulSoup) -> list[tuple[str | None, str | None]]:
    """Extract the home and away team links from results or logos."""
    team_links = []

    for row in soup.select("table.sp-event-results tbody tr"):
        team_name, team_url = _first_anchor_info(row.select_one("td.data-name"))
        if team_name:
            team_links.append((team_name, team_url))

    if team_links:
        return team_links[:2]

    for logo in soup.select("div.sp-event-logos span.sp-team-logo"):
        team_name = _safe_text(logo.select_one("strong.sp-team-name"))
        team_url = None
        anchor = logo.select_one("a")
        if anchor is not None:
            team_url = anchor.get("href")
            if team_name is None:
                team_name = _safe_text(anchor.select_one("strong.sp-team-name")) or _safe_text(anchor)

        if team_name:
            team_links.append((team_name, team_url))

    return team_links[:2]


def _extract_match_row(soup: BeautifulSoup, match_url: str) -> dict[str, Any]:
    """Extract match-level metadata from a match page."""
    match_row: dict[str, Any] = {column: None for column in MATCH_COLUMNS}
    match_row["match_id"] = _extract_match_post_id(soup)
    match_row["match_url"] = match_url
    match_row["source_page_title"] = _safe_text(soup.select_one("h1.entry-title"))

    if match_row["source_page_title"] and " vs " in match_row["source_page_title"]:
        teams = match_row["source_page_title"].split(" vs ", maxsplit=1)
        match_row["home_team"] = _normalize_whitespace(teams[0])
        match_row["away_team"] = _normalize_whitespace(teams[1])

    team_links = _extract_team_links(soup)
    if team_links:
        home_team_name, home_team_url = team_links[0]
        away_team_name, away_team_url = team_links[1] if len(team_links) > 1 else (None, None)

        match_row["home_team"] = match_row["home_team"] or home_team_name
        match_row["away_team"] = match_row["away_team"] or away_team_name
        match_row["home_team_url"] = home_team_url
        match_row["away_team_url"] = away_team_url

    event_details_table = soup.select_one("table.sp-event-details")
    if event_details_table is not None:
        headers = [_normalize_key(th.get_text(strip=True)) for th in event_details_table.select("thead th")]
        data = [_normalize_whitespace(td.get_text(strip=True)) for td in event_details_table.select("tbody td")]
        for key, value in zip(headers, data):
            match_row[key] = value

    venue_table = soup.select_one("table.sp-event-venue")
    if venue_table is not None:
        match_row["ground_name"] = _safe_text(venue_table.select_one("thead th"))
        match_row["ground_address"] = _safe_text(venue_table.select_one("tr.sp-event-venue-address-row td"))

    excerpt = _safe_text(soup.select_one("p.sp-excerpt"))
    if excerpt:
        man_of_the_match_match = re.search(r"Man of The Match:\s*(.*?)\s*\((.*?)\)", excerpt)
        if man_of_the_match_match:
            match_row["man_of_the_match"] = man_of_the_match_match.group(1).strip()
            match_row["man_of_the_match_team"] = man_of_the_match_match.group(2).strip()
        else:
            match_row["man_of_the_match"] = excerpt

    for index, row in enumerate(soup.select("table.sp-event-results tbody tr")[:2]):
        side = "home" if index == 0 else "away"
        match_row[f"{side}_score"] = _safe_text(row.select_one("td.data-goals"))
        match_row[f"{side}_first_half_goals"] = _safe_text(row.select_one("td.data-firsthalf"))
        match_row[f"{side}_second_half_goals"] = _safe_text(row.select_one("td.data-secondhalf"))

    return match_row


def _infer_team_side(team_name: str | None, match_row: dict[str, Any], section_index: int) -> str | None:
    """Infer whether a team section belongs to the home or away team."""
    if team_name and match_row.get("home_team") and team_name == match_row["home_team"]:
        return "home"
    if team_name and match_row.get("away_team") and team_name == match_row["away_team"]:
        return "away"
    return "home" if section_index == 0 else "away"


def _extract_lineups_and_staff(soup: BeautifulSoup, match_row: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Extract team lineups and staff from the performance sections."""
    lineups: list[dict[str, Any]] = []
    staff_rows: list[dict[str, Any]] = []

    team_sections = soup.select("div.sp-event-performance-tables > div.sp-template-event-performance")

    for section_index, section in enumerate(team_sections):
        team_name = _safe_text(section.select_one("h4.sp-table-caption"))
        team_side = _infer_team_side(team_name, match_row, section_index)

        for row in section.select("table.sp-event-performance tbody tr"):
            row_classes = set(row.get("class", []))
            if "lineup" in row_classes:
                squad_role = "starting_xi"
            elif "sub" in row_classes:
                squad_role = "bench"
            else:
                squad_role = "unknown"

            player_cell = row.select_one("td.data-name")
            player_name, player_url = _first_anchor_info(player_cell)

            swap_badge = player_cell.select_one("span.sub-in, span.sub-out") if player_cell else None
            swap_badge_type = None
            linked_player_name = None
            linked_shirt_number = None

            if swap_badge is not None:
                swap_badge_type = "sub_in" if "sub-in" in swap_badge.get("class", []) else "sub_out"
                linked_player_name = _normalize_whitespace(swap_badge.get("title"))
                linked_shirt_number = _normalize_whitespace(swap_badge.get_text(strip=True))

            lineups.append(
                {
                    "match_id": match_row.get("match_id"),
                    "match_url": match_row.get("match_url"),
                    "season": match_row.get("season"),
                    "match_day": match_row.get("match_day"),
                    "home_team": match_row.get("home_team"),
                    "away_team": match_row.get("away_team"),
                    "team_name": team_name,
                    "team_side": team_side,
                    "squad_role": squad_role,
                    "shirt_number": _safe_text(row.select_one("td.data-number")),
                    "player_name": player_name,
                    "player_url": player_url,
                    "player_position": _safe_text(player_cell.select_one("small.sp-player-position")) if player_cell else None,
                    "is_player_of_match": bool(player_cell and player_cell.select_one("span.sp-event-stars")),
                    "swap_badge_type": swap_badge_type,
                    "linked_player_name": linked_player_name,
                    "linked_shirt_number": linked_shirt_number,
                }
            )

        staff_container = section.select_one("div.sp-template-event-staff p.sp-event-staff")
        if staff_container is None:
            continue

        for segment in _split_node_segments(staff_container):
            segment_text = _segment_text(segment)
            if not segment_text or ":" not in segment_text:
                continue

            role, _ = segment_text.split(":", maxsplit=1)
            person_name, person_url = _extract_player_from_segment(segment)
            staff_rows.append(
                {
                    "match_id": match_row.get("match_id"),
                    "match_url": match_row.get("match_url"),
                    "season": match_row.get("season"),
                    "match_day": match_row.get("match_day"),
                    "home_team": match_row.get("home_team"),
                    "away_team": match_row.get("away_team"),
                    "team_name": team_name,
                    "team_side": team_side,
                    "role": _normalize_whitespace(role),
                    "person_name": person_name,
                    "person_url": person_url,
                }
            )

    return lineups, staff_rows


def _extract_officials(soup: BeautifulSoup, match_row: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract match officials from the officials table."""
    officials_table = soup.select_one("table.sp-event-officials")
    if officials_table is None:
        return []

    headers = [_safe_text(th) for th in officials_table.select("thead th")]
    cells = officials_table.select("tbody tr td")
    officials: list[dict[str, Any]] = []

    for role, cell in zip(headers, cells):
        for official_name in [_normalize_whitespace(text) for text in cell.stripped_strings]:
            if official_name:
                officials.append(
                    {
                        "match_id": match_row.get("match_id"),
                        "match_url": match_row.get("match_url"),
                        "season": match_row.get("season"),
                        "match_day": match_row.get("match_day"),
                        "home_team": match_row.get("home_team"),
                        "away_team": match_row.get("away_team"),
                        "role": role,
                        "official_name": official_name,
                    }
                )

    return officials


def _extract_stats(soup: BeautifulSoup, match_row: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract the summary stat tables shown below the lineups."""
    stats_container = soup.select_one("div.sp-template-event-statistics")
    if stats_container is None:
        return []

    stats_rows: list[dict[str, Any]] = []

    for label in stats_container.select("strong.sp-statistic-label"):
        table = label.find_next_sibling("table")
        if table is None:
            continue

        values = table.select("td.sp-statistic-value")
        home_value = _safe_text(values[0]) if len(values) > 0 else None
        away_value = _safe_text(values[1]) if len(values) > 1 else None

        stats_rows.append(
            {
                "match_id": match_row.get("match_id"),
                "match_url": match_row.get("match_url"),
                "season": match_row.get("season"),
                "match_day": match_row.get("match_day"),
                "home_team": match_row.get("home_team"),
                "away_team": match_row.get("away_team"),
                "statistic_name": _safe_text(label),
                "home_value": home_value,
                "away_value": away_value,
            }
        )

    return stats_rows


def parse_match_page(match_html: bytes, match_url: str) -> dict[str, Any]:
    """
    Extract structured tables from one match page.

    Output shape:
    - one match row
    - zero or more related rows for each secondary table
    """
    soup = BeautifulSoup(match_html, "html.parser")

    match_row = _extract_match_row(soup, match_url)
    events = _extract_timeline_events(soup, match_row)
    lineups, staff_rows = _extract_lineups_and_staff(soup, match_row)
    officials = _extract_officials(soup, match_row)
    stats_rows = _extract_stats(soup, match_row)

    match_row["has_timeline"] = bool(events)
    match_row["has_lineups"] = bool(lineups)
    match_row["has_officials"] = bool(officials)
    match_row["has_stats"] = bool(stats_rows)

    return {
        "match": match_row,
        "events": events,
        "lineups": lineups,
        "staff": staff_rows,
        "officials": officials,
        "stats": stats_rows,
    }


