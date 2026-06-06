UPL Lens — Text Wireframe Layouts

1. Wireframe purpose

These wireframes define the layout structure for each major UPL Lens page before visual design and coding.

The intelligence-layer page wireframes near the top of this file take
precedence over older baseline page examples when they conflict.

**They are intentionally low-fidelity. They describe:**

- what appears on each page

- where it appears

- what the user sees first

- how sections relate to each other

- what actions are available

- how desktop and mobile layouts differ

- They do not define final colours, typography, spacing, animations, or implementation details.

Source-record boundary:

- The official UPL website is the source archive.

- UPL Lens should transform source details into football intelligence, summarize
  compact context where needed, and link to the official source for full archive
  detail.

- Wireframes should not recreate full official match pages, raw timelines,
  lineups, officials lists, or plain fixtures unless the layout adds analytical
  meaning.

## Intelligence-layer page wireframes

Use these current content wireframes when implementing the backend-upgraded
pages. They describe page purpose, main modules, and the data shapes the UI
should surface.

- Overview
  - Page header, Season Pulse, Things to Notice, Recent Signal Matches, Team
    Signals, Featured Insight, Data Quality / Freshness Note.
  - Visual slots: compact gauge bars, trend teaser mini-chart, small match
    signal cards.
  - Backend: `/seasons/overview`, `/overview/intelligence`,
    `/matches/intelligence`, `/teams`, `/insights/goal-timing`.
- Matches
  - Page header, signal filter panel, intelligence summary strip, match signal
    cards/list, evidence quality summary.
  - Visual slots: interest sort chips, compact signal labels, result/late-drama
    indicators.
  - Backend: `/matches/intelligence`, `/matches/{match_id}`.
- Match Detail
  - Page header, signal summary, key moments, event timeline rail, score
    progression, event phase summary, compact source metadata, data
    completeness note, official source link.
  - Visual slots: key-moment rail, phase groupings, score progression strip.
  - Backend: `/matches/{match_id}`.
- Teams
  - Page header, team summary strip, attack vs defence comparison, points vs
    goal difference comparison, archetype/profile labels, team ranking cards.
  - Visual slots: scatter plots, horizontal comparison bars.
  - Backend: `/teams`.
- Team Detail
  - Page header, record summary, attack/defence profile, home/away split,
    recent form strip, recent goals for/against visual, goal timing mini-chart,
    discipline summary, data quality note.
  - Visual slots: form strip, mini chart, comparison cards.
  - Backend: `/teams/{team_slug}/profile`.
- Players
  - Page header, grouped leaderboards, filters/search/sort, contribution
    categories, data-quality caveat.
  - Visual slots: contribution bars, leaderboard cards, goals vs starts
    scatter.
  - Backend: `/players`, `/players/leaderboards`.
- Player Detail
  - Page header, contribution identity, output rates, starts share, season
    trend, recent involvement, data-quality note.
  - Visual slots: season trend strip, contribution metrics, recent-match rows.
  - Backend: `/players/{player_slug}`.
- Trends
  - Page header, trends summary cards, scoring over time, discipline over
    time, home/draw/away result trend, high-scoring match share, late-goal
    trend, timeline/data coverage quality, season comparison table.
  - Visual slots: season charts, 100% stacked bars, timeline coverage bars.
  - Backend: `/trends/seasons`.
- About
  - Page header, independent/not official note, source record vs intelligence
    layer explanation, data pipeline summary, data-quality notes, maintainer
    links, social links.
  - Backend: mostly static, optional `/health` status chip.

- 2. Global layout wireframe

- ## Desktop app shell

```text
┌──────────────────────────────────────────────────────────────────────────────┐

│ SIDEBAR │ TOP BAR │

│ │ ┌────────────────────────────────────────┐ │

│ [UPL Lens] │ │ Season selector | Search | Data status │ │

│ Uganda Premier League │ └────────────────────────────────────────┘ │

│ match intelligence │ │

│ │ PAGE CONTENT AREA │

│ PRIMARY NAV │ ┌────────────────────────────────────────┐ │

│ ○ Overview │ │ │ │

│ ○ Matches │ │ Current page content │ │

│ ○ Teams │ │ │ │

│ ○ Insights │ │ │ │

│ ○ Trends │ │ │ │

│ │ └────────────────────────────────────────┘ │

│ │ │

│ SECONDARY NAV │ FOOTER STRIP │

│ ○ About │ ┌────────────────────────────────────────┐ │

│ ○ Methodology │ │ UPL Lens | Built by Humphrey | Links │ │

│ ○ GitHub │ └────────────────────────────────────────┘ │

│ ○ Social links │ │

│ │ │

│ DATA STATUS │ │

│ [Data live / waking up] │ │

└──────────────────────────────────────────────────────────────────────────────┘

```
## Mobile app shell

```text
┌────────────────────────────────────┐

│ TOP HEADER │

│ [UPL Lens] [Menu/Search] │

│ Uganda Premier League insights │

├────────────────────────────────────┤

│ PRIMARY NAV / MENU │

│ Overview | Matches | Teams | More │

├────────────────────────────────────┤

│ SEASON / DATA STATUS │

│ [2025/26 ▼] [Data live] │

├────────────────────────────────────┤

│ PAGE CONTENT │

│ │

│ Current page sections │

│ stacked vertically │

│ │

├────────────────────────────────────┤

│ FOOTER │

│ UPL Lens │

│ Built and maintained by Humphrey │

│ About | Methodology | GitHub │

│ Social links │

└────────────────────────────────────┘

```
3. Overview page wireframe

Route

/

Desktop wireframe

```text
┌──────────────────────────────────────────────────────────────────────────────┐

│ PAGE HEADER │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ UPL Lens │ │

│ │ Uganda Premier League match intelligence and statistical insights. │ │

│ │ │ │

│ │ UPL Lens helps fans, analysts, and football professionals understand │ │

│ │ the Uganda Premier League through trusted match data, statistical │ │

│ │ insights, and team-level exploration. │ │

│ │ │ │

│ │ [Selected season: 2025/26 ▼] [Data live] [Last updated: date] │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

│ │

│ KPI ROW │

│ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ │

│ │ Matches │ │ Teams │ │ Timeline │ │ Cards │ │

│ │ covered │ │ tracked │ │ goals │ │ logged │ │

│ │ 000 │ │ 00 │ │ 000 │ │ 000 │ │

│ │ context text │ │ context text │ │ context text │ │ context text │ │

│ └───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘ │

│ │

│ MAIN OVERVIEW GRID │

│ ┌───────────────────────────────────────────────┐ ┌──────────────────────┐ │

│ │ FEATURED INSIGHT │ │ TEAM SIGNALS │ │

│ │ │ │ │ │

│ │ [Label: Featured insight] │ │ Top teams / signals │ │

│ │ Goal Timing │ │ │ │

│ │ Short insight summary │ │ 1. Team name metric │ │

│ │ │ │ 2. Team name metric │ │

│ │ [Compact chart preview] │ │ 3. Team name metric │ │

│ │ │ │ │ │

│ │ Main finding / key number │ │ [View Teams →] │ │

│ │ [Open insight →] [Read full write-up →] │ │ │ │

│ └───────────────────────────────────────────────┘ └──────────────────────┘ │

│ │

│ ┌───────────────────────────────────────────────┐ ┌──────────────────────┐ │

│ │ RECENT MATCHES │ │ TRENDS TEASER │ │

│ │ │ │ │ │

│ │ Match row: Team A 2–1 Team B │ │ Compare seasons by │ │

│ │ Match row: Team C 0–0 Team D │ │ goals, cards, teams, │ │

│ │ Match row: Team E 1–3 Team F │ │ and match coverage. │ │

│ │ Match row: Team G 2–2 Team H │ │ │ │

│ │ │ │ [View Trends →] │ │

│ │ [View all matches →] │ │ │ │

│ └───────────────────────────────────────────────┘ └──────────────────────┘ │

│ │

│ QUIET TRUST NOTE │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ Built from official UPL match pages. Methodology and data notes are │ │

│ │ available. [View methodology →] │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

└──────────────────────────────────────────────────────────────────────────────┘

```
Mobile wireframe

```text
┌────────────────────────────────────┐

│ UPL Lens │

│ Uganda Premier League match │

│ intelligence and statistical │

│ insights. │

│ │

│ Core product promise text │

│ │

│ [2025/26 ▼] [Data live] │

├────────────────────────────────────┤

│ KPI GRID │

│ ┌──────────────┐ ┌──────────────┐ │

│ │ Matches │ │ Teams │ │

│ │ 000 │ │ 00 │ │

│ └──────────────┘ └──────────────┘ │

│ ┌──────────────┐ ┌──────────────┐ │

│ │ Goals │ │ Cards │ │

│ │ 000 │ │ 000 │ │

│ └──────────────┘ └──────────────┘ │

├────────────────────────────────────┤

│ FEATURED INSIGHT │

│ Goal Timing │

│ Short summary │

│ [Compact chart] │

│ Key finding │

│ [Open insight →] │

├────────────────────────────────────┤

│ RECENT MATCHES │

│ Team A 2–1 Team B │

│ Team C 0–0 Team D │

│ Team E 1–3 Team F │

│ [View all matches →] │

├────────────────────────────────────┤

│ TEAM SIGNALS │

│ 1. Team name — metric │

│ 2. Team name — metric │

│ 3. Team name — metric │

│ [View Teams →] │

├────────────────────────────────────┤

│ TRENDS │

│ Compare seasons across scoring, │

│ cards, and coverage. │

│ [View Trends →] │

├────────────────────────────────────┤

│ TRUST NOTE │

│ Built from official UPL match │

│ pages. [Methodology →] │

└────────────────────────────────────┘

```
4. Matches page wireframe

Route

/matches

Desktop wireframe

```text
┌──────────────────────────────────────────────────────────────────────────────┐

│ PAGE HEADER │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ Matches │ │

│ │ Browse UPL matches by season, team, result, and matchday, then open │ │

│ │ match intelligence briefs. │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

│ │

│ FILTER PANEL │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ Search matches... │ │

│ │ [Search input] │ │

│ │ │ │

│ │ [Season ▼] [Team ▼] [Matchday ▼] [Result ▼] [Clear filters] │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

│ │

│ FILTERED SUMMARY │

│ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ │

│ │ Matches found │ │ Completed │ │ Avg goals │ │ Teams shown │ │

│ │ 000 │ │ 000 │ │ 0.0 │ │ 00 │ │

│ └───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘ │

│ │

│ MATCH LIST │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ Match card / row │ │

│ │ Date | Matchday | Venue │ │

│ │ Home Team 2 - 1 Away Team │ │

│ │ Result label | data indicator [Open match →] │ │

│ ├──────────────────────────────────────────────────────────────────────────┤ │

│ │ Match card / row │ │

│ │ Date | Matchday | Venue │ │

│ │ Home Team 0 - 0 Away Team │ │

│ │ Result label | data indicator [Open match →] │ │

│ ├──────────────────────────────────────────────────────────────────────────┤ │

│ │ Match card / row │ │

│ │ Date | Matchday | Venue │ │

│ │ Home Team 3 - 2 Away Team │ │

│ │ Result label | data indicator [Open match →] │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

│ │

│ PAGINATION / LOAD MORE │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ [Previous] [Page / count] [Next] or [Load more matches] │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

└──────────────────────────────────────────────────────────────────────────────┘

```
Mobile wireframe

```text
┌────────────────────────────────────┐

│ Matches │

│ Browse UPL matches by season, team,│

│ result, and matchday. │

├────────────────────────────────────┤

│ SEARCH │

│ [Search matches...] │

├────────────────────────────────────┤

│ FILTERS │

│ [Season ▼] │

│ [Team ▼] │

│ [Matchday ▼] │

│ [Result ▼] │

│ [Clear filters] │

├────────────────────────────────────┤

│ SUMMARY │

│ Matches found: 000 │

│ Completed: 000 │

│ Avg goals: 0.0 │

├────────────────────────────────────┤

│ MATCH CARD │

│ Date | Matchday │

│ Home Team │

│ 2 - 1 │

│ Away Team │

│ Venue │

│ [Open match →] │

├────────────────────────────────────┤

│ MATCH CARD │

│ Date | Matchday │

│ Home Team │

│ 0 - 0 │

│ Away Team │

│ Venue │

│ [Open match →] │

├────────────────────────────────────┤

│ [Load more matches] │

└────────────────────────────────────┘

```
5. Match Intelligence Brief page wireframe

Route

/matches/:matchId

Desktop wireframe

```text
┌──────────────────────────────────────────────────────────────────────────────┐

│ BREADCRUMB / BACK LINK │

│ ← Back to Matches │

│ │

│ MATCH HEADER │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ Season | Matchday | Date | Venue │ │

│ │ │ │

│ │ ┌────────────────────┐ SCORELINE ┌────────────────────┐ │ │

│ │ │ Home Team │ 2 - 1 │ Away Team │ │ │

│ │ │ [View profile] │ │ [View profile] │ │ │

│ │ └────────────────────┘ └────────────────────┘ │ │

│ │ │ │

│ │ Result label | Man of the match, if available | Source link │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

│ │

│ MAIN MATCH GRID │

│ ┌───────────────────────────────────────────────┐ ┌──────────────────────┐ │

│ │ MATCH INTELLIGENCE │ │ MATCH CONTEXT │ │

│ │ │ │ │ │

│ │ Key pattern │ │ League │ │

│ │ Team A scored twice before halftime │ │ Season │ │

│ │ and protected the lead late. │ │ Matchday │ │

│ │ │ │ Date/time │ │

│ │ Supporting events │ │ Venue │ │

│ │ 12' Goal Team A Player Name │ │ Ground address │ │

│ │ 45' Goal Team A Player Name │ │ │ │

│ │ 88' Goal Team B Player Name │ │ DATA COMPLETENESS │ │

│ │ [Open full official record] │ │ [Event intelligence] │ │

│ │ │ │ [Stats available] │ │

│ │ │ │ [Officials context] │ │

│ └───────────────────────────────────────────────┘ └──────────────────────┘ │

│ │

│ LOWER MATCH GRID │

│ ┌───────────────────────────────────────────────┐ ┌──────────────────────┐ │

│ │ MATCH STATS │ │ OFFICIALS CONTEXT │ │

│ │ │ │ │ │

│ │ Statistic Home Away │ │ Referee: Name │ │

│ │ Possession 00 00 │ │ Discipline context, if │ │

│ │ Shots 00 00 │ │ available │ │

│ │ Corners 00 00 │ │ [Full official source] │ │

│ │ Fouls 00 00 │ │ │ │

│ └───────────────────────────────────────────────┘ └──────────────────────┘ │

│ │

│ RELATED ACTIONS │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ [View Home Team] [View Away Team] [View all Matches] [Methodology] │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

└──────────────────────────────────────────────────────────────────────────────┘

```
Mobile wireframe

```text
┌────────────────────────────────────┐

│ ← Back to Matches │

├────────────────────────────────────┤

│ MATCH HEADER │

│ Season | Matchday | Date │

│ Venue │

│ │

│ Home Team │

│ 2 - 1 │

│ Away Team │

│ │

│ Result label │

│ [Source link] │

├────────────────────────────────────┤

│ DATA STATUS │

│ [Event intelligence] │

│ [Stats available] │

│ [Officials context] │

├────────────────────────────────────┤

│ MATCH INTELLIGENCE │

│ Key pattern │

│ Team A scored twice before │

│ halftime and protected the │

│ lead late. │

│ │

│ Supporting events │

│ 12' Goal — Team A — Player │

│ 45' Goal — Team A — Player │

│ 88' Goal — Team B — Player │

│ [Open full official record] │

├────────────────────────────────────┤

│ MATCH STATS │

│ Statistic Home Away │

│ Shots 00 00 │

│ Corners 00 00 │

│ Fouls 00 00 │

├────────────────────────────────────┤

│ OFFICIALS CONTEXT │

│ Referee: Name │

│ Discipline note, if available │

│ [Full official source] │

├────────────────────────────────────┤

│ RELATED │

│ [Home team profile] │

│ [Away team profile] │

│ [All matches] │

└────────────────────────────────────┘

```
6. Teams page wireframe

Route

/teams

Desktop wireframe

```text
┌──────────────────────────────────────────────────────────────────────────────┐

│ PAGE HEADER │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ Teams │ │

│ │ Compare UPL teams by record, scoring, conceding, and season-level │ │

│ │ performance signals. │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

│ │

│ CONTROLS │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ [Season ▼] [Search team...] [Sort by ▼] │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

│ │

│ TEAM SUMMARY ROW │

│ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ │

│ │ Teams tracked │ │ Top attack │ │ Tightest def. │ │ Best GD │ │

│ │ 00 │ │ Team / goals │ │ Team / goals │ │ Team / value │ │

│ └───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘ │

│ │

│ TEAM RANKING / CARD GRID │

│ ┌──────────────────────────────┐ ┌──────────────────────────────┐ │

│ │ #1 Team Name │ │ #2 Team Name │ │

│ │ Record: W-D-L │ │ Record: W-D-L │ │

│ │ Matches: 00 │ │ Matches: 00 │ │

│ │ GF: 00 | GA: 00 | GD: +00 │ │ GF: 00 | GA: 00 | GD: +00 │ │

│ │ Win rate: 00% │ │ Win rate: 00% │ │

│ │ [Open profile →] │ │ [Open profile →] │ │

│ └──────────────────────────────┘ └──────────────────────────────┘ │

│ │

│ ┌──────────────────────────────┐ ┌──────────────────────────────┐ │

│ │ #3 Team Name │ │ #4 Team Name │ │

│ │ Record: W-D-L │ │ Record: W-D-L │ │

│ │ Matches: 00 │ │ Matches: 00 │ │

│ │ GF: 00 | GA: 00 | GD: +00 │ │ GF: 00 | GA: 00 | GD: +00 │ │

│ │ [Open profile →] │ │ [Open profile →] │ │

│ └──────────────────────────────┘ └──────────────────────────────┘ │

└──────────────────────────────────────────────────────────────────────────────┘

```
Mobile wireframe

```text
┌────────────────────────────────────┐

│ Teams │

│ Compare UPL teams by record, │

│ scoring, and conceding. │

├────────────────────────────────────┤

│ CONTROLS │

│ [Season ▼] │

│ [Search team...] │

│ [Sort by ▼] │

├────────────────────────────────────┤

│ SUMMARY │

│ Teams tracked: 00 │

│ Top attack: Team / goals │

│ Tightest defence: Team / conceded │

├────────────────────────────────────┤

│ TEAM CARD │

│ #1 Team Name │

│ W-D-L │

│ Matches: 00 │

│ GF 00 | GA 00 | GD +00 │

│ [Open profile →] │

├────────────────────────────────────┤

│ TEAM CARD │

│ #2 Team Name │

│ W-D-L │

│ Matches: 00 │

│ GF 00 | GA 00 | GD +00 │

│ [Open profile →] │

└────────────────────────────────────┘

```
7. Team Profile page wireframe

Route

/teams/:teamSlug

Desktop wireframe

```text
┌──────────────────────────────────────────────────────────────────────────────┐

│ BREADCRUMB / BACK LINK │

│ ← Back to Teams │

│ │

│ TEAM HEADER │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ [Team marker] Team Name │ │

│ │ Season: [2025/26 ▼] │ │

│ │ Record: W-D-L | Matches: 00 | Goal difference: +00 │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

│ │

│ TEAM KPI ROW │

│ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ │

│ │ Matches │ │ Wins │ │ Goals for │ │ Goals against │ │

│ │ 00 │ │ 00 │ │ 00 │ │ 00 │ │

│ └───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘ │

│ │

│ MAIN TEAM GRID │

│ ┌───────────────────────────────────────────────┐ ┌──────────────────────┐ │

│ │ RECENT MATCHES │ │ SCORING PROFILE │ │

│ │ │ │ │ │

│ │ Date | Opponent | H/A | Score | Result │ │ Goals for: 00 │ │

│ │ Date | Opponent | H/A | Score | Result │ │ Goals against: 00 │ │

│ │ Date | Opponent | H/A | Score | Result │ │ GD: +00 │ │

│ │ Date | Opponent | H/A | Score | Result │ │ Goals per match │ │

│ │ │ │ Conceded per match │ │

│ │ [View all team matches →] │ │ │ │

│ └───────────────────────────────────────────────┘ └──────────────────────┘ │

│ │

│ SECONDARY TEAM GRID │

│ ┌───────────────────────────────────────────────┐ ┌──────────────────────┐ │

│ │ EVENT SUMMARY │ │ RELATED │ │

│ │ │ │ │ │

│ │ Goals: 00 │ │ [All Teams] │ │

│ │ Yellow cards: 00 │ │ [Team matches] │ │

│ │ Red cards: 00 │ │ [Relevant insights] │ │

│ │ Substitutions: 00 │ │ [Methodology] │ │

│ └───────────────────────────────────────────────┘ └──────────────────────┘ │

└──────────────────────────────────────────────────────────────────────────────┘

```
Mobile wireframe

```text
┌────────────────────────────────────┐

│ ← Back to Teams │

├────────────────────────────────────┤

│ TEAM HEADER │

│ [Team marker] Team Name │

│ [Season ▼] │

│ Record: W-D-L │

│ Goal difference: +00 │

├────────────────────────────────────┤

│ KPI GRID │

│ Matches: 00 │

│ Wins: 00 │

│ Goals for: 00 │

│ Goals against: 00 │

├────────────────────────────────────┤

│ RECENT MATCHES │

│ Date | Opponent | Score | Result │

│ Date | Opponent | Score | Result │

│ Date | Opponent | Score | Result │

│ [View all team matches →] │

├────────────────────────────────────┤

│ SCORING PROFILE │

│ Goals for: 00 │

│ Goals against: 00 │

│ Goal difference: +00 │

│ Goals per match: 0.0 │

├────────────────────────────────────┤

│ EVENT SUMMARY │

│ Goals: 00 │

│ Yellow cards: 00 │

│ Red cards: 00 │

├────────────────────────────────────┤

│ RELATED │

│ [All Teams] │

│ [Relevant insights] │

└────────────────────────────────────┘

```
8. Insights Library page wireframe

Route

/insights

Desktop wireframe

```text
┌──────────────────────────────────────────────────────────────────────────────┐

│ PAGE HEADER │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ Insights │ │

│ │ Explore promoted UPL analyses developed from notebook research and │ │

│ │ turned into interactive product features. │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

│ │

│ FEATURED / LATEST INSIGHT │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ Featured Insight │ │

│ │ Goal Timing │ │

│ │ │ │

│ │ Short summary of the football question and main finding. │ │

│ │ │ │

│ │ Primary metric / finding │ │

│ │ Season scope | Promoted date | Data note │ │

│ │ │ │

│ │ [Open interactive insight →] [Read full write-up →] │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

│ │

│ INSIGHT LIBRARY GRID │

│ ┌──────────────────────────────┐ ┌──────────────────────────────┐ │

│ │ Insight Card │ │ Future Insight Card │ │

│ │ Goal Timing │ │ Discipline Trends │ │

│ │ Football question │ │ Status: future/not shown if │ │

│ │ Main metric │ │ not promoted │ │

│ │ Season scope │ │ │ │

│ │ [Open →] [Write-up →] │ │ │ │

│ └──────────────────────────────┘ └──────────────────────────────┘ │

│ │

│ METHODOLOGY LINK │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ How insights are promoted from notebook research. [Methodology →] │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

└──────────────────────────────────────────────────────────────────────────────┘

```
Mobile wireframe

```text
┌────────────────────────────────────┐

│ Insights │

│ Promoted UPL analyses from │

│ notebook research, turned into │

│ interactive product features. │

├────────────────────────────────────┤

│ FEATURED INSIGHT │

│ Goal Timing │

│ Short summary │

│ Main finding │

│ Season scope │

│ [Open insight →] │

│ [Read write-up →] │

├────────────────────────────────────┤

│ INSIGHT CARD │

│ Goal Timing │

│ Football question │

│ Main metric │

│ [Open →] │

├────────────────────────────────────┤

│ METHODOLOGY │

│ How insights are promoted. │

│ [Methodology →] │

└────────────────────────────────────┘

```
9. Insight Detail page wireframe

Route

/insights/:insightSlug

Example

/insights/goal-timing

Desktop wireframe

```text
┌──────────────────────────────────────────────────────────────────────────────┐

│ BREADCRUMB / BACK LINK │

│ ← Back to Insights │

│ │

│ INSIGHT HEADER │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ Goal Timing │ │

│ │ Short summary of the insight. │ │

│ │ Season scope | Promoted insight | Updated date │ │

│ │ [Season selector ▼] │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

│ │

│ INSIGHT STORY + SUMMARY │

│ ┌───────────────────────────────────────────────┐ ┌──────────────────────┐ │

│ │ FOOTBALL QUESTION │ │ MAIN FINDING │ │

│ │ │ │ │ │

│ │ When do UPL goals arrive during regular time? │ │ Peak interval │ │

│ │ │ │ Total regular goals │ │

│ │ Short explanation of what the insight tests. │ │ Second-half share │ │

│ │ │ │ │ │

│ └───────────────────────────────────────────────┘ └──────────────────────┘ │

│ │

│ INTERACTIVE MODULE │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ Goal timing distribution │ │

│ │ │ │

│ │ [Bar chart: 0–15 | 16–30 | 31–45 | 46–60 | 61–75 | 76–90] │ │

│ │ │ │

│ │ Tooltip / hover details │ │

│ │ Peak interval highlighted │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

│ │

│ INTERPRETATION + CAVEAT │

│ ┌───────────────────────────────────────────────┐ ┌──────────────────────┐ │

│ │ SHORT INTERPRETATION │ │ DATA NOTE │ │

│ │ │ │ │ │

│ │ What the chart suggests, written briefly. │ │ Added-time goals are │ │

│ │ Avoid overclaiming. │ │ excluded. Uses │ │

│ │ │ │ cleaned event data. │ │

│ └───────────────────────────────────────────────┘ └──────────────────────┘ │

│ │

│ FULL WRITE-UP + RELATED │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ [Read the full analysis on Substack →] │ │

│ │ [Back to Insights] [View Trends] [View Methodology] │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

└──────────────────────────────────────────────────────────────────────────────┘

```
Mobile wireframe

```text
┌────────────────────────────────────┐

│ ← Back to Insights │

├────────────────────────────────────┤

│ Goal Timing │

│ Short summary │

│ Season scope | Updated date │

│ [Season ▼] │

├────────────────────────────────────┤

│ FOOTBALL QUESTION │

│ When do UPL goals arrive during │

│ regular time? │

├────────────────────────────────────┤

│ MAIN FINDING │

│ Peak interval: 00–00 │

│ Total regular goals: 000 │

│ Second-half share: 00% │

├────────────────────────────────────┤

│ CHART │

│ [Responsive bar chart] │

│ 0–15 | 16–30 | 31–45 | etc. │

├────────────────────────────────────┤

│ INTERPRETATION │

│ Short explanation of what this │

│ suggests. │

├────────────────────────────────────┤

│ DATA NOTE │

│ Added-time goals excluded. Uses │

│ cleaned event timeline data. │

├────────────────────────────────────┤

│ [Read full analysis on Substack] │

│ [Methodology] │

└────────────────────────────────────┘

```
10. Trends page wireframe

Route

/trends

Desktop wireframe

```text
┌──────────────────────────────────────────────────────────────────────────────┐

│ PAGE HEADER │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ Trends │ │

│ │ Compare UPL seasons across match coverage, scoring, cards, and other │ │

│ │ league-wide signals. │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

│ │

│ TRENDS SUMMARY ROW │

│ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ │

│ │ Seasons │ │ Latest season │ │ Total matches │ │ Total goals │ │

│ │ available │ │ 2025/26 │ │ 000 │ │ 000 │ │

│ └───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘ │

│ │

│ MAIN TRENDS GRID │

│ ┌───────────────────────────────────────────────┐ ┌──────────────────────┐ │

│ │ GOALS BY SEASON │ │ MATCH COVERAGE │ │

│ │ │ │ │ │

│ │ [Line/bar chart] │ │ [Chart/cards] │ │

│ │ Season → goals │ │ Season → matches │ │

│ │ │ │ Season → teams │ │

│ └───────────────────────────────────────────────┘ └──────────────────────┘ │

│ │

│ SECONDARY TRENDS GRID │

│ ┌───────────────────────────────────────────────┐ ┌──────────────────────┐ │

│ │ CARDS BY SEASON │ │ SEASON WINDOWS │ │

│ │ │ │ │ │

│ │ [Chart if reliable] │ │ Season date ranges │ │

│ │ Yellow cards / red cards │ │ First match │ │

│ │ │ │ Last match │ │

│ └───────────────────────────────────────────────┘ └──────────────────────┘ │

│ │

│ COVERAGE NOTE │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ Historical comparisons depend on available source coverage. See │ │

│ │ methodology for data notes. [Methodology →] │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

└──────────────────────────────────────────────────────────────────────────────┘

```
Mobile wireframe

```text
┌────────────────────────────────────┐

│ Trends │

│ Compare UPL seasons across scoring,│

│ cards, teams, and coverage. │

├────────────────────────────────────┤

│ SUMMARY │

│ Seasons available: 00 │

│ Latest season: 2025/26 │

│ Total matches: 000 │

│ Total goals: 000 │

├────────────────────────────────────┤

│ GOALS BY SEASON │

│ [Responsive chart] │

├────────────────────────────────────┤

│ MATCH COVERAGE │

│ [Chart/cards] │

├────────────────────────────────────┤

│ CARDS BY SEASON │

│ [Chart if reliable] │

├────────────────────────────────────┤

│ SEASON WINDOWS │

│ 2025/26: date → date │

│ 2024/25: date → date │

├────────────────────────────────────┤

│ COVERAGE NOTE │

│ Historical comparison depends on │

│ available source coverage. │

│ [Methodology →] │

└────────────────────────────────────┘

```
11. About page wireframe

Route

/about

Desktop wireframe

```text
┌──────────────────────────────────────────────────────────────────────────────┐

│ PAGE HEADER │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ About UPL Lens │ │

│ │ UPL Lens is an independent Uganda Premier League football intelligence │ │

│ │ product. │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

│ │

│ ABOUT CONTENT GRID │

│ ┌───────────────────────────────────────────────┐ ┌──────────────────────┐ │

│ │ WHAT IT IS │ │ PRODUCT LINKS │ │

│ │ │ │ │ │

│ │ UPL Lens turns official UPL match data into │ │ GitHub │ │

│ │ structured views, statistical insights, and │ │ Substack │ │

│ │ team-level exploration. │ │ X/Twitter │ │

│ │ │ │ LinkedIn, if used │ │

│ └───────────────────────────────────────────────┘ └──────────────────────┘ │

│ │

│ ┌───────────────────────────────────────────────┐ ┌──────────────────────┐ │

│ │ WHY IT EXISTS │ │ MAINTAINER │ │

│ │ │ │ │ │

│ │ The official UPL website is the source │ │ Built and maintained │ │

│ │ archive. UPL Lens helps users understand │ │ by Humphrey. │ │

│ │ patterns that are difficult to see from │ │ │ │

│ │ individual match pages alone. │ │ │ │

│ └───────────────────────────────────────────────┘ └──────────────────────┘ │

│ │

│ INDEPENDENCE NOTE │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ UPL Lens is independent and is not a replacement for the official UPL │ │

│ │ website. │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

└──────────────────────────────────────────────────────────────────────────────┘

```
Mobile wireframe

```text
┌────────────────────────────────────┐

│ About UPL Lens │

│ Independent Uganda Premier League │

│ football intelligence product. │

├────────────────────────────────────┤

│ WHAT IT IS │

│ UPL Lens turns official UPL match │

│ data into structured views, │

│ insights, and team exploration. │

├────────────────────────────────────┤

│ WHY IT EXISTS │

│ The official UPL website is the │

│ source archive. UPL Lens helps │

│ users understand patterns beyond │

│ individual match pages. │

├────────────────────────────────────┤

│ MAINTAINER │

│ Built and maintained by Humphrey. │

├────────────────────────────────────┤

│ LINKS │

│ GitHub │

│ Substack │

│ X/Twitter │

│ LinkedIn │

├────────────────────────────────────┤

│ NOTE │

│ UPL Lens is independent and is not │

│ a replacement for the official UPL │

│ website. │

└────────────────────────────────────┘

```
12. Methodology page wireframe

Route

/methodology

Desktop wireframe

```text
┌──────────────────────────────────────────────────────────────────────────────┐

│ PAGE HEADER │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ Methodology & Data Quality │ │

│ │ How UPL Lens collects, structures, validates, and presents official UPL │ │

│ │ match data. │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

│ │

│ DATA SOURCE + FRESHNESS GRID │

│ ┌───────────────────────────────────────────────┐ ┌──────────────────────┐ │

│ │ DATA SOURCE │ │ DATA FRESHNESS │ │

│ │ │ │ │ │

│ │ Official UPL match pages are the source │ │ Data status │ │

│ │ archive. UPL Lens is the analysis layer. │ │ Latest refresh date │ │

│ │ │ │ Current season │ │

│ │ │ │ coverage │ │

│ └───────────────────────────────────────────────┘ └──────────────────────┘ │

│ │

│ PIPELINE │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ Official UPL website → scraper → Postgres → FastAPI → React frontend │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

│ │

│ METRIC DEFINITIONS │

│ ┌───────────────────────────────────────────────┐ ┌──────────────────────┐ │

│ │ Timeline goals │ │ Scoreline goals │ │

│ │ Definition in plain language │ │ Definition │ │

│ ├───────────────────────────────────────────────┤ ├──────────────────────┤ │

│ │ Cards logged │ │ Goal timing │ │

│ │ Definition │ │ Definition │ │

│ └───────────────────────────────────────────────┘ └──────────────────────┘ │

│ │

│ INSIGHT PROMOTION WORKFLOW │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ Notebook experiment → validated feature package → promoted insight → │ │

│ │ backend/API endpoint → frontend insight page │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

│ │

│ DATA QUALITY STATES │

│ ┌──────────────────────────┐ ┌──────────────────────────┐ ┌──────────────┐ │

│ │ Publishable │ │ Publishable with caveat │ │ Blocked │ │

│ │ Safe to show normally │ │ Show with explanation │ │ Do not show │ │

│ └──────────────────────────┘ └──────────────────────────┘ └──────────────┘ │

│ │

│ KNOWN LIMITATIONS │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ - Source pages may change │ │

│ │ - Some timelines may be incomplete │ │

│ │ - Some stats may be unavailable │ │

│ │ - Historical coverage may vary by season │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

│ │

│ REPOSITORY / RELATED LINKS │

│ ┌──────────────────────────────────────────────────────────────────────────┐ │

│ │ [GitHub repository] [About UPL Lens] │ │

│ └──────────────────────────────────────────────────────────────────────────┘ │

└──────────────────────────────────────────────────────────────────────────────┘

```
Mobile wireframe

```text
┌────────────────────────────────────┐

│ Methodology & Data Quality │

│ How UPL Lens collects, structures, │

│ validates, and presents UPL data. │

├────────────────────────────────────┤

│ DATA SOURCE │

│ Official UPL match pages are the │

│ source archive. UPL Lens is the │

│ analysis layer. │

├────────────────────────────────────┤

│ DATA FRESHNESS │

│ Status: Data live │

│ Latest refresh: date │

│ Current season coverage │

├────────────────────────────────────┤

│ PIPELINE │

│ Official UPL website │

│ → scraper │

│ → Postgres │

│ → FastAPI │

│ → React frontend │

├────────────────────────────────────┤

│ METRIC DEFINITIONS │

│ Timeline goals │

│ Scoreline goals │

│ Cards logged │

│ Goal timing intervals │

├────────────────────────────────────┤

│ INSIGHT PROMOTION │

│ Notebook experiment │

│ → validated feature package │

│ → promoted insight │

│ → API endpoint │

│ → frontend insight page │

├────────────────────────────────────┤

│ DATA QUALITY STATES │

│ Publishable │

│ Publishable with caveat │

│ Blocked from public display │

├────────────────────────────────────┤

│ KNOWN LIMITATIONS │

│ Source pages may change. │

│ Some timelines/stats may be │

│ incomplete. Historical coverage │

│ may vary by season. │

├────────────────────────────────────┤

│ LINKS │

│ [GitHub] [About] │

└────────────────────────────────────┘

```
13. Global search wireframe

Desktop search closed state

```text
┌──────────────────────────────────────────────┐

│ [Search teams, matches...] │

└──────────────────────────────────────────────┘

```
Desktop search open state

```text
┌──────────────────────────────────────────────┐

│ Search │

│ [Vipers______________________________] │

├──────────────────────────────────────────────┤

│ TEAMS │

│ Vipers SC [Open →] │

├──────────────────────────────────────────────┤

│ MATCHES │

│ Vipers SC 2–1 KCCA FC [Open →] │

│ SC Villa 0–0 Vipers SC [Open →] │

├──────────────────────────────────────────────┤

│ [View all results] optional │

└──────────────────────────────────────────────┘

```
Mobile search open state

```text
┌────────────────────────────────────┐

│ Search UPL Lens │

│ [Search...] │

├────────────────────────────────────┤

│ TEAMS │

│ Vipers SC │

├────────────────────────────────────┤

│ MATCHES │

│ Vipers SC 2–1 KCCA FC │

│ SC Villa 0–0 Vipers SC │

└────────────────────────────────────┘

```
Search should not appear as a fake placeholder. It must route to real pages.

14. Loading state wireframes

## Overview loading

```text
┌────────────────────────────────────┐

│ Header skeleton │

├────────────────────────────────────┤

│ KPI skeleton | KPI skeleton │

│ KPI skeleton | KPI skeleton │

├────────────────────────────────────┤

│ Featured insight skeleton │

├────────────────────────────────────┤

│ Recent matches skeleton │

├────────────────────────────────────┤

│ Team signals skeleton │

└────────────────────────────────────┘

```
## Match Intelligence Brief loading

```text
┌────────────────────────────────────┐

│ Back link │

├────────────────────────────────────┤

│ Scoreline header skeleton │

├────────────────────────────────────┤

│ Intelligence summary skeleton │

├────────────────────────────────────┤

│ Match stats skeleton │

├────────────────────────────────────┤

│ Officials context skeleton │

└────────────────────────────────────┘

```
## Team Profile loading

```text
┌────────────────────────────────────┐

│ Team header skeleton │

├────────────────────────────────────┤

│ KPI skeletons │

├────────────────────────────────────┤

│ Recent matches skeleton │

├────────────────────────────────────┤

│ Scoring profile skeleton │

└────────────────────────────────────┘

```
15. Empty state wireframes

Generic empty state

```text
┌────────────────────────────────────┐

│ No results found │

│ Short explanation of what is empty │

│ and what the user can try next. │

│ │

│ [Clear filters] [Go back] │

└────────────────────────────────────┘

```
Matches empty state

```text
┌────────────────────────────────────┐

│ No matches found │

│ No matches fit the current filters.│

│ Try changing the team, result, │

│ matchday, or season. │

│ │

│ [Clear filters] │

└────────────────────────────────────┘

```
Insight unavailable state

```text
┌────────────────────────────────────┐

│ Insight unavailable │

│ This promoted insight is not │

│ available for the selected season. │

│ │

│ [Back to Insights] [Change season] │

└────────────────────────────────────┘

```
16. Error state wireframes

API/data error

```text
┌────────────────────────────────────┐

│ Data service unavailable │

│ UPL Lens could not load data right │

│ now. The hosted API may be waking │

│ up or temporarily unavailable. │

│ │

│ [Retry] [View Methodology] │

└────────────────────────────────────┘

```
Match not found

```text
┌────────────────────────────────────┐

│ Match not found │

│ This match could not be found in │

│ the available UPL Lens data. │

│ │

│ [Back to Matches] │

└────────────────────────────────────┘

```
Team not found

```text
┌────────────────────────────────────┐

│ Team not found │

│ This team could not be found for │

│ the selected season. │

│ │

│ [Back to Teams] [Change season] │

└────────────────────────────────────┘

```
17. Final wireframe page order

**For implementation planning, use this page order:**

- 1. Global shell

- 2. Overview

- 3. Matches

- 4. Match Intelligence Brief

- 5. Teams

- 6. Team Profile

- 7. Insights Library

- 8. Insight Detail

- 9. Trends

- 10. About

- 11. Methodology

- 12. Search

- 13. Footer/support areas

- 14. Loading/empty/error states

- This order matches the public-launch priority and avoids building disconnected screens.
