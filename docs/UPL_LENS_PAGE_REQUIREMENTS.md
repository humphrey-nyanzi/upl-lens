
UPL Lens — Page-by-Page Frontend Requirements

1. Document purpose

This document defines the page-by-page frontend requirements for UPL Lens.

It should guide the next implementation phase after the information architecture. It is not a coding prompt yet. It defines what each page should do, what users need from it, what data it requires, what UI states it must handle, and what should remain out of scope.

The purpose is to prevent random frontend work and ensure the app grows as a coherent public football intelligence product.

2. Product context

## Product name

UPL Lens

## Product descriptor

Uganda Premier League match intelligence and statistical insights.

## Core product promise

UPL Lens helps fans, analysts, and football professionals understand the Uganda Premier League through trusted match data, statistical insights, and team-level exploration.

## Product type

UPL Lens is a public sports intelligence site.

**It should feel like:**

- a public football intelligence product

- - a league analysis layer

- - an interactive sports data publication

- **It should not feel like:**

- a generic admin dashboard

- a personal portfolio page

- a fixtures/results clone

- a betting-style stats site

- a notebook dump

- ## Main navigation

- **Primary product navigation:**

- Overview

- Matches

- Teams

- Insights

- Trends

- **Secondary/support navigation:**

- About

- Methodology

- GitHub

- Social links

- 3. Global frontend requirements

- ## Routing

- The frontend should move from hash-based navigation to proper routing.

- **Required routes:**

- / Overview

- /matches Match Explorer

- /matches/:matchId Match Detail

- /teams Team Index

- /teams/:teamSlug Team Profile

- /insights Insights Library

- /insights/:insightSlug Insight Detail

- /trends Historical Trends

- /about About

- /methodology Methodology & Data Quality

- Future routes should not be implemented unless the product and data are ready.

- **Future possible routes:**

- /players

- /players/:playerSlug

- /officials

- /search

- /contact

- ## Global shell

- The app should use a consistent product shell.

- **Desktop shell:**

- Sidebar

- Main workspace

- Top controls

- Page content

- Footer strip

- **Mobile shell:**

- Compact top header

- Primary navigation access

- Season selector where needed

- Single-column content

- Footer after content

- ## Global sidebar / navigation

- **The sidebar should include:**

- UPL Lens brand lockup

- Primary navigation

- Secondary/support links

- Data status indicator

- Primary navigation should be visually dominant.

- Secondary links should be visually quieter and placed near the bottom of the sidebar or in a separate support area.

- ## Global footer

- **The footer should include:**

- UPL Lens

- Uganda Premier League match intelligence and statistical insights.

- Built and maintained by Humphrey.

- © [year] UPL Lens.

- About

- Methodology

- GitHub

- Substack

- X/Twitter

- LinkedIn, if available

- **Footer behaviour:**

- Desktop: subtle footer strip at bottom of main content

- Mobile: footer after page content

- The footer must not overpower the product content.

- ## Global season selector

- The latest/current available season should be selected by default.

- **Season selection should affect:**

- Overview

- Matches

- Teams

- Team Profile

- Insight Detail, where season-specific

- Trends, where relevant

- The Trends page may compare multiple seasons and should not behave exactly like current-season pages.

- ## Global search

- Search should be real if displayed.

- **Minimum search scope:**

- teams

- matches

- venues, if available

- matchdays

- **Search results should be grouped:**

- Teams

- Matches

- Insights, later

- Players, later

- **Search should route users to:**

- /teams/:teamSlug

- /matches/:matchId

- /insights/:insightSlug, later

- Do not show a fake search placeholder in public launch UI.

- ## Global data status

- **A compact data status indicator should show:**

- API/data service status

- latest refresh/check date where available

- current selected season context

- **Possible labels:**

- Data live

- Data loading

- Service waking up

- Data unavailable

- Avoid large warning banners unless the data service is down or unsafe.

- ## Global loading states

- Each page must have a loading state shaped like the content being loaded.

- Avoid generic full-screen spinners except for the first app-level load.

- ## Global error states

- Error states should explain what failed.

- **Examples:**

- Could not load season overview.

- Could not load matches.

- Match not found.

- Team profile unavailable.

- Search failed.

- **Errors should offer a clear next step where possible:**

- Try refreshing.

- Return to Matches.

- Change season.

- ## Global empty states

- Empty states should be calm and helpful.

- **Bad:**

- No data.

- **Better:**

- No matches found for this filter. Try changing the team, result, or matchday.

- 4. Page requirements

- ## Overview Page

- Route

- /

- Page role

- The Overview page is the public landing page and main entry point into UPL Lens.

- It should quickly explain what the product is and show useful current-season football intelligence.

- Primary user questions

- **The page should answer:**

- What is UPL Lens?

- What is happening in the current UPL season?

- What insight should I pay attention to?

- Which matches or teams can I explore next?

- Can I trust this data?

- Target users

- UPL fans

- analysts

- journalists

- club staff

- technical reviewers

- Required page sections

- 1. Compact product header

- **Purpose:**

- Explain the product in one clear first impression.

- **Required content:**

- UPL Lens

- Uganda Premier League match intelligence and statistical insights.

- Core product promise

- Selected season context

- **Use this statement:**

- UPL Lens helps fans, analysts, and football professionals understand the Uganda Premier League through trusted match data, statistical insights, and team-level exploration.

- **Requirements:**

- Must not feel like a marketing landing hero.

- Must not be too tall.

- Must allow KPIs and featured insight to appear quickly.

- 2. Current season KPI row

- **Purpose:**

- Give a fast statistical snapshot of the selected season.

- **Suggested KPI cards:**

- Matches covered

- Teams tracked

- Timeline goals

- Cards logged

- Latest match date / season window

- **Each KPI should include:**

- short label

- large value

- one short context line

- optional subtle caveat if needed

- Avoid raw database labels.

- 3. Featured Insight module

- **Purpose:**

- Show the editor-selected featured insight.

- **Default logic:**

- If no editor-selected insight exists, show the latest promoted insight.

- **Current likely featured insight:**

- Goal Timing

- **Required content:**

- Insight title

- Short summary

- Main finding or key metric

- Compact chart/visual

- Link to insight detail page

- Optional link to full Substack write-up

- **Behaviour:**

- Clicking the module opens /insights/:insightSlug

- **Requirements:**

- Should feel like a public football insight, not a chart dump.

- Should be visually important but not dominate the whole page.

- 4. Recent Matches module

- **Purpose:**

- Help users enter the match exploration flow.

- **Required content per match:**

- date

- matchday

- home team

- away team

- scoreline

- venue, if available

- link to match detail

- **Behaviour:**

- Clicking a match opens /matches/:matchId

- **Requirements:**

- Show a compact set of recent matches.

- Do not show too many rows.

- Avoid raw table styling.

- 5. Team Signals module

- **Purpose:**

- Show current team-level signals and route users into team profiles.

- **Possible signals:**

- Top teams by points/wins

- Best attack

- Tightest defence

- Goal difference leaders

- **Required content per team:**

- team name

- short metric

- record or supporting stat

- link to team profile

- **Behaviour:**

- Clicking a team opens /teams/:teamSlug

- 6. Trends teaser

- **Purpose:**

- Introduce historical comparison without making the homepage historical-first.

- **Required content:**

- short sentence about cross-season comparison

- link to /trends

- **Example:**

- See how scoring, cards, and season coverage compare across UPL seasons.

- 7. Quiet trust note

- **Purpose:**

- Build credibility without overloading the homepage.

- **Suggested content:**

- Built from official UPL match pages. Methodology and data notes are available.

- **Links:**

- /methodology

- /about

- Data requirements

- **Existing data:**

- GET /health

- GET /seasons

- GET /seasons/{season}/overview

- GET /matches?season=...

- GET /teams?season=...

- GET /insights/goal-timing?season=...

- **Future recommended data:**

- GET /insights

- GET /featured-insight

- Loading state

- **Show:**

- header skeleton

- KPI skeleton cards

- featured insight skeleton

- recent matches skeleton

- team signals skeleton

- Empty state

- **Possible empty states:**

- No season data available.

- No matches found for selected season.

- No featured insight available yet.

- Error state

- **Possible errors:**

- Could not load overview.

- Could not connect to data service.

- Featured insight unavailable.

- Out of scope

- **Do not include:**

- full methodology explanation

- full match tables

- discipline dashboard

- export report button

- fake search

- personal portfolio hero

- ## Matches Page

- Route

- /matches

- Page role

- The Matches page is the match exploration index.

- It should help users find matches and open match detail pages.

- Primary user questions

- **The page should answer:**

- Which matches are available?

- Can I filter by season, team, matchday, or result?

- Can I search for a match?

- Can I open a detailed match view?

- Target users

- fans

- journalists

- analysts

- club staff

- Required page sections

- 1. Page header

- **Required content:**

- Matches

- Short explanation

- Selected season context

- **Suggested text:**

- Browse UPL matches by season, team, result, and matchday, then open full match details.

- 2. Search and filter panel

- **Required controls:**

- search query

- season

- team

- matchday

- result

- **Result filter values:**

- All results

- Home wins

- Away wins

- Draws

- **Optional future filters:**

- venue

- date range

- goal count

- home/away

- data completeness

- **Requirements:**

- Filters should be close to the match list.

- Filters should work on mobile.

- Filters should not overwhelm the page.

- 3. Match summary strip

- **Purpose:**

- Summarise the current filtered result set.

- **Suggested metrics:**

- Matches found

- Completed matches

- Average goals

- Teams represented

- 4. Match list

- **Required content per match:**

- match date

- season

- matchday

- home team

- away team

- home score

- away score

- result

- venue

- source/data indicator if needed

- **Behaviour:**

- Click match row/card → /matches/:matchId

- **Display style:**

- compact match cards or rows

- not raw database table by default

- 5. Pagination / load more

- Required if more matches exist than displayed.

- **Options:**

- Load more

- Pagination controls

- **Initial simple version may use:**

- limit and offset

- Data requirements

- **Current:**

- GET /matches?season=&team=&match_day=&limit=&offset=

- **Recommended backend improvement:**

- GET /matches?season=&team=&match_day=&result=&q=&limit=&offset=

- Loading state

- **Show:**

- filter panel remains visible

- match list skeleton rows

- summary metric skeletons

- Empty state

- **Example:**

- No matches found for the current filters. Try changing the team, result, or matchday.

- Error state

- **Example:**

- Could not load matches for this season.

- **Actions:**

- Retry

- Clear filters

- Return to Overview

- Out of scope

- **Do not include:**

- full event timelines inline

- team profile content

- advanced discipline filters

- player search unless backend supports it

- ## Match Detail Page

- Route

- /matches/:matchId

- Page role

- The Match Detail page explains one match clearly using structured match data.

- This is one of the highest-priority new pages.

- Primary user questions

- **The page should answer:**

- Who played?

- What was the score?

- When did key events happen?

- Who scored or received cards?

- What stats are available?

- Who officiated the match?

- Can I open the original source?

- Is the data complete?

- Target users

- fans

- journalists

- analysts

- club staff

- Required page sections

- 1. Match header

- **Required content:**

- home team

- away team

- scoreline

- result

- season

- matchday

- date

- time, if available

- venue

- **Behaviour:**

- Team names should link to team profiles.

- 2. Scoreline panel

- **Purpose:**

- Make the result immediately clear.

- **Required content:**

- home team

- home score

- away score

- away team

- winner/draw state

- 3. Match metadata

- **Required content:**

- league

- season

- matchday

- date

- time

- ground name

- ground address, if available

- man of the match, if available

- source link

- 4. Event timeline

- **Required content per event:**

- minute

- event type

- team name

- player name

- goal type, if available

- substitution out/in, if available

- card type

- **Timeline should support:**

- goals

- own goals

- penalty goals

- yellow cards

- red cards

- substitutions

- **Preferred grouping:**

- First half

- Second half

- Added time, if useful

- **Requirements:**

- Must be readable on mobile.

- Must not look like a raw event table.

- Use football labels, not database names.

- 5. Match stats panel

- **Required content:**

- statistic name

- home value

- away value

- **Display style:**

- comparison rows

- home vs away visual balance

- **If no stats:**

- Show calm empty state.

- 6. Officials panel

- **Required content:**

- role

- official name

- **If no officials:**

- Show quiet empty state.

- 7. Data completeness/source note

- **Required indicators:**

- timeline available

- officials available

- stats available

- source anomaly flag, if present

- source URL

- Use quiet chips or a compact data note.

- If the match has a source anomaly, display a stronger but still clear note.

- 8. Related navigation

- **Useful links:**

- Back to Matches

- View home team profile

- View away team profile

- View selected season overview

- Data requirements

- **Existing:**

- GET /matches/{match_id}

- **Needed frontend API client method:**

- getMatchDetail(matchId)

- Loading state

- **Show:**

- scoreline skeleton

- metadata skeleton

- timeline skeleton

- stats panel skeleton

- officials panel skeleton

- Empty state

- **Possible empty sections:**

- No timeline events available for this match.

- No match stats available.

- No officials listed.

- Error state

- **Possible errors:**

- Match not found.

- Could not load match details.

- **Actions:**

- Return to Matches

- Retry

- Out of scope

- **Do not include:**

- predictive analysis

- player profile links unless player routes exist

- unsupported tactical claims

- fake logos

- ## Teams Page

- Route

- /teams

- Page role

- The Teams page is the team exploration index.

- It should guide users into team profiles and allow comparison of basic team signals.

- Primary user questions

- **The page should answer:**

- Which teams are available in this season?

- Who has the strongest record?

- Who scores most?

- Who concedes least?

- Can I open a team profile?

- Target users

- fans

- analysts

- journalists

- club staff

- Required page sections

- 1. Page header

- **Required content:**

- Teams

- Short explanation

- Selected season context

- **Suggested text:**

- Compare UPL teams by record, scoring, conceding, and season-level performance signals.

- 2. Season/team controls

- **Required controls:**

- season selector

- team search/filter

- sort selector

- **Sort options:**

- points/wins

- goals for

- goals against

- goal difference

- team name

- Only include sort options supported by available data.

- 3. Team summary strip

- **Suggested metrics:**

- Teams tracked

- Top attack

- Tightest defence

- Highest goal difference

- 4. Team cards/ranking list

- **Required content per team:**

- team name

- matches played

- wins

- draws

- losses

- goals for

- goals against

- goal difference

- points, if supported

- win rate, if supported

- link to team profile

- **Behaviour:**

- Click team → /teams/:teamSlug

- **Display style:**

- ranking cards or compact rows

- not a dense generic table by default

- Data requirements

- **Current:**

- GET /teams?season=&team=

- **Recommended backend additions:**

- points

- goal_difference

- win_rate

- goals_per_match

- conceded_per_match

- Loading state

- **Show:**

- team summary skeleton

- team card/list skeleton

- Empty state

- **Example:**

- No team summaries are available for this season yet.

- Error state

- **Example:**

- Could not load team summaries.

- **Actions:**

- Retry

- Return to Overview

- Out of scope

- **Do not include:**

- fake standings if points logic is not confirmed

- team logos unless real assets exist

- discipline rankings, unless included later

- player lists, unless backend supports them

- ## Team Profile Page

- Route

- /teams/:teamSlug

- Page role

- The Team Profile page gives a deeper, season-specific view of one team.

- This page turns Teams from a simple ranking page into a true team profile system.

- Primary user questions

- **The page should answer:**

- How is this team performing?

- What is their record?

- How many goals do they score/concede?

- What are their recent matches?

- Can I open their match details?

- Target users

- fans

- analysts

- journalists

- club staff

- Required page sections

- 1. Team header

- **Required content:**

- team name

- selected season

- matches played

- record

- goal difference

- **Visual identity:**

- Use stable initials or restrained team marker.

- Do not invent official crests.

- 2. Season selector

- **Purpose:**

- Allow viewing team profile by season.

- **Behaviour:**

- Changing season reloads team profile data.

- 3. Record summary cards

- **Required metrics:**

- matches played

- wins

- draws

- losses

- points, if supported

- win rate, if supported

- 4. Scoring/conceding summary

- **Required metrics:**

- goals for

- goals against

- goal difference

- goals per match, if supported

- conceded per match, if supported

- 5. Recent matches

- **Required content per match:**

- date

- opponent

- home/away indicator

- scoreline

- result

- venue, if available

- link to match detail

- **Behaviour:**

- Click match → /matches/:matchId

- 6. Team event summary

- **Initial possible metrics:**

- goals

- yellow cards

- red cards

- substitutions, if useful

- Only include if data is reliable and endpoint supports it.

- 7. Related routes

- **Links:**

- Back to Teams

- View all matches for this team

- View relevant insights, if available

- Data requirements

- **Current possible composition:**

- GET /teams?team=&season=

- GET /matches?team=&season=

- GET /events?team=&season=

- **Recommended backend endpoint:**

- GET /teams/profile?team=&season=

- **or:**

- GET /teams/{teamSlug}/summary?season=

- **Suggested response:**

- team_name

- season

- matches_played

- wins

- draws

- losses

- points

- goals_for

- goals_against

- goal_difference

- win_rate

- goals_per_match

- conceded_per_match

- recent_matches[]

- event_summary

- home_record

- away_record

- Loading state

- **Show:**

- team header skeleton

- record card skeletons

- recent matches skeleton

- Empty state

- **Possible empty states:**

- No team profile data found for this season.

- No recent matches available.

- No event summary available.

- Error state

- **Possible errors:**

- Team not found.

- Could not load team profile.

- **Actions:**

- Return to Teams

- Change season

- Retry

- Out of scope

- **Do not include:**

- full player squad unless lineups/player endpoints are promoted

- advanced tactical analysis

- fake logos

- discipline deep dive

- ## Insights Library Page

- Route

- /insights

- Page role

- The Insights page is the library of promoted notebook-derived analyses.

- It should show public insights that have passed through the feature promotion workflow.

- Primary user questions

- **The page should answer:**

- What insights are available?

- Which one is featured/latest?

- What football question does each insight answer?

- Can I open the interactive insight?

- Can I read the full write-up?

- Target users

- fans

- analysts

- journalists

- technical reviewers

- Required page sections

- 1. Page header

- **Required content:**

- Insights

- Short explanation

- **Suggested text:**

- Explore promoted UPL analyses developed from notebook research and turned into interactive product features.

- 2. Featured/latest insight

- **Purpose:**

- Highlight the editor-selected or latest promoted insight.

- **Required content:**

- insight title

- summary

- main finding

- season/data scope

- link to insight detail

- link to full write-up, if available

- 3. Insight cards

- **Required content per insight:**

- title

- short summary

- football question

- status

- season scope

- primary metric/finding

- promoted date or updated date, if available

- link to interactive insight

- link to full write-up, if available

- 4. Methodology link

- **Purpose:**

- Explain how insights are promoted.

- **Suggested link text:**

- How insights are promoted from notebook research

- **Destination:**

- /methodology

- Insight inclusion rule

- **Only show insights that are:**

- promoted

- published

- **Do not show:**

- ideas

- experimental notebooks

- unvalidated findings

- Data requirements

- **Recommended future endpoint:**

- GET /insights

- **Suggested response:**

- slug

- title

- summary

- status

- featured

- promoted_at

- updated_at

- season_scope

- primary_metric

- api_endpoint

- writeup_url

- **Initial fallback:**

- Frontend static insight registry

- This fallback is acceptable only while there are very few promoted insights.

- Loading state

- **Show:**

- featured insight skeleton

- insight card skeletons

- Empty state

- **Example:**

- No promoted insights are available yet. Promoted insights will appear here after they are validated and published.

- Error state

- **Example:**

- Could not load insights.

- Out of scope

- **Do not include:**

- experimental insight ideas

- raw notebook outputs

- long-form article text

- discipline dashboard until promoted

- ## Insight Detail Page

- Route

- /insights/:insightSlug

- **Example:**

- /insights/goal-timing

- Page role

- An Insight Detail page presents one promoted analysis as a hybrid interactive insight surface.

- It should not be too blog-like and not too dashboard-heavy.

- The full written analysis should live on Substack. The app page should focus on the interactive/product version of the insight.

- Primary user questions

- **The page should answer:**

- What football question is this insight asking?

- What is the main finding?

- What data supports it?

- Can I interact with the chart or filters?

- What caveats apply?

- Where can I read the full write-up?

- Target users

- fans

- journalists

- analysts

- researchers

- technical reviewers

- Required page sections

- 1. Insight header

- **Required content:**

- title

- short summary

- season scope

- promoted/updated status

- 2. Football question

- **Required content:**

- clear question the insight answers

- **Example for Goal Timing:**

- When do UPL goals arrive during regular time?

- 3. Main finding

- **Required content:**

- headline finding

- key number

- short interpretation

- **Tone should be careful:**

- The available match event data shows...

- Avoid overclaiming.

- 4. Interactive module

- Required content depends on the insight.

- **For Goal Timing:**

- season selector

- bar/distribution chart

- six 15-minute intervals

- peak interval highlighted

- regular-time goal total

- second-half share

- tooltip/details

- 5. Short interpretation

- **Purpose:**

- Explain what the user should take from the chart.

- **Length:**

- short paragraph or compact notes

- 6. Caveat/data note

- Required when relevant.

- **For Goal Timing:**

- Added-time goals are excluded from this comparison.

- The chart uses goals available in the cleaned event timeline.

- 7. Full write-up link

- Required if available.

- **Link text:**

- Read the full analysis on Substack

- 8. Related links

- **Possible links:**

- Back to Insights

- View Trends

- View Matches

- View Methodology

- Data requirements

- **For Goal Timing:**

- GET /insights/goal-timing?season=

- Future insight detail pages must define their own API needs in the feature promotion workflow.

- Loading state

- **Show:**

- insight header skeleton

- chart skeleton

- summary skeleton

- Empty state

- **Example:**

- This insight is not available for the selected season.

- Error state

- **Examples:**

- Insight not found.

- Could not load this insight.

- **Actions:**

- Return to Insights

- Change season

- Retry

- Out of scope

- **Do not include:**

- full Substack article copied into the app

- raw notebook images

- unsupported exploratory charts

- unpromoted insight ideas

- ## Trends Page

- Route

- /trends

- Page role

- The Trends page provides historical season comparison.

- It should make historical data available without making the entire app historical-first.

- Primary user questions

- **The page should answer:**

- How do seasons compare?

- Has scoring changed?

- Has card frequency changed?

- How complete is each season’s data?

- Which patterns are visible across seasons?

- Target users

- fans

- analysts

- journalists

- researchers

- Required page sections

- 1. Page header

- **Required content:**

- Trends

- Short explanation

- **Suggested text:**

- Compare UPL seasons across match coverage, scoring, cards, and other league-wide signals.

- 2. Season comparison summary

- **Required metrics:**

- number of seasons available

- latest season

- total matches across selected seasons

- total goals/cards where reliable

- 3. Goals by season

- **Required content:**

- season

- goal count

- goals per match, if supported

- scoreline vs timeline goal note, where relevant

- **Display:**

- chart or compact comparison cards

- 4. Matches and teams by season

- **Required content:**

- season

- match count

- team count

- season date range

- 5. Cards by season

- Include only if reliable enough.

- **Required content:**

- yellow cards

- red cards

- cards per match, if supported

- If data quality is uncertain, include a quiet caveat or omit.

- 6. Data coverage note

- **Purpose:**

- Help users interpret historical comparison fairly.

- **Content:**

- season coverage

- date range

- data source limitations

- 7. Related links

- **Links:**

- Insights

- Methodology

- Overview

- Data requirements

- **Current partial:**

- GET /seasons

- **Recommended endpoint:**

- GET /trends/seasons

- **or:**

- GET /insights/season-trends

- **Suggested response:**

- season

- match_count

- team_count

- goal_count

- scoreline_goal_count

- timeline_goal_count

- yellow_card_count

- red_card_count

- first_match_date

- last_match_date

- data_quality_status

- Loading state

- **Show:**

- summary skeleton

- chart skeletons

- comparison card skeletons

- Empty state

- **Example:**

- Historical trend data is not available yet.

- Error state

- **Example:**

- Could not load season trends.

- Out of scope

- **Do not include:**

- deep insight pages

- team profile details

- discipline dashboard

- complex statistical modelling

- ## About Page

- Route

- /about

- Page role

- The About page explains what UPL Lens is, why it exists, and who maintains it.

- It should build credibility without making the product feel like a portfolio homepage.

- Primary user questions

- **The page should answer:**

- What is UPL Lens?

- Why does it exist?

- Who maintains it?

- Where can I find more from the creator?

- Is this official?

- Target users

- fans

- journalists

- analysts

- technical reviewers

- potential collaborators

- Required page sections

- 1. What UPL Lens is

- **Required content:**

- UPL Lens is an independent Uganda Premier League football intelligence product.

- It turns official match data into structured views, statistical insights, and team-level exploration.

- 2. Why it exists

- **Required content:**

- The official UPL website is the source archive.

- UPL Lens exists to help users understand patterns that are difficult to see from individual match pages alone.

- 3. Maintainer note

- **Required wording:**

- Built and maintained by Humphrey.

- Keep this balanced and understated.

- 4. Product links/social links

- **Include:**

- GitHub

- Substack

- X/Twitter

- LinkedIn, if available

- 5. Relationship to official UPL data

- **Required clarification:**

- UPL Lens is independent and is not a replacement for the official UPL website.

- 6. Footer

- Standard footer.

- Data requirements

- This can be mostly static.

- **Optional:**

- GET /health

- for live data status if desired.

- Loading state

- Usually not needed unless live data is included.

- Empty state

- Not applicable.

- Error state

- Only needed if live data status is included and fails.

- Out of scope

- **Do not include:**

- long CV

- full portfolio pitch

- sales language

- technical implementation deep dive

- ## Methodology Page

- Route

- /methodology

- Page role

- The Methodology page explains the data source, pipeline, update logic, metric logic, and caveats.

- It is the main trust and data-quality page.

- Primary user questions

- **The page should answer:**

- Where does the data come from?

- How is it processed?

- How fresh is it?

- What are the limitations?

- How are insights promoted?

- How should I interpret caveats?

- Target users

- analysts

- journalists

- technical reviewers

- fans who care about credibility

- Required page sections

- 1. Data source

- **Required content:**

- UPL Lens uses official UPL match pages as the source archive.

- The official website remains the source.

- UPL Lens is an analysis layer built from that source.

- 2. Data pipeline

- **Required visual/text:**

- Official UPL website

- → scraper

- → Postgres raw/staging/analytics schemas

- → FastAPI

- → React frontend

- This can be a simple diagram or structured list.

- 3. Data freshness

- **Required content:**

- latest data check/refresh date, if available

- current season coverage

- API/database status, if available

- 4. Metric definitions

- **Should define common visible metrics such as:**

- Timeline goals

- Scoreline goals

- Cards logged

- Goal timing intervals

- Regular-time goals

- Match coverage

- Keep definitions plain-language.

- 5. Insight promotion workflow

- **Required content:**

- Notebook experiment

- → validated feature package

- → promoted insight

- → backend/API endpoint

- → frontend insight page

- This explains why only certain insights appear publicly.

- 6. Data quality states

- **Required framework:**

- Publishable

- Publishable with caveat

- Blocked from public display

- Explain each in plain language.

- 7. Known limitations

- **Possible limitations:**

- source pages may change

- some timelines may be incomplete

- some stats may be unavailable

- historical coverage may vary by season

- scraped data can contain source anomalies

- 8. Repository/method links

- **Include:**

- GitHub repository

- About page

- Data requirements

- **Current:**

- GET /health

- GET /seasons

- GET /seasons/{season}/overview

- **Future optional:**

- GET /data-quality/summary

- **Suggested response:**

- latest_staging_run_id

- latest_completed_at

- validation_issue_count

- warning_count

- error_count

- failed_match_count

- affected_seasons

- Loading state

- **If live data is shown:**

- freshness/status skeleton

- coverage skeleton

- Empty state

- **Example:**

- Live data freshness is unavailable, but the methodology remains visible.

- Error state

- **Example:**

- Could not load live data status.

- The static methodology content should still render.

- Out of scope

- **Do not include:**

- full developer documentation

- raw validation logs

- database schema dumps

- long technical setup instructions

- 5. Component-level requirements

- ## Shared components needed

- **The frontend should define or refine reusable components for:**

- AppShell

- Sidebar

- TopBar

- Footer

- SeasonSelector

- SearchBox

- DataStatusChip

- PageHeader

- KpiCard

- SectionPanel

- EmptyState

- ErrorState

- LoadingSkeleton

- MatchCard

- MatchTimeline

- MatchStatsPanel

- OfficialsPanel

- TeamCard

- TeamProfileHeader

- InsightCard

- InsightChartPanel

- TrendChartPanel

- MethodologyBlock

- ## Chart requirements

- **Charts should:**

- answer a football question

- use readable labels

- work on mobile

- avoid unnecessary decoration

- include caveats where needed

- use consistent visual styling

- Recharts is the preferred chart library.

- ## Card/list requirements

- **Cards and lists should:**

- prioritise football-readable labels

- show key numbers clearly

- avoid raw database fields

- link clearly to detail pages

- handle missing data gracefully

- 6. Data and API requirement summary

- ## Existing API endpoints to use

- GET /health

- GET /seasons

- GET /seasons/{season}/overview

- GET /matches

- GET /matches/{match_id}

- GET /teams

- GET /events

- GET /officials

- GET /insights/goal-timing

- ## Recommended new endpoints

- Search

- GET /search?q=

- Insight registry

- GET /insights

- Team profile

- GET /teams/profile?team=&season=

- **or:**

- GET /teams/{teamSlug}/summary?season=

- Trends

- GET /trends/seasons

- **or:**

- GET /insights/season-trends

- Data quality, later

- GET /data-quality/summary

- ## Backend change rule

- **A backend endpoint should only be added when:**

- a clear frontend page requires it

- existing endpoints cannot support the need cleanly

- the metric/data shape is stable enough

- the feature improves a real user workflow

- 7. Launch readiness requirements

- **Before public launch, the frontend should have:**

- UPL Lens branding applied consistently

- proper routing

- working Overview

- working Matches page

- working Match Detail page

- working Teams page

- working Team Profile page, at least V1

- working Insights page

- working Goal Timing insight detail

- working Trends page, at least V1

- working About page

- working Methodology page

- real search or no search shown

- footer/support links

- mobile responsiveness

- desktop layout quality

- loading states

- empty states

- error states

- quiet trust/data notes

- no fake export button

- no fake logos

- no unpromoted insights

- 8. Implementation priority

- Phase 1: Product shell and routing

- Rename UI to UPL Lens

- Introduce proper routing

- Build primary/secondary navigation

- Add footer

- Remove export report

- Keep current pages functioning

- Phase 2: Overview redesign

- Compact product header

- KPI row

- Featured insight

- Recent matches

- Team signals

- Trends teaser

- Quiet trust note

- Phase 3: Match workflow

- Improve Matches page

- Add Match Detail page

- Add match detail API client

- Build timeline/stats/officials panels

- Phase 4: Team profile system

- Improve Teams page

- Add Team Profile page

- Add team-profile data flow

- Add backend endpoint if needed

- Phase 5: Insights system

- Create Insights Library

- Move Goal Timing under Insights

- Create Insight Detail structure

- Add Substack write-up link support

- Plan insight registry

- Phase 6: Search

- Implement real team/match search

- Add grouped results

- Add backend search endpoint if needed

- Phase 7: Trends

- Build Trends page

- Add historical metrics

- Add backend trends endpoint if needed

- Phase 8: Methodology/data quality refinement

- Improve Methodology page

- Add data quality states

- Add live freshness/status details

- Plan future data-quality endpoint

- 9. Final page list

- **The frontend should ultimately support these pages for the next public-launch version:**

- Overview

- Matches

- Match Detail

- Teams

- Team Profile

- Insights

- Insight Detail

- Trends

- About

- Methodology

- **This structure gives UPL Lens a clear public product shape:**

- Overview = first impression

- Matches = match exploration

- Match Detail = match understanding

- Teams = team comparison

- Team Profile = team understanding

- Insights = promoted analysis library

- Insight Detail = interactive analysis surface

- Trends = historical comparison

- About = product identity

- Methodology = trust and data quality
