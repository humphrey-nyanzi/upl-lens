# Research Ideas

This is the editable backlog for football intelligence ideas.

Use this document before a formal feature package exists. It is a place for a
human user, researcher, developer, or AI agent to write down football questions,
possible metrics, rough data needs, and prioritization notes.

This file is intentionally lighter than [FEATURE_REGISTRY.md](FEATURE_REGISTRY.md).
The registry should stay small and factual. This document can hold rougher
thinking.

## How This Fits The Feature Workflow

Use this flow:

```text
research idea
  -> candidate selected for exploration
  -> feature package under notebooks/features/
  -> row in FEATURE_REGISTRY.md
  -> notebook analysis
  -> research_brief.md
  -> product_plan.md
  -> FastAPI/React promotion
```

Do not add every rough idea to the feature registry. Add a registry row when the
idea becomes an actual feature package or has clearly entered research.

## Status Labels

Use these statuses:

| Status | Meaning |
|--------|---------|
| `idea` | Interesting question, but not ready to work on yet. |
| `candidate` | Plausible next research topic. Needs prioritization. |
| `selected` | Chosen as an upcoming feature package, but not created yet. |
| `researching` | Feature package exists and notebook work has started. |
| `validated` | Research produced a useful finding, metric, or chart. |
| `promotion_ready` | Ready for product planning and implementation. |
| `parked` | Keep the idea, but do not work on it soon. |
| `rejected` | Do not pursue unless revived later. |

## How To Add An Idea

Copy this template into the right category.

```text
### Idea: Short Name

Status: idea

Football question:

Why it matters:

Possible data:

Possible metric/output:

Possible product surface:

Caveats or risks:

Next research step:

Priority notes:
```

You can leave fields blank. The goal is to capture the football question clearly
enough that a future notebook or agent can start without guessing.

## AI Agent Instructions

When asked to work on Research & Football Intelligence, an AI agent should:

1. Read `AGENTS.md`.
2. Read [START_HERE.md](START_HERE.md).
3. Read this file.
4. Read [FEATURE_PROMOTION_WORKFLOW.md](FEATURE_PROMOTION_WORKFLOW.md).
5. Read [FEATURE_DATA_ACCESS.md](FEATURE_DATA_ACCESS.md).
6. Read [FEATURE_REGISTRY.md](FEATURE_REGISTRY.md).
7. Work only on ideas marked `selected`, unless the user explicitly asks to
   explore a different status.
8. When starting a real feature, copy `notebooks/features/_feature_template/`
   into a numbered feature folder and add a row to
   [FEATURE_REGISTRY.md](FEATURE_REGISTRY.md).
9. Keep notebooks exploratory, but keep production paths API-only:

```text
Postgres staging/analytics -> FastAPI -> JSON -> React
```

## Priority Queue

Use this queue for the next likely research features.

```text
1. Card Trends And Discipline - candidate
2. Match Explorer Data Questions - candidate
3. Team Profiles And Home/Away Strength - idea
```

## Discipline And Cards

Use this section for yellow cards, red cards, card timing, team discipline,
official patterns, and match impact.

### Idea: Card Trends And Discipline

Status: candidate

Football question:

```text
Which teams are most disciplined or most card-prone, and how does discipline
change by season?
```

Why it matters:

```text
Discipline is easy for football users to understand, and card patterns are not
well summarized by individual official match pages.
```

Possible data:

```text
staging.events
staging.matches
staging.officials
```

Possible metric/output:

```text
one row per team per season
matches_played
yellow_cards
red_cards
cards_per_match
red_cards_per_match
card_minutes_by_interval
```

Possible product surface:

```text
Discipline Dashboard
Team Profile discipline section
League Overview insight card
```

Caveats or risks:

```text
Need to verify whether all card events are consistently captured across seasons.
Cards to coaches/staff may need special handling if they appear in source text.
Red-card impact requires match-state logic, not just card counts.
```

Next research step:

```text
Create a feature package only after confirming that `staging.events` has enough
card coverage for the target seasons.
```

Priority notes:

```text
Strong Feature 2 candidate because it connects directly to the planned
Discipline Dashboard.
```

### Idea: Red Card Match Impact

Status: idea

Football question:

```text
Do teams that receive red cards lose more often, concede later, or drop points
after the card?
```

Why it matters:

```text
This moves beyond counting discipline events and asks how cards affect match
outcomes.
```

Possible data:

```text
staging.events
staging.matches
```

Possible metric/output:

```text
matches with red cards
team receiving red card
red card minute
final result
goals before and after red card if match-state reconstruction is reliable
```

Possible product surface:

```text
Discipline Dashboard
Match Explorer detail notes
```

Caveats or risks:

```text
Requires careful match-state reconstruction. It may be too complex for the
first discipline slice.
```

Next research step:

```text
Park until basic card trends are validated.
```

Priority notes:

```text
Potential follow-up after Card Trends And Discipline.
```

## Match Drama And Match State

Use this section for comebacks, late goals, first-goal importance, winners,
equalizers, and dramatic timelines.

### Idea: Dramatic Match Timelines

Status: idea

Football question:

```text
Which matches had the most dramatic timelines?
```

Why it matters:

```text
This could make Match Explorer more interesting than a list of fixtures.
```

Possible data:

```text
staging.matches
staging.events
```

Possible metric/output:

```text
late goals
lead changes
equalizers
winning goals after minute 75
red cards plus goals in the same match
```

Possible product surface:

```text
Match Explorer
League Overview spotlight
```

Caveats or risks:

```text
Needs reliable goal event ordering and match-state reconstruction.
```

Next research step:

```text
Define a simple drama score in a notebook and test whether it produces sensible
matches.
```

Priority notes:

```text
Good product idea, but probably after Match Explorer exists.
```

### Idea: First Goal Importance

Status: idea

Football question:

```text
How often does the team that scores first win in the UPL?
```

Why it matters:

```text
This is a simple, understandable football question that can lead to stronger
team and match-state analysis.
```

Possible data:

```text
staging.events
staging.matches
```

Possible metric/output:

```text
first scoring team
final result
first-goal win rate
first-goal draw/loss rate
season trend
```

Possible product surface:

```text
League Overview
Team Profile
Match Explorer
```

Caveats or risks:

```text
Needs own goals and neutral/unknown teams handled carefully.
```

Next research step:

```text
Prototype a direct SQL query over goals and match results.
```

Priority notes:

```text
Good early candidate if discipline data is messier than expected.
```

## Teams

Use this section for team profiles, home/away strength, scoring/conceding
patterns, form, and style summaries.

### Idea: Team Home And Away Strength

Status: idea

Football question:

```text
Which teams are strongest at home, and which are vulnerable away?
```

Why it matters:

```text
Home/away patterns are useful for fans and analysts and fit naturally into team
profiles.
```

Possible data:

```text
staging.matches
staging.teams or team summary query
```

Possible metric/output:

```text
home points per match
away points per match
home goal difference
away goal difference
home/away split by season
```

Possible product surface:

```text
Team Profile
League Overview comparison table
```

Caveats or risks:

```text
Need to account for neutral or unclear venues if they appear.
```

Next research step:

```text
Check whether staging match home/away fields are complete enough for all target
seasons.
```

Priority notes:

```text
Good candidate after Match Explorer or Team Profile navigation exists.
```

## Players And Lineups

Use this section for starters, appearances, substitutions, impact players, and
player continuity across seasons.

### Idea: Regular Starters And Impact Substitutes

Status: idea

Football question:

```text
Which players are regular starters, and which players are frequent substitutes
or late-impact contributors?
```

Why it matters:

```text
Player usage is a richer layer than match results alone and could make team
profiles more useful.
```

Possible data:

```text
staging.lineups
staging.events
staging.matches
```

Possible metric/output:

```text
starts
bench appearances if available
substitution in/out counts
goals after substitute entry if reliable
```

Possible product surface:

```text
Team Profile
future Player Profile
```

Caveats or risks:

```text
Lineup completeness may vary by match. Player identity may need stronger stable
IDs than names alone.
```

Next research step:

```text
Audit lineup coverage before treating this as a near-term feature.
```

Priority notes:

```text
Interesting, but likely not the next feature until player identity is stronger.
```

## Officials

Use this section for referee assignments, cards by official, and official match
patterns.

### Idea: Officials And Card Rates

Status: idea

Football question:

```text
Which officials are associated with the highest card rates?
```

Why it matters:

```text
Official patterns are rarely visible from basic match listings and could be an
interesting intelligence layer.
```

Possible data:

```text
staging.officials
staging.events
staging.matches
```

Possible metric/output:

```text
matches officiated
yellow cards per match
red cards per match
cards by home/away team
```

Possible product surface:

```text
Discipline Dashboard
future Officials page
```

Caveats or risks:

```text
Need to know which official role is the center referee if multiple officials
are listed. Small sample sizes can be misleading.
```

Next research step:

```text
Inspect official role coverage and decide whether card rates can be attributed
fairly.
```

Priority notes:

```text
Good follow-up to basic discipline analysis, not the first slice.
```

## Match Stats

Use this section for possession, shots, corners, fouls if available, and stat
relationships with results.

### Idea: Match Stats Most Associated With Winning

Status: idea

Football question:

```text
Which recorded match stats are most associated with winning?
```

Why it matters:

```text
This could turn raw stat tables into an interpretable football insight.
```

Possible data:

```text
staging.stats
staging.matches
```

Possible metric/output:

```text
stat difference by match
winner team
correlation or grouped comparison
```

Possible product surface:

```text
League Overview
Match Explorer
Team Profile
```

Caveats or risks:

```text
Stats availability and consistency must be checked first. Correlation should
not be presented as causation.
```

Next research step:

```text
Audit stat table completeness and field meanings.
```

Priority notes:

```text
Potentially valuable, but depends heavily on source data quality.
```

## Promoted Or Packaged Ideas

Move a short note here when an idea becomes a formal feature package.

```text
Feature 1 - Goal Timing: promoted. See notebooks/features/feature_01_goal_timing/
```

