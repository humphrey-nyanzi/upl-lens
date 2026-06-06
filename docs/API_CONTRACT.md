# API Contract

This is the frontend-facing API contract for UPL Lens intelligence-layer
pages.

Use this document when syncing `frontend/src/api/client.ts` and
`frontend/src/api/types.ts`, planning page upgrades, or checking whether a page
should use a routine intelligence module or a promoted insight.

The product boundary remains:

```text
Official UPL website = source record.
UPL Lens = analytical meaning layer.
```

Routine intelligence modules belong on normal pages. Promoted notebook-backed
insights belong in `/insights`.

## Endpoint Summary

| Endpoint | Purpose | Frontend pages using it | Important response fields | Caveats / data-quality notes | Status |
|---|---|---|---|---|---|
| `GET /health` | Database and API health check. | Global shell, About, Methodology, debug states | `status`, `database`, `latest_staging_run_id`, `latest_staging_completed_at` | Useful for freshness and service status only. | existing |
| `GET /seasons` | Available seasons and coverage. | Overview, Trends, Matches, Teams, Players, detail pages | `season`, `match_count`, `first_match_date`, `last_match_date`, `team_count` | Seasonal coverage may differ. | existing |
| `GET /seasons/overview` | Season pulse and aggregate summary for overview screens. | Overview, Methodology | `match_count`, `team_count`, `goal_count`, `timeline_goal_count`, `scoreline_goal_count`, `yellow_card_count`, `red_card_count`, `event_breakdown` | Use as the overview summary, not a full timeline feed. | extended |
| `GET /overview/intelligence` | Editorial overview modules: season pulse, notices, signal matches, team signals, data quality. | Overview | `season_pulse`, `things_to_notice`, `recent_signal_matches`, `team_signals`, `data_quality` | This is the page-level intelligence composition endpoint. | new |
| `GET /trends/seasons` | Season-by-season trend charts and comparison table. | Trends, Overview teasers, Methodology | `seasons[]`, `summary`, `goals_per_match`, `cards_per_match`, `home_win_share`, `away_win_share`, `draw_share`, `high_scoring_match_share`, `timeline_coverage_share`, `data_quality_status` | Coverage, administrative results, and source anomalies affect reliability. | new |
| `GET /matches` | Basic match list and lightweight archive filters. | Matches, Overview, team links | `match_id`, `home_team`, `away_team`, `result`, `timeline_status`, `match_url` | Use for simple lists. Prefer intelligence for triage surfaces. | existing |
| `GET /matches/intelligence` | Match triage list with backend-computed interest and signal labels. | Matches, Overview signal cards, Trends teasers | `interest_score`, `primary_signal`, `signal_labels`, `event_count`, `goal_count`, `yellow_card_count`, `red_card_count`, `late_goal_count`, `final_15_goal_count` | Supports sorting and signal filtering. Excludes source anomalies. | new |
| `GET /matches/{match_id}` | Match intelligence brief with event timeline, officials, stats, and extended summary fields. | Match Detail | `intelligence_summary`, `key_moments`, `event_phase_summary`, `score_progression`, `events`, `officials`, `stats`, `timeline_status` | Do not lead with the raw event list. Show key moments and caveats first. | extended |
| `GET /teams` | Team index with season summaries and rate fields. | Teams, Overview team signals | `goal_difference`, `goals_per_match`, `conceded_per_match`, `win_rate`, `points_per_match`, `profile_labels` | This is now an intelligence board, not a standings clone. | extended |
| `GET /teams/{team_slug}/profile` | Team dossier with split records, form, events, timing, discipline, and caveats. | Team Detail | `home_record`, `away_record`, `form`, `recent_matches`, `event_summary`, `goal_timing`, `discipline_summary`, `profile_labels`, `data_quality` | The page should combine record context with analytical signals. | new |
| `GET /players` | Player index with rankings and rate fields. | Players, player links | `goals`, `assists`, `appearances`, `starts`, `cards`, `goal_contributions`, `starts_share`, `profile_labels` | Use for browsing and sorting. | extended |
| `GET /players/leaderboards` | Grouped leaderboard slices for player contribution pages. | Players | `goals`, `assists`, `appearances`, `starts`, `goal_contributions`, `cards`, `bench_impact`, `data_quality_note` | This is the preferred page entrypoint for contribution boards. | new |
| `GET /players/{player_slug}` | Player contribution profile with season breakdown and trend fields. | Player Detail | `season_breakdown`, `recent_matches`, `goal_contributions`, `goals_per_appearance`, `assists_per_appearance`, `goal_contributions_per_appearance`, `starts_share`, `season_trend`, `data_quality_note` | Keep data-quality notes visible because player data depends on lineups and event parsing. | extended |
| `GET /events` | Raw event browse endpoint for deeper debugging or secondary detail views. | Match Detail, Team Detail, debugging | `event_type`, `minute_total`, `minute_period`, `team_name`, `player_name`, `goal_type` | Useful as supporting data, not as the default public story. | existing |
| `GET /officials` | Officials browse endpoint for contextual source data. | Match Detail, Methodology, debugging | `role`, `official_name`, `match_id` | Should be contextualized, not copied as a plain list unless needed. | existing |
| `GET /insights/goal-timing` | Promoted Feature 1 insight. | Insights, Goal Timing, Overview featured insight | `intervals`, `peak_interval`, `total_regular_time_goals`, `season_count`, `scope_key` | This is a featured insight, not a routine page widget. | existing |

## Frontend Notes

- Use `/overview/intelligence` and `/matches/intelligence` for richer overview
  and triage pages.
- Use `/teams/{team_slug}/profile` and `/players/leaderboards` to avoid
  rebuilding backend logic in React.
- Use `/matches/{match_id}` for match briefs, but show `key_moments` and
  `intelligence_summary` before any full event list.
- Use `data_quality_note`, `timeline_status`, `source_anomaly_reason`, and
  similar fields as visible caveats, not hidden footnotes.

## Sync Rule

When the backend contract changes:

1. Update this document.
2. Update `frontend/src/api/types.ts`.
3. Update `frontend/src/api/client.ts`.
4. Update the relevant page requirements and wireframes.
5. Update the roadmap if the implementation order changes.
