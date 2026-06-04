
# UPL Lens — High-Fidelity Frontend Design Brief

1. Purpose of this brief

This brief defines the final high-fidelity design direction for UPL Lens before implementation.

It supersedes earlier wireframes or page requirements where there are contradictions. The latest clarified decisions in this brief take precedence.

**This document should guide the frontend implementation agent on:**

- visual identity

- theme

- typography

- layout

- navigation

- logo treatment

- homepage design

- page-level design direction

- component styling

- team badge treatment

- mobile behaviour

- footer/sidebar behaviour

- content hierarchy

- implementation priorities

- The goal is to make UPL Lens feel like a polished, public-facing football intelligence product, not a generic dashboard, notebook export, or personal portfolio project.

- 2. Final design direction

- ## Chosen concept

- **The selected visual direction is:**

- Option 1 — Editorial Light

- This direction should be used as the aspiration for implementation.

- **The final UI should feel:**

- public

- clean

- editorial

- trustworthy

- football-native

- data-informed

- professional

- warm

- easy to scan

- **It should not feel:**

- generic AI dashboard

- admin panel

- betting product

- official UPL product

- developer portfolio homepage

- heavy dark analytics control room

- overdesigned SaaS template

- ## Product personality

- **UPL Lens should feel like:**

- a public football intelligence front page

- - compact dashboard modules

- - interactive sports data publication

- The homepage should communicate value immediately, then allow users to explore deeper through Matches, Teams, Insights, and Trends.

- ## Source record vs intelligence layer

- **Durable product boundary:**

```text
Official UPL site = source record.
UPL Lens = analytical meaning.
```

- UPL Lens must not become a prettier clone of the official UPL website.

- Official fixtures, results, match reports, raw event timelines, lineups,
  officials lists, and source metadata should appear only when they are
  transformed into insight or compactly support an analytical view.

- Use this treatment ladder:

- **Transform:** timing patterns, match rhythm, card pressure, late-drama
  signals, team trend context, official tendencies, season-relative comparison,
  or anomaly flags.

- **Summarize:** scoreline, key events, short match context, compact data note.

- **Link out:** full raw timeline, full lineup, plain officials list, and full
  official match record when UPL Lens does not add analytical meaning yet.

- Match Detail should be a **Match Intelligence Brief**, not an official
  match-page clone. It should explain why a match matters and link to the
  official source for full archive detail.

- 3. Product name and logo treatment

- ## Product name

- **The product name remains:**

- UPL Lens

- Do not rename it to UPLens.

- Although UPLens is compact, it risks looking odd, unclear, and less professional. The better solution is to design a compact brand lockup where UPL and Lens feel like one unit without merging the words awkwardly.

- ## Logo lockup concept

- **Use a custom text-based lockup:**

- UPL

- Lens

- The two words should sit inside the same compact square/rectangular brand area.

- Recommended structure

```text
┌──────────┐

│ UPL │

│ Lens │

└──────────┘

```
**or slightly more refined:**

```text
┌────────────┐

│ UPL │

│ Lens │

└────────────┘

```
## Logo hierarchy

UPL should be larger and stronger.

Lens should sit below it, smaller, calmer, and preferably in green.

**Suggested hierarchy:**

- UPL = bold, large, dark navy/charcoal

- Lens = smaller, medium weight, green

- ## Logo component requirement

- The brand lockup must be implemented as a reusable component.

- **Suggested component name:**

- BrandMark

- **or:**

- UPLLensLogo

- **It should be used consistently in:**

- desktop sidebar

- mobile top bar

- footer

- About page

- loading/empty states where needed

- Do not manually recreate the logo text in multiple places.

- ## Logo style rules

- **The logo should be:**

- text-based

- minimal

- independent

- not official-looking

- not badge-heavy

- not using UPL official marks

- not using Uganda flag styling

- **Avoid:**

- official league logo resemblance

- football crest shape

- national flag colours as a main identity

- overly decorative football icons

- 4. Visual identity

- ## Theme

- **Default theme:**

- Editorial Light

- **Future optional theme:**

- Dark Intelligence

- For V1, implement light theme first. Design tokens should allow future dark mode, but dark mode does not need to be fully implemented now.

- ## Colour palette

- Use a warm, editorial light palette.

- Core light palette

- App background: #F6F8F3

- Surface/card: #FFFFFF

- Soft surface: #EEF3EA

- Primary text: #142019

- Secondary text: #526158

- Muted text: #7C887E

- Primary green: #1F7A3A

- Deep green: #0B5D2A

- Soft green: #DDEEDC

- Muted gold: #D4A017

- Soft gold: #FFF3D6

- Border: #E3E8DE

- Strong border: #B9C8B2

- Error/risk: #C2410C

- Colour usage rules

- **Use green for:**

- active navigation

- primary actions

- positive/live status

- selected states

- football data emphasis

- **Use muted gold for:**

- featured insight label

- peak chart value

- special highlight

- editorial emphasis

- **Use red/orange only for:**

- errors

- risk

- red cards

- negative states

- Do not overuse gold. It should feel like a highlight, not the brand’s main colour.

- ## Avoid official identity confusion

- **The visual identity must avoid looking like:**

- an official UPL product

- a Uganda national identity product

- a federation product

- a club product

- **Do not heavily use:**

- Uganda flag colour combinations

- UPL official visual identity

- club crests/logos

- official league marks

- UPL Lens should feel independent, analytical, and public-facing.

- 5. Typography

- ## Font pairing

- **Use:**

- Headings: Manrope

- Body/UI: Inter

- Numbers: Inter

- ## Heading style

- **Headings should be:**

- clear

- confident

- not oversized

- not decorative

- editorial but modern

- **Suggested heading usage:**

- Page titles: Manrope SemiBold/Bold

- Section headings: Manrope SemiBold

- Card titles: Manrope Medium/SemiBold

- Body text: Inter Regular

- Labels: Inter Medium, small uppercase where appropriate

- Numbers: Inter SemiBold/Bold

- ## Number hierarchy

- Major numbers should be easy to scan.

- **KPI cards should follow:**

- small label

- large number

- short context line

- **Example:**

- Matches covered

- 132

- - 12 this week

- **Avoid raw database-style labels such as:**

- timeline_goal_count

- event_breakdown

- team_row_key

- Use football-readable labels.

- 6. Layout system

- ## Desktop layout

- **Desktop should use:**

- left sidebar

- top control bar

- main content workspace

- subtle footer strip

- **High-level structure:**

```text
┌───────────────┬──────────────────────────────────────────────┐

│ Sidebar │ Top controls │

│ ├──────────────────────────────────────────────┤

│ │ Page content │

│ │ │

│ ├──────────────────────────────────────────────┤

│ │ Footer strip │

└───────────────┴──────────────────────────────────────────────┘

```
The desktop sidebar is approved.

## Sidebar design

The sidebar should feel light, restrained, and product-like.

It should not feel like a heavy admin dashboard.

Sidebar content

**Primary sidebar structure:**

- Brand lockup

- **Primary navigation:**

- - Overview

- - Matches

- - Teams

- - Insights

- - Trends

- **Support:**

- - About

- **Bottom social row:**

- X | GitHub | Substack | LinkedIn

- ## Sidebar clarification: About and Methodology

- Earlier documents separated About and Methodology. This brief updates that decision.

- **Final decision:**

- Only show About as a support navigation link in the sidebar.

- **The About page should contain:**

- About UPL Lens

- Methodology

- Data source

- Data quality

- Insight promotion workflow

- Maintainer note

- Social links

- **Methodology can exist as a section inside About, either as:**

- /about#methodology

- or as an internal tab/section within the About page.

- A separate /methodology route may still exist if technically convenient, but it should not appear as a separate sidebar item in V1. If retained, it should be accessible from inside About or via footer/support links, not primary sidebar navigation.

- ## Sidebar bottom area

- The bottom of the sidebar must not feel cluttered.

- Do not include multiple stacked support links, large data cards, or profile-like blocks at the bottom.

- **Final sidebar bottom design:**

- About

- X GitHub Substack LinkedIn

- The four social links should sit in one horizontal row at the extreme bottom.

- No large maintainer card in the sidebar.

- No “Humphrey profile card” in the sidebar.

- No separate Methodology sidebar item.

- ## Top bar

- **The desktop top bar should include:**

- season selector

- search field

- data status chip

- optional theme icon placeholder, if token-ready

- **Suggested order:**

- [Season 2024/25 ▼] [Search teams, matches, insights...] [Data up to date]

- **Do not include:**

- Export report

- fake notifications

- profile avatar

- unnecessary settings icons

- ## Mobile layout

- **Mobile should use:**

- top brand bar

- bottom navigation

- More sheet/drawer

- single-column content

- footer after content

- Mobile top bar

- **Mobile top bar should show:**

- Brand lockup

- Search icon

- More/menu icon, if needed

- Mobile bottom navigation

- **Use bottom navigation for primary product sections:**

- Overview

- Matches

- Teams

- Insights

- More

- **More should open a sheet containing:**

- Trends

- About

- X

- GitHub

- Substack

- LinkedIn

- Rationale: Trends is important, but five bottom nav items plus More may become tight. The most repeated user journeys are likely Overview, Matches, Teams, and Insights.

- **Alternative acceptable mobile bottom nav if space works well:**

- Overview

- Matches

- Teams

- Insights

- Trends

- **Then put About/socials in a menu. But the preferred pattern is:**

- Overview | Matches | Teams | Insights | More

- ## Footer

- A subtle footer should appear at the bottom of main content.

- **Footer content:**

- UPL Lens

- Uganda Premier League match intelligence and statistical insights.

- Built and maintained by Humphrey.

- © [year] UPL Lens.

- X | GitHub | Substack | LinkedIn

- Footer should be small, calm, and professional.

- It should not dominate the page.

- 7. Homepage design

- ## Homepage model

- **The homepage should be:**

- publication front page with dashboard modules

- **It should not be:**

- a long generic dashboard

- a marketing landing page

- a full report page

- a personal portfolio intro

- ## First viewport contract

- The first visible screen must communicate the product clearly.

- **On desktop, the first viewport should show:**

- brand/product promise

- selected season/data status

- KPI row

- featured insight preview

- recent matches

- team signals or trends teaser

- The user should understand UPL Lens without needing to scroll.

- ## Homepage scroll length

- Avoid too much scrolling.

- The homepage should be compact. It can have below-the-fold content, but the first screen should carry the value.

- **Recommended homepage structure:**

- 1. Compact editorial product header

- 2. KPI row

- 3. Featured Insight + Recent Matches + Team Signals

- 4. Trends teaser / explore deeper strip

- 5. Quiet trust/about link

- 6. Footer

- ## Homepage header

- The header should be compact and high-impact.

- **Suggested headline direction:**

- Understand the Uganda Premier League.

- **Use green emphasis only on key phrase if tasteful:**

- Understand the Uganda Premier League.

- **Subtext:**

- UPL Lens helps fans, analysts, and football professionals understand the Uganda Premier League through trusted match data, statistical insights, and team-level exploration.

- Do not use salesy copy.

- **Avoid:**

- Unlock the power of football data

- Revolutionising Ugandan football analytics

- The ultimate UPL dashboard

- ## Homepage imagery

- Option 1 used a faint football image in the header. This can be used if it remains subtle.

- **Rules:**

- must be abstract/subtle

- must not use official UPL imagery

- must not use club imagery

- must not dominate the layout

- must not reduce text readability

- If implementation complexity is high, omit the image and rely on strong typography and data modules.

- ## KPI row

- Use 4–5 compact KPI cards.

- **Recommended KPIs:**

- Matches covered

- Goals scored

- Home win %

- Average goals/match

- Clean sheets or Cards logged

- If clean sheets are not available from current backend, use Cards logged or another supported metric.

- **Each KPI card:**

- icon

- label

- large value

- short context

- ## Featured insight

- The featured insight should be prominent but not full-page dominant.

- **Current featured insight:**

- Goal Timing

- **Display as:**

- Featured Insight

- Goal Timing: The Decisive Minutes

- Short summary

- Key value

- Compact chart

- CTA: Explore Goal Timing

- Optional CTA: Read full write-up

- **The featured insight should route to:**

- /insights/goal-timing

- Do not create /goal-timing as a top-level page.

- ## Recent matches module

- Display compact rows.

- **Each row:**

- date

- home team

- score

- away team

- team badges/initials

- Rows should route to match detail pages.

- ## Team signals module

- Display top/team signal rows.

- **Use:**

- rank

- team badge/initials

- team name

- form dots or compact signal

- points/metric

- Avoid making this look like a full league table unless the data supports it.

- ## Trends teaser

- Keep this compact.

- **Purpose:**

- encourage historical exploration without making homepage too long

- **Link to:**

- /trends

- ## Quiet trust note

- **Use a small line near the bottom:**

- Built from official UPL match pages. See About for methodology and data notes.

- **Link to:**

- /about

- 8. Page design requirements

- ## Overview

- **Route:**

- /

- **Purpose:**

- public product entry point

- **Design style:**

- editorial front page

- compact dashboard modules

- high first-screen clarity

- **Must include:**

- product promise

- season/data status

- KPI row

- featured insight

- recent matches

- team signals

- trends teaser

- quiet About/data note

- **Must avoid:**

- export button

- long methodology blocks

- personal profile blocks

- fake search

- too much scrolling

- ## Matches

- **Route:**

- /matches

- **Purpose:**

- browse and find matches

- **Design style:**

- clean match explorer

- filterable card/list view

- **Must include:**

- page header

- season/team/matchday/result filters

- search

- match summary strip

- match list

- pagination/load more

- **Match rows/cards should include:**

- date

- matchday

- team names

- initials badges

- scoreline

- venue if available

- open match action

- Team badge colours should be close to team native colours where known.

- **Example:**

- KCCA FC yellow/gold badge

- Express FC red badge

- Vipers SC green/dark green badge

- SC Villa blue badge

- URA FC yellow/blue-inspired badge

- BUL FC green/yellow-inspired badge

- Kitara FC red/yellow-inspired badge, if known

- If exact colours are uncertain, use restrained approximations and keep names readable.

- ## Match Intelligence Brief

- **Route:**

- /matches/:matchId

- **Purpose:**

- explain why one match matters

- **Design style:**

- structured football intelligence brief

- selected match signals with compact source context

- **Must include:**

- back to Matches

- scoreline header

- date/venue/matchday

- home and away team links

- match intelligence summary

- match stats

- officials context, only where useful

- source/data completeness note

- related actions

- Supporting events should be visual but selective.

- Avoid raw database table presentation and full official-source replication.

- ## Teams

- **Route:**

- /teams

- **Purpose:**

- browse teams and open team profiles

- **Design style:**

- team index with analytical summaries

- **Must include:**

- page header

- season selector

- team search/filter

- sort selector

- summary cards

- team ranking/cards

- links to team profiles

- **Team list should use:**

- team name

- optional initials badge

- record

- goals for

- goals against

- goal difference

- points/wins if available

- Do not use downloaded team logos in V1.

- ## Team Profile

- **Route:**

- /teams/:teamSlug

- **Purpose:**

- show one team’s season profile

- **Design style:**

- clean team report card

- **Must include:**

- team header

- season selector

- record summary

- scoring/conceding summary

- recent matches

- event summary if supported

- related links

- **Team identity:**

- team name first

- restrained initials badge where useful

- badge colour close to native team colour

- no official crest

- ## Insights

- **Route:**

- /insights

- **Purpose:**

- library of promoted notebook-derived analyses

- **Design style:**

- interactive insight library

- not blog archive

- not raw dashboard gallery

- **Must include:**

- page header

- featured/latest insight

- insight cards

- promotion methodology link to About

- Only show promoted/published insights.

- Do not show experimental notebook ideas.

- ## Insight Detail

- **Route:**

- /insights/:insightSlug

- **Example:**

- /insights/goal-timing

- **Purpose:**

- interactive product version of one promoted analysis

- **Design style:**

- hybrid analysis surface

- concise editorial summary

- interactive chart/module

- **Must include:**

- insight title

- football question

- main finding

- interactive chart/module

- short interpretation

- data note

- Substack link if available

- related links

- Do not copy the full Substack article into the app.

- Do not make the page too dashboard-heavy.

- ## Trends

- **Route:**

- /trends

- **Purpose:**

- historical season comparison

- **Design style:**

- compact trend explorer

- **Must include:**

- page header

- season comparison summary

- goals by season

- matches/teams by season

- cards by season if reliable

- coverage note

- link to About/methodology section

- Avoid making this a second homepage.

- ## About

- **Route:**

- /about

- **Purpose:**

- product identity + methodology + trust layer

- This brief changes earlier navigation guidance: About and Methodology should be consolidated visually.

- **About should include sections for:**

- What UPL Lens is

- Why it exists

- Independence note

- Built and maintained by Humphrey

- Data source

- Methodology

- Data quality states

- Insight promotion workflow

- Known limitations

- Social links

- GitHub/Substack/X/LinkedIn

- **Suggested page structure:**

- About UPL Lens

- What it is

- Why it exists

- Built and maintained by Humphrey

- Data source and methodology

- Data quality states

- Insight promotion workflow

- Known limitations

- Links

- **The page should feel:**

- clear

- credible

- understated

- not portfolio-heavy

- not salesy

- Do not include a long CV or aggressive personal pitch.

- 9. Team badges and team identity

- ## No official logos in V1

- Do not download club logos for V1.

- **Reasons:**

- copyright/trademark uncertainty

- asset quality inconsistency

- risk of appearing official

- maintenance burden

- possible privacy/policy concerns

- ## Badge style

- Use simple initials badges where helpful.

- **Examples:**

- VIP Vipers SC

- KCC KCCA FC

- EXP Express FC

- SCV SC Villa

- URA URA FC

- BUL BUL FC

- KIT Kitara FC

- ## Badge colour rules

- Badge colours should be very close to, or clearly inspired by, the team’s native colours where known.

- **Examples:**

- KCCA FC yellow/gold base

- Express FC red base

- Vipers SC green/dark green base

- SC Villa blue base

- URA FC yellow/blue-inspired

- BUL FC green/yellow-inspired

- Kitara FC red/yellow-inspired if known

- NEC FC use known/available colour if known, otherwise neutral

- Maroons FC maroon/dark red if known

- **If a team’s colours are uncertain:**

- use a neutral restrained badge

- do not invent a fake official identity

- prioritise readability

- ## Badge accessibility

- Badges must not rely on colour alone.

- **Always show:**

- initials

- team name nearby

- sufficient contrast

- 10. Icons and visual markers

- ## Icon style

- Use simple outline icons.

- **Style:**

- thin to medium stroke

- rounded line style

- minimal

- not playful

- not overly sporty

- **Use icons for:**

- navigation

- KPI cards

- status chips

- small section markers

- Avoid icon clutter.

- ## Football visual language

- **Use football-native cues lightly:**

- match rows

- team signals

- form dots

- scoreline structure

- goal timing chart

- season/trend context

- **Avoid:**

- fake crests

- club logos

- betting odds styling

- excessive football pitch graphics

- 11. Chart design

- ## Chart style

- **Charts should be:**

- clear

- compact

- labelled

- mobile-readable

- not decorative

- Use restrained green scales with muted gold only for peak/featured values.

- ## Goal Timing chart

- Goal Timing should use a bar/distribution chart, not a fake heatmap.

- **Use intervals:**

- 0–15

- 16–30

- 31–45

- 46–60

- 61–75

- 76–90

- 90+

- **If the backend only supports regular-time intervals, use:**

- 0–15

- 16–30

- 31–45

- 46–60

- 61–75

- 76–90

- Do not duplicate time across two axes.

- Highlight the peak interval using green or muted gold.

- ## Trends charts

- **Trends charts should be simple:**

- line charts

- bar charts

- small multiples if needed

- Avoid advanced statistical visuals unless clearly explained.

- 12. Buttons and interaction design

- ## Primary buttons

- Primary buttons should use green.

- **Example:**

- Explore Insight

- View Matches

- Open Profile

- ## Secondary buttons

- Secondary buttons should be white/transparent with border.

- **Example:**

- View all

- Read write-up

- Back to Teams

- ## Link style

- Inline links should be simple, underlined or green text with arrow.

- Avoid loud CTAs.

- ## Removed feature

- **Remove:**

- Export report

- It should not appear in V1.

- Future export/share can be planned later.

- 13. Search design

- ## Search visibility

- Search should appear only if functional.

- Top search placeholder should not remain fake.

- ## Search scope

- **V1 search should support:**

- teams

- matches

- insights if feasible

- If full search cannot be implemented immediately, use page-level search/filter controls instead and omit global search until ready.

- ## Search UI

- **Desktop:**

- search field in top bar

- dropdown grouped results

- **Mobile:**

- search icon in top bar

- full-screen or sheet search panel

- **Search result groups:**

- Teams

- Matches

- Insights

- 14. Responsive design

- ## Desktop

- Desktop should use the available width well.

- No overly narrow article column for analytical pages.

- Overview should fit key content in first viewport.

- ## Medium screens/laptops

- The layout must work well on moderate laptop widths.

- **Requirements:**

- sidebar should not consume too much width

- content grids should collapse gracefully

- cards should not become cramped

- top bar should not overflow

- ## Mobile

- **Mobile should prioritise:**

- brand

- season/status

- key numbers

- featured insight

- primary navigation

- Use bottom nav.

- Avoid horizontal scroll except for legitimate tables, and even then use sparingly.

- 15. Loading, empty, and error states

- ## Loading states

- Use skeletons that match content shape.

- **Examples:**

- KPI card skeletons

- match row skeletons

- team card skeletons

- chart skeletons

- timeline skeletons

- Avoid generic spinner-only states.

- ## Empty states

- Use calm, helpful messages.

- **Example:**

- No matches found for these filters. Try changing the team, result, or matchday.

- ## Error states

- Use specific messages.

- **Examples:**

- Could not load match details.

- Team profile unavailable for this season.

- The data service may be waking up.

- **Offer useful actions:**

- Retry

- Back to Matches

- Clear filters

- View About

- 16. Content tone

- ## General tone

- **Use:**

- neutral

- analytical

- clear

- football-specific

- trustworthy

- not salesy

- **Good phrases:**

- The available match data shows...

- This trend suggests...

- This period accounts for...

- Built from official UPL match pages...

- **Avoid:**

- This proves...

- Ultimate dashboard...

- Revolutionary insights...

- Guaranteed football intelligence...

- ## Homepage copy

- **Use the confirmed core promise:**

- UPL Lens helps fans, analysts, and football professionals understand the Uganda Premier League through trusted match data, statistical insights, and team-level exploration.

- ## About copy

- **Use:**

- Built and maintained by Humphrey.

- Do not use full formal name in the main UI.

- 17. Final navigation model

- ## Desktop sidebar

- **Final desktop sidebar:**

- [UPL/Lens brand lockup]

- Overview

- Matches

- Teams

- Insights

- Trends

- About

- X GitHub Substack LinkedIn

- ## Mobile navigation

- **Preferred mobile bottom nav:**

- Overview

- Matches

- Teams

- Insights

- More

- **More sheet:**

- Trends

- About

- X

- GitHub

- Substack

- LinkedIn

- **Alternative acceptable if tested and visually clean:**

- Overview

- Matches

- Teams

- Insights

- Trends

- with About/socials in top menu or footer.

- ## Routes

- **Final V1 route structure:**

- /

- /matches

- /matches/:matchId

- /teams

- /teams/:teamSlug

- /insights

- /insights/:insightSlug

- /trends

- /about

- **Optional internal/redirect route:**

- /methodology → /about#methodology

- Do not show Methodology as a separate primary/sidebar nav item in V1.

- 18. Final homepage content hierarchy

- **Desktop first viewport should aim for:**

- **Top bar:**

- Season | Search | Data status

- **Header:**

- UPL Lens promise

- **KPI row:**

- 4–5 compact metrics

- **Main grid:**

- Featured Insight

- Recent Matches

- Team Signals

- **Lower strip:**

- Trends teaser / Explore deeper

- **Mobile first viewport should aim for:**

- Brand

- Short product promise

- Season/data status

- 2x2 KPI grid

- Featured insight title + key visual/action

- 19. Implementation priority from design perspective

- Phase 1: Brand and shell

- Implement UPL Lens brand lockup component

- Apply Editorial Light tokens

- Rebuild sidebar

- Add mobile bottom nav

- Remove export/report/profile clutter

- Add footer/social link structure

- Phase 2: Overview visual rebuild

- Compact editorial header

- KPI row

- Featured insight card

- Recent matches card

- Team signals card

- Trends teaser

- Trust/About link

- Phase 3: Core exploration pages

- Matches

- Match Intelligence Brief

- Teams

- Team Profile

- Phase 4: Insight system

- Insights index

- Goal Timing under /insights/goal-timing

- Substack link support

- Promoted insight structure

- Phase 5: Trends and About

- Trends page

- About page with methodology/data quality sections

- Phase 6: Search

- Real global search

- Grouped results

- No fake placeholders

- 20. Design acceptance criteria

- **A frontend implementation is acceptable if:**

- It clearly looks like UPL Lens, not UPL Match Intelligence.

- The brand lockup uses UPL above Lens in one compact component.

- The default theme is Editorial Light.

- The homepage communicates the product in the first screen.

- The sidebar is clean and not cluttered.

- The sidebar bottom only has About plus one-line social links.

- Methodology is consolidated into About or linked from it.

- Goal Timing lives under Insights, not as a top-level page.

- There is no Export Report button.

- Team badges use initials and restrained native-colour-inspired palettes.

- No official logos or official UPL branding are used.

- The UI feels public-facing, not like an admin dashboard.

- Mobile uses bottom navigation or an equally clear app-like navigation model.

- The product is readable on both mobile and medium-sized laptop screens.

- Caveats and data quality notes are visible but quiet.

- 21. Final design summary

- UPL Lens should launch as a light, editorial football intelligence product.

- The selected design direction is Editorial Light: warm off-white background, white cards, deep text, green accents, muted gold highlights, compact dashboard modules, and publication-style hierarchy.

- The UI should use a custom reusable brand lockup with UPL stacked above Lens, not the awkward merged form UPLens.

- The desktop experience should use a clean sidebar, but the sidebar must remain minimal: primary navigation, one About support link, and a single-line social row at the bottom.

- The mobile experience should use app-like bottom navigation.

- The homepage must be compact and high-impact: product promise, season/data status, KPIs, featured insight, recent matches, and team signals should be visible quickly.

- The product must avoid official UPL visual identity, Uganda flag-heavy identity, downloaded team logos, and anything that could imply official affiliation.

- This brief is the design source of truth for the next implementation stage.
