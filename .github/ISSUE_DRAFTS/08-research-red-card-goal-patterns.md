# [Research] Goal scoring patterns after red cards

Labels: `area: research-intelligence`, `type: research`, `priority: medium`, `status: needs-triage`
Milestone: `v0.5 Feature 2 Discipline Research`

## Research Question

How do goal-scoring patterns change after a player receives a red card?

## Why This Matters

Red cards are major match-state events. If the data supports it, UPL Lens could
explain whether red cards shift scoring volume, timing, or match outcomes.

## Scope

- Identify matches with red-card events.
- Compare goals before and after red cards.
- Separate team receiving the red card vs opponent where source data allows.
- Report sample size and timeline coverage.
- Document caveats before recommending promotion.

## Acceptance Criteria

- [ ] Notebook query completed using cleaned `staging.*` data.
- [ ] Red-card match sample size and coverage are reported.
- [ ] Post-red-card goal patterns are summarized in plain football language.
- [ ] Caveats are documented.
- [ ] Recommendation is recorded: promote, revise, park, or reject.
- [ ] Follow-up API/frontend Issues are created if promotion is worthwhile.

## Related Documents

- `docs/FEATURE_PROMOTION_WORKFLOW.md`
- `docs/PRODUCT_STRATEGY.md`
