# Feature Notebook Template

Copy this folder when starting a new experimental feature.

Recommended naming:

```text
feature_02_card_trends
feature_03_home_advantage
feature_04_official_cards
```

Use this folder as the research lab. The notebook can stay exploratory, but the
two markdown files keep the feature easy to promote or modify later through the
Postgres -> FastAPI -> React product path.

After copying the folder, add the new feature to
`docs/FEATURE_REGISTRY.md`. Start with status `researching`, then update it as
the feature moves through `validated`, `promotion_ready`, and `promoted`.

For data access, start from cleaned Postgres `staging.*` tables unless you have
a specific reason to debug raw source data. See
`docs/FEATURE_DATA_ACCESS.md` for the full rule. If the metric becomes stable
or reusable, use `docs/ANALYTICS_VIEW_CONVENTIONS.md` to decide whether it
should become an `analytics.*` view.

Folder shape:

```text
feature_xx_short_name/
  README.md
  analysis.ipynb
  research_brief.md
  product_plan.md
  outputs/
```

Before asking an AI agent to promote the feature, update:

- `research_brief.md` with the football question, finding, metrics, and caveats.
- `product_plan.md` with what you want the product to do and the readiness
  checklist.
- `docs/FEATURE_REGISTRY.md` with the current lifecycle status.

After promotion, keep using `product_plan.md` for change requests. The AI agent
should treat these markdown files as the source of truth, then use the notebook
for evidence and implementation detail.
