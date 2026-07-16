# Research Brief: Feature XX - Short Feature Name

This file captures the football thinking behind the feature. Keep it close to
the notebook and write it in plain English.

## Status

researching

Use one of:

- `idea`
- `researching`
- `validated`
- `promotion_ready`
- `promoted`
- `needs_revision`
- `parked`
- `rejected`

These statuses are defined in `docs/FEATURE_PROMOTION_WORKFLOW.md`.

## Feature Question

What question are you trying to answer?

Example:

> Which teams receive the most yellow cards per match by season?

## Why This Matters

Explain why this is more useful than reading individual match pages.

## Data Used In Research

Describe the research data source.

- Tables or files used:
- Seasons included:
- Filters used:
- Known missing data:

Default to `staging.*` tables for feature research. If this notebook uses
`raw.*` or CSV files, explain why and describe how the result should be
reproduced from Postgres before promotion.

## Final Finding

Write the final insight in plain English after the notebook supports it.

## Metric Definitions

Define each final metric exactly enough that another person can reproduce it.

Example:

```text
cards_per_match = total_yellow_cards / matches_played
```

## Caveats

List data-quality limitations, excluded cases, or interpretation warnings.

## Evidence

Point to the notebook sections, output images, or SQL snippets that prove the
finding.

```text
analysis.ipynb - section/cell:
outputs/ - reference image:
```
