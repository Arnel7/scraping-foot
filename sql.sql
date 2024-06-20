

CREATE TABLE matches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date_text VARCHAR(255),
    unix_timestamp BIGINT,
    team_a_logo_url VARCHAR(255),
    team_a_name VARCHAR(255),
    team_a_goal INT,
    team_b_logo_url VARCHAR(255),
    team_b_name VARCHAR(255),
    team_b_goal INT,
    day INT
);

CREATE TABLE stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    match_id INT,
    team_a_short VARCHAR(255),
    team_b_short VARCHAR(255),
    team_a_shots_on_target INT,
    team_b_shots_on_target INT,
    team_a_possession INT,
    team_b_possession INT,
    team_a_passes INT,
    team_b_passes INT,
    team_a_pass_accuracy INT,
    team_b_pass_accuracy INT,
    team_a_fouls INT,
    team_b_fouls INT,
    team_a_yellow_cards INT,
    team_b_yellow_cards INT,
    team_a_red_cards INT,
    team_b_red_cards INT,
    team_a_offsides INT,
    team_b_offsides INT,
    team_a_corners INT,
    team_b_corners INT,
    team_a_goal_times JSON,
    team_b_goal_times JSON,
    FOREIGN KEY (match_id) REFERENCES matches(id)
);
