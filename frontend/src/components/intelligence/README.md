# Intelligence Components

Reusable UPL Lens modules for routine page intelligence. They are presentational:
pages map FastAPI response fields into these props.

- `SignalChip` / `SignalChipGroup`: API signal and profile labels for matches, teams, and players.
- `DataQualityNote`: compact or full caveats near charts, profiles, and detail views.
- `MetricDelta`: neutral metric value plus optional context or delta.
- `HorizontalComparisonBar`: compact multi-value comparison for teams, stats, and contributions.
- `MiniBarChart`: responsive Recharts bar chart for small trends and distributions.
- `StackedShareBar`: share-of-whole bar for result splits, cards, and coverage.
- `ScatterComparisonPlot`: two-axis Recharts comparison for teams or players.
- `TimelineRail`: key match moments across 0-90+ minutes.
- `FormStrip`: W/D/L/N/A recent form display.
- `ScoreProgression`: readable score-change sequence after goals.
- `InsightEmptyState`: analytical empty state for pages and cards.

Example:

```tsx
<SignalChipGroup items={match.signal_labels} maxVisible={3} />
<DataQualityNote tone="caution" note={season.data_quality_note} compact />
```
