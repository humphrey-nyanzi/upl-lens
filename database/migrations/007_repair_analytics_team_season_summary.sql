CREATE SCHEMA IF NOT EXISTS analytics;

CREATE TABLE IF NOT EXISTS analytics.team_season_summary (
    season TEXT NOT NULL,
    team_name TEXT NOT NULL,
    matches_played INTEGER NOT NULL DEFAULT 0,
    goals_for INTEGER NOT NULL DEFAULT 0,
    goals_against INTEGER NOT NULL DEFAULT 0,
    wins INTEGER NOT NULL DEFAULT 0,
    draws INTEGER NOT NULL DEFAULT 0,
    losses INTEGER NOT NULL DEFAULT 0,
    refreshed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (season, team_name)
);

ALTER TABLE analytics.team_season_summary DISABLE ROW LEVEL SECURITY;

CREATE INDEX IF NOT EXISTS idx_team_season_summary_team_name
ON analytics.team_season_summary (team_name);

CREATE OR REPLACE FUNCTION analytics.refresh_team_season_summary(_target_seasons TEXT[] DEFAULT NULL)
RETURNS void
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM analytics.team_season_summary
    WHERE _target_seasons IS NULL OR season = ANY(_target_seasons);

    INSERT INTO analytics.team_season_summary (
        season,
        team_name,
        matches_played,
        goals_for,
        goals_against,
        wins,
        draws,
        losses,
        refreshed_at
    )
    WITH team_matches AS (
        SELECT
            season,
            home_team AS team_name,
            match_id,
            CASE WHEN result = 'home_win' THEN 1 ELSE 0 END AS wins,
            CASE WHEN result = 'draw' THEN 1 ELSE 0 END AS draws,
            CASE WHEN result = 'away_win' THEN 1 ELSE 0 END AS losses
        FROM staging.matches
        WHERE home_team IS NOT NULL
            AND is_source_anomaly IS NOT TRUE
            AND (_target_seasons IS NULL OR season = ANY(_target_seasons))
        UNION ALL
        SELECT
            season,
            away_team AS team_name,
            match_id,
            CASE WHEN result = 'away_win' THEN 1 ELSE 0 END AS wins,
            CASE WHEN result = 'draw' THEN 1 ELSE 0 END AS draws,
            CASE WHEN result = 'home_win' THEN 1 ELSE 0 END AS losses
        FROM staging.matches
        WHERE away_team IS NOT NULL
            AND is_source_anomaly IS NOT TRUE
            AND (_target_seasons IS NULL OR season = ANY(_target_seasons))
    ),
    actual_goals AS (
        SELECT
            events.season,
            events.match_id,
            events.team_name,
            COUNT(*) AS goals_for
        FROM staging.events AS events
        INNER JOIN staging.matches AS matches
            ON matches.match_id = events.match_id
        WHERE events.event_type IN ('goal', 'own_goal', 'penalty_goal')
            AND events.team_name IS NOT NULL
            AND matches.is_source_anomaly IS NOT TRUE
            AND (_target_seasons IS NULL OR events.season = ANY(_target_seasons))
        GROUP BY events.season, events.match_id, events.team_name
    ),
    team_rows AS (
        SELECT
            team_matches.season,
            team_matches.team_name,
            team_matches.match_id,
            team_matches.wins,
            team_matches.draws,
            team_matches.losses,
            COALESCE(for_goals.goals_for, 0) AS goals_for,
            COALESCE(against_goals.goals_for, 0) AS goals_against
        FROM team_matches
        LEFT JOIN actual_goals AS for_goals
            ON for_goals.season = team_matches.season
            AND for_goals.match_id = team_matches.match_id
            AND for_goals.team_name = team_matches.team_name
        LEFT JOIN actual_goals AS against_goals
            ON against_goals.season = team_matches.season
            AND against_goals.match_id = team_matches.match_id
            AND against_goals.team_name <> team_matches.team_name
    )
    SELECT
        season,
        team_name,
        COUNT(*)::integer AS matches_played,
        SUM(COALESCE(goals_for, 0))::integer AS goals_for,
        SUM(COALESCE(goals_against, 0))::integer AS goals_against,
        SUM(wins)::integer AS wins,
        SUM(draws)::integer AS draws,
        SUM(losses)::integer AS losses,
        NOW() AS refreshed_at
    FROM team_rows
    GROUP BY season, team_name;
END;
$$;
