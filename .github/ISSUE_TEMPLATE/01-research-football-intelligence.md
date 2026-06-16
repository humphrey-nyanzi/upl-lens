---
name: Research / Football Intelligence
about: Notebook-first research before a metric becomes an API or product feature
title: "[Research] "
labels: "area: research-intelligence, type: research, status: needs-triage"
assignees: ""
---

## Research Question

What football question do we need to answer?

## Why This Matters

Why would this help UPL Lens explain the league better than raw match pages?

## Scope

- Included:
- Excluded:

## Data Sources

- Expected tables or endpoints:
- Known caveats:

## Notebook / Evidence Plan

Describe the notebook-first approach. Use cleaned `staging.*` tables by default.

Example research shape:

```text
Identify red-card events -> compare goals before/after red cards -> separate
team receiving red card vs opponent where data allows -> document caveats.
```

## Acceptance Criteria

- [ ] Research uses a notebook or reproducible SQL query.
- [ ] Sample size and data coverage are reported.
- [ ] Findings are summarized in plain football language.
- [ ] Caveats are documented.
- [ ] Recommendation is recorded: promote, revise, park, or reject.
- [ ] Follow-up implementation Issues are created if promotion is worthwhile.

## Related Documents

- `docs/FEATURE_PROMOTION_WORKFLOW.md`
- `docs/PRODUCT_STRATEGY.md`

## Verification / Evidence

Link notebook, SQL, screenshots, or summary evidence here.
