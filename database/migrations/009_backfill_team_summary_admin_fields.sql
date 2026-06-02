UPDATE analytics.team_season_summary
SET
    played_matches = CASE
        WHEN COALESCE(played_matches, 0) = 0 AND matches_played > 0
        THEN matches_played
        ELSE played_matches
    END,
    sporting_points = CASE
        WHEN COALESCE(sporting_points, 0) = 0 AND (wins > 0 OR draws > 0)
        THEN wins * 3 + draws
        ELSE sporting_points
    END,
    official_points = CASE
        WHEN COALESCE(official_points, 0) = 0 AND (wins > 0 OR draws > 0)
        THEN wins * 3 + draws + COALESCE(points_adjustment, 0)
        ELSE official_points
    END
WHERE COALESCE(played_matches, 0) = 0
    OR COALESCE(sporting_points, 0) = 0
    OR COALESCE(official_points, 0) = 0;

SELECT analytics.refresh_team_season_summary(NULL);
