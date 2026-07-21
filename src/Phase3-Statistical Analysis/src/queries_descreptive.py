class NBAPlayerExtractionQuaries:

    query_top50_league_players = """
    WITH LeaguePlayerPerformance AS (
    SELECT 
        p.id AS player_id,
        p.fullname,
        p.height,
        s.season_years,
        SUM(sp.pts + 1.5 * sp.assists + 2 * sp.total_rebounds + 3 * sp.steals + 3 * sp.block - sp.turnovers) AS performance_index
        FROM season_player sp
        JOIN players p ON sp.player_id = p.id
        JOIN season s ON sp.season_id = s.id
        WHERE s.season_years IN ('2019-2020', '2020-2021', '2021-2022', '2022-2023', '2023-2024')
        GROUP BY p.id, p.fullname, p.height, s.season_years
    )
    SELECT 
        player_id,
        fullname,
        MAX(height) AS height,
        SUM(performance_index) AS total_performance_index
    FROM LeaguePlayerPerformance
    GROUP BY player_id, fullname
    ORDER BY total_performance_index DESC
    LIMIT 50;"""

    query_top15_league_players_height = """
    WITH LeaguePlayerPerformance AS (
    SELECT 
        p.id AS player_id,
        p.fullname,
        p.height,
        s.season_years,
        SUM(sp.pts + 1.5 * sp.assists + 2 * sp.total_rebounds + 3 * sp.steals + 3 * sp.block - sp.turnovers) AS performance_index
        FROM season_player sp
        JOIN players p ON sp.player_id = p.id
        JOIN season s ON sp.season_id = s.id
        WHERE s.season_years IN ('2019-2020', '2020-2021', '2021-2022', '2022-2023', '2023-2024')
        GROUP BY p.id, p.fullname, p.height, s.season_years
    )
    SELECT 
        player_id,

        fullname,
        MAX(height) AS height,
        SUM(performance_index) AS total_performance_index
    FROM LeaguePlayerPerformance
    GROUP BY player_id, fullname
    ORDER BY total_performance_index DESC
    LIMIT 15;"""
    
    query_top15_league_players_experience = """
    WITH RankedLeaguePlayers AS (
        SELECT 
            p.id AS player_id,
            p.fullname,
            s.season_years,
            (
                SELECT COUNT(DISTINCT sp_sub.season_id)
                FROM season_player sp_sub
                JOIN season s_sub ON sp_sub.season_id = s_sub.id
                WHERE sp_sub.player_id = p.id AND s_sub.season_years <= s.season_years
            ) AS experience_years,
            SUM(sp.pts + 1.5 * sp.assists + 2 * sp.total_rebounds + 3 * sp.steals + 3 * sp.block - sp.turnovers) AS performance_index,
            ROW_NUMBER() OVER(PARTITION BY s.season_years ORDER BY SUM(sp.pts + 1.5 * sp.assists + 2 * sp.total_rebounds + 3 * sp.steals + 3 * sp.block - sp.turnovers) DESC) AS ranking
        FROM season_player sp
        JOIN players p ON sp.player_id = p.id
        JOIN season s ON sp.season_id = s.id
        WHERE s.season_years IN ('2019-2020', '2020-2021', '2021-2022', '2022-2023', '2023-2024')
        GROUP BY p.id, p.fullname, s.season_years
    )
    SELECT 
        player_id,
        fullname,
        experience_years,
        season_years,
        performance_index
    FROM RankedLeaguePlayers
    WHERE ranking <= 15;
    """


    query_micheljordan_tropy_list = """
    SELECT 
    p.id AS player_id,
    p.fullname,
    p.height,
    s.season_years,
    a.name AS mvp_award_name
    FROM awards a
    JOIN season_player sp ON a.season_player_id = sp.id
    JOIN players p ON sp.player_id = p.id
    JOIN season s ON sp.season_id = s.id
    WHERE a.name LIKE 'MVP%%';"""

    query_champions_top15_height = """
    WITH RankedPlayers AS (
        SELECT
            p.id AS player_id,
            p.fullname,
            p.height,
            s.season_years,
            c.name AS team_name,
            SUM(sp.pts + 1.5 * sp.assists + 2 * sp.total_rebounds + 3 * sp.steals + 3 * sp.block - sp.turnovers) AS performance_index,
            ROW_NUMBER() OVER(PARTITION BY s.season_years ORDER BY SUM(sp.pts + 1.5 * sp.assists + 2 * sp.total_rebounds + 3 * sp.steals + 3 * sp.block - sp.turnovers) DESC) AS ranking
        FROM season_player sp
        JOIN players p ON sp.player_id = p.id
        JOIN season s ON sp.season_id = s.id
        JOIN player_season_club psc ON psc.player_id = sp.player_id AND psc.season_id = sp.season_id
        JOIN clubs c ON psc.club_id = c.id
        WHERE s.season_years IN ('2022-2023', '2023-2024')
        AND c.champ = 1
        GROUP BY p.id, p.fullname, p.height, s.season_years, c.name
    )
    SELECT
        player_id,
        fullname,
        height,
        season_years,
        team_name,
        performance_index
    FROM RankedPlayers
    WHERE ranking <= 15;
    """

    query_champions_top15_experience = """WITH RankedPlayers AS (
        SELECT
            p.id AS player_id,
            p.fullname,
            (
                SELECT COUNT(DISTINCT sp_sub.season_id)
                FROM season_player sp_sub
                JOIN season s_sub ON sp_sub.season_id = s_sub.id
                WHERE sp_sub.player_id = p.id AND s_sub.season_years <= s.season_years
            ) AS experience_years,
            s.season_years,
            c.name AS team_name,
            SUM(sp.pts + 1.5 * sp.assists + 2 * sp.total_rebounds + 3 * sp.steals + 3 * sp.block - sp.turnovers) AS performance_index,
            ROW_NUMBER() OVER(PARTITION BY s.season_years ORDER BY SUM(sp.pts + 1.5 * sp.assists + 2 * sp.total_rebounds + 3 * sp.steals + 3 * sp.block - sp.turnovers) DESC) AS ranking
        FROM season_player sp
        JOIN players p ON sp.player_id = p.id
        JOIN season s ON sp.season_id = s.id
        JOIN player_season_club psc ON psc.player_id = sp.player_id AND psc.season_id = sp.season_id
        JOIN clubs c ON psc.club_id = c.id
        WHERE s.season_years IN ('2022-2023', '2023-2024')
        AND c.champ = 1
        GROUP BY p.id, p.fullname, p.height, s.season_years, c.name
    )
    SELECT
        player_id,
        fullname,
        experience_years,
        season_years,
        team_name,
        performance_index
    FROM RankedPlayers
    WHERE ranking <= 15;
    """

    query_suggested_players = """
    WITH SuggestedPlayers AS (
    SELECT 
        p.id AS player_id,
        p.fullname,
        COUNT(DISTINCT sp.season_id) AS mvp_nomination_count
    FROM players p
    JOIN player_position pp ON p.id = pp.player_id
    JOIN position pos ON pp.position_id = pos.id
    JOIN season_player sp ON p.id = sp.player_id
    JOIN season s ON sp.season_id = s.id
    JOIN awards a ON a.season_player_id = sp.id
    WHERE pos.name = 'Point Guard'
      AND a.name LIKE 'MVP%%'
      AND s.season_years IN ('2019-2020', '2020-2021', '2021-2022', '2022-2023', '2023-2024')
    GROUP BY p.id, p.fullname
    )
    SELECT 
    player_id,
    fullname,
    mvp_nomination_count
    FROM SuggestedPlayers
    ORDER BY mvp_nomination_count DESC
    """