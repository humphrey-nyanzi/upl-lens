# Product Strategy

This document defines the product principles for the repository. NOTE: the
public frontend product has been rebranded to **UPL Lens**. This strategy
document continues to describe product priorities and should be read together
with [UPL_LENS_FRONTEND_START_HERE.md](UPL_LENS_FRONTEND_START_HERE.md) for
frontend-specific design and launch direction.

Use this document before major UI, API, research-promotion, or documentation
changes. It should help a human contributor or AI agent understand the kind of
project they are working on before deciding what to build.

## Product Definition

The public product is now called **UPL Lens**. UPL Lens is an independent
statistical observatory for the Uganda Premier League (the project previously
described public-facing work as "UPL Match Intelligence"). The consolidation
into the UPL Lens brand preserves the same data-to-product philosophy while
bringing a focused frontend redesign and new naming.

It turns official match data into trustworthy football intelligence: curated
statistical findings, reusable analytical features, and deeper exploration for
people who want to understand the league beyond fixtures, results, and tables.

The short version:

```text
Official UPL match data -> trusted database -> statistical insight -> public
football intelligence product
```

The product question remains the same:

```text
What do the UPL numbers reveal that the official website does not explain?
```

## Origin And Growth Philosophy

The project began as a portfolio and passion project for analysing Uganda
Premier League data. It should still work well as a portfolio project, but the
public-facing experience should not be about showing off code first.

The preferred growth path is organic:

- Build a credible public product.
- Share it with football fans, colleagues, and online audiences.
- Add new analyses when they are useful and validated.
- Let traffic, public credibility, job opportunities, partnerships, or
  monetization emerge later if the product earns that attention.

Do not design the product as a large commercial platform too early. Monetization,
club-facing sales, and advanced scouting workflows are possible future paths,
but they should not complicate the current product direction.

## What This App Is

This app is:

- An analytical layer on top of official UPL match data.
- A modern sports statistics product for curious UPL fans.
- A place for neutral, statistical, sports-science informed football analysis.
- A public home for notebook-backed insights that have been promoted into
  reliable product features.
- A project that quietly demonstrates data engineering, backend, frontend,
  automation, deployment, and analytical storytelling ability.
- A product that values accuracy, caveats, and data freshness as part of its
  credibility.

## What This App Is Not

This app is not:

- A replacement for the official UPL website.
- A fixtures-first or results-first fan site.
- A generic league table clone.
- A personal homepage centered on the author.
- A developer portfolio page where the stack is the main attraction.
- A notebook dump, static chart gallery, or exported analysis archive.
- A full commercial scouting platform at the current stage.
- A product that hides source-data limitations to look more polished.

The official UPL website remains the source archive. UPL Lens should explain
patterns, trends, and meaning that are hard to see from official match pages
alone.

## Source Record Vs Intelligence Layer

The product boundary is:

```text
Official UPL site = source record.
UPL Lens = analytical meaning.
```

Do not reproduce a raw official UPL page unless the app transforms that source
record into insight. The app should avoid becoming a cleaner clone of official
fixtures, results, match reports, lineups, officials, or timelines.

For every raw-data element, choose one of three treatments:

1. **Transform**
   - Show it because UPL Lens adds analytical value.
   - Examples: goal timing context, card timing, match rhythm, team trend
     impact, official card-rate context, late-drama tags, or season-relative
     comparisons.

2. **Summarize**
   - Show a compact version because it supports the analysis.
   - Examples: scoreline, key goals, decisive cards, a short match context
     strip, or a short event summary.

3. **Link Out**
   - Do not duplicate it. Link to the official source when the user wants the
     complete archive detail.
   - Examples: full raw timeline, full lineup list, plain officials list, full
     official match record, or other source details that UPL Lens has not yet
     contextualized.

Match pages should be treated as **Match Intelligence Briefs**, not official
match-page clones. A match page should answer why the match matters through
signals such as timing, momentum, cards, trend fit, anomalies, or team context.
If UPL Lens cannot add that layer yet, show only compact supporting facts and a
clear official-source link.

## Routine Intelligence Modules

Routine intelligence modules are reusable backend-supported features that can
appear on normal product pages without becoming promoted research insights.

Examples include:

- team profile labels
- match signal labels
- trends charts
- scoring and carding rates
- data coverage indicators
- form strips
- attack/defence comparisons
- player contribution categories

These modules should live on overview, match, team, player, and trends pages
when they help users interpret the league. They should be built as ordinary
page intelligence, not as featured research products.

## Featured Insights

Featured insights are promoted research products that move through the
notebook -> validation -> API -> frontend workflow.

Examples include:

- Goal Timing
- future Discipline insight, if researched and promoted
- future Home Advantage insight, if researched and promoted

Do not force routine page intelligence into `/insights`. Do not replace
featured insights with shallow dashboard widgets.

## Target Audiences

### Primary Audience

The primary audience is a UPL fan who cares about stats and wants a deeper
understanding of the league.

This user should be able to land on the app and quickly understand:

- this is an analytical product, not just a results page
- the numbers are meaningful and football-specific
- there are insights here they cannot easily get from generic sites
- the product is credible enough to revisit

### Secondary Audiences

Secondary audiences include:

- football analysts and researchers
- sports journalists and media people
- club staff or football professionals browsing for useful signals
- recruiters or technical reviewers who notice the quality of the system
- data people interested in the end-to-end workflow

These audiences matter, but the public interface should still lead with football
intelligence rather than technical self-promotion.

## Product Positioning

The best product model is:

```text
An analytical sports publication with dashboard-style drilldowns.
```

This means:

- Curated findings come first.
- Users can then dig deeper into filters, comparisons, team summaries, match
  events, and season trends.
- The interface should be understandable to a local football fan, while still
  serious enough for an analyst.

Avoid making the app only a dense analyst workspace. That can become
intimidating and reduce public usefulness.

Avoid making it only a simple dashboard. That can become a set of cards and
charts without a clear football story.

## First Ten Seconds

Within ten seconds of opening the app, a user should understand:

```text
This product helps me understand the Uganda Premier League through data and
analysis that I cannot easily get from ordinary fixture or results pages.
```

The first screen should make the analytical value obvious. It can include
ordinary league facts such as total goals or season coverage, but those should
support the bigger message rather than become the main product.

## Product Layers

The app should grow in layers.

### 1. League Intelligence Overview

Purpose: give a fast, useful view of the league through analytical summaries.

This should not be a plain fixtures page. It should show useful patterns such as
season totals, goal timing signals, recent analytical highlights, unusual team
trends, data freshness, and caveats that affect interpretation.

### 2. Featured Insights

Purpose: present validated analyses as readable football stories with charts and
supporting evidence.

Feature 1, Goal Timing, is the current flagship example. A good featured insight
should explain:

- the question being asked
- the data used
- the metric definition
- the finding
- why it matters in football or sports-science terms
- what caveats apply
- how the user can dig deeper

### 3. Explore The Numbers

Purpose: let users investigate the underlying data after the curated summary.

Likely surfaces include:

- team analytical summaries
- team comparisons
- match and event explorer
- goal timing explorer
- discipline dashboard
- player analytical summaries when the data is reliable enough
- season filters and trend views

These views should support exploration and comparison, not merely reproduce the
official website's profile pages.

### 4. Methodology And Data Quality

Purpose: build trust without making methodology the main feature.

The app should include a visible but quiet methodology/about/contact area that
explains:

- who maintains the project
- what the data source is
- how data moves through the system
- how often it is updated
- what the known limitations are
- how caveats are handled
- how to contact the maintainer

This section can also satisfy portfolio/recruiting curiosity without turning the
main product into a technical showcase.

## Content Priorities

Prioritize analysis that adds meaning beyond the official website:

- goal timing and period trends
- late goals and second-half patterns
- team scoring and conceding tendencies
- discipline and card trends
- cards and match outcomes
- home and away patterns
- player starts, substitutions, and impact indicators
- official/referee patterns
- season-over-season changes
- unusual or dramatic match timelines

Do not prioritize generic fixtures, results, and tables as the main feature.
They may exist as supporting context, but they should not define the product.
When a workflow risks copying the official website, prefer analytical
summaries, compact context, and official-source links over reproducing the whole
source page.

## Feature Philosophy

Each important analytical feature should be reusable over time.

When a new analysis is promoted, it should not be a one-off static post. It
should become a continuing feature that can update as new seasons and matches
enter the database, when the underlying data supports that.

The preferred flow remains:

```text
notebook research -> research brief -> product plan -> Postgres/FastAPI ->
React feature
```

Use notebooks for discovery. Use the app for trusted, repeatable public
presentation.

## Voice And Tone

The product voice should be:

- neutral
- statistical
- sports-science informed
- clear enough for local fans
- serious enough for analysts and researchers
- honest about uncertainty

Avoid overconfident hot takes. Avoid tactical language that pretends to know
more than the data supports. Avoid jargon-heavy research language that makes the
product inaccessible to fans.

Good tone:

```text
This trend suggests...
This period accounts for...
The available match event data shows...
This should be read with caution because...
```

Avoid tone like:

```text
This proves...
This team always...
The data is perfect...
```

## Visual Direction

The visual identity should feel like a modern global sports analytics product.

Current preference:

- modern and polished
- analytical rather than decorative
- mobile-first
- clean and credible
- not heavily themed around Ugandan flag colors at this stage
- not a generic admin template
- not a marketing landing page

Local identity can be added later if it supports the product, but the first
priority is a professional sports analytics feel.

## Data Trust And Caveats

Credibility is central. The product runs on numbers, so wrong or misleading
numbers can damage trust quickly.

Every public number should fit one of these states:

1. **Publishable**
   - The data is complete enough and the metric is reliable enough to show
     normally.

2. **Publishable With Caveat**
   - The number can be shown, but nearby text should explain the limitation.
   - Examples: missing match event data, unusual season structure, known source
     limitations, incomplete player data.

3. **Blocked From Public Display**
   - The number should not be shown because it would likely mislead users.
   - Examples: broken source scrape, structural validation failure, row-count
     mismatch, missing data that changes the meaning of a ranking.

The app should never hide meaningful uncertainty. If there were 15 clubs in a
season, missing matches, unusual source behavior, or other anomalies, that
context is part of the analysis.

## Source Data Risk

The data source is the official UPL website, and the project currently depends
on scraping that source. This is useful but not guaranteed forever.

Product and technical decisions should acknowledge this:

- The app should show data freshness.
- The pipeline should log failures and validation issues.
- Broken or incomplete updates should not silently publish misleading values.
- Methodology should explain that the product is based on official source pages.
- If source structure changes, data reliability work takes priority over new
  product features.

This risk does not weaken the project. It is part of why transparent caveats,
validation, and methodology matter.

## Portfolio Role

This remains a strong portfolio project, but the portfolio value should be
secondary in the user interface.

The app should impress by being useful first. Recruiters and technical reviewers
can discover the engineering depth through:

- the repository
- documentation
- methodology/about notes
- visible data freshness and caveat handling
- the reliability of the public product

Do not make the main navigation or homepage revolve around the tech stack.

## Technical Implications

Product strategy should shape technical choices.

### Frontend

- Build analytical product surfaces, not decorative landing pages.
- Lead with curated insight and useful summaries.
- Keep drilldowns close to the story they support.
- Make mobile layouts first-class.
- Show loading, empty, error, and caveat states clearly.
- Use football language instead of raw database language.

### API

- Add endpoints when a real product surface needs them.
- Keep route functions thin.
- Put reusable query logic under `src/api/`.
- Do not make React duplicate durable SQL or backend logic.
- Prefer stable response shapes that match visible user workflows.

### Database And Analytics

- Keep raw, staging, and analytics concerns separate.
- Use `staging.*` for cleaned app-facing data.
- Use `analytics.*` views when a metric becomes stable, reusable, or complex.
- Use direct API queries for small first slices when that is simpler and clear.
- Do not serve production features from notebooks, CSVs, or exported images.

### Research

- Keep notebooks as the research lab.
- Promote only useful, validated findings.
- Record metric definitions and caveats in feature docs.
- Treat caveats as product content, not private notes.

### Operations

- Protect public credibility through validation, logs, and escalation.
- Prefer hands-off scheduled updates, but make failures visible.
- Do not let automation publish structurally broken or misleading data.

## Minimum Serious Product

A minimum serious public version should include:

1. A polished mobile-friendly League Intelligence Overview.
2. Goal Timing as the first proper featured insight.
3. Team analytical summaries, not just standings.
4. Basic match or event exploration for evidence and drilldown.
5. Clear data freshness and caveat display.
6. A simple Methodology/About/Contact area.

This is not the final product. It is the minimum shape that communicates the
right identity.

## Deferred Until Later

These ideas may become useful later, but should not drive the immediate
redesign:

- monetization
- paid club/scouting tools
- heavy player profile pages
- social share-card generation
- full fixture/result duplication
- strong local color branding
- advanced commercial dashboards
- login/accounts or private workspaces

## Decision Rules For Future Work

When deciding whether to build something, ask:

1. Does this reveal something meaningful about the UPL?
2. Is this different from what the official website already provides?
3. Can the number or claim be traced to trusted data, a query, or a notebook?
4. Does the UI make caveats visible when they matter?
5. Will the feature keep working as new seasons are added?
6. Is this useful to a stats-interested fan before it is useful to a recruiter?
7. Does the technical work support the product promise, or only add complexity?
8. Are we transforming the official source record, summarizing it for context,
   or linking out instead of duplicating it?

If the answer to the first three questions is not clear, do more product or
research thinking before implementation.

## Agent Checklist

Before coding product-facing work, an AI agent should check:

- [START_HERE.md](START_HERE.md)
- this product strategy document
- [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md)
- the relevant work-area docs
- the current files for the specific feature or surface being changed

For frontend work, also check:

- [FRONTEND_UX_REQUESTS.md](FRONTEND_UX_REQUESTS.md)
- [FRONTEND_DESIGN_SYSTEM.md](FRONTEND_DESIGN_SYSTEM.md)

For research promotion work, also check:

- [FEATURE_PROMOTION_WORKFLOW.md](FEATURE_PROMOTION_WORKFLOW.md)
- the relevant feature folder under `notebooks/features/`

Do not implement a product feature only because it is technically possible.
Implement it because it advances the product promise:

```text
trusted UPL data, turned into meaningful football intelligence
```
