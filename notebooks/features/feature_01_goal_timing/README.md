# Feature 01 - Goal Timing

This is the original UPL goal timing pilot and the first notebook insight
promoted into the product.

## Folder Contents

```text
feature_01_goal_timing/
  analysis.ipynb
  analysis_v2.ipynb
  research_brief.md
  product_plan.md
  outputs/
```

`analysis.ipynb` contains the original interval-distribution analysis.
`analysis_v2.ipynb` explores later goal-state ideas such as decisive impact and
opponent vulnerability windows. Those later ideas are research notes, not fully
promoted features yet.
`research_brief.md` explains the football logic and evidence.
`product_plan.md` records the promoted implementation and future change requests.

## Product Status

Lifecycle status:

```text
promoted
```

Promoted slice:

```text
regular-time goal distribution by 15-minute interval
```

Current product path:

```text
staging.events
  -> src/api/queries.py:get_goal_timing_insight
  -> GET /insights/goal-timing?season=...
  -> React Goal Timing Explorer panel
```

Registry:

```text
docs/FEATURE_REGISTRY.md
```

## Important Caveat

The promoted interval chart excludes added-time goals, matching the original
notebook analysis.
