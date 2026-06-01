ALTER TABLE staging.matches
ADD COLUMN IF NOT EXISTS is_administrative_result BOOLEAN NOT NULL DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS administrative_result_type TEXT,
ADD COLUMN IF NOT EXISTS administrative_note TEXT,
ADD COLUMN IF NOT EXISTS played_on_pitch BOOLEAN NOT NULL DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS home_awarded_points INTEGER,
ADD COLUMN IF NOT EXISTS away_awarded_points INTEGER;

UPDATE staging.matches
SET
    is_administrative_result = is_forfeit,
    administrative_result_type = CASE
        WHEN is_forfeit THEN COALESCE(administrative_result_type, 'forfeit')
        ELSE administrative_result_type
    END,
    played_on_pitch = CASE WHEN is_forfeit THEN FALSE ELSE played_on_pitch END,
    home_awarded_points = CASE
        WHEN result = 'home_win' THEN 3
        WHEN result = 'draw' THEN 1
        WHEN result = 'away_win' THEN 0
        ELSE home_awarded_points
    END,
    away_awarded_points = CASE
        WHEN result = 'away_win' THEN 3
        WHEN result = 'draw' THEN 1
        WHEN result = 'home_win' THEN 0
        ELSE away_awarded_points
    END;

CREATE INDEX IF NOT EXISTS idx_staging_matches_admin_result
ON staging.matches (is_administrative_result);

ALTER TABLE analytics.team_season_summary
ADD COLUMN IF NOT EXISTS played_matches INTEGER NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS administrative_matches INTEGER NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS expected_matches INTEGER,
ADD COLUMN IF NOT EXISTS missing_matches INTEGER NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS sporting_points INTEGER NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS administrative_points INTEGER NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS points_adjustment INTEGER NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS official_points INTEGER NOT NULL DEFAULT 0,
ADD COLUMN IF NOT EXISTS points_note TEXT;

CREATE TABLE IF NOT EXISTS analytics.team_season_point_adjustments (
    season TEXT NOT NULL,
    team_name TEXT NOT NULL,
    points_adjustment INTEGER NOT NULL DEFAULT 0,
    note TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (season, team_name)
);

ALTER TABLE analytics.team_season_point_adjustments DISABLE ROW LEVEL SECURITY;

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
        played_matches,
        administrative_matches,
        expected_matches,
        missing_matches,
        goals_for,
        goals_against,
        wins,
        draws,
        losses,
        sporting_points,
        administrative_points,
        points_adjustment,
        official_points,
        points_note,
        refreshed_at
    )
    WITH app_safe_matches AS (
        SELECT *
        FROM staging.matches
        WHERE is_source_anomaly IS NOT TRUE
            AND (_target_seasons IS NULL OR season = ANY(_target_seasons))
    ),
    season_team_counts AS (
        SELECT
            season,
            COUNT(DISTINCT team_name)::integer AS team_count,
            GREATEST((COUNT(DISTINCT team_name)::integer - 1) * 2, 0) AS expected_matches
        FROM (
            SELECT season, home_team AS team_name FROM app_safe_matches WHERE home_team IS NOT NULL
            UNION
            SELECT season, away_team AS team_name FROM app_safe_matches WHERE away_team IS NOT NULL
        ) AS teams
        GROUP BY season
    ),
    team_matches AS (
        SELECT
            season,
            home_team AS team_name,
            match_id,
            COALESCE(played_on_pitch, TRUE) AS played_on_pitch,
            COALESCE(is_administrative_result, FALSE) AS is_administrative_result,
            COALESCE(home_awarded_points, CASE WHEN result = 'home_win' THEN 3 WHEN result = 'draw' THEN 1 ELSE 0 END) AS awarded_points,
            CASE WHEN result = 'home_win' THEN 1 ELSE 0 END AS wins,
            CASE WHEN result = 'draw' THEN 1 ELSE 0 END AS draws,
            CASE WHEN result = 'away_win' THEN 1 ELSE 0 END AS losses
        FROM app_safe_matches
        WHERE home_team IS NOT NULL
        UNION ALL
        SELECT
            season,
            away_team AS team_name,
            match_id,
            COALESCE(played_on_pitch, TRUE) AS played_on_pitch,
            COALESCE(is_administrative_result, FALSE) AS is_administrative_result,
            COALESCE(away_awarded_points, CASE WHEN result = 'away_win' THEN 3 WHEN result = 'draw' THEN 1 ELSE 0 END) AS awarded_points,
            CASE WHEN result = 'away_win' THEN 1 ELSE 0 END AS wins,
            CASE WHEN result = 'draw' THEN 1 ELSE 0 END AS draws,
            CASE WHEN result = 'home_win' THEN 1 ELSE 0 END AS losses
        FROM app_safe_matches
        WHERE away_team IS NOT NULL
    ),
    actual_goals AS (
        SELECT
            events.season,
            events.match_id,
            events.team_name,
            COUNT(*) AS goals_for
        FROM staging.events AS events
        INNER JOIN app_safe_matches AS matches
            ON matches.match_id = events.match_id
        WHERE events.event_type IN ('goal', 'own_goal', 'penalty_goal')
            AND events.team_name IS NOT NULL
            AND (_target_seasons IS NULL OR events.season = ANY(_target_seasons))
        GROUP BY events.season, events.match_id, events.team_name
    ),
    team_rows AS (
        SELECT
            team_matches.season,
            team_matches.team_name,
            team_matches.match_id,
            team_matches.played_on_pitch,
            team_matches.is_administrative_result,
            team_matches.awarded_points,
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
    ),
    team_summary AS (
        SELECT
            team_rows.season,
            team_rows.team_name,
            COUNT(*)::integer AS matches_played,
            COUNT(*) FILTER (WHERE played_on_pitch)::integer AS played_matches,
            COUNT(*) FILTER (WHERE is_administrative_result)::integer AS administrative_matches,
            COALESCE(season_team_counts.expected_matches, COUNT(*)::integer) AS expected_matches,
            GREATEST(COALESCE(season_team_counts.expected_matches, COUNT(*)::integer) - COUNT(*)::integer, 0) AS missing_matches,
            SUM(COALESCE(goals_for, 0))::integer AS goals_for,
            SUM(COALESCE(goals_against, 0))::integer AS goals_against,
            SUM(wins)::integer AS wins,
            SUM(draws)::integer AS draws,
            SUM(losses)::integer AS losses,
            SUM(awarded_points)::integer AS sporting_points,
            SUM(awarded_points) FILTER (WHERE is_administrative_result)::integer AS administrative_points
        FROM team_rows
        LEFT JOIN season_team_counts
            ON season_team_counts.season = team_rows.season
        GROUP BY team_rows.season, team_rows.team_name, season_team_counts.expected_matches
    )
    SELECT
        team_summary.season,
        team_summary.team_name,
        team_summary.matches_played,
        team_summary.played_matches,
        team_summary.administrative_matches,
        team_summary.expected_matches,
        team_summary.missing_matches,
        team_summary.goals_for,
        team_summary.goals_against,
        team_summary.wins,
        team_summary.draws,
        team_summary.losses,
        team_summary.sporting_points,
        COALESCE(team_summary.administrative_points, 0) AS administrative_points,
        COALESCE(adjustments.points_adjustment, 0) AS points_adjustment,
        team_summary.sporting_points + COALESCE(adjustments.points_adjustment, 0) AS official_points,
        NULLIF(CONCAT_WS(
            ' ',
            CASE
                WHEN team_summary.administrative_matches > 0
                THEN team_summary.administrative_matches || ' administrative result(s) included.'
            END,
            CASE
                WHEN team_summary.missing_matches > 0
                THEN team_summary.missing_matches || ' expected fixture(s) missing from app-safe data.'
            END,
            adjustments.note
        ), '') AS points_note,
        NOW() AS refreshed_at
    FROM team_summary
    LEFT JOIN analytics.team_season_point_adjustments AS adjustments
        ON adjustments.season = team_summary.season
        AND adjustments.team_name = team_summary.team_name;
END;
$$;
