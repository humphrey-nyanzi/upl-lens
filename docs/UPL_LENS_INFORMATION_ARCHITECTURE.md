UPL Lens — Formal Information Architecture

1. Product identity

## Product name

UPL Lens

## Product descriptor

Uganda Premier League match intelligence and statistical insights.

## Core product promise

UPL Lens helps fans, analysts, and football professionals understand the Uganda Premier League through trusted match data, statistical insights, and team-level exploration.

## Product positioning

UPL Lens is a public football intelligence product built on official Uganda Premier League match data. It is not a replacement for the official UPL website. The official site remains the source archive; UPL Lens is the analysis layer on top of that data.

**UPL Lens should feel like:**

- a public football intelligence product

- - a league analysis layer

- - an interactive sports data publication

- **It should not feel like:**

- a generic dashboard

- a personal portfolio page

- a fixtures/results clone

- a betting-style stats site

- a notebook dump

- a developer portfolio homepage

- The product should lead with football value, not technical self-promotion. Its credibility should come from the usefulness, clarity, and trustworthiness of the data experience.

- 2. Product audience

- UPL Lens serves a blended audience. The product should be public and accessible, but with enough depth for serious users.

- ## Primary blended audience

- **The main audience includes:**

- Curious UPL fans
- Want to understand the league beyond scores and fixtures.
- Need clear, readable, football-native insights.
- Should not feel overwhelmed by technical language.
- Football analysts and researchers
- Want structured data views, trends, comparisons, and caveats.
- Need confidence that metrics are reproducible and sourced properly.
- Should find enough depth to take the product seriously.
- Sports journalists and media users
- Want story angles, patterns, and quick evidence.
- Need concise insight summaries and shareable findings.
- Should be able to understand key numbers quickly.
- Club staff and football professionals
- Want team-level exploration, match details, and performance signals.
- Need practical football information without excessive complexity.
- Should see value in team profiles, match details, and trends.
- Technical/recruiting reviewers
- May inspect the product as a portfolio demonstration.
- Should notice the quality of the system through the product, methodology, and repository links.
- Should not be the main audience of the homepage.
- ## Audience hierarchy

- The interface should prioritise football understanding first.

- Football value first

- Technical credibility second

- Personal branding third

- 3. Product principles

- ## Current-season first

- The default experience should focus on the latest/current available season. Historical data should be available, but it should not dominate the first experience.

- ## Insight-led, not table-led

- The app should not behave like a raw database viewer. It should surface useful football patterns first, then allow users to drill down into matches, teams, insights, and trends.

- ## Source record vs intelligence layer

- The official UPL website is the source record and archive. UPL Lens is the
  intelligence layer built from that source.

- Any surface that uses match-page details should choose one of three treatments:
  transform the detail into insight, summarize it as compact context, or link to
  the official source for full archive detail.

- Do not rebuild official match pages, raw timelines, plain fixtures, full
  lineups, or officials lists unless UPL Lens adds a clear analytical layer.

## Page Roles

The core pages should read as distinct football-intelligence surfaces:

- Overview = editorial control room
- Matches = match intelligence triage
- Match Detail = match intelligence brief
- Teams = team intelligence board
- Team Detail = team dossier
- Players = player contribution board
- Player Detail = player contribution profile
- Insights = promoted research library
- Trends = league evolution
- About = trust and methodology

Normal pages can contain routine intelligence modules such as signal labels,
profile labels, comparison bars, and data-quality notes. Those modules do not
turn a page into a promoted insight. Promoted insights remain the notebook ->
validation -> API -> frontend outputs that live under `/insights`.

- ## Drilldowns over clutter

- The Overview page should not try to show everything. It should act as a launchpad into deeper product areas.

- ## Quiet trust layer

- The app should be honest about source-data limitations without overwhelming every chart or page with disclaimers.

- **Trust should be handled through:**

- subtle freshness indicators

- clear methodology page

- quiet caveats near sensitive data

- data quality explanations where needed

- ## No fake product features

- The app should not show non-functional placeholders as if they are complete. If search appears, it must work. If an insight appears, it must be backed by the feature promotion workflow.

- ## Backend-first data logic

- The frontend should consume FastAPI JSON. It should not read CSVs, notebooks, exported images, or local files.

- Durable league-wide metrics should live in the backend/API/database layer, not be recreated as fragile frontend-only calculations.

- 4. Primary navigation model

- ## Main product navigation

- **The primary navigation should contain:**

- Overview

- Matches

- Teams

- Insights

- Trends

- These are the main football intelligence areas of the product.

- ## Secondary/support navigation

- **Secondary navigation should contain:**

- About

- Methodology

- GitHub

- Social links

- These should be visually separated from the main product navigation.

- On desktop, they should appear near the bottom of the sidebar or in a clearly secondary area.

- On mobile, they may appear in a menu, footer, or secondary navigation section after the main product links.

- ## Footer navigation

- A subtle footer should appear at the bottom of page content or mobile flows.

- **The footer should include:**

- UPL Lens

- Short descriptor

- Built and maintained by Humphrey

- Copyright notice

- About

- Methodology

- GitHub

- Social links

- The footer should support product credibility without making the app feel like a personal portfolio page.

- 5. Route structure

- ## Core routes

- / Overview

- /matches Match Explorer

- /matches/:matchId Match Intelligence Brief

- /teams Team Index

- /teams/:teamSlug Team Profile

- /insights Insights Library

- /insights/:insightSlug Insight Detail

- /trends Historical Trends

- /about About

- /methodology Methodology & Data Quality

- ## Future routes

- These routes should not be built until the underlying data and product need are ready.

- /discipline Future discipline dashboard, if later separated

- /players Future player explorer

- /players/:playerSlug Future player profile

- /officials Future officials explorer

- /search Optional full search results page

- /contact Optional contact page

- At the current stage, discipline should live in the future Insights system rather than becoming a top-level page.

- 6. Global layout architecture

- ## Desktop layout

- **Desktop should use an app-like product shell:**

- Sidebar | Main workspace

- | Top controls

- | Page content

- | Footer strip

- **The sidebar should include:**

- UPL Lens brand lockup

- Primary navigation

- Secondary/support links

- Small data status/freshness signal

- **The main workspace should include:**

- top bar

- page header

- page content

- footer strip

- ## Mobile layout

- Mobile should not be a squeezed desktop version.

- **Mobile should use:**

- compact top header

- menu or compact navigation

- season selector where needed

- single-column page content

- footer after content

- **Mobile priority order should be:**

- 1. page title/context

- 2. key numbers or core insight

- 3. primary interaction

- 4. deeper panels/lists

- 5. support links/footer

- ## App shell responsibilities

- **The global shell should manage:**

- brand identity

- primary navigation

- secondary navigation

- selected season control

- search access

- data status/freshness indicator

- responsive layout

- footer/support links

- The shell should not contain page-specific analytical logic.

- 7. Global controls and states

- ## Season selector

- A season selector should be globally available or page-level depending on context.

- **Default selected season:**

- latest/current available season

- **Pages affected by season selection:**

- Overview

- Matches

- Teams

- Insights, where the insight is season-specific

- Trends, where comparison requires multiple seasons

- ## Search

- Search should be real in the next version.

- **Search should support at minimum:**

- teams

- matches

- venues, if available

- matchdays

- **Possible search behaviour:**

- User enters “Vipers”

- **→ grouped results:**

- Teams

- Matches

- Search should not be displayed as a major product feature until it is functional.

- **Search results should route users to:**

- /teams/:teamSlug

- /matches/:matchId

- A dedicated /search page is optional. Initially, a global search dropdown/panel may be enough.

- ## Data freshness indicator

- A compact data status indicator should be visible but not dominant.

- **It should communicate:**

- data service status

- latest refresh/check date where available

- current season coverage where helpful

- **Example labels:**

- Data live

- Last updated: [date]

- Current season data available

- Avoid large warning banners unless the API/data is actually unavailable or unsafe.

- ## Loading states

- Each page should have a loading state that matches its expected layout.

- **Examples:**

- Overview → KPI skeletons + featured insight skeleton

- Matches → match list skeleton

- Match Intelligence Brief → scoreline header skeleton + intelligence summary
  skeleton

- Teams → team card skeletons

- Team Profile → profile header skeleton + recent matches skeleton

- Insights → insight card skeletons

- Trends → chart/card skeletons

- ## Empty states

- Empty states should be clear, calm, and product-facing.

- **Bad:**

- No data

- **Better:**

- No matches were found for this filter.

- Try changing the team, matchday, or season.

- ## Error states

- **Error states should distinguish between:**

- API unavailable

- season data unavailable

- match not found

- team not found

- search failed

- insight unavailable

- Cold-start/API wake-up messaging should be polite and simple.

- 8. Page architecture

- ## Overview

- Page route

- /

- Page role

- The Overview is the public landing page and main product entry point.

- **It should answer:**

- What is UPL Lens, and what can I understand here immediately?

- Primary user needs

- **Users should be able to:**

- understand the product quickly

- see current-season league intelligence

- view the featured insight

- find recent matches

- identify top team signals

- move into Matches, Teams, Insights, or Trends

- trust the data source and freshness

- Page structure

- **Recommended content order:**

- 1. Compact product header

- 2. Current season selector/status

- 3. KPI summary row

- 4. Featured Insight module

- 5. Recent Matches module

- 6. Team Signals module

- 7. Trends teaser

- 8. Quiet trust note

- 9. Footer

- Required content

- Compact product header

- **Should include:**

- UPL Lens

- Uganda Premier League match intelligence and statistical insights.

- Core product promise

- **Use the confirmed statement:**

- UPL Lens helps fans, analysts, and football professionals understand the Uganda Premier League through trusted match data, statistical insights, and team-level exploration.

- KPI summary row

- **Should show current season metrics such as:**

- Matches covered

- Teams tracked

- Timeline goals

- Cards logged

- Latest match date or season window

- Featured Insight module

- Should show the editor-selected featured insight.

- **Default rule:**

- If no manual featured insight is set, show latest promoted insight.

- For now, this is likely Goal Timing.

- **Should include:**

- insight title

- short summary

- main number/finding

- compact chart or visual

- link to full insight page

- optional link to Substack full write-up

- Recent Matches module

- Should show a compact list of recent/current-season matches.

- **Each row/card should include:**

- date

- matchday

- home team

- away team

- score

- venue, if available

- link to match detail

- Team Signals module

- Should show top/relevant team summaries.

- **Possible signals:**

- top teams by points/wins

- best attack

- tightest defence

- goal difference leaders

- Avoid calling this a league table unless it behaves as a proper table.

- Trends teaser

- Should gently introduce historical comparison.

- **Example:**

- See how scoring, cards, and season coverage compare across UPL seasons.

- **Link to:**

- /trends

- Quiet trust note

- **Should include a small note such as:**

- Built from official UPL match pages. Methodology and data notes are available.

- **Link to:**

- /methodology

- Data required

- **Existing data:**

- GET /health

- GET /seasons

- GET /seasons/{season}/overview

- GET /matches?season=...

- GET /teams?season=...

- GET /insights/...

- **Future optional:**

- GET /homepage

- GET /featured-insight

- UX notes

- The Overview should be concise. It should feel like a football intelligence front page, not a long dashboard report.

- ## Matches

- Page route

- /matches

- Page role

- The Matches page is the match exploration entry point.

- It should help users find matches and move into match detail pages.

- Primary user needs

- **Users should be able to:**

- browse matches by season

- filter by team

- filter by matchday

- filter by result

- search for a match

- open match details

- understand recent and historical matches

- Page structure

- **Recommended content order:**

- 1. Page header

- 2. Search and filters

- 3. Match summary cards/KPIs

- 4. Match list

- 5. Pagination/load more

- 6. Footer

- Required filters

- **Minimum filters:**

- season

- team

- matchday

- result

- search query

- **Optional later filters:**

- venue

- date range

- home/away

- goal count

- source completeness

- Match list item content

- **Each match card/row should include:**

- match date

- matchday

- home team

- away team

- home score

- away score

- result status

- venue

- small data completeness indicator if needed

- link to match detail

- Data required

- **Current:**

- GET /matches?season=&team=&match_day=&limit=&offset=

- **Recommended backend improvement:**

- GET /matches?season=&team=&match_day=&result=&q=&limit=&offset=

- UX notes

- The page should not display a giant raw table by default. It should use compact, scannable match cards or rows.

- ## Match Intelligence Brief

- Page route

- /matches/:matchId

- Page role

- The Match Intelligence Brief explains why one match matters using the
  scoreline, structured match data, analytical signals, and compact source
  context.

- This is the next major workflow after the Overview.

- It should not recreate the official match page. Full archive detail belongs on
  the official source page; UPL Lens should show the football meaning.

- Primary user needs

- **Users should be able to:**

- see the match scoreline

- understand the key match pattern or turning point

- see the events that support that pattern

- see officials only as source context or analytical signal

- view match stats where available

- open the original source page

- understand whether data is complete

- Page structure

- **Recommended content order:**

- 1. Match header

- 2. Scoreline panel

- 3. Compact match context

- 4. Match intelligence summary

- 5. Match stats

- 6. Officials context, if useful

- 7. Source/data quality note

- 8. Related navigation

- 9. Footer

- Match header

- **Should include:**

- home team

- away team

- scoreline

- result

- season

- matchday

- date

- venue

- Match intelligence summary

- **Should include:**

- key scoring windows

- turning points

- event clusters

- late-drama signal, if present

- first-half vs second-half balance

- selected event details that support the interpretation

- Events should be visually grouped and readable.

- Do not show a full raw event list by default. If users need the complete
  archive timeline, link to the official source page.

- **Possible analytical groups:**

- First half

- Second half

- Final 15 minutes

- Match stats

- Should display home/away comparison where available.

- Fields come from the stats array returned by the match detail endpoint.

- Officials context panel

- **Should show only when useful:**

- lead referee

- official names tied to an analytical discipline/referee signal

- official source link for the complete list

- Data quality/source note

- **Should show quiet indicators such as:**

- Event intelligence available

- Officials context available

- Stats available

- Source anomaly, if present

- Do not overdo disclaimers unless the data is incomplete or anomalous.

- Data required

- **Current backend already supports:**

- GET /matches/{match_id}

- **This returns:**

- match summary

- events

- officials

- stats

- data completeness flags

- source URL

- UX notes

- Match Intelligence Brief should feel like a clean football intelligence report
  powered by structured data, not a database dump or official-site clone.

- ## Teams

- Page route

- /teams

- Page role

- The Teams page is the entry point into team-level exploration.

- It should not be just a generic standings page. It should guide users toward team profiles and analytical comparisons.

- Primary user needs

- **Users should be able to:**

- browse teams in a season

- compare team records

- identify strong attacks/defences

- open team profiles

- understand team-level summaries

- Page structure

- **Recommended content order:**

- 1. Page header

- 2. Season selector/filter

- 3. Team summary KPIs

- 4. Team ranking/cards

- 5. Optional comparison controls

- 6. Footer

- Team card content

- **Each team card should include:**

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

- Data required

- **Current:**

- GET /teams?season=&team=

- **Recommended future addition:**

- points

- goal_difference

- win_rate

- home_record

- away_record

- These can be added to the team summary endpoint or calculated in an analytics view.

- UX notes

- Use team cards/ranking rows rather than a dense table by default. A table view can come later if useful.

- ## Team Profile

- Page route

- /teams/:teamSlug

- Page role

- The Team Profile page gives a deeper view of one club.

- This is a major product direction: Teams should become a profile system.

- Primary user needs

- **Users should be able to:**

- understand one team’s season record

- see recent matches

- inspect scoring/conceding profile

- compare basic team tendencies

- open related matches

- Page structure

- **Recommended content order:**

- 1. Team header

- 2. Season selector

- 3. Record summary

- 4. Scoring/conceding summary

- 5. Recent matches

- 6. Team event summary

- 7. Links to related insights/trends

- 8. Footer

- Team header

- **Should include:**

- team name

- season

- matches played

- record

- goal difference

- If real crest assets are unavailable, use stable initials or restrained visual markers. Do not invent official club logos.

- Record summary

- **Should include:**

- matches played

- wins

- draws

- losses

- points, if supported

- win rate

- Scoring summary

- **Should include:**

- goals for

- goals against

- goal difference

- goals per match

- conceded per match

- Recent matches

- Should include matches involving that team, with links to match detail.

- Data required

- **Possible current composition:**

- GET /teams?team=&season=

- GET /matches?team=&season=

- GET /events?team=&season=

- **Recommended backend addition:**

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

- UX notes

- Team Profile should be analytical but not overloaded. Start with reliable summaries and recent matches. Add richer features later.

- ## Insights

- Page route

- /insights

- Page role

- The Insights page is a library of promoted notebook-derived analyses.

- Goal Timing should live here as the first promoted insight, not as a top-level page.

- Primary user needs

- **Users should be able to:**

- browse promoted insights

- understand what each insight is about

- open an interactive insight page

- see which insight is featured/latest

- access full write-ups on Substack where available

- Insight promotion rule

- An insight should appear publicly only when it has passed through the feature promotion workflow.

- **Promotion path:**

- Jupyter notebook experiment

- → validated feature package

- → documented as promoted

- → backend/API promotion

- → frontend insight surface

- The frontend should not create public insights from rough notebook ideas.

- Page structure

- **Recommended content order:**

- 1. Page header

- 2. Featured/latest insight

- 3. Insight library cards

- 4. Methodology link

- 5. Footer

- Insight card content

- **Each insight card should include:**

- title

- short summary

- status: promoted

- football question

- main metric/finding

- season scope

- last updated, if available

- link to interactive insight

- link to full write-up, if available

- Current first insight

- Goal Timing

- **Possible future insights:**

- Discipline trends

- Late goals

- Home/away patterns

- Cards and outcomes

- Official/referee patterns

- Team scoring periods

- Data required

- **Recommended future endpoint:**

- GET /insights

- **Suggested response:**

- slug

- title

- summary

- status

- featured

- promoted_at

- season_scope

- primary_metric

- api_endpoint

- writeup_url

- **Current workaround:**

- Hardcode the insight registry in the frontend until the backend insight registry exists. However, for a serious product, a backend-driven insight registry is preferable.

- ## Insight Detail

- Page route

- /insights/:insightSlug

- **Example:**

- /insights/goal-timing

- Page role

- An Insight Detail page presents one promoted analysis as an interactive product surface.

- **It should be a hybrid:**

- not too blog-like

- not too dashboard-heavy

- interactive enough to explore

- summarised enough to understand quickly

- linked to full Substack write-up

- Primary user needs

- **Users should be able to:**

- understand the football question

- see the main finding

- interact with the key chart/filter

- read a concise explanation

- understand caveats

- open the full write-up externally

- Page structure

- **Recommended content order:**

- 1. Insight header

- 2. Football question

- 3. Main finding

- 4. Interactive chart/module

- 5. Short interpretation

- 6. Caveat/data note

- 7. Link to full write-up

- 8. Related insights or routes

- 9. Footer

- Required content

- Insight header

- **Should include:**

- title

- short summary

- season scope

- promoted/updated status

- Football question

- **Example:**

- When do UPL goals arrive during regular time?

- Main finding

- Should be clear and number-led, but not overclaim.

- **Good wording:**

- The available regular-time event data shows...

- **Avoid:**

- This proves...

- Interactive chart/module

- **For Goal Timing:**

- bar/distribution chart

- six 15-minute intervals

- peak interval highlighted

- season selector

- summary stats

- Full write-up link

- **Since detailed writing lives on Substack, include:**

- Read the full analysis

- This should link externally and should not dominate the page.

- Data required

- **For Goal Timing:**

- GET /insights/goal-timing?season=

- Future insight detail pages should define their own API needs as part of the promotion workflow.

- UX notes

- Each insight should feel like a polished public analysis module, not a raw dashboard or copied notebook output.

- ## Trends

- Page route

- /trends

- Page role

- The Trends page provides historical season comparison.

- It should encourage historical exploration without overwhelming the default current-season experience.

- Primary user needs

- **Users should be able to:**

- compare seasons

- see league-wide changes

- understand scoring/card trends

- see data coverage differences

- move into related insights

- Page structure

- **Recommended content order:**

- 1. Page header

- 2. Season comparison summary

- 3. Goals by season

- 4. Matches/teams by season

- 5. Cards by season, if reliable

- 6. Featured historical note

- 7. Data coverage note

- 8. Footer

- Initial trend metrics

- **Start with reliable broad metrics:**

- matches per season

- teams per season

- goals per season

- timeline goals per season

- scoreline goals per season

- yellow cards per season

- red cards per season

- season date range

- Only include card trends if card data is consistent enough.

- Data required

- **Current partial support:**

- GET /seasons

- **Recommended backend addition:**

- GET /insights/season-trends

- **or:**

- GET /trends/seasons

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

- UX notes

- Trends should not become a second homepage. It should be focused on cross-season comparison.

- ## About

- Page route

- /about

- Page role

- The About page explains what UPL Lens is, who maintains it, and why it exists.

- It should build credibility without making the product feel like a personal portfolio.

- Primary user needs

- **Users should be able to:**

- understand the purpose of UPL Lens

- know who maintains it

- find social/repository links

- understand the product’s public value

- Page structure

- **Recommended content order:**

- 1. What UPL Lens is

- 2. Why it exists

- 3. Who maintains it

- 4. What it uses

- 5. Links/socials

- 6. Footer

- Required wording direction

- **Use:**

- Built and maintained by Humphrey.

- Do not overuse the maintainer identity in the main product pages.

- Suggested content

- **About should mention:**

- UPL Lens is an independent football intelligence product.

- It uses official UPL match pages as its source archive.

- It turns match data into structured views, insights, and exploration tools.

- It is maintained by Humphrey.

- Social/repository links

- **Include:**

- GitHub

- Substack

- X/Twitter

- LinkedIn, if available

- The full list should be confirmed before implementation.

- UX notes

- The About page should be clean, professional, and understated. Avoid sales language.

- ## Methodology

- Page route

- /methodology

- Page role

- The Methodology page is the main trust and data-quality explanation.

- It should remain separate from About.

- Primary user needs

- **Users should be able to:**

- understand the data source

- understand the data pipeline

- understand update/freshness logic

- understand limitations

- understand why some caveats exist

- Page structure

- **Recommended content order:**

- 1. Data source

- 2. Data pipeline

- 3. Refresh/freshness

- 4. Metric definitions

- 5. Known limitations

- 6. Data quality states

- 7. Repository/methodology links

- 8. Footer

- Data source section

- **Should explain:**

- The source is official UPL match pages.

- The official website remains the source archive.

- UPL Lens is an analysis layer built from that source.

- Data pipeline section

- **Should summarise:**

- Official UPL website

- → scraper

- → Postgres raw/staging/analytics schemas

- → FastAPI

- → React frontend

- Data quality states

- **Use a clear framework:**

- Publishable

- Publishable with caveat

- Blocked from public display

- This keeps caveats disciplined without crowding every page.

- Data required

- **Current:**

- GET /health

- GET /seasons

- GET /seasons/{season}/overview

- **Future optional:**

- GET /data-quality/summary

- **Suggested future response:**

- latest_staging_run_id

- latest_completed_at

- validation_issue_count

- warning_count

- error_count

- failed_match_count

- affected_seasons

- UX notes

- Methodology should be understandable to non-technical users. Technical details can link to GitHub.

- 9. Insight system architecture

- ## Insight lifecycle

- **A public insight should follow this lifecycle:**

- idea

- → experimental notebook

- → validated finding

- → promoted feature

- → backend/API endpoint

- → frontend insight page

- → optional featured homepage placement

- ## Insight status labels

- **Possible internal statuses:**

- idea

- experimental

- validated

- promoted

- published

- archived

- Only promoted or published insights should appear in the public Insights library.

- ## Featured insight selection

- **Featured insight rule:**

- editor-selected featured insight

- default fallback: latest promoted insight

- The homepage should not always feature Goal Timing forever if newer and more relevant insights are promoted.

- ## Insight page requirements

- **Each public insight should have:**

- title

- slug

- short summary

- football question

- main finding

- data scope

- interactive element

- caveat/data note

- Substack/full write-up link, if available

- related routes

- ## Insight registry

- A future insight registry should be backend-driven.

- **Recommended endpoint:**

- GET /insights

- **Suggested fields:**

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

- 10. Search information architecture

- ## Search role

- Search should help users move quickly to teams and matches.

- It should not try to become a full site search before the product has enough content.

- ## Search scope for next version

- **Minimum search scope:**

- team names

- matches

- venues, if available

- matchdays

- **Future scope:**

- players

- officials

- insights

- articles/write-ups

- ## Search result grouping

- **Search results should be grouped:**

- Teams

- Matches

- Insights, later

- Players, later

- ## Search behaviour

- **Example:**

- Query: Vipers

- **Results:**

- Teams

- - Vipers SC

- Matches

- - Vipers SC 2–1 KCCA FC

- - SC Villa 0–0 Vipers SC

- ## Data requirements

- **Recommended endpoint:**

- GET /search?q=

- **Suggested response:**

- query

- teams[]

- matches[]

- insights[]

- Search should not appear as a fake placeholder.

- 11. Backend/API implications

- The frontend should not drive unnecessary backend rewrites. However, backend endpoints should be added when a core frontend workflow clearly requires them.

- ## Existing endpoints sufficient for

- Overview V1

- Match Explorer V1

- Match Intelligence Brief V1

- Teams Index V1

- Goal Timing Insight V1

- Methodology V1

- ## Recommended new endpoints

- Team Profile

- GET /teams/profile?team=&season=

- **or:**

- GET /teams/{teamSlug}/summary?season=

- Insight Registry

- GET /insights

- Search

- GET /search?q=

- Season Trends

- GET /trends/seasons

- **or:**

- GET /insights/season-trends

- Data Quality Summary, later

- GET /data-quality/summary

- ## Backend change rule

- **Before adding a backend endpoint, answer:**

- Which frontend page needs this?

- Which user task does it support?

- Can an existing endpoint support it cleanly?

- Is the metric stable enough to live in backend/API?

- Does it need an analytics table/view?

- 12. Frontend data architecture

- ## Data scopes

- **Split frontend data into clear scopes:**

- App-level data

- Page-level data

- Detail-level data

- Search data

- ## App-level data

- **App-level data includes:**

- health/status

- available seasons

- selected season

- navigation state

- global search state

- ## Page-level data

- **Page-level data includes:**

- overview data

- match list

- team list

- insights list

- trends data

- methodology freshness data

- ## Detail-level data

- **Detail-level data includes:**

- single match detail

- single team profile

- single insight detail

- ## Search data

- **Search data includes:**

- query

- grouped results

- loading/error state

- recent searches, optional later

- ## Frontend anti-patterns

- **Avoid:**

- one giant dashboard hook fetching everything

- frontend-only durable metrics

- raw database labels in UI

- deeply nested prop drilling

- fake placeholder controls

- 13. Recommended frontend folder architecture

- This is a planning structure, not an immediate coding instruction.

- frontend/src/

- app/

- routes/

- layout/

- providers/

- types.ts

- api/

- client.ts

- types.ts

- endpoints/

- health.ts

- seasons.ts

- matches.ts

- teams.ts

- insights.ts

- trends.ts

- search.ts

- pages/

- overview/

- OverviewPage.tsx

- matches/

- MatchExplorerPage.tsx

- MatchDetailPage.tsx

- teams/

- TeamIndexPage.tsx

- TeamProfilePage.tsx

- insights/

- InsightsIndexPage.tsx

- InsightDetailPage.tsx

- trends/

- TrendsPage.tsx

- about/

- AboutPage.tsx

- methodology/

- MethodologyPage.tsx

- components/

- common/

- layout/

- navigation/

- search/

- season/

- charts/

- matches/

- teams/

- insights/

- trends/

- data-quality/

- footer/

- hooks/

- useAppStatus.ts

- useSeasons.ts

- useOverviewData.ts

- useMatchList.ts

- useMatchDetail.ts

- useTeamList.ts

- useTeamProfile.ts

- useInsights.ts

- useInsightDetail.ts

- useTrends.ts

- useSearch.ts

- utils/

- format.ts

- slugs.ts

- routes.ts

- 14. Visual hierarchy and tone

- ## Visual direction

- **UPL Lens should feel:**

- modern

- football-native

- credible

- analytical

- public-facing

- mobile-first

- polished but restrained

- **Avoid:**

- heavy glassmorphism

- fake AI gradients

- betting-site styling

- generic admin dashboard styling

- overly academic presentation

- portfolio-heavy hero sections

- ## Tone of voice

- **Use tone that is:**

- neutral

- analytical

- clear

- football-specific

- honest about uncertainty

- **Good wording:**

- The available match data shows...

- This trend suggests...

- This period accounts for...

- This should be read with caution because...

- **Avoid:**

- This proves...

- This team always...

- The data is perfect...

- Guaranteed insight...

- ## Personal branding tone

- **Use:**

- Built and maintained by Humphrey.

- Avoid making the homepage about the creator. The product should stand first.

- 15. Footer architecture

- ## Desktop footer

- Desktop can use a subtle footer strip at the bottom of the main content area.

- **Footer content:**

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

- ## Sidebar support area

- **At the bottom of the desktop sidebar:**

- About

- Methodology

- GitHub

- Social links

- Data status

- This area should be visually quieter than primary navigation.

- ## Mobile footer

- On mobile, footer appears after page content.

- **Mobile footer should include:**

- UPL Lens

- short descriptor

- About

- Methodology

- GitHub/social links

- copyright

- 16. Data quality and caveat architecture

- ## Caveat levels

- **Use three public display states:**

- Publishable

- Publishable with caveat

- Blocked from public display

- ## Where caveats appear

- Overview

- - quiet trust note only

- Charts

- - small caveat only when interpretation could be affected

- Match Intelligence Brief

- - data completeness indicators

- Team Profile

- - caveats only if team data is incomplete

- Methodology

- - full explanation

- Trends

- - coverage caveat where historical comparison may be affected

- ## Data quality UI patterns

- **Use:**

- small status chips

- quiet inline notes

- methodology links

- source links

- **Avoid:**

- large warning blocks on every page

- technical validation jargon in public UI

- hiding uncertainty completely

- 17. Public launch scope

- ## Must have for public launch

- UPL Lens branding

- proper routing

- Overview page

- Matches page

- Match Intelligence Brief page

- Teams page

- Team Profile page, at least V1

- Insights page

- Goal Timing insight detail

- Trends page, at least V1

- About page

- Methodology page

- real search, at least teams and matches

- footer/support links

- loading states

- empty states

- error states

- mobile responsiveness

- desktop workspace quality

- ## Should not be included yet

- Discipline dashboard as a top-level page

- Player profiles

- Official/referee analytics

- Export report

- Monetisation language

- Fake club logos

- Authentication

- Complex scouting features

- Betting-style statistics

- ## Future planning backlog

- Discipline insight/dashboard

- Player explorer

- Officials explorer

- Share/export reports

- Advanced team comparison

- Historical insight archive

- Automated featured insight selection

- Data quality summary endpoint

- 18. Implementation sequencing

- Phase 1: Routing and product shell

- **Goal:**

- Move from pilot dashboard navigation to proper product navigation.

- **Scope:**

- real route structure

- UPL Lens branding

- primary/secondary navigation

- footer/support links

- remove export report

- keep existing data working

- Phase 2: Overview redesign

- **Goal:**

- Make the homepage public-launch quality.

- **Scope:**

- compact product promise

- current-season-first summary

- featured insight

- recent matches

- team signals

- trends teaser

- quiet trust note

- Phase 3: Match Intelligence Brief workflow

- **Goal:**

- Make matches explorable without recreating official match pages.

- **Scope:**

- /matches

- /matches/:matchId

- match intelligence API client

- scoreline header

- intelligence summary

- stats

- officials context

- source link

- data completeness

- Phase 4: Team profile system

- **Goal:**

- Turn teams into a real product area.

- **Scope:**

- /teams

- /teams/:teamSlug

- team index

- team profile

- recent team matches

- team summary stats

- backend endpoint if needed

- Phase 5: Insights system

- **Goal:**

- Turn notebook-promoted analyses into a public insight library.

- **Scope:**

- /insights

- /insights/goal-timing

- insight cards

- featured/latest insight logic

- Substack write-up link

- future insight-ready structure

- Phase 6: Search

- **Goal:**

- Make global search real and useful.

- **Scope:**

- team search

- match search

- grouped results

- route to team/match pages

- backend search endpoint if needed

- Phase 7: Trends

- **Goal:**

- Introduce historical comparison.

- **Scope:**

- /trends

- season comparison

- goals/matches/teams/cards, where reliable

- coverage note

- backend trends endpoint if needed

- Phase 8: Data quality refinement

- **Goal:**

- Strengthen trust without cluttering the product.

- **Scope:**

- methodology improvements

- data status signals

- quality states

- future data-quality endpoint

- 19. Final sitemap

- UPL Lens

```text
│

├── Overview

│ └── Featured Insight preview

│

├── Matches

│ ├── Match Explorer

│ └── Match Intelligence Brief

│

├── Teams

│ ├── Team Index

│ └── Team Profile

│

├── Insights

│ ├── Insights Library

│ └── Insight Detail

│ └── Goal Timing

│

├── Trends

│ └── Historical Season Comparison

│

├── About

│

├── Methodology

│ └── Data Quality / Source Notes

│

└── Footer / Support Links

├── GitHub

├── Substack

├── X/Twitter

├── LinkedIn, if available

└── Copyright

```
20. Final IA summary

**UPL Lens should be structured as a public football intelligence product with five core product areas:**

- Overview

- Matches

- Teams

- Insights

- Trends

- The product should lead with current-season understanding, provide drilldowns into matches and teams, promote notebook-derived analyses through an Insights system, and offer historical comparison through Trends.

- About and Methodology should remain separate support areas. They should build credibility without turning the interface into a portfolio page.
