

-- This SQL query aggregates various football event statistics by season from the 'staging.events' table. It calculates the total number of assists, goals, yellow cards, red cards, and substitutions for each season.

SELECT 
    season,
    SUM(CASE WHEN event_type = 'assist' THEN 1 ELSE 0 END) AS total_assists,
    SUM(CASE WHEN event_type = 'goal' THEN 1 ELSE 0 END) AS total_goals,
    SUM(CASE WHEN event_type = 'yellow_card' THEN 1 ELSE 0 END) AS total_yellow_cards,
    SUM(CASE WHEN event_type = 'red_card' THEN 1 ELSE 0 END) AS total_red_cards,
    SUM(CASE WHEN is_substitution = TRUE THEN 1 ELSE 0 END) AS total_substitutions
FROM staging.events
GROUP BY season
ORDER BY season ASC;


-- This SQL query aggregates various football event statistics by season from the 'raw.events' table. It calculates the total number of assists, goals, yellow cards, red cards, and substitutions for each season.

SELECT 
    season,
    SUM(CASE WHEN event_type = 'assist' THEN 1 ELSE 0 END) AS total_assists,
    SUM(CASE WHEN event_type = 'goal' THEN 1 ELSE 0 END) AS total_goals,
    SUM(CASE WHEN event_type = 'yellow_card' THEN 1 ELSE 0 END) AS total_yellow_cards,
    SUM(CASE WHEN event_type = 'red_card' THEN 1 ELSE 0 END) AS total_red_cards,
    SUM(CASE WHEN event_type = 'substitution' THEN 1 ELSE 0 END) AS total_substitutions
FROM raw.events
GROUP BY season
ORDER BY season ASC; 


